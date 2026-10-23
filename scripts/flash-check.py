"""Flash-safety screen of a finished file or a folder of frames (broadcast area by default).

    python scripts/flash-check.py <video.mp4 | folder of frames> [--from s] [--to s] [--fps n]
                                  [--area 0.25] [--max-flashes 3]

The rule (WCAG 2.2 SC 2.3.1, https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html,
and ITU-R BT.1702-3, https://www.itu.int/rec/R-REC-BT.1702-3-202311-I/en):
no more than three general flashes and no more than three red flashes in any
one-second window. A flash is a pair of opposing changes in relative luminance
of 10 percent or more of full scale where the darker state is below 0.80, over
more than a quarter of the screen (the television reading of the area rule; WCAG's
own limit for close viewing is a quarter of any 10-degree field, much smaller, so
pass --area to tighten it). A red flash is a pair of opposing changes involving
saturated red: R/(R+G+B) at least 0.8 and a change in (R-G-B) x 320 above 20.
Flashing sequences longer than five seconds carry risk even under the limit
(BT.1702-3), so they are reported as a warning.

Which area to trust. The default, --area 0.25, is the broadcast (television)
reading: ITU-R BT.1702 counts a flash only over a quarter of the screen. A PASS at
the default is NOT a WCAG 2.3.1 claim, because WCAG's own limit is a quarter of any
10-degree field, about 3 percent of the screen. So for web delivery (LinkedIn,
YouTube, a site) also run `--area 0.03` and judge each region that fails
(references/safety-and-rights.md, section 2). A broadcast ad needs a certified test.

How it measures: each frame is shrunk to about 96 x 54 (area average) and turned
into relative luminance (linear sRGB, 0.2126 R + 0.7152 G + 0.0722 B). Each cell
follows its own rise or fall: a change accumulates over frames until it reverses
by more than 1 percent, so a fade over three frames counts the same as a cut.
A cell is "in transition" once its rise (or fall) reaches 0.10 with the darker
end below 0.80. The frame registers a transition when the cells in transition
the same way first cover --area of the screen; transitions alternate up and down.
Two transitions make one flash. FAIL when any one-second window holds more than
2 x --max-flashes transitions (that is, more than three flashes).

A saturated red field over a quarter of the screen is reported as a warning even
when it does not flash: the film's rule is no saturated red fields.

This is a screening tool, not a certified analyser (no viewing distance, no
spatial pattern test). Run it on the graded file: the grade's contrast can push a
0.09 change over 0.10. For a folder, frames are read in name order; names like
f0123_t004.10.jpg (shots.mjs, film-frames.py) give the film frame numbers.

Exit codes: 0 PASS, 3 FAIL, 2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
HYST = 0.01      # a reversal smaller than this (relative luminance) does not end a rise or fall
RED_HYST = 2.0   # the same for (R-G-B) x 320


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,avg_frame_rate,r_frame_rate,nb_frames:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"flash-check: ffprobe could not read {path}")
    j = json.loads(out.stdout)
    st = (j.get("streams") or [{}])[0]

    def rate(s: str) -> float:
        a, _, b = (s or "0/1").partition("/")
        return float(a) / float(b or 1) if float(b or 1) else 0.0

    return {"w": int(st.get("width", 0)), "h": int(st.get("height", 0)),
            "fps": rate(st.get("avg_frame_rate")) or rate(st.get("r_frame_rate")),
            "duration": float((j.get("format") or {}).get("duration") or 0)}


def grid_size(w: int, h: int) -> tuple[int, int]:
    """About 96 x 54 for 16:9, keeping the aspect ratio (54 x 96 for 9:16)."""
    if w >= h:
        return 96, max(2, round(96 * h / w))
    return max(2, round(96 * w / h)), 96


def video_frames(path: Path, t0: float, t1: float, fps_req: float | None):
    info = probe(path)
    fps = fps_req or info["fps"] or 30.0
    gw, gh = grid_size(info["w"], info["h"])
    first = int(np.floor(t0 * fps + 0.5)) if t0 > 0 else 0
    cmd = ["ffmpeg", "-v", "error"]
    if first > 0:
        cmd += ["-ss", f"{(first - 0.5) / fps:.6f}"]
    cmd += ["-i", str(path)]
    if t1 > t0:
        cmd += ["-frames:v", str(max(1, int(np.floor(t1 * fps + 0.5)) - first))]
    vf = (f"fps={fps}," if fps_req else "") + f"scale={gw}:{gh}:flags=area"
    cmd += ["-vf", vf, "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = gw * gh * 3

    def gen():
        n = first
        while True:
            buf = p.stdout.read(size)
            if len(buf) < size:
                break
            yield n, np.frombuffer(buf, np.uint8).reshape(gh, gw, 3)
            n += 1
        p.stdout.close()
        if p.wait() != 0:
            raise SystemExit("flash-check: ffmpeg failed while decoding")

    return gen(), fps, (gw, gh)


def dir_frames(path: Path, fps: float, t0: float, t1: float):
    import cv2
    files = sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXT)
    if not files:
        raise SystemExit(f"flash-check: no images in {path}")
    nums = []
    for i, f in enumerate(files):
        m = re.match(r"f(\d+)", f.stem)
        nums.append(int(m.group(1)) if m else i)
    if len(set(nums)) != len(nums):
        nums = list(range(len(files)))
    pairs = sorted(zip(nums, files))
    gaps = sum(1 for (a, _), (b, _) in zip(pairs, pairs[1:]) if b - a != 1)
    if gaps:
        print(f"flash-check: warning: {gaps} gaps in the frame numbers; a gap reads as one frame, so render every frame (shots.mjs --seq)")
    im0 = cv2.imread(str(pairs[0][1]), cv2.IMREAD_COLOR)
    gw, gh = grid_size(im0.shape[1], im0.shape[0])

    def gen():
        for n, f in pairs:
            t = n / fps
            if t < t0 - 1e-9 or (t1 > t0 and t >= t1 - 1e-9):
                continue
            im = cv2.imread(str(f), cv2.IMREAD_COLOR)
            im = cv2.resize(im, (gw, gh), interpolation=cv2.INTER_AREA)
            yield n, cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

    return gen(), fps, (gw, gh)


def linear(rgb: np.ndarray) -> np.ndarray:
    c = rgb.astype(np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


class Tracker:
    """Per-cell rise/fall runs of one quantity; reports cells whose run is a transition."""

    def __init__(self, v0: np.ndarray, hyst: float, sat0: np.ndarray | None = None):
        self.start = v0.copy()
        self.ext = v0.copy()
        self.dir = np.ones(v0.shape, np.int8)  # +1 rising (or not yet moving), -1 falling
        self.hyst = hyst
        self.sat_hi = sat0.copy() if sat0 is not None else None

    def step(self, v: np.ndarray, sat: np.ndarray | None = None) -> None:
        up = self.dir == 1
        higher = up & (v > self.ext)
        self.ext = np.where(higher, v, self.ext)
        if self.sat_hi is not None:
            self.sat_hi = np.where(higher, sat, self.sat_hi)
        rev_down = up & (v < self.ext - self.hyst)
        self.start = np.where(rev_down, self.ext, self.start)
        self.ext = np.where(rev_down, v, self.ext)
        dn = (self.dir == -1) & ~rev_down
        self.ext = np.where(dn & (v < self.ext), v, self.ext)
        rev_up = dn & (v > self.ext + self.hyst)
        self.start = np.where(rev_up, self.ext, self.start)
        self.ext = np.where(rev_up, v, self.ext)
        if self.sat_hi is not None:
            self.sat_hi = np.where(rev_up, sat, self.sat_hi)
        self.dir = np.where(rev_down, -1, np.where(rev_up, 1, self.dir)).astype(np.int8)

    def amplitude(self) -> np.ndarray:
        return self.ext - self.start


def main() -> int:
    ap = argparse.ArgumentParser(prog="flash-check.py", description="General and red flash screen after WCAG 2.3.1 and ITU-R BT.1702 (exit 3 on FAIL). "
                                 "The default --area 0.25 is the broadcast reading, not a WCAG 2.3.1 claim: "
                                 "for web delivery also run --area 0.03 (references/safety-and-rights.md, section 2).")
    ap.add_argument("src", help="an mp4 (any ffmpeg input) or a folder of sequential frames")
    ap.add_argument("--from", dest="t0", type=float, default=0.0, help="start, seconds (default 0)")
    ap.add_argument("--to", dest="t1", type=float, default=0.0, help="end, seconds (default: the end)")
    ap.add_argument("--fps", type=float, default=None, help="frame rate (video: resample to it; folder: default timeline fps, else 30)")
    ap.add_argument("--area", type=float, default=0.25, help="share of the screen that must change together (default 0.25, the broadcast reading; "
                         "use 0.03 for web delivery, which approximates WCAG's smaller limit)")
    ap.add_argument("--max-flashes", type=float, default=3, help="flashes allowed in any one second (default 3)")
    ap.add_argument("--long", type=float, default=5.0, help="warn on flashing sequences longer than this, seconds (default 5)")
    a = ap.parse_args()
    src = Path(a.src)
    if not src.exists():
        print(f"flash-check: {src} not found")
        return 2
    if src.is_dir():
        fps = a.fps
        if fps is None:
            tl = Path("data/timeline.json")
            fps = float(json.loads(tl.read_text(encoding="utf-8")).get("fps", 30)) if tl.exists() else 30.0
        frames, fps, grid = dir_frames(src, fps, a.t0, a.t1)
    else:
        try:
            frames, fps, grid = video_frames(src, a.t0, a.t1, a.fps)
        except FileNotFoundError:
            print("flash-check: ffmpeg or ffprobe not found on PATH")
            return 1

    lum_t = red_t = None
    gen_events: list[tuple[int, int]] = []   # (frame, +1 / -1)
    red_events: list[tuple[int, int]] = []
    last_gen = last_red = 0
    prev_up = prev_dn = prev_rup = prev_rdn = False
    red_field_max, red_field_at = 0.0, None
    first_n = last_n = None
    count = 0
    for n, rgb in frames:
        lin = linear(rgb)
        L = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
        ssum = lin.sum(axis=2)
        ratio = np.where(ssum > 0, lin[..., 0] / np.maximum(ssum, 1e-9), 0.0)
        redv = np.clip((lin[..., 0] - lin[..., 1] - lin[..., 2]) * 320.0, 0, None)
        sat = ratio >= 0.8
        field = float(np.mean(sat & (redv > 20)))
        if field > red_field_max:
            red_field_max, red_field_at = field, n
        count += 1
        if lum_t is None:
            lum_t, red_t = Tracker(L, HYST), Tracker(redv, RED_HYST, sat)
            first_n = last_n = n
            continue
        last_n = n
        lum_t.step(L)
        red_t.step(redv, sat)
        amp = lum_t.amplitude()
        darker = np.minimum(lum_t.start, lum_t.ext)
        up = float(np.mean((amp >= 0.10) & (darker < 0.80))) >= a.area
        dn = float(np.mean((amp <= -0.10) & (darker < 0.80))) >= a.area
        ramp = red_t.amplitude()
        rup = float(np.mean((ramp > 20) & red_t.sat_hi)) >= a.area
        rdn = float(np.mean((ramp < -20) & red_t.sat_hi)) >= a.area
        if up and not prev_up and last_gen != 1:
            gen_events.append((n, 1))
            last_gen = 1
        elif dn and not prev_dn and last_gen != -1:
            gen_events.append((n, -1))
            last_gen = -1
        if rup and not prev_rup and last_red != 1:
            red_events.append((n, 1))
            last_red = 1
        elif rdn and not prev_rdn and last_red != -1:
            red_events.append((n, -1))
            last_red = -1
        prev_up, prev_dn, prev_rup, prev_rdn = up, dn, rup, rdn
    if count < 2:
        print("flash-check: need at least two frames")
        return 2

    win = int(round(fps))

    def worst(events: list[tuple[int, int]]) -> tuple[int, int | None]:
        fr = [e[0] for e in events]
        best, at, j = 0, None, 0
        for i, f in enumerate(fr):
            while fr[j] <= f - win:
                j += 1
            if i - j + 1 > best:
                best, at = i - j + 1, fr[j]
        return best, at

    def long_runs(events: list[tuple[int, int]]) -> list[tuple[int, int, int]]:
        """Chains of transitions at most half a second apart (a flash a second or faster)."""
        fr = [e[0] for e in events]
        runs, i = [], 0
        while i < len(fr):
            j = i
            while j + 1 < len(fr) and fr[j + 1] - fr[j] <= win / 2:
                j += 1
            if j > i and fr[j] - fr[i] > a.long * fps:
                runs.append((fr[i], fr[j], j - i + 1))
            i = j + 1
        return runs

    tt = lambda f: f"{f / fps:.2f}s (f{f})"
    gw_, gat = worst(gen_events)
    rw_, rat = worst(red_events)
    limit = int(2 * a.max_flashes)
    print(f"flash-check: {src.as_posix()}")
    print(f"frames {count} (f{first_n}..f{last_n}, {first_n / fps:.2f}-{(last_n + 1) / fps:.2f} s) at {fps:g} fps, grid {grid[0]}x{grid[1]}, area {a.area:.0%}"
          + (" (broadcast reading, not a WCAG 2.3.1 claim; for web delivery also run --area 0.03)" if a.area > 0.05 else ""))
    print(f"general: {len(gen_events)} luminance transitions = {len(gen_events) / 2:g} flashes; worst one-second window "
          f"{gw_} transitions = {gw_ / 2:g} flashes" + (f" from {tt(gat)}" if gat is not None else "") + f" (limit {a.max_flashes:g})")
    print(f"red:     {len(red_events)} saturated-red transitions = {len(red_events) / 2:g} flashes; worst one-second window "
          f"{rw_} transitions = {rw_ / 2:g} flashes" + (f" from {tt(rat)}" if rat is not None else ""))
    if gen_events:
        print("transitions: " + ", ".join(f"{e[0] / fps:.2f}{'+' if e[1] > 0 else '-'}" for e in gen_events[:80])
              + (" ..." if len(gen_events) > 80 else "") + "   (+ brighter, - darker)")
    warn = []
    for kind, evs in (("flashing", gen_events), ("red flashing", red_events)):
        for f0, f1, k in long_runs(evs):
            warn.append(f"{kind} sequence {f0 / fps:.2f}-{f1 / fps:.2f} s: {k} transitions, none more than half a second apart, "
                        f"for {(f1 - f0) / fps:.1f} s (over {a.long:g} s carries risk even under the limit)")
    if red_field_max >= a.area:
        warn.append(f"saturated red covers {red_field_max:.0%} of the screen at {tt(red_field_at)}: no saturated red fields")
    for w in warn:
        print(f"WARN: {w}")
    fail = gw_ > limit or rw_ > limit
    print("FAIL: more than three flashes in one second" if fail else "PASS")
    return 3 if fail else 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
