"""Motion trace of a render: freezes, jumps and one-frame pops, per frame.

    python scripts/motion-check.py <video.mp4 | folder of frames> [--from s] [--to s] [--sections]
                                   [--out out/motion] [--freeze 4] [--still 0.3] [--pop 8] [--jump 12]

Every frame is shrunk to a 192 px wide grey copy (area average) and compared
with the one before: the mean absolute difference, 0..255, is the frame's
"change". Run it on pass1 or the ungraded render: the grade's grain
(timeline.grade.grain) lifts every frame above --still, so freezes in a graded
file are not found. From that trace:

  pop     a frame far from both neighbours while the neighbours are close to
          each other: change in and out both at least --pop (default 8) and the
          frame before and the frame after differ by at most 0.4 of that. A
          missing plate, a stray test card, a one-frame flash of the wrong picture.
  freeze  --freeze (default 4) or more identical frames (change under --still,
          default 0.3) with motion on both sides (median change over the 8
          frames before and after at least 1.0). A plate that ran out, a clock
          that stopped. A held shot with nothing moving around it is not a freeze.
  jump    a change of at least --jump (default 12) and four times the change
          around it. At a section boundary or a transition window edge it is
          listed as a cut; anywhere else it is a jump to look at (a cut inside
          a section is fine if it was meant).

Writes out/motion/<name>.csv (frame, t, section, change, skip_change, flag) and
out/motion/<name>.png (the trace in rows of 30 s, sections marked), where
<name> is the file or folder name plus the range when --from or --to is given.
--sections adds a table per section (needs data/timeline.json). Stills say
nothing about motion; this was the gap in every review of We Built a Mind.

Exit codes: 0 no pop and no freeze, 3 a pop or a freeze inside motion, 2 bad input, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
GW = 192


def F(t: float, fps: float) -> int:
    return int(math.floor(t * fps + 0.5))


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,avg_frame_rate", "-of", "json", str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"motion-check: ffprobe could not read {path}")
    st = json.loads(out.stdout)["streams"][0]
    a, _, b = st.get("avg_frame_rate", "30/1").partition("/")
    return {"w": int(st["width"]), "h": int(st["height"]), "fps": float(a) / float(b or 1)}


def _video(path: Path, t0: float, t1: float, fps_hint: float | None):
    info = probe(path)
    fps = info["fps"] or fps_hint or 30.0
    gh = max(2, 2 * round(GW * info["h"] / info["w"] / 2))
    first = F(t0, fps) if t0 > 0 else 0
    cmd = ["ffmpeg", "-v", "error"]
    if first:
        cmd += ["-ss", f"{(first - 0.5) / fps:.6f}"]
    cmd += ["-i", str(path)]
    if t1 > t0:
        cmd += ["-frames:v", str(max(1, F(t1, fps) - first))]
    cmd += ["-vf", f"scale={GW}:{gh}:flags=area", "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def gen():
        n = first
        while True:
            buf = p.stdout.read(GW * gh)
            if len(buf) < GW * gh:
                break
            yield n, np.frombuffer(buf, np.uint8).reshape(gh, GW).astype(np.float32)
            n += 1
        p.stdout.close()
        if p.wait() != 0:
            raise SystemExit("motion-check: ffmpeg failed while decoding")

    return gen(), fps


def _folder(path: Path, t0: float, t1: float, fps: float):
    from PIL import Image
    files = sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXT)
    if not files:
        raise SystemExit(f"motion-check: no images in {path}")
    nums = [int(m.group(1)) if (m := re.match(r"f(\d+)", f.stem)) else i for i, f in enumerate(files)]
    if len(set(nums)) != len(nums):
        nums = list(range(len(files)))

    def gen():
        for n, f in sorted(zip(nums, files)):
            t = n / fps
            if t < t0 - 1e-9 or (t1 > t0 and t >= t1 - 1e-9):
                continue
            with Image.open(f) as im:
                g = im.convert("L")
                g = g.resize((GW, max(2, round(GW * g.height / g.width))), Image.BOX)
                yield n, np.asarray(g, np.float32)

    return gen(), fps


def picture_change(src: Path, t0: float = 0.0, t1: float = 0.0, fps: float | None = None) -> dict:
    """Per-frame change of a video or a frame folder. d[i]: frame i vs i-1; s[i]: i+1 vs i-1 (nan at gaps and ends)."""
    if src.is_dir():
        frames, fps = _folder(src, t0, t1, fps or 30.0)
    else:
        frames, fps = _video(src, t0, t1, fps)
    ns, d, s = [], [], []
    g2 = g1 = None
    n2 = n1 = None
    for n, g in frames:
        ns.append(n)
        d.append(float(np.abs(g - g1).mean()) if g1 is not None and n == n1 + 1 else math.nan)
        s.append(math.nan)
        if g2 is not None and n1 == n2 + 1 and n == n1 + 1:
            s[-2] = float(np.abs(g - g2).mean())
        g2, n2, g1, n1 = g1, n1, g, n
    return {"frames": np.array(ns, int), "d": np.array(d), "s": np.array(s), "fps": fps}


def find_events(pc: dict, still: float, freeze_n: int, pop_thr: float, jump_thr: float) -> dict:
    ns, d, s = pc["frames"], pc["d"], pc["s"]
    n = len(ns)
    pops, freezes, jumps = [], [], []
    for i in range(1, n - 1):
        din, dout = d[i], d[i + 1]
        if math.isnan(din) or math.isnan(dout) or math.isnan(s[i]):
            continue
        m = min(din, dout)
        if m >= pop_thr and s[i] <= 0.4 * m:
            pops.append((int(ns[i]), din, dout, s[i]))
    i = 1
    while i < n:
        if not math.isnan(d[i]) and d[i] < still:
            j = i
            while j + 1 < n and not math.isnan(d[j + 1]) and d[j + 1] < still:
                j += 1
            frames_identical = j - i + 2
            if frames_identical >= freeze_n:
                before = d[max(1, i - 8):i]
                after = d[j + 1:j + 9]
                mb = float(np.nanmedian(before)) if len(before) and not np.all(np.isnan(before)) else 0.0
                ma = float(np.nanmedian(after)) if len(after) and not np.all(np.isnan(after)) else 0.0
                if mb >= 1.0 and ma >= 1.0:
                    freezes.append((int(ns[i - 1]), int(ns[j]), frames_identical, mb, ma))
            i = j + 1
        else:
            i += 1
    for i in range(1, n):
        if math.isnan(d[i]) or d[i] < jump_thr:
            continue
        around = np.concatenate([d[max(1, i - 15):i], d[i + 1:i + 16]])
        around = around[~np.isnan(around)]
        base = float(np.median(around)) if len(around) else 0.0
        if d[i] >= 4 * base:
            jumps.append((int(ns[i]), d[i], base))
    return {"pops": pops, "freezes": freezes, "jumps": jumps}


def main() -> int:
    ap = argparse.ArgumentParser(prog="motion-check.py", description="Per-frame motion trace: freezes, jumps, one-frame pops (exit 3 on a pop or freeze). "
                                 "Run it on pass1 or the ungraded render: the grade's grain lifts every frame above --still, "
                                 "so freezes in a graded file are not found.")
    ap.add_argument("src", help="an mp4 or a folder of sequential frames (f<frame>_... names)")
    ap.add_argument("--from", dest="t0", type=float, default=0.0, help="start, seconds")
    ap.add_argument("--to", dest="t1", type=float, default=0.0, help="end, seconds (default: the end)")
    ap.add_argument("--sections", action="store_true", help="a table per section (needs data/timeline.json)")
    ap.add_argument("--out", default="out/motion", help="folder for <name>.csv and <name>.png (default out/motion)")
    ap.add_argument("--freeze", type=int, default=4, help="identical frames in a row that count as a freeze (default 4)")
    ap.add_argument("--still", type=float, default=0.3, help="change below this counts as identical (default 0.3)")
    ap.add_argument("--pop", type=float, default=8.0, help="change in and out of a pop frame (default 8)")
    ap.add_argument("--jump", type=float, default=12.0, help="change that counts as a jump (default 12)")
    a = ap.parse_args()
    src = Path(a.src)
    if not src.exists():
        print(f"motion-check: {src} not found")
        return 2
    tlp = Path("data/timeline.json")
    tl = json.loads(tlp.read_text(encoding="utf-8")) if tlp.exists() else None
    if a.sections and not tl:
        print("motion-check: --sections needs data/timeline.json (run from the film project root)")
        return 2
    try:
        pc = picture_change(src, a.t0, a.t1, float(tl["fps"]) if tl else None)
    except FileNotFoundError:
        print("motion-check: ffmpeg or ffprobe not found on PATH")
        return 1
    ns, d, fps = pc["frames"], pc["d"], pc["fps"]
    if len(ns) < 3:
        print("motion-check: need at least three frames")
        return 2
    ev = find_events(pc, a.still, a.freeze, a.pop, a.jump)

    sections, cuts = [], set()
    if tl:
        for sct in tl.get("sections") or []:
            sections.append((sct["id"], F(sct["from"], fps), F(sct["to"], fps)))
            cuts.add(F(sct["from"], fps))
        for tr in tl.get("transitions") or []:
            cuts.update({F(tr["at"] - tr.get("pre", 0), fps), F(tr["at"], fps), F(tr["at"] + tr.get("post", 0), fps)})

    def sec_of(f: int) -> str:
        for sid, f0, f1 in sections:
            if f0 <= f < f1:
                return sid
        return ""

    jumps_cut = [j for j in ev["jumps"] if any(abs(j[0] - c) <= 1 for c in cuts)]
    jumps_in = [j for j in ev["jumps"] if j not in jumps_cut]
    runs: list[list[tuple]] = []  # consecutive jump frames read as one event
    for j in jumps_in:
        if runs and j[0] - runs[-1][-1][0] <= 2:
            runs[-1].append(j)
        else:
            runs.append([j])
    gaps = int(np.sum(np.isnan(d[1:])))

    name = src.stem if src.is_file() else src.name
    if a.t0 or a.t1:
        name += f"_{a.t0:.2f}-{a.t1:.2f}" if a.t1 else f"_{a.t0:.2f}-end"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    flags: dict[int, str] = {}
    for f, *_ in ev["pops"]:
        flags[f] = "pop"
    for f0, f1, *_ in ev["freezes"]:
        for f in range(f0, f1 + 1):
            flags.setdefault(f, "freeze")
    for f, *_ in jumps_cut:
        flags.setdefault(f, "cut")
    for f, *_ in jumps_in:
        flags.setdefault(f, "jump")
    with (out / f"{name}.csv").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("frame,t,section,change,skip_change,flag\n")
        for i, f in enumerate(ns):
            dv = "" if math.isnan(d[i]) else f"{d[i]:.3f}"
            sv = "" if math.isnan(pc["s"][i]) else f"{pc['s'][i]:.3f}"
            fh.write(f"{f},{f / fps:.4f},{sec_of(int(f))},{dv},{sv},{flags.get(int(f), '')}\n")
    png = plot(out / f"{name}.png", ns, d, fps, sections, ev, jumps_cut, jumps_in, name)

    print(f"motion-check: {src.as_posix()}  frames {ns[0]}..{ns[-1]} ({len(ns)}) at {fps:g} fps" + (f", {gaps} gaps" if gaps else ""))
    valid = d[~np.isnan(d)]
    print(f"change per frame (0..255, 192 px grey): median {np.median(valid):.2f}, p95 {np.percentile(valid, 95):.2f}, max {valid.max():.2f}; "
          f"still frames {np.mean(valid < a.still):.0%}")
    print(f"pops: {len(ev['pops'])}")
    for f, din, dout, sk in ev["pops"][:40]:
        print(f"  POP f{f} ({f / fps:.2f} s) {sec_of(f)}: change in {din:.1f}, out {dout:.1f}, neighbours differ {sk:.1f}")
    print(f"freezes inside motion: {len(ev['freezes'])}")
    for f0, f1, k, mb, ma in ev["freezes"][:40]:
        print(f"  FREEZE f{f0}..f{f1} ({f0 / fps:.2f}-{f1 / fps:.2f} s) {sec_of(f0)}: {k} identical frames, motion {mb:.1f} before, {ma:.1f} after")
    print(f"jumps: {len(jumps_cut)} frames at cuts; {len(runs)} jumps inside sections ({len(jumps_in)} frames)"
          + (", the 30 biggest:" if len(runs) > 30 else ""))
    for run in sorted(sorted(runs, key=lambda r: -max(x[1] for x in r))[:30], key=lambda r: r[0][0]):
        f0, f1 = run[0][0], run[-1][0]
        big = max(run, key=lambda x: x[1])
        span = f"f{f0}" if f0 == f1 else f"f{f0}..f{f1}"
        print(f"  jump {span} ({f0 / fps:.2f} s) {sec_of(f0)}: change {big[1]:.1f} against {big[2]:.1f} around it")
    if a.sections and sections:
        print(f"  {'section':<22}{'frames':>8}{'median':>8}{'p95':>8}{'still':>7}{'pops':>6}{'frz':>5}{'jumps':>6}")
        for sid, f0, f1 in sections:
            m = (ns >= f0) & (ns < f1)
            dv = d[m]
            dv = dv[~np.isnan(dv)]
            if not len(dv):
                continue
            np_ = sum(1 for p in ev["pops"] if f0 <= p[0] < f1)
            nf = sum(1 for z in ev["freezes"] if f0 <= z[0] < f1)
            nj = sum(1 for r in runs if f0 <= r[0][0] < f1)
            print(f"  {sid:<22}{int(m.sum()):>8}{np.median(dv):>8.2f}{np.percentile(dv, 95):>8.2f}{np.mean(dv < a.still):>7.0%}{np_:>6}{nf:>5}{nj:>6}")
    print(f"wrote {(out / (name + '.csv')).as_posix()}" + (f" and {png}" if png else ""))
    bad = bool(ev["pops"] or ev["freezes"])
    print("FLAGGED: look at the frames named above" if bad else "OK")
    return 3 if bad else 0


def plot(path: Path, ns, d, fps, sections, ev, jumps_cut, jumps_in, title) -> str | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    t = ns / fps
    span = t[-1] - t[0]
    row_s = 30.0 if span > 40 else max(span, 1 / fps)
    rows = max(1, int(math.ceil(span / row_s - 1e-9)))
    valid = d[~np.isnan(d)]
    top = max(10.0, float(np.percentile(valid, 99.5)) * 1.3) if len(valid) else 10.0
    fig, axes = plt.subplots(rows, 1, figsize=(18, 2.3 * rows + 0.6), squeeze=False)
    for r in range(rows):
        ax = axes[r][0]
        a0, a1 = t[0] + r * row_s, t[0] + (r + 1) * row_s
        m = (t >= a0) & (t <= a1)
        ax.plot(t[m], np.minimum(d[m], top), color="k", lw=0.7)
        for sid, f0, f1 in sections:
            if a0 <= f0 / fps <= a1:
                ax.axvline(f0 / fps, color="tab:blue", lw=0.8, alpha=0.6)
                ax.text(f0 / fps, top * 0.92, f" {sid}", fontsize=7, color="tab:blue", va="top")
        for f, *_ in ev["pops"]:
            if a0 <= f / fps <= a1:
                ax.plot([f / fps], [top * 0.8], marker="v", color="red", ms=6)
        for f0, f1, *_ in ev["freezes"]:
            if f1 / fps >= a0 and f0 / fps <= a1:
                ax.axvspan(f0 / fps, (f1 + 1) / fps, color="tab:cyan", alpha=0.35)
        for f, *_ in jumps_in:
            if a0 <= f / fps <= a1:
                ax.plot([f / fps], [top * 0.7], marker="o", color="tab:orange", ms=4)
        ax.set_xlim(a0, a1)
        ax.set_ylim(0, top)
        ax.set_ylabel("change", fontsize=8)
        ax.tick_params(labelsize=7)
    axes[0][0].set_title(f"{title}: change per frame (red = pop, cyan = freeze, orange = jump inside a section, blue = section start)",
                         fontsize=9, loc="left")
    axes[-1][0].set_xlabel("seconds")
    fig.tight_layout()
    fig.savefig(path, dpi=70)
    plt.close(fig)
    return path.as_posix()


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
