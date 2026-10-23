"""How far is every cut, mark and cue from the music? In frames.

    python scripts/snap.py [--tol 2] [--beats data/beats.json] [--min-onset 0.25] [--all]

For each section boundary (and the transition that sits on it), each mark and
each cue start in data/timeline.json, finds the nearest measured event of each
kind in data/beats.json: beat, downbeat, onset (strength at least --min-onset),
hit, structure point, fitted pulse, loudness landmark
(loudest, rise, drop, silence). Distances are signed frames, event minus
item: +1 means the music moves one frame after the picture does.

An item is "ok" when some event lies within --tol frames (default 2), "OFF" when
none does, and "silent" when it sits after the music has ended (nothing to cut
to). A cut more than two frames from the music reads as late or early; that is
the rule SKILL.md sets for every boundary ("within two frames of a measured
event, or a logged reason"). Marks and cue starts are reported the same way but
only section boundaries decide the exit code. By default only OFF cues are
listed; --all lists every cue.

Run from the film project root. Exit codes: 0 every boundary ok (or nothing to
snap to), 3 a boundary is OFF, 2 no data/timeline.json.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

KINDS = ("beat", "down", "onset", "hit", "struct", "pulse", "level")


def F(t: float, fps: float) -> int:
    """Seconds -> frame, rounding half up like the kit's Math.round."""
    return int(math.floor(t * fps + 0.5))


def asc(s: str) -> str:
    table = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u00a0": " "}
    return "".join(table.get(c, c) for c in str(s)).encode("ascii", "backslashreplace").decode("ascii")


def load_events(beats: dict, fps: float, min_onset: float = 0.25) -> dict[str, list[float]]:
    """beats.json -> {kind: sorted event times as fractional frames}."""
    ev: dict[str, list[float]] = {k: [] for k in KINDS}
    ev["beat"] = [b * fps for b in beats.get("beats") or []]
    ev["down"] = [b * fps for b in beats.get("downbeats") or []]
    for o in beats.get("onsets") or []:
        t, s = (o, 1.0) if isinstance(o, (int, float)) else (o.get("t"), o.get("s", 1.0))
        if t is not None and (s is None or s >= min_onset):
            ev["onset"].append(t * fps)
    ev["hit"] = [h["t"] * fps for h in beats.get("hits") or [] if "t" in h]
    ev["struct"] = [s["t"] * fps for s in beats.get("structure") or [] if "t" in s]
    ev["pulse"] = [p * fps for r in beats.get("pumped_regions") or [] for p in r.get("pulses", [])]
    # loudness landmarks: the loudest moment, sudden rises and drops, where the music falls silent
    lv = [beats.get("loudest"), beats.get("silence_from")]
    lv += [r.get("t") for r in (beats.get("rises") or []) + (beats.get("drops") or [])]
    ev["level"] = [t * fps for t in lv if isinstance(t, (int, float))]
    return {k: sorted(v) for k, v in ev.items()}


def nearest(events: list[float], f: float) -> float | None:
    """Signed distance (event - f) to the nearest event, in frames, or None."""
    if not events:
        return None
    lo, hi = 0, len(events)
    while lo < hi:
        mid = (lo + hi) // 2
        if events[mid] < f:
            lo = mid + 1
        else:
            hi = mid
    cands = [events[i] - f for i in (lo - 1, lo) if 0 <= i < len(events)]
    return min(cands, key=abs)


def best(ev: dict[str, list[float]], f: float) -> tuple[str | None, float | None, dict[str, float | None]]:
    per = {k: nearest(ev[k], f) for k in KINDS}
    found = [(abs(d), k, d) for k, d in per.items() if d is not None]
    if not found:
        return None, None, per
    _, k, d = min(found)
    return k, d, per


def music_end(beats: dict, tl: dict) -> float | None:
    """Seconds after which there is nothing to cut to."""
    ends = [x for x in (beats.get("silence_from"), (tl.get("audio") or {}).get("duration"), beats.get("duration")) if x]
    return min(ends) if ends else None


