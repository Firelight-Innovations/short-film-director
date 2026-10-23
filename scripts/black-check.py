"""Measure the frames that must be black, the last frame and the letterbox bars of a finished file.

    python scripts/black-check.py <film.mp4> [--tol 2] [--bar-tol 12] [--every 7]

Reads data/timeline.json:
  checks.black      [[from, to], ...] seconds; every frame in [F(from), F(to)) must be black
  checks.lastFrameBlack
  letterbox         bar height as a fraction of h; 0 means no bars and no bar test
For each black range it prints the three frames before it and the first four in
it, then the whole range's brightest value, and names the first frame that is
not black. Then the last four frames of the file. Then the bars on every
--every-th frame: top and bottom, leaving out the two rows of each bar that
touch the picture, where the encoder rings.

Luma is read through ffmpeg's gray format, which is full range: 0 is black,
whatever range the file uses. A frame counts as black when its brightest pixel
is at most --tol (default 2); a bar may reach --bar-tol (default 12) from
ringing. Why this exists: on We Built a Mind the bars came out grey (RGB 16)
against picture black, and grain landed on the first black frame because the
grade was gated by seconds instead of frame number. Frames are streamed one at
a time, so a long film is walked without holding it in memory.

Run from the film project root. Exit codes: 0 PASS, 3 FAIL, 2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

EDGE = 2  # rows of a bar next to the picture that are not measured


def F(t: float, fps: float) -> int:
    return int(math.floor(t * fps + 0.5))


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,avg_frame_rate,nb_frames", "-of", "json", str(path)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"black-check: ffprobe could not read {path}")
    st = json.loads(out.stdout)["streams"][0]
    n = st.get("nb_frames")
    if not n or not str(n).isdigit():
        cnt = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                              "stream=nb_read_packets", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        n = cnt.stdout.strip() or "0"
    a, _, b = st.get("avg_frame_rate", "0/1").partition("/")
    return {"w": int(st["width"]), "h": int(st["height"]), "frames": int(n), "fps": float(a) / float(b or 1)}


def stream(path: Path, w: int, h: int, terms: list[str], pred, limit: int):
    """Yield (n, gray frame) for the frames ffmpeg's select keeps. pred(n) must match the expression."""
    expr = "+".join(terms)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"select='{expr}'", "-fps_mode", "passthrough",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    size = w * h
    n = -1
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        n += 1
        while not pred(n):
            n += 1
            if n > limit:
                raise SystemExit("black-check: frame numbering lost (select and its predicate disagree)")
        yield n, np.frombuffer(buf, np.uint8).reshape(h, w)
    p.stdout.close()
    if p.wait() != 0:
        raise SystemExit("black-check: ffmpeg failed while decoding")


