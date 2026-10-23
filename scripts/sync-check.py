"""Does the picture move when the music does? Picture-change peaks against the measured music.

    python scripts/sync-check.py <film.mp4> [--sections] [--tol 2] [--min-onset 0.25] [--peak 3]

Takes the per-frame change trace of motion-check.py (192 px grey, mean absolute
difference) and finds its peaks: frames whose change is at least --peak (default
3, on 0..255) and twice the median of the half second around them, and the
largest within two frames either side. Each peak is matched to the nearest
event in data/beats.json: beat, downbeat, onset (strength at least
--min-onset), hit, fitted pulse. Distances are signed frames, event minus
picture: +1 means the music lands one frame after the picture moved.

Prints, for the film or per section (--sections): the number of peaks, the
share within --tol frames of an event ("on the beat"), the median distance, the
correlation between picture change and the music's onset curve, and the
off-beat moves (peaks further than --tol from every event), biggest first.
Peaks after the music has ended are counted apart. Writes out/sync/<name>.csv.

This is the measured half of the sound gate: on We Built a Mind no agent heard
the film, and sync was never checked after the cut. A person still watches the
graded file with the sound on. A visual move within about 45 ms of the sound
reads as together (ITU-R BT.1359 puts detectability at +45 ms / -125 ms),
which is about one and a half frames at 30 fps; --tol 2 allows two.

Run from the film project root. Exit codes: 0 (it reports, it does not judge),
2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

KINDS = ("beat", "down", "onset", "hit", "pulse")


def sibling(name: str):
    p = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_")[:-3], p)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # no __pycache__ in the project's scripts/
    spec.loader.exec_module(mod)
    return mod


def F(t: float, fps: float) -> int:
    return int(math.floor(t * fps + 0.5))


def main() -> int:
    ap = argparse.ArgumentParser(prog="sync-check.py", description="Picture-change peaks against beats.json onsets and beats.")
    ap.add_argument("film", help="the render (mp4) or a folder of sequential frames")
    ap.add_argument("--sections", action="store_true", help="report per section")
    ap.add_argument("--tol", type=float, default=2, help="frames between a peak and an event that still count as on it (default 2)")
    ap.add_argument("--min-onset", type=float, default=0.25, help="weakest onset that counts, 0..1 (default 0.25)")
    ap.add_argument("--peak", type=float, default=3.0, help="smallest change that counts as a picture move (default 3)")
    ap.add_argument("--out", default="out/sync", help="folder for <name>.csv (default out/sync)")
    a = ap.parse_args()
    src = Path(a.film)
    if not src.exists():
        print(f"sync-check: {src} not found")
        return 2
    tlp, bp = Path("data/timeline.json"), Path("data/beats.json")
    if not tlp.exists():
        print("sync-check: no data/timeline.json here; run from the film project root")
        return 2
    tl = json.loads(tlp.read_text(encoding="utf-8"))
    beats = json.loads(bp.read_text(encoding="utf-8")) if bp.exists() else {}
    fps = float(tl["fps"])
    snap = sibling("snap.py")
    ev = snap.load_events(beats, fps, a.min_onset)
    ev = {k: ev[k] for k in KINDS}
    if not any(ev.values()):
        print("sync-check: data/beats.json has no events (no track, or analyze_music.py not run); nothing to sync to")
        return 0
    end = snap.music_end(beats, tl)
    try:
        pc = sibling("motion-check.py").picture_change(src, 0.0, 0.0, fps)
    except FileNotFoundError:
        print("sync-check: ffmpeg or ffprobe not found on PATH")
        return 1
    ns, d = pc["frames"], pc["d"]
    if abs(pc["fps"] - fps) > 0.01:
        print(f"WARN: the file runs at {pc['fps']:g} fps, the timeline at {fps:g}")
    dd = np.nan_to_num(d, nan=0.0)
    half = int(round(fps / 4))
    peaks = []
    for i in range(1, len(dd)):
        v = dd[i]
        if v < a.peak:
            continue
        lo, hi = max(1, i - 2), min(len(dd), i + 3)
        if v < dd[lo:hi].max():
            continue
        around = np.concatenate([dd[max(1, i - half):i], dd[i + 1:i + half + 1]])
        if len(around) and v < 2 * float(np.median(around)):
            continue
        peaks.append((int(ns[i]), float(v)))

    sections = [(s["id"], F(s["from"], fps), F(s["to"], fps)) for s in tl.get("sections") or []]
    starts = {f0 for _, f0, _ in sections}

    def sec_of(f: int) -> str:
        for sid, f0, f1 in sections:
            if f0 <= f < f1:
                return sid
        return ""

    rows = []
    for f, v in peaks:
        best = None
        for k, evs in ev.items():
            dist = snap.nearest(evs, f)
            if dist is not None and (best is None or abs(dist) < abs(best[1])):
                best = (k, dist)
        silent = end is not None and f > end * fps + 1
        rows.append({"frame": f, "t": f / fps, "section": sec_of(f), "change": v, "kind": best[0] if best else "",
                     "dist": best[1] if best else math.nan, "silent": silent, "cut": f in starts})

    onset_curve = np.array((beats.get("frames") or {}).get("onset") or [], float)

    def corr(f0: int, f1: int) -> float | None:
        if not len(onset_curve):
            return None
        m = (ns >= f0) & (ns < min(f1, len(onset_curve)))
        if m.sum() < 10:
            return None
        x, y = dd[m], onset_curve[ns[m]]
        if x.std() == 0 or y.std() == 0:
            return None
        return float(np.corrcoef(x, y)[0, 1])

    def report(label: str, f0: int, f1: int, show: int) -> None:
        rs = [r for r in rows if f0 <= r["frame"] < f1]
        live = [r for r in rs if not r["silent"]]
        on = [r for r in live if abs(r["dist"]) <= a.tol]
        off = sorted([r for r in live if abs(r["dist"]) > a.tol], key=lambda r: -r["change"])
        med = float(np.median([abs(r["dist"]) for r in live])) if live else math.nan
        c = corr(f0, f1)
        share = f"{len(on) / len(live):.0%}" if live else "-"
        print(f"  {label:<22}{len(rs):>6}{len(live):>6}{share:>7}{med:>8.1f}{('-' if c is None else f'{c:+.2f}'):>10}{len(rs) - len(live):>8}")
        for r in off[:show]:
            print(f"      off-beat f{r['frame']} ({r['t']:.2f} s): change {r['change']:.1f}, nearest {r['kind']} {r['dist']:+.1f} frames"
                  + ("  (section start)" if r["cut"] else ""))

    print(f"sync-check: {src.as_posix()}  {len(ns)} frames; {len(peaks)} picture-change peaks (change >= {a.peak:g}); "
          f"events: " + ", ".join(f"{len(v)} {k}" for k, v in ev.items()) + (f"; music ends {end:.2f} s" if end else ""))
    print(f"  {'':<22}{'peaks':>6}{'live':>6}{'on':>7}{'median':>8}{'r(onset)':>10}{'silent':>8}")
    total = F(tl["dur"], fps)
    if a.sections:
        for sid, f0, f1 in sections:
            report(sid, f0, f1, 8)
    else:
        report("film", 0, total, 20)
    print(f"  on = share of peaks during the music within {a.tol:g} frames of an event; median = median distance in frames; "
          f"r(onset) = correlation of change with the onset curve")

    name = src.stem if src.is_file() else src.name
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / f"{name}.csv").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("frame,t,section,change,nearest,distance_frames,during_music,section_start\n")
        for r in rows:
            dist = "" if math.isnan(r["dist"]) else f"{r['dist']:+.2f}"
            fh.write(f"{r['frame']},{r['t']:.4f},{r['section']},{r['change']:.3f},{r['kind']},{dist},"
                     f"{int(not r['silent'])},{int(r['cut'])}\n")
    print(f"wrote {(out / (name + '.csv')).as_posix()}")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
