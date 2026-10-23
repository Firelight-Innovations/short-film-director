"""A small copy of the finished film for phones and chat: two-pass H.264 to a size, then checked.

    python scripts/preview.py [<in.mp4> <out.mp4>] [--max-mib 28] [--height 720] [--audio-kbps 128]

Defaults: out/<slug>-graded.mp4 -> out/<slug>-preview.mp4 (slug from
data/timeline.json). The picture is scaled to --height lines (never up; for a
9:16 film pass --height 1280 to get 720 x 1280), audio is AAC at --audio-kbps.
The video bitrate is what fits --max-mib after the audio and a 4 percent
margin for the container, but never more than the input's own video bitrate
(a short film would otherwise come out larger than its master), and a two-pass
encode lands on it. The result's size
is then measured; if it is still over, the bitrate is cut by the overshoot and
the encode repeated, up to two more times.

Why 28 MiB: chat apps and email cap uploads around 25 to 30 MB, and a file
under the cap plays inline on a phone. The preview is for watching, not for
posting; post the graded file.

Run from the film project root. Exit codes: 0 written and under the size,
3 still over the size after the retries, 2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

MIB = 1024 * 1024


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,bit_rate:format=duration,bit_rate", "-of", "json", str(path)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"preview: ffprobe could not read {path}")
    j = json.loads(out.stdout)
    v = next((s for s in j.get("streams") or [] if s.get("codec_type") == "video"), None)
    if not v:
        raise SystemExit(f"preview: {path} has no video")
    def bits(x) -> int:
        try:
            return int(x)
        except (TypeError, ValueError):
            return 0
    streams = j.get("streams") or []
    vbr = bits(v.get("bit_rate"))
    if not vbr:  # some muxers leave the stream rate out: take the file's rate less its audio
        vbr = bits(j["format"].get("bit_rate")) - sum(bits(s.get("bit_rate")) for s in streams if s.get("codec_type") == "audio")
    return {"w": int(v["width"]), "h": int(v["height"]), "duration": float(j["format"]["duration"]),
            "audio": any(s.get("codec_type") == "audio" for s in streams), "vkbps": max(0, vbr) // 1000}


def encode(inp: Path, out: Path, kbps: int, height: int, audio_kbps: int, has_audio: bool, logdir: Path) -> bool:
    vf = f"scale=-2:{height}:flags=lanczos,format=yuv420p"
    common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.5)}k", "-bufsize", f"{kbps * 2}k",
              "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
              "-passlogfile", str(logdir / "x264")]
    p1 = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(inp), "-map", "0:v:0", "-vf", vf] + common + ["-pass", "1", "-an", "-f", "null", os.devnull]
    p2 = (["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(inp), "-map", "0:v:0"] + (["-map", "0:a:0"] if has_audio else [])
          + ["-vf", vf] + common + ["-pass", "2"]
          + (["-c:a", "aac", "-b:a", f"{audio_kbps}k"] if has_audio else ["-an"]) + ["-movflags", "+faststart", str(out)])
    for cmd in (p1, p2):
        if subprocess.run(cmd).returncode != 0:
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(prog="preview.py", description="Two-pass H.264 preview under a size, for phones and chat.")
    ap.add_argument("inp", nargs="?", help="the graded film (default out/<slug>-graded.mp4)")
    ap.add_argument("out", nargs="?", help="the preview (default out/<slug>-preview.mp4)")
    ap.add_argument("--max-mib", type=float, default=28, help="largest file size in MiB (default 28)")
    ap.add_argument("--height", type=int, default=720, help="picture height in lines, never scaled up (default 720)")
    ap.add_argument("--audio-kbps", type=int, default=128, help="AAC bitrate (default 128)")
    a = ap.parse_args()
    slug = "film"
    tlp = Path("data/timeline.json")
    if tlp.exists():
        slug = json.loads(tlp.read_text(encoding="utf-8")).get("slug") or slug
    inp = Path(a.inp) if a.inp else Path("out") / f"{slug}-graded.mp4"
    out = Path(a.out) if a.out else Path("out") / f"{slug}-preview.mp4"
    if not inp.exists():
        print(f"preview: {inp} not found")
        return 2
    try:
        info = probe(inp)
    except FileNotFoundError:
        print("preview: ffprobe not found on PATH")
        return 1
    height = min(a.height, info["h"])
    height -= height % 2
    dur = info["duration"]
    budget_bits = a.max_mib * MIB * 8 * 0.96
    audio_bits = (a.audio_kbps * 1000 * dur) if info["audio"] else 0
    kbps = int((budget_bits - audio_bits) / dur / 1000)
    if kbps < 150:
        print(f"preview: {a.max_mib:g} MiB leaves {kbps} kb/s for {dur:.1f} s of picture; raise --max-mib or lower --audio-kbps")
        return 2
    capped = 0 < info["vkbps"] < kbps
    if capped:
        kbps = max(150, info["vkbps"])  # more bits than the master has buy nothing
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"preview: {inp.as_posix()} ({info['w']}x{info['h']}, {dur:.2f} s) -> {out.as_posix()}, height {height}, "
          f"target {a.max_mib:g} MiB: video {kbps} kb/s" + (" (the input's own video bitrate)" if capped else "")
          + (f" + audio {a.audio_kbps} kb/s" if info["audio"] else ", no audio"))
    with tempfile.TemporaryDirectory(prefix="preview-") as tmp:
        for attempt in range(3):
            try:
                ok = encode(inp, out, kbps, height, a.audio_kbps, info["audio"], Path(tmp))
            except FileNotFoundError:
                print("preview: ffmpeg not found on PATH")
                return 1
            if not ok:
                print("preview: ffmpeg failed")
                return 1
            size = out.stat().st_size
            print(f"  pass {attempt + 1}: {size / MIB:.2f} MiB at {kbps} kb/s")
            if size <= a.max_mib * MIB:
                o = probe(out)
                print(f"preview: wrote {out.as_posix()}: {o['w']}x{o['h']}, {o['duration']:.2f} s, {size / MIB:.2f} MiB "
                      f"(limit {a.max_mib:g} MiB)")
                return 0
            kbps = int(kbps * (a.max_mib * MIB) / size * 0.97)
    print(f"FAIL: {out.as_posix()} is {out.stat().st_size / MIB:.2f} MiB, over {a.max_mib:g} MiB after three tries")
    return 3


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
