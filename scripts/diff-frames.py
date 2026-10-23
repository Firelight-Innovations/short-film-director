"""Which frames changed between two renders? Ranges, and before/after sheets for a second review.

    python scripts/diff-frames.py <old.mp4> <new.mp4> [--threshold 2.0] [--out out/diff] [--per-range 6] [--max-sheets 40]

Both files are decoded side by side at 320 px wide. A frame's score is the
largest mean absolute difference (0..255, over R, G, B) of any 20 x 20 block,
so a changed word in one corner counts as much as a changed sky; the film-wide
mean would hide it. A frame changed when its score is above --threshold
(default 2.0, well above what re-encoding the same picture moves).

Prints the changed ranges (frames, seconds, sections, largest score) and writes
into --out (default out/diff):
  old/ new/ delta/     full-size frames from each file, and |new - old| x 4
  sheet-NN.jpg         one per group of nearby ranges (gaps under half a
                       second are joined): up to --per-range frames across
                       (first, largest change, last, and evenly between), rows
                       old, new and the difference
  frames.json          the ranges and, per sheet, its frames and tiles

Use it after the polish pass: keep the first graded file, re-render, re-grade,
then run this on the two graded files and give only these sheets to the short
second final review (final-review.js mode "diff"). On We Built a Mind the lead
looked at the changed frames itself; a fresh pair of eyes on a diff is cheap.

Run from the film project root (the timeline, if present, names the sections).
Exit codes: 0 written (whether or not anything changed), 2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

GW = 320
BLOCK = 20


def sibling(name: str):
    p = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_")[:-3], p)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # no __pycache__ in the project's scripts/
    spec.loader.exec_module(mod)
    return mod


def F(t: float, fps: float) -> int:
    return int(math.floor(t * fps + 0.5))


def reader(path: Path, gw: int, gh: int):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={gw}:{gh}:flags=area", "-fps_mode", "passthrough",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = gw * gh * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, np.uint8).reshape(gh, gw, 3)
    p.stdout.close()
    if p.wait() != 0:
        raise SystemExit(f"diff-frames: ffmpeg failed on {path}")


def main() -> int:
    ap = argparse.ArgumentParser(prog="diff-frames.py", description="Frames that changed between two renders, with before/after sheets.")
    ap.add_argument("old", help="the earlier render")
    ap.add_argument("new", help="the later render")
    ap.add_argument("--threshold", type=float, default=2.0, help="block score above which a frame changed (default 2.0)")
    ap.add_argument("--out", default="out/diff", help="output folder (default out/diff)")
    ap.add_argument("--per-range", type=int, default=6, help="frames shown across a sheet (default 6)")
    ap.add_argument("--max-sheets", type=int, default=40, help="most sheets to write (default 40)")
    a = ap.parse_args()
    old, new = Path(a.old), Path(a.new)
    for p in (old, new):
        if not p.exists():
            print(f"diff-frames: {p} not found")
            return 2
    ff = sibling("film-frames.py")
    try:
        io, inn = ff.probe(old), ff.probe(new)
    except FileNotFoundError:
        print("diff-frames: ffprobe not found on PATH")
        return 1
    if (io["w"], io["h"]) != (inn["w"], inn["h"]):
        print(f"diff-frames: warning: sizes differ ({io['w']}x{io['h']} and {inn['w']}x{inn['h']}); both are compared at {GW} px wide")
    fps = io["fps"] or 30.0
    tlp = Path("data/timeline.json")
    tl = json.loads(tlp.read_text(encoding="utf-8")) if tlp.exists() else {}
    if tl.get("fps"):
        fps = float(tl["fps"])
    sections = [(s["id"], F(s["from"], fps), F(s["to"], fps)) for s in tl.get("sections") or []]
    gh = max(BLOCK, 2 * round(GW * io["h"] / io["w"] / 2))
    by, bx = gh // BLOCK, GW // BLOCK

    scores, means = [], []
    for fa, fb in zip(reader(old, GW, gh), reader(new, GW, gh)):
        d = np.abs(fa.astype(np.int16) - fb.astype(np.int16)).astype(np.float32).mean(axis=2)
        blocks = d[: by * BLOCK, : bx * BLOCK].reshape(by, BLOCK, bx, BLOCK).mean(axis=(1, 3))
        scores.append(float(blocks.max()))
        means.append(float(d.mean()))
    n = len(scores)
    scores_a = np.array(scores)
    changed = np.nonzero(scores_a > a.threshold)[0]
    ranges: list[list[int]] = []
    for f in changed:
        if ranges and f == ranges[-1][1] + 1:
            ranges[-1][1] = int(f)
        else:
            ranges.append([int(f), int(f)])

    def secs(f0: int, f1: int) -> list[str]:
        return [sid for sid, s0, s1 in sections if s0 <= f1 and f0 < s1]

    print(f"diff-frames: {old.as_posix()} ({io['frames']} frames) -> {new.as_posix()} ({inn['frames']} frames)")
    if io["frames"] != inn["frames"]:
        print(f"WARN: frame counts differ; compared the first {n}")
    print(f"block score (largest {BLOCK}x{BLOCK} block mean abs diff at {GW}x{gh}): median {np.median(scores_a):.2f}, "
          f"max {scores_a.max():.2f}; threshold {a.threshold:g}")
    print(f"{len(changed)} of {n} frames changed, in {len(ranges)} ranges")
    for f0, f1 in ranges[:60]:
        mx = float(scores_a[f0:f1 + 1].max())
        print(f"  f{f0}..f{f1} ({f0 / fps:.2f}-{(f1 + 1) / fps:.2f} s, {f1 - f0 + 1} frames) {' '.join(secs(f0, f1))}: largest {mx:.1f}")
    if len(ranges) > 60:
        print(f"  ... {len(ranges) - 60} more in frames.json")

    out = Path(a.out)
    for sub in ("old", "new", "delta"):
        shutil.rmtree(out / sub, ignore_errors=True)
    if out.exists():
        for f in list(out.glob("sheet-*.jpg")) + [out / "frames.json"]:
            if f.exists():
                f.unlink()
    out.mkdir(parents=True, exist_ok=True)

    groups: list[list[list[int]]] = []
    for r in ranges:
        if groups and r[0] - groups[-1][-1][1] <= int(fps / 2):
            groups[-1].append(r)
        else:
            groups.append([r])
    picks: list[list[int]] = []
    for g in groups[: a.max_sheets]:
        f0, f1 = g[0][0], g[-1][1]
        frames_in = [f for r in g for f in range(r[0], r[1] + 1)]
        peak = max(frames_in, key=lambda f: scores[f])
        k = max(1, a.per_range)
        chosen = {f0, f1, peak}
        if len(frames_in) > len(chosen):
            for x in np.linspace(0, len(frames_in) - 1, k):
                if len(chosen) >= k:
                    break
                chosen.add(frames_in[int(round(x))])
        picks.append(sorted(chosen)[:k] if len(chosen) > k else sorted(chosen))
    if len(groups) > a.max_sheets:
        print(f"WARN: {len(groups)} groups of changes; sheets for the first {a.max_sheets} only")

    sheets = []
    if picks:
        name = lambda f: f"f{f:04d}_t{f / fps:06.2f}.jpg"
        wanted_old = {(f, None): [out / "old" / name(f)] for p in picks for f in p}
        wanted_new = {(f, None): [out / "new" / name(f)] for p in picks for f in p}
        try:
            ff.grab(old, wanted_old)
            ff.grab(new, wanted_new)
        except FileNotFoundError:
            print("diff-frames: ffmpeg not found on PATH")
            return 1
        from PIL import Image
        (out / "delta").mkdir(parents=True, exist_ok=True)
        make_sheet = sibling("sheet.py").make_sheet
        for i, p in enumerate(picks):
            files, labels = [], []
            for f in p:
                po, pn = out / "old" / name(f), out / "new" / name(f)
                if po.exists() and pn.exists():
                    with Image.open(po) as A, Image.open(pn) as B:
                        B = B.convert("RGB").resize(A.size) if B.size != A.size else B.convert("RGB")
                        dlt = np.clip(np.abs(np.asarray(A.convert("RGB"), np.int16) - np.asarray(B, np.int16)) * 4, 0, 255).astype(np.uint8)
                    Image.fromarray(dlt).save(out / "delta" / name(f), quality=90)
            ok = [f for f in p if (out / "old" / name(f)).exists() and (out / "new" / name(f)).exists()]
            for row in ("old", "new", "delta"):
                for f in ok:
                    files.append(out / row / name(f))
                    labels.append(f"f{f} {f / fps:.2f}s {row if row != 'delta' else 'diff x4'} ({scores[f]:.1f})")
            if not ok:
                continue
            g = groups[i]
            file = out / f"sheet-{i + 1:02d}.jpg"
            make_sheet(file, files, cols=len(ok), width=480, labels=labels,
                       title=f"changed f{g[0][0]}..f{g[-1][1]} ({g[0][0] / fps:.2f}-{(g[-1][1] + 1) / fps:.2f} s) "
                             f"{' '.join(secs(g[0][0], g[-1][1]))}: rows old, new, difference x4")
            sheets.append({"file": file.as_posix(), "from": g[0][0], "to": g[-1][1], "frames": ok,
                           "ranges": [[r[0], r[1]] for r in g]})
    info = {"old": old.as_posix(), "new": new.as_posix(), "fps": fps, "frames_compared": n,
            "frames_old": io["frames"], "frames_new": inn["frames"], "threshold": a.threshold,
            "metric": f"largest {BLOCK}x{BLOCK} block mean abs RGB difference at {GW}x{gh}, 0..255",
            "changed_frames": int(len(changed)),
            "ranges": [{"from": r[0], "to": r[1], "t_from": round(r[0] / fps, 3), "t_to": round((r[1] + 1) / fps, 3),
                        "largest": round(float(scores_a[r[0]:r[1] + 1].max()), 2), "sections": secs(r[0], r[1])} for r in ranges],
            "sheets": sheets}
    (out / "frames.json").write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(sheets)} sheets and frames.json to {out.as_posix()}")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
