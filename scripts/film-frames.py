"""Frames out of a FINISHED file for the final review: by clock, by cue, by transition, at phone size.

    python scripts/film-frames.py <film.mp4> [--every 0.5] [--last 3] [--out out/final-review]

Reads the delivered mp4 itself (usually out/<slug>-graded.mp4), so the reviewer
judges what a viewer gets: grade, grain, vignette, encode. Writes into --out:

  clock/        one frame every --every seconds (default 0.5), 960 px wide
  last/         every frame of the last --last seconds (default 3) before the
                first checks.black range, and six frames into it (or the end of
                the film when there is no black range), 960 px
  cues/         every cue's first frame + 2 (is the line whole when it should be
                readable?) and its midpoint, full size
  transitions/  every transition window's first and last frame (a hard cut:
                the frame before and the cut frame), full size
  full/         key stills at full size: first and last frame, the frames around
                the cut to black, every cut frame, every section's midpoint, the
                midpoint of every data, quote, thesis and logo cue
  clock-NN.jpg  last-NN.jpg  cues-NN.jpg  transitions-NN.jpg
                contact sheets, 24 tiles of 480 px, labelled with frame, time
                and (for cues and transitions) the id
  phone-NN.jpg  every cue's midpoint as a 360 px tile, three across, so a
                sheet is seen at phone size without being scaled down again
  frames.json   every sheet with its tiles (frame, time, label, image file)

Why: on We Built a Mind a half-second clock missed two seven-frame words, and
the one broken item in the film was a chart that only failed at phone size.
Frames are named f<frame>_t<seconds>, as shots.mjs names them. The file is
decoded once: ffmpeg splits it into branches that each select up to 25 terms,
because its expression parser fails on a few hundred.

Run from the film project root. Exit codes: 0 written, 2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TERMS_PER_BRANCH = 25
BRANCHES_PER_RUN = 12


def sibling(name: str):
    p = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_")[:-3], p)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # no __pycache__ in the project's scripts/
    spec.loader.exec_module(mod)
    return mod


def F(t: float, fps: float) -> int:
    return int(math.floor(t * fps + 0.5))


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,avg_frame_rate,nb_frames", "-of", "json", str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"ffprobe could not read {path}")
    st = json.loads(out.stdout)["streams"][0]
    n = st.get("nb_frames")
    if not n or not str(n).isdigit():
        cnt = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                              "stream=nb_read_packets", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        n = cnt.stdout.strip() or "0"
    a, _, b = st.get("avg_frame_rate", "30/1").partition("/")
    return {"w": int(st["width"]), "h": int(st["height"]), "frames": int(n), "fps": float(a) / float(b or 1)}


def terms_for(frames: list[int]) -> list[str]:
    """Short select terms for a sorted frame list: runs and regular steps become one term each."""
    terms, i = [], 0
    while i < len(frames):
        j = i
        while j + 1 < len(frames) and frames[j + 1] == frames[j] + 1:
            j += 1
        if j - i >= 2:
            terms.append(f"between(n\\,{frames[i]}\\,{frames[j]})")
            i = j + 1
            continue
        if i + 3 < len(frames):
            step = frames[i + 1] - frames[i]
            k = i + 1
            while k + 1 < len(frames) and frames[k + 1] - frames[k] == step:
                k += 1
            if k - i >= 3:
                terms.append(f"between(n\\,{frames[i]}\\,{frames[k]})*not(mod(n-{frames[i]}\\,{step}))")
                i = k + 1
                continue
        terms.append(f"eq(n\\,{frames[i]})")
        i += 1
    return terms


def grab(src: Path, wanted: dict[tuple[int, int | None], list[Path]], quality: int = 2) -> list[int]:
    """Write frames of src to files in as few decodes as possible.

    wanted maps (frame, width or None for full size) to the files that frame goes to.
    Returns the frames that could not be read (past the end of the file)."""
    by_width: dict[int | None, list[int]] = {}
    for (f, w) in wanted:
        by_width.setdefault(w, []).append(f)
    branches: list[tuple[int | None, list[int], list[str]]] = []
    for w, frames in by_width.items():
        frames = sorted(set(frames))
        chunk: list[int] = []
        for f in frames:
            if len(terms_for(chunk + [f])) > TERMS_PER_BRANCH:
                branches.append((w, chunk, terms_for(chunk)))
                chunk = []
            chunk.append(f)
        if chunk:
            branches.append((w, chunk, terms_for(chunk)))
    missing: list[int] = []
    with tempfile.TemporaryDirectory(prefix="film-frames-") as tmp:
        tmpd = Path(tmp)
        for r0 in range(0, len(branches), BRANCHES_PER_RUN):
            run = branches[r0:r0 + BRANCHES_PER_RUN]
            k = len(run)
            graph = [f"[0:v]split={k}" + "".join(f"[s{i}]" for i in range(k)) if k > 1 else "[0:v]null[s0]"]
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src)]
            outs = []
            for i, (w, frames, terms) in enumerate(run):
                scale = f",scale={w}:-2:flags=lanczos" if w else ""
                graph.append(f"[s{i}]select='{'+'.join(terms)}'{scale}[o{i}]")
                pat = tmpd / f"r{r0:03d}b{i:02d}_%05d.jpg"
                outs += ["-map", f"[o{i}]", "-fps_mode", "passthrough", "-q:v", str(quality), str(pat)]
            cmd += ["-filter_complex", ";".join(graph)] + outs
            p = subprocess.run(cmd, capture_output=True, text=True)
            if p.returncode != 0:
                raise SystemExit(f"ffmpeg failed: {p.stderr.strip()[:400]}")
            for i, (w, frames, _) in enumerate(run):
                got = sorted(tmpd.glob(f"r{r0:03d}b{i:02d}_*.jpg"))
                for f, file in zip(frames, got):
                    dests = wanted[(f, w)]
                    for d in dests[1:]:
                        d.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(file, d)
                    dests[0].parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file), dests[0])
                missing += frames[len(got):]
    return sorted(set(missing))


def main() -> int:
    ap = argparse.ArgumentParser(prog="film-frames.py", description="Frames, sheets and frames.json from a finished film, for the final review.")
    ap.add_argument("film", help="the finished mp4 (usually out/<slug>-graded.mp4)")
    ap.add_argument("--every", type=float, default=0.5, help="seconds between clock samples (default 0.5)")
    ap.add_argument("--last", type=float, default=3.0, help="seconds before the first black range (or the end) dumped frame by frame (default 3)")
    ap.add_argument("--out", default="out/final-review", help="output folder (default out/final-review)")
    a = ap.parse_args()
    src = Path(a.film)
    if not src.exists():
        print(f"film-frames: {src} not found")
        return 2
    tlp = Path("data/timeline.json")
    if not tlp.exists():
        print("film-frames: no data/timeline.json here; run from the film project root")
        return 2
    tl = json.loads(tlp.read_text(encoding="utf-8"))
    fps = float(tl["fps"])
    try:
        info = probe(src)
    except FileNotFoundError:
        print("film-frames: ffprobe not found on PATH")
        return 1
    N = info["frames"]
    expected = F(tl["dur"], fps)
    if N != expected:
        print(f"WARN: the file has {N} frames, the timeline {expected}")
    out = Path(a.out)
    for sub in ("clock", "last", "cues", "transitions", "full"):
        shutil.rmtree(out / sub, ignore_errors=True)
    if out.exists():
        mine = [f for pre in ("clock", "last", "cues", "transitions", "phone") for f in out.glob(f"{pre}-[0-9][0-9]*.jpg")]
        for f in mine + [out / "frames.json"]:
            if f.exists():
                f.unlink()
    out.mkdir(parents=True, exist_ok=True)

    def name(f: int, suffix: str = "") -> str:
        return f"f{f:04d}_t{f / fps:06.2f}" + (f"_{suffix}" if suffix else "") + ".jpg"

    wanted: dict[tuple[int, int | None], list[Path]] = {}
    groups: dict[str, list[tuple[int, Path, str]]] = {k: [] for k in ("clock", "last", "cues", "transitions", "full", "phone")}

    def want(group: str, f: int, width: int | None, suffix: str = "", label: str | None = None) -> None:
        if not 0 <= f < N:
            return
        p = out / group / name(f, suffix)
        lst = wanted.setdefault((f, width), [])
        if p not in lst:
            lst.append(p)
        groups[group].append((f, p, label or p.stem))

    step = max(1, F(a.every, fps))
    for f in range(0, N, step):
        want("clock", f, 960)
    blacks = sorted(F(r[0], fps) for r in (tl.get("checks") or {}).get("black") or [])
    B = blacks[0] if blacks else None
    end = B if B is not None else N
    for f in range(max(0, end - F(a.last, fps)), min(N, end + 6) if B is not None else N):
        want("last", f, 960)
    cues = tl.get("cues") or []
    for c in cues:
        f0, f1 = F(c["from"], fps), F(c["to"], fps)
        first = f0 + 2 if f0 + 2 < f1 else f0
        mid = F((c["from"] + c["to"]) / 2, fps)
        cid = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in str(c["id"]))
        want("cues", first, None, f"{cid}-first")
        want("cues", mid, None, f"{cid}-mid")
        groups["phone"].append((mid, out / "cues" / name(mid, f"{cid}-mid"), f"{cid} {mid / fps:.2f}s"))
    for tr in tl.get("transitions") or []:
        if not tr.get("a") or not tr.get("b"):
            continue
        at, wa, wb = F(tr["at"], fps), F(tr["at"] - tr.get("pre", 0), fps), F(tr["at"] + tr.get("post", 0), fps)
        tid = str(tr["id"])
        if wb > wa:
            want("transitions", wa, None, f"{tid}-first")
            want("transitions", wb - 1, None, f"{tid}-last")
        else:
            want("transitions", at - 1, None, f"{tid}-before")
            want("transitions", at, None, f"{tid}-cut")
    keys = {0, N - 1}
    if B is not None:
        keys |= {B - 1, B, B + 1}
    for tr in tl.get("transitions") or []:
        f = F(tr["at"], fps)
        if 0 < f < N:
            keys.add(f)
    for s in tl.get("sections") or []:
        keys.add(F((s["from"] + s["to"]) / 2, fps))
    for c in cues:
        if c.get("role") in ("data", "quote", "thesis", "logo"):
            keys.add(F((c["from"] + c["to"]) / 2, fps))
    for f in sorted(keys):
        want("full", f, None)

    try:
        missing = grab(src, wanted)
    except FileNotFoundError:
        print("film-frames: ffmpeg not found on PATH")
        return 1
    if missing:
        print(f"WARN: {len(missing)} frames could not be read: {missing[:10]}")

    make_sheet = sibling("sheet.py").make_sheet
    sheets = []

    def sheet_set(group: str, prefix: str, per: int, cols: int, width: int, title: str) -> None:
        items = [(f, p, lab) for f, p, lab in groups[group] if p.exists()]
        if group in ("clock", "last", "full"):
            items = sorted({p: (f, p, lab) for f, p, lab in items}.values())
        for i in range(0, len(items), per):
            part = items[i:i + per]
            file = out / f"{prefix}-{i // per + 1:02d}.jpg"
            make_sheet(file, [p for _, p, _ in part], cols=cols, width=width,
                       title=f"{title} ({i // per + 1}/{math.ceil(len(items) / per)})", labels=[lab for _, _, lab in part])
            sheets.append({"file": file.as_posix(), "kind": group if group != "phone" else "phone", "tile_width": width, "cols": cols,
                           "tiles": [{"frame": f, "t": round(f / fps, 3), "label": lab, "image": p.as_posix()} for f, p, lab in part]})

    sheet_set("clock", "clock", 24, 6, 480, f"every {a.every:g} s")
    sheet_set("last", "last", 24, 6, 480, f"every frame, last {a.last:g} s" + (" before black" if B is not None else ""))
    sheet_set("cues", "cues", 24, 6, 480, "every cue: first frame + 2, midpoint")
    sheet_set("transitions", "transitions", 24, 6, 480, "every transition: first and last frame of the window")
    sheet_set("phone", "phone", 12, 3, 360, "phone size (360 px): every cue's midpoint")

    info_json = {
        "source": src.as_posix(), "fps": fps, "frames": N, "timeline_frames": expected,
        "cut_to_black_frame": B, "every": a.every, "last_seconds": a.last,
        "folders": {g: (out / g).as_posix() for g in ("clock", "last", "cues", "transitions", "full")},
        "full_size": sorted(p.as_posix() for _, p, _ in groups["full"] if p.exists()),
        "sheets": sheets,
        "missing_frames": missing,
    }
    (out / "frames.json").write_text(json.dumps(info_json, indent=1) + "\n", encoding="utf-8")
    counts = {g: len({p for _, p, _ in groups[g]}) for g in groups}
    print(f"film-frames: {src.as_posix()} ({N} frames) -> {out.as_posix()}")
    print(f"  clock {counts['clock']}, last {counts['last']}, cues {counts['cues']}, transitions {counts['transitions']}, "
          f"full {counts['full']}; {len(sheets)} sheets ({sum(1 for s in sheets if s['kind'] == 'phone')} phone-size); frames.json")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