def main() -> int:
    ap = argparse.ArgumentParser(prog="snap.py", description="Distance in frames from every cut, mark and cue start to the nearest measured musical event.")
    ap.add_argument("--tol", type=float, default=2, help="frames allowed between a cut and an event (default 2)")
    ap.add_argument("--beats", default="data/beats.json", help="the analysis to read (default data/beats.json)")
    ap.add_argument("--min-onset", type=float, default=0.25, help="weakest onset that counts, 0..1 (default 0.25)")
    ap.add_argument("--all", action="store_true", help="list every cue, not only the OFF ones")
    a = ap.parse_args()

    tlp = Path("data/timeline.json")
    if not tlp.exists():
        print("snap: no data/timeline.json here; run from the film project root")
        return 2
    tl = json.loads(tlp.read_text(encoding="utf-8"))
    fps = float(tl["fps"])
    total = F(tl["dur"], fps)
    bp = Path(a.beats)
    beats = json.loads(bp.read_text(encoding="utf-8")) if bp.exists() else {}
    ev = load_events(beats, fps, a.min_onset)
    n_ev = sum(len(v) for v in ev.values())
    if not n_ev:
        print(f"snap: no measured events ({bp.as_posix()} {'is empty' if bp.exists() else 'not found'}); nothing to snap to")
        return 0
    end = music_end(beats, tl)
    end_f = end * fps if end else None
    print(f"snap: tolerance {a.tol:g} frames at {fps:g} fps; {bp.as_posix()}: " + ", ".join(f"{len(ev[k])} {k}" for k in KINDS)
          + (f"; music ends {end:.3f} s (f{end_f:.0f})" if end else ""))
    print("distances are event minus item, in frames ('.' = none within 30)")

    head = f"  {'item':<40}{'frame':>6}  " + "".join(f"{k:>7}" for k in KINDS) + "   nearest       status"
    marks = tl.get("marks") or {}

    def row(label: str, t: float) -> tuple[str, str]:
        f = F(t, fps)
        k, d, per = best(ev, f)
        cells = "".join(f"{('.' if v is None or abs(v) > 30 else f'{v:+.1f}'):>7}" for v in per.values())
        if f == 0:
            status = "start"
        elif f >= total:
            status = "end"
        elif end_f is not None and f > end_f + 1:
            status = "silent"
        elif d is not None and abs(d) <= a.tol:
            status = "ok"
        else:
            status = "OFF"
        near = f"{k} {d:+.1f}" if k else "-"
        return f"  {asc(label)[:39]:<40}{f:>6}  {cells}   {near:<13} {status}", status

    off_cuts = []
    print("\nsection boundaries")
    print(head)
    trans = {}
    for tr in tl.get("transitions") or []:
        trans.setdefault(F(tr["at"], fps), []).append(tr)
    for s in tl.get("sections") or []:
        f = F(s["from"], fps)
        names = ", ".join(f"{tr['id']} {tr.get('name', '')}".strip() for tr in trans.get(f, []))
        line, st = row(f"{s['id']}" + (f" ({names})" if names else ""), s["from"])
        print(line)
        if st == "OFF":
            off_cuts.append(s["id"])
        for tr in trans.get(f, []):
            beat = tr.get("beat") or ""
            if beat in marks:
                mf = F(marks[beat], fps)
                say = "on it" if mf == f else f"{mf - f:+d} frames from it"
                print(f"      {tr['id']} beat '{asc(beat)}' is mark f{mf}: the cut is {say}")

    if marks:
        print("\nmarks")
        print(head)
        off_marks = 0
        for name, t in sorted(marks.items(), key=lambda kv: kv[1]):
            line, st = row(name, t)
            off_marks += st == "OFF"
            print(line)
    cues = tl.get("cues") or []
    off_cues = []
    print(f"\ncue starts ({'all' if a.all else 'OFF only'})")
    print(head)
    for c in cues:
        line, st = row(f"{c['id']} [{c.get('role', '')}]", c["from"])
        if st == "OFF":
            off_cues.append(c["id"])
        if a.all or st == "OFF":
            print(line)
    if not a.all and not off_cues:
        print("  none")

    print()
    print(f"snap: {len(off_cuts)} boundaries OFF" + (f" ({', '.join(off_cuts)})" if off_cuts else "")
          + f", {len(off_cues)} of {len(cues)} cue starts OFF")
    if off_cuts:
        print("FAIL: move each OFF boundary to a measured event, or log why it stays (python scripts/log-decision.py)")
        return 3
    print("PASS")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