def main() -> int:
    ap = argparse.ArgumentParser(prog="black-check.py", description="Black ranges, last frame and letterbox bars of a finished file (exit 3 on FAIL).")
    ap.add_argument("film", help="the finished mp4, usually out/<slug>-graded.mp4")
    ap.add_argument("--tol", type=int, default=2, help="brightest pixel allowed on a black frame, 0..255 full range (default 2)")
    ap.add_argument("--bar-tol", type=int, default=12, help="brightest pixel allowed in a bar (default 12)")
    ap.add_argument("--every", type=int, default=7, help="test the bars on every n-th frame (default 7)")
    a = ap.parse_args()
    path = Path(a.film)
    if not path.exists():
        print(f"black-check: {path} not found")
        return 2
    tlp = Path("data/timeline.json")
    if not tlp.exists():
        print("black-check: no data/timeline.json here; run from the film project root")
        return 2
    tl = json.loads(tlp.read_text(encoding="utf-8"))
    fps = float(tl["fps"])
    try:
        info = probe(path)
    except FileNotFoundError:
        print("black-check: ffprobe not found on PATH")
        return 1
    W, H, N = info["w"], info["h"], info["frames"]
    expected = F(tl["dur"], fps)
    checks = tl.get("checks") or {}
    ranges = [(F(r[0], fps), F(r[1], fps)) for r in checks.get("black") or []]
    last_black = bool(checks.get("lastFrameBlack"))
    bar = int(math.floor(H * float(tl.get("letterbox") or 0) + 0.5))
    print(f"black-check: {path.as_posix()}  {W}x{H}, {N} frames at {info['fps']:g} fps")
    bad: list[str] = []
    if N != expected:
        print(f"WARN: the file has {N} frames; the timeline says {expected} ({tl['dur']} s at {fps:g} fps)")
    if abs(info["fps"] - fps) > 0.01:
        print(f"WARN: the file runs at {info['fps']:g} fps, the timeline at {fps:g}")

    # One decode: every frame any test needs, chosen by one short select expression.
    every = max(1, a.every)
    terms, preds = [], []
    for f0, f1 in ranges:
        lo, hi = max(0, f0 - 3), min(N, f1) - 1
        if hi >= lo:
            terms.append(f"between(n\\,{lo}\\,{hi})")
            preds.append(lambda n, lo=lo, hi=hi: lo <= n <= hi)
    tail = max(0, N - 4)
    terms.append(f"gte(n\\,{tail})")
    preds.append(lambda n: n >= tail)
    if bar > EDGE:
        terms.append(f"not(mod(n\\,{every}))")
        preds.append(lambda n: n % every == 0)
    pred = lambda n: any(p(n) for p in preds)

    stats = {i: {"max": 0, "frames": 0, "first_bad": None} for i in range(len(ranges))}
    around: dict[int, list[str]] = {i: [] for i in range(len(ranges))}
    tail_rows, top, bottom, bar_n = [], 0, 0, 0
    for n, f in stream(path, W, H, terms, pred, N + 1000):
        mx = int(f.max())
        for i, (f0, f1) in enumerate(ranges):
            if f0 - 3 <= n < min(f1, f0 + 4):
                around[i].append(f"  f{n}: Y mean {f.mean():6.2f}  max {mx:3d}" + ("" if n >= f0 else "   (before)"))
            if f0 <= n < f1:
                s = stats[i]
                s["frames"] += 1
                s["max"] = max(s["max"], mx)
                if mx > a.tol and s["first_bad"] is None:
                    s["first_bad"] = (n, mx)
        if n >= tail:
            tail_rows.append((n, f.mean(), mx))
        if bar > EDGE and n % every == 0:
            top = max(top, int(f[: bar - EDGE].max()))
            bottom = max(bottom, int(f[H - bar + EDGE:].max()))
            bar_n += 1

    for i, (f0, f1) in enumerate(ranges):
        s = stats[i]
        print(f"black range {i + 1}: frames {f0}..{f1 - 1} ({f0 / fps:.3f}-{f1 / fps:.3f} s)")
        for line in around[i]:
            print(line)
        want = max(0, min(f1, N) - f0)
        print(f"  {s['frames']} of {want} frames read, brightest {s['max']}")
        if s["frames"] < want:
            bad.append(f"black range {i + 1}: only {s['frames']} of {want} frames found in the file")
        if s["first_bad"]:
            n, mx = s["first_bad"]
            bad.append(f"black range {i + 1}: frame {n} ({n / fps:.3f} s) is not black (max Y {mx}); the range must be black to frame {f1 - 1}")
    if not ranges:
        print("no checks.black ranges in the timeline")
    print("the end:")
    for n, mean, mx in tail_rows:
        print(f"  f{n}: Y mean {mean:6.2f}  max {mx:3d}")
    if last_black:
        if not tail_rows or tail_rows[-1][0] != N - 1:
            bad.append("could not read the last frame")
        elif tail_rows[-1][2] > a.tol:
            bad.append(f"last frame {N - 1} is not black (max Y {tail_rows[-1][2]})")
    if bar > EDGE:
        print(f"letterbox {bar} px: every {every}th frame ({bar_n} frames), rows 0..{bar - EDGE - 1} and {H - bar + EDGE}..{H - 1}: "
              f"top max Y {top}, bottom max Y {bottom}")
        if max(top, bottom) > a.bar_tol:
            bad.append(f"letterbox bars carry picture (max Y {max(top, bottom)}, allowed {a.bar_tol})")
    else:
        print("letterbox 0: no bar test")
    for b in bad:
        print(f"FAIL: {b}")
    print("PASS" if not bad else "FAIL")
    return 3 if bad else 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
