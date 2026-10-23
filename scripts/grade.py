"""The film's one unifying pass: grade, vignette and grain, gated by frame number; bars repainted black.

    python scripts/grade.py [<in.mp4> <out.mp4>] [--crf 17] [--preset slow]

Defaults: out/<slug>.mp4 -> out/<slug>-graded.mp4, slug from data/timeline.json
(so `npm run grade` needs no arguments). The numbers come from timeline.grade:

  contrast, saturation, gamma   ffmpeg eq
  vignette                      angle = vignette x PI/3 (0 = none); 1/3 gives PI/9,
                                the corner near 80 percent that We Built a Mind
                                settled on after PI/5 read as a dirty lens
  grain                         ffmpeg noise alls=<grain>, temporal and uniform (0 = none)
  until                         seconds; the pass is off from this frame on (null = whole film)

Missing values take the defaults 1.05, 0.97, 0.985, 0.35, 5, and `until` the
start of the first checks.black range. The pass is also off inside every
checks.black range, because those frames must stay pure black.

Order, and why each step is there:
  1. scale to limited range (tv) BT.709 and yuv420p first, so the tags written at
     the end are true whatever the render used (a full-range render re-tagged
     without converting made the bars grey against picture black)
  2. eq, vignette, noise, each with enable='<frame gate>': gated on the frame
     number n, not on t, because 99.8667 s is a hair after frame 2996 and a
     time gate graded the first black frame
  3. drawbox the two letterbox bars black AFTER the grain, so no grain lands in
     the bars (letterbox 0: no bars)
  4. setparams and the encoder flags tag the result bt709 tv; audio is copied
     untouched; +faststart for the web
Grade and grain happen once, here, never per section.

Run from the film project root. Exit codes: 0 graded, 2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

DEFAULTS = {"contrast": 1.05, "saturation": 0.97, "gamma": 0.985, "vignette": 0.35, "grain": 5}


def F(t: float, fps: float) -> int:
    return int(math.floor(t * fps + 0.5))


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height,avg_frame_rate,nb_frames,pix_fmt,color_range,color_space,color_transfer,color_primaries",
                          "-of", "json", str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"grade: ffprobe could not read {path}")
    streams = json.loads(out.stdout).get("streams") or []
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not v:
        raise SystemExit(f"grade: {path} has no video stream")
    return {"v": v, "audio": any(s.get("codec_type") == "audio" for s in streams)}


def main() -> int:
    ap = argparse.ArgumentParser(prog="grade.py", description="Grade + vignette + grain from timeline.grade, gated by frame; letterbox repainted; bt709 tv; audio copied.")
    ap.add_argument("inp", nargs="?", help="the render (default out/<slug>.mp4)")
    ap.add_argument("out", nargs="?", help="the graded file (default out/<slug>-graded.mp4)")
    ap.add_argument("--crf", type=float, default=17, help="x264 quality (default 17)")
    ap.add_argument("--preset", default="slow", help="x264 preset (default slow)")
    a = ap.parse_args()
    tlp = Path("data/timeline.json")
    if not tlp.exists():
        print("grade: no data/timeline.json here; run from the film project root")
        return 2
    tl = json.loads(tlp.read_text(encoding="utf-8"))
    slug = tl.get("slug") or "film"
    inp = Path(a.inp) if a.inp else Path("out") / f"{slug}.mp4"
    out = Path(a.out) if a.out else inp.with_name(inp.stem + "-graded.mp4")
    if not inp.exists():
        print(f"grade: {inp} not found (render it first: npm run render:final)")
        return 2
    if inp.resolve() == out.resolve():
        print("grade: input and output are the same file")
        return 2
    try:
        info = probe(inp)
    except FileNotFoundError:
        print("grade: ffprobe not found on PATH")
        return 1
    v = info["v"]
    H = int(v["height"])
    fps = float(tl["fps"])
    g = {**DEFAULTS, **{k: val for k, val in (tl.get("grade") or {}).items() if val is not None}}
    blacks = [(F(r[0], fps), F(r[1], fps)) for r in (tl.get("checks") or {}).get("black") or []]
    if tl.get("grade") and "until" in tl["grade"]:
        until = tl["grade"]["until"]
    else:
        until = min((r[0] for r in (tl.get("checks") or {}).get("black") or []), default=None)
    U = F(until, fps) if until is not None else None

    gate = []
    if U is not None:
        gate.append(f"lt(n\\,{U})")
    for b0, b1 in blacks:
        if U is None or b0 < U:
            gate.append(f"not(between(n\\,{b0}\\,{b1 - 1}))")
    en = f":enable='{'*'.join(gate)}'" if gate else ""
    bar = int(math.floor(H * float(tl.get("letterbox") or 0) + 0.5))

    vf = ["scale=out_range=tv:out_color_matrix=bt709", "format=yuv420p"]
    if (g["contrast"], g["saturation"], g["gamma"]) != (1, 1, 1):
        vf.append(f"eq=contrast={g['contrast']}:saturation={g['saturation']}:gamma={g['gamma']}{en}")
    if g["vignette"] and g["vignette"] > 0:
        vf.append(f"vignette=angle={g['vignette'] * math.pi / 3:.6f}{en}")
    if g["grain"] and g["grain"] > 0:
        vf.append(f"noise=alls={int(round(g['grain']))}:allf=t+u{en}")
    if bar > 0:
        vf.append(f"drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill")
        vf.append(f"drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill")
    vf.append("setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709")

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats", "-i", str(inp), "-map", "0:v:0", "-map", "0:a?",
           "-vf", ",".join(vf),
           "-c:v", "libx264", "-crf", f"{a.crf:g}", "-preset", a.preset, "-maxrate", "40M", "-bufsize", "80M", "-pix_fmt", "yuv420p",
           "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-movflags", "+faststart", "-c:a", "copy", str(out)]
    print(f"grade: {inp.as_posix()} -> {out.as_posix()}")
    print(f"  contrast {g['contrast']}, saturation {g['saturation']}, gamma {g['gamma']}, vignette {g['vignette']} "
          f"(angle {g['vignette'] * math.pi / 3:.4f} rad), grain {g['grain']}")
    print(f"  off from frame {U} ({until} s)" if U is not None else "  on for the whole film (grade.until is null)")
    if blacks:
        print("  off inside checks.black: " + ", ".join(f"frames {b0}..{b1 - 1}" for b0, b1 in blacks))
    print(f"  letterbox: {bar} px bars repainted black after the grain" if bar else "  letterbox 0: no bars")
    print(f"  input: {v.get('width')}x{H} {v.get('pix_fmt')} range {v.get('color_range', '?')} matrix {v.get('color_space', '?')}"
          + ("" if info["audio"] else ", no audio stream"))
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        p = subprocess.run(cmd)
    except FileNotFoundError:
        print("grade: ffmpeg not found on PATH")
        return 1
    if p.returncode != 0:
        print("grade: ffmpeg failed")
        return 1
    o = probe(out)["v"]
    print(f"grade: wrote {out.as_posix()}: {o.get('width')}x{o.get('height')} {o.get('pix_fmt')}, range {o.get('color_range')}, "
          f"{o.get('color_space')}/{o.get('color_primaries')}/{o.get('color_transfer')}, {o.get('nb_frames')} frames (input {v.get('nb_frames')})")
    if str(o.get("nb_frames")) != str(v.get("nb_frames")):
        print("WARN: the frame count changed")
    print("next: python scripts/black-check.py " + out.as_posix() + " and python scripts/flash-check.py " + out.as_posix())
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
