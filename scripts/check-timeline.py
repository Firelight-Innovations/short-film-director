"""Check data/timeline.json (schema version 3) before anything is built on it.

    python scripts/check-timeline.py [--timeline data/timeline.json]

Errors (exit 3), the contract every section, the animatic and the render rely on:
  - version 3; slug usable in file names; w and h even; fps and dur positive;
    letterbox in [0, 0.5); safe fractions in (0, 1]
  - sections contiguous and in order, covering [0, dur) in whole frames after
    snapping (frame = round(t * fps)), none empty; ids like 00-name
  - every id unique (sections, transitions, cues); transition ids look like
    t-00-01 (t-, then lower case letters, digits and dashes: t-start and t-end
    pass), the form review-frames.mjs and review-boundaries.js accept
  - transitions join adjacent sections a then b at their boundary; owner is a
    or b; windows [at - pre, at + post) stay inside the two sections and do not
    overlap; t-start / t-end (no a or no b) have pre = post = 0
  - cues: non-empty text, a known section, from < to, inside the section's
    render range (its span plus the transition windows either side); data and
    quote cues carry a source; a `shown` window lies inside the render range too
  - checks.black ranges inside [0, dur]; audio.src exists under assets/
Warnings (exit 0), things a person should look at:
  - a time more than a quarter of a frame from any frame (it snaps to a frame nobody chose)
  - a boundary without a transition row; a transition `beat` naming a mark the
    cut is not on
  - cue ids that are not role-based (stamp-1, data-3): content in an id goes
    stale (We Built a Mind's stamp-1962 ended up saying 1966)
  - a cue on screen for less than its reading time, 0.4 s a word plus 0.5 s and
    never under 5/6 s (150 words a minute; text and attribution counted), for
    more than 7 s, or on more than two lines
  - a `shown` window that starts after or ends before the readable window
  - unknown cue roles; missing names; palette colours that are not #rrggbb
  - every data or quote cue needs a row in docs/research/facts.md (the table in
    the contract, part G4) with verdict verified or corrected, on-screen words
    equal to the cue, and a re-verify-by date still ahead
  - with data/beats.json: a boundary more than 2 frames from a measured event
    (snap.py has the detail), and an analysis made at another fps or of another
    file than audio.src

Reading-time numbers: about 150 words a minute for on-screen text, each text
event between 5/6 s and 7 s, at most two lines (dev/references digests, carried
in the contract G7). Run from the film project root.
Exit codes: 0 no errors, 3 errors, 2 no timeline or not JSON.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

KNOWN_ROLES = {"stamp", "slam", "narration", "sub", "quote", "data", "thesis", "question", "credit", "logo", "caption", "vo"}
FACT_ROLES = {"data", "quote"}
SECTION_ID = re.compile(r"^[0-9]{2}-[a-z0-9-]+$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TRANSITION_ID = re.compile(r"^t-[a-z0-9][a-z0-9-]*$")  # t-00-01, t-start, t-end
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
G4_COLUMNS = ["cue", "on screen", "source", "url", "published", "exact wording at source", "verdict", "as of",
              "re-verify by", "check a", "check b"]


def asc(s: object) -> str:
    table = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u00a0": " "}
    return "".join(table.get(c, c) for c in str(s)).encode("ascii", "backslashreplace").decode("ascii")


def short(s: str, n: int = 48) -> str:
    s = asc(s).replace("\n", " / ")
    return s if len(s) <= n else s[: n - 3] + "..."


def sibling(name: str):
    p = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_")[:-3], p)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # no __pycache__ in the project's scripts/
    spec.loader.exec_module(mod)
    return mod


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def num(x: object) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def parse_facts(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    """The first markdown table whose header starts with 'cue' -> {cue id: {column: cell}}."""
    rows: dict[str, dict[str, str]] = {}
    header: list[str] | None = None
    problems: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if rows:
                break  # the first facts table is the one that counts
            header = None
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip("|"))]
        if header is None:
            low = [c.lower().strip("* ") for c in cells]
            if low and low[0] == "cue":
                header = low
                missing = [c for c in G4_COLUMNS if c not in header]
                if missing:
                    problems.append(f"facts.md table lacks columns: {', '.join(missing)}")
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        row = {header[i]: (cells[i] if i < len(cells) else "") for i in range(len(header))}
        cue = row.get("cue", "").strip("` ")
        if cue:
            rows[cue] = row
    if header is None and not rows:
        problems.append("facts.md has no table whose first column is 'cue' (contract G4)")
    return rows, problems


def norm_words(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.IGNORECASE).replace("\\n", " ").replace("\n", " ")
    s = s.strip().strip("`").strip()
    return " ".join(s.split())


def main() -> int:
    ap = argparse.ArgumentParser(prog="check-timeline.py", description="Check data/timeline.json against the v3 rules (errors exit 3).")
    ap.add_argument("--timeline", default="data/timeline.json", help="file to check (default data/timeline.json)")
    a = ap.parse_args()
    path = Path(a.timeline)
    if not path.exists():
        print(f"check-timeline: {path.as_posix()} not found; run from the film project root")
        return 2
    try:
        tl = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"check-timeline: {path.as_posix()} is not valid JSON: {e}")
        return 2
    r = Report()

    # --- top level -------------------------------------------------------------
    if tl.get("version") != 3:
        r.err(f"version is {tl.get('version')!r}; this schema is version 3")
    slug = tl.get("slug")
    if not isinstance(slug, str) or not SLUG.match(slug):
        r.err(f"slug {slug!r} must be lower case letters, digits and dashes (it names out/<slug>.mp4)")
    title = tl.get("title")
    if not isinstance(title, str) or not title.strip() or title.startswith("__"):
        r.warn(f"title {title!r} is empty or a placeholder")
    for k in ("w", "h"):
        v = tl.get(k)
        if not isinstance(v, int) or v <= 0:
            r.err(f"{k} must be a positive integer (got {v!r})")
        elif v % 2:
            r.err(f"{k} = {v} is odd; H.264 in yuv420p needs even sizes")
    fps, dur = tl.get("fps"), tl.get("dur")
    if not num(fps) or fps <= 0 or not num(dur) or dur <= 0:
        r.err(f"fps and dur must be positive numbers (got {fps!r}, {dur!r})")
        return finish(r, tl)
    total = F(dur, fps)
    lb = tl.get("letterbox", 0)
    if not num(lb) or not 0 <= lb < 0.5:
        r.err(f"letterbox {lb!r} must be a fraction in [0, 0.5)")
    safe = tl.get("safe") or {}
    for k in ("title", "action"):
        v = safe.get(k)
        if v is not None and (not num(v) or not 0 < v <= 1):
            r.err(f"safe.{k} {v!r} must be in (0, 1]")
    if num(safe.get("title")) and num(safe.get("action")) and safe["title"] > safe["action"]:
        r.warn("safe.title is larger than safe.action: words would be allowed where action is not")

    def frame_check(label: str, t: object) -> None:
        if num(t):
            frac = abs(t * fps - round(t * fps))
            if frac > 0.25:
                lo, hi = math.floor(t * fps), math.floor(t * fps) + 1
                r.warn(f"{label} = {t} is {t * fps:.3f} frames, more than a quarter of a frame from any frame: write {lo / fps:.4f} or {hi / fps:.4f}")

    # --- sections ----------------------------------------------------------------
    sections = tl.get("sections") or []
    if not sections:
        r.err("no sections")
        return finish(r, tl)
    ids: dict[str, str] = {}

    def claim(kind: str, i: object) -> None:
        if not isinstance(i, str) or not i:
            r.err(f"a {kind} has no id")
            return
        if i in ids:
            r.err(f"id {i!r} is used twice ({ids[i]} and {kind})")
        ids[i] = kind

    sec_by_id: dict[str, dict] = {}
    order: dict[str, int] = {}
    prev_to = 0
    for n, s in enumerate(sections):
        sid = s.get("id")
        claim("section", sid)
        if isinstance(sid, str) and not SECTION_ID.match(sid):
            r.err(f"section id {sid!r} must look like 00-name (two digits, a dash, lower case)")
        if not (num(s.get("from")) and num(s.get("to"))):
            r.err(f"section {sid}: from and to must be numbers")
            continue
        frame_check(f"section {sid} from", s["from"])
        frame_check(f"section {sid} to", s["to"])
        f0, f1 = F(s["from"], fps), F(s["to"], fps)
        if f0 != prev_to:
            what = "a gap" if f0 > prev_to else "an overlap"
            r.err(f"section {sid} starts at frame {f0} but the previous one ends at frame {prev_to}: {what}")
        if f1 <= f0:
            r.err(f"section {sid} has no frames after snapping ({f0} to {f1})")
        prev_to = f1
        for k in ("label", "style"):
            if not s.get(k):
                r.warn(f"section {sid} has no {k}")
        pal = s.get("palette")
        if pal is not None:
            if not isinstance(pal, dict):
                r.warn(f"section {sid}: palette should be an object")
            else:
                for k, v in pal.items():
                    if not isinstance(v, str) or not HEX.match(v):
                        r.warn(f"section {sid}: palette.{k} {v!r} is not #rrggbb")
        if isinstance(sid, str):
            sec_by_id[sid] = s
            order[sid] = n
    if prev_to != total:
        r.err(f"the last section ends at frame {prev_to}, the film at frame {total} (dur {dur} s at {fps} fps)")

    # --- transitions ----------------------------------------------------------------
    trans = tl.get("transitions") or []
    windows = []
    boundary_tr: dict[int, list[str]] = {}
    marks = tl.get("marks") or {}
    win_of: dict[str, tuple[int, int, int]] = {}
    for tr in trans:
        tid = tr.get("id")
        claim("transition", tid)
        if isinstance(tid, str) and tid and not TRANSITION_ID.fullmatch(tid):
            r.err(f"transition id {tid!r} must look like t-00-01 (t-, then lower case letters, digits and dashes): "
                  "review-frames.mjs and the boundary review workflow only accept that form")
        at, pre, post = tr.get("at"), tr.get("pre", 0), tr.get("post", 0)
        if not (num(at) and num(pre) and num(post)) or pre < 0 or post < 0:
            r.err(f"transition {tid}: at, pre and post must be numbers, pre and post not negative")
            continue
        frame_check(f"transition {tid} at", at)
        frame_check(f"transition {tid} at - pre", at - pre)
        frame_check(f"transition {tid} at + post", at + post)
        fa, wa, wb = F(at, fps), F(at - pre, fps), F(at + post, fps)
        sa, sb, owner = tr.get("a"), tr.get("b"), tr.get("owner")
        for k in ("name", "device"):
            if not tr.get(k):
                r.warn(f"transition {tid} has no {k}")
        if sa is None and sb is None:
            r.err(f"transition {tid} has neither a nor b")
            continue
        if sa is None or sb is None:
            edge = sb if sa is None else sa
            if edge not in sec_by_id:
                r.err(f"transition {tid}: unknown section {edge!r}")
                continue
            if wa != fa or wb != fa:
                r.err(f"transition {tid} is an edge (no {'a' if sa is None else 'b'}) and must have pre = post = 0")
            if sa is None and (order[edge] != 0 or fa != 0):
                r.err(f"transition {tid} (no a) must be at 0 on the first section")
            if sb is None and (order[edge] != len(sections) - 1 or fa != total):
                r.err(f"transition {tid} (no b) must be at the end ({dur}) on the last section")
            if owner != edge:
                r.err(f"transition {tid}: owner {owner!r} must be {edge!r}")
            continue
        if sa not in sec_by_id or sb not in sec_by_id:
            r.err(f"transition {tid}: unknown section {sa if sa not in sec_by_id else sb!r}")
            continue
        if order[sb] != order[sa] + 1:
            r.err(f"transition {tid}: {sa} and {sb} are not adjacent in that order")
            continue
        A, B = sec_by_id[sa], sec_by_id[sb]
        if fa != F(A["to"], fps) or fa != F(B["from"], fps):
            r.err(f"transition {tid} at frame {fa} is not on the {sa}/{sb} boundary ({sa} ends at frame {F(A['to'], fps)}, {sb} starts at frame {F(B['from'], fps)})")
        if owner not in (sa, sb):
            r.err(f"transition {tid}: owner {owner!r} must be {sa} or {sb}")
        if wa < F(A["from"], fps) or wb > F(B["to"], fps):
            r.err(f"transition {tid}: window frames {wa}..{wb - 1} leave {sa} + {sb} (frames {F(A['from'], fps)}..{F(B['to'], fps) - 1})")
        if wb > wa:
            windows.append((wa, wb, tid))
        boundary_tr.setdefault(fa, []).append(tid)
        win_of[tid] = (wa, fa, wb)
        beat = tr.get("beat")
        if isinstance(beat, str) and beat in marks and num(marks[beat]) and F(marks[beat], fps) != fa:
            r.warn(f"transition {tid}: beat names mark '{beat}' at frame {F(marks[beat], fps)}, but the cut is frame {fa}")
    windows.sort()
    for (a0, a1, ia), (b0, b1, ib) in zip(windows, windows[1:]):
        if b0 < a1:
            r.err(f"transition windows {ia} (frames {a0}..{a1 - 1}) and {ib} (frames {b0}..{b1 - 1}) overlap")
    for s in sections[1:]:
        if num(s.get("from")):
            f = F(s["from"], fps)
            if len(boundary_tr.get(f, [])) > 1:
                r.err(f"boundary at frame {f} has {len(boundary_tr[f])} transitions: {', '.join(boundary_tr[f])}")
            elif f not in boundary_tr:
                r.warn(f"no transition row for the boundary at frame {f} ({s.get('id')}): a hard cut with no owner or name")

    def render_range(sid: str) -> tuple[int, int]:
        s = sec_by_id[sid]
        lo, hi = F(s["from"], fps), F(s["to"], fps)
        for tr in trans:
            w = win_of.get(tr.get("id"))
            if not w:
                continue
            if tr.get("b") == sid and tr.get("a"):
                lo = min(lo, w[0])
            if tr.get("a") == sid and tr.get("b"):
                hi = max(hi, w[2])
        return lo, hi

    # --- marks -------------------------------------------------------------------------
    for k, v in marks.items():
        if not num(v) or not 0 <= v <= dur:
            r.warn(f"mark {k!r} = {v!r} is not a time inside the film")
        else:
            frame_check(f"mark {k}", v)

    # --- cues ----------------------------------------------------------------------------
    cues = tl.get("cues") or []
    not_role_based: list[str] = []
    for c in cues:
        cid = c.get("id")
        claim("cue", cid)
        sid, role, text = c.get("section"), c.get("role"), c.get("text")
        if not isinstance(text, str) or not text.strip():
            r.err(f"cue {cid}: text is empty")
            text = ""
        if sid not in sec_by_id:
            r.err(f"cue {cid}: unknown section {sid!r}")
            continue
        if not (num(c.get("from")) and num(c.get("to"))):
            r.err(f"cue {cid}: from and to must be numbers")
            continue
        frame_check(f"cue {cid} from", c["from"])
        frame_check(f"cue {cid} to", c["to"])
        f0, f1 = F(c["from"], fps), F(c["to"], fps)
        lo, hi = render_range(sid)
        if f1 <= f0:
            r.err(f"cue {cid}: from {c['from']} is not before to {c['to']} in whole frames")
        elif f0 < lo or f1 > hi:
            r.err(f"cue {cid}: frames {f0}..{f1 - 1} leave the render range of {sid} (frames {lo}..{hi - 1})")
        if role in FACT_ROLES and not str(c.get("source") or "").strip():
            r.err(f"cue {cid}: a {role} cue needs a source")
        if role not in KNOWN_ROLES:
            r.warn(f"cue {cid}: role {role!r} has no meaning in the kit (known: {' '.join(sorted(KNOWN_ROLES))})")
        if isinstance(cid, str) and isinstance(role, str) and not re.fullmatch(re.escape(role) + r"-[0-9]+[a-z]?", cid):
            not_role_based.append(f"{cid} ({role}-<n>)")
        shown = c.get("shown")
        if shown is not None:
            if not (isinstance(shown, dict) and num(shown.get("from")) and num(shown.get("to"))):
                r.err(f"cue {cid}: shown must be {{\"from\": s, \"to\": s}}")
            else:
                s0, s1 = F(shown["from"], fps), F(shown["to"], fps)
                frame_check(f"cue {cid} shown.from", shown["from"])
                frame_check(f"cue {cid} shown.to", shown["to"])
                if s1 <= s0:
                    r.err(f"cue {cid}: shown.from is not before shown.to")
                elif s0 < lo or s1 > hi:
                    r.err(f"cue {cid}: shown frames {s0}..{s1 - 1} extend outside the render range of {sid} (frames {lo}..{hi - 1})")
                elif f1 > f0 and (s0 > f0 or s1 < f1):
                    r.warn(f"cue {cid}: shown {s0}..{s1 - 1} does not cover the readable window {f0}..{f1 - 1}: the words are not drawn while they should be read")
        if text and f1 > f0:
            words = len(text.split()) + (len(str(c.get("attribution") or "").split()) if role in FACT_ROLES else 0)
            need = max(5 / 6, 0.4 * words + 0.5)
            have = (f1 - f0) / fps
            if have + 1e-9 < need:
                r.warn(f"cue {cid}: {have:.2f} s on screen for {words} words; reading needs {need:.2f} s (0.4 s a word + 0.5 s): \"{short(text)}\"")
            if have > 7 + 1e-9 and role not in ("logo", "credit"):
                r.warn(f"cue {cid}: {have:.2f} s on screen; one text event should stay at most about 7 s")
            if text.count("\n") >= 2:
                r.warn(f"cue {cid}: {text.count(chr(10)) + 1} lines; keep a text event to two lines")

    if not_role_based:
        r.warn(f"{len(not_role_based)} cue ids are not role-based, so their content can go stale (stamp-1962 once said 1966): "
               + ", ".join(not_role_based))

    # --- checks, audio, grade --------------------------------------------------------------
    checks = tl.get("checks") or {}
    for rng in checks.get("black") or []:
        if not (isinstance(rng, list) and len(rng) == 2 and num(rng[0]) and num(rng[1])):
            r.err(f"checks.black entry {rng!r} must be [from, to]")
            continue
        if not (0 <= rng[0] < rng[1] <= dur):
            r.err(f"checks.black range {rng} must lie inside [0, {dur}] with from < to")
        frame_check("checks.black from", rng[0])
        frame_check("checks.black to", rng[1])
    if "lastFrameBlack" in checks and not isinstance(checks["lastFrameBlack"], bool):
        r.warn("checks.lastFrameBlack should be true or false")
    audio = tl.get("audio")
    if audio is not None:
        src = (audio or {}).get("src") if isinstance(audio, dict) else None
        if not src:
            r.err("audio must be null or have a src under assets/")
        else:
            ap_ = Path("assets") / src
            if not ap_.exists():
                r.err(f"audio.src {src!r} not found as {ap_.as_posix()}")
            else:
                d = audio.get("duration")
                real = probe_duration(ap_)
                if real is not None and num(d) and abs(real - d) > 0.05:
                    r.warn(f"audio.duration {d} s but the file plays {real:.3f} s")
                if real is not None and real > dur + 0.05:
                    r.warn(f"the track ({real:.2f} s) is longer than the film ({dur} s): it will be cut off")
        if isinstance(audio, dict) and "gain" in audio and not num(audio["gain"]):
            r.warn("audio.gain should be a number")
    grade = tl.get("grade")
    if isinstance(grade, dict):
        for k in ("contrast", "saturation", "gamma", "vignette", "grain"):
            if k in grade and not num(grade[k]):
                r.err(f"grade.{k} must be a number")
        u = grade.get("until")
        if u is not None and (not num(u) or not 0 <= u <= dur):
            r.err(f"grade.until {u!r} must be null or a time inside the film")
        elif num(u):
            frame_check("grade.until", u)

    # --- facts (contract G4) ----------------------------------------------------------------
    fact_cues = [c for c in cues if c.get("role") in FACT_ROLES]
    facts_path = Path("docs/research/facts.md")
    if fact_cues:
        if not facts_path.exists():
            r.warn(f"{len(fact_cues)} data/quote cues but no docs/research/facts.md: every one needs a checked row")
        else:
            rows, problems = parse_facts(facts_path)
            for p in problems:
                r.warn(p)
            today = dt.date.today()
            for c in fact_cues:
                row = rows.get(c.get("id"))
                if row is None:
                    r.warn(f"cue {c.get('id')}: no row in docs/research/facts.md")
                    continue
                verdict = row.get("verdict", "").strip("`* ").lower()
                if verdict not in ("verified", "corrected"):
                    r.warn(f"cue {c.get('id')}: facts.md verdict is {verdict or 'empty'!r}; only verified or corrected may go on screen")
                on = row.get("on screen")
                if on is not None and norm_words(on) != norm_words(c.get("text") or ""):
                    r.warn(f"cue {c.get('id')}: on-screen words differ from facts.md: \"{short(c.get('text') or '')}\" vs \"{short(on)}\"")
                rv = row.get("re-verify by", "")
                m = re.search(r"\d{4}-\d{2}-\d{2}", rv)
                if m:
                    try:
                        if dt.date.fromisoformat(m.group(0)) < today:
                            r.warn(f"cue {c.get('id')}: re-verify-by date {m.group(0)} has passed")
                    except ValueError:
                        pass
                elif not rv.strip():
                    r.warn(f"cue {c.get('id')}: facts.md row has no re-verify-by date")
            known = {c.get("id") for c in cues}
            for cid in rows:
                if cid not in known:
                    r.warn(f"facts.md row for {cid!r}, which is not a cue in the timeline")

    # --- the music ------------------------------------------------------------------------------
    bp = Path("data/beats.json")
    if bp.exists():
        try:
            beats = json.loads(bp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            beats = {}
            r.warn("data/beats.json is not valid JSON")
        if beats.get("beats") or beats.get("onsets"):
            if num(beats.get("fps")) and beats["fps"] != fps:
                r.warn(f"data/beats.json was made at {beats['fps']} fps, the film is {fps}: re-run analyze_music.py")
            src = (audio or {}).get("src") if isinstance(audio, dict) else None
            ba = str(beats.get("audio") or "")
            if src and ba and Path(ba).name != Path(src).name:
                r.warn(f"data/beats.json measured {ba!r}, but audio.src is {src!r}: re-run analyze_music.py")
            try:
                snap = sibling("snap.py")
                ev = snap.load_events(beats, fps)
                end = snap.music_end(beats, tl)
                for s in sections[1:]:
                    f = F(s["from"], fps)
                    if end and f > end * fps + 1:
                        continue
                    k, d, _ = snap.best(ev, f)
                    if d is None or abs(d) > 2:
                        r.warn(f"boundary {s.get('id')} (frame {f}) is {'far from' if d is None else f'{abs(d):.1f} frames from'} the nearest measured event; see snap.py")
            except Exception as e:  # snap.py missing or broken: say so, do not fail the check
                r.warn(f"could not compare boundaries with the music ({e})")

    return finish(r, tl, len(sections), len(trans), len(cues), len(marks), total, fps, dur)


def probe_duration(p: Path) -> float | None:
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return float(out)
    except (ValueError, subprocess.SubprocessError, OSError):
        return None


def F(t: float, fps: float) -> int:
    """Seconds -> frame, rounding half up like the kit's Math.round."""
    return int(math.floor(t * fps + 0.5))


def finish(r: Report, tl: dict, ns: int = 0, nt: int = 0, nc: int = 0, nm: int = 0, total: int = 0, fps: float = 0, dur: float = 0) -> int:
    if ns:
        print(f"check-timeline: {asc(tl.get('title', ''))} ({asc(tl.get('slug', ''))}): {ns} sections, {nt} transitions, "
              f"{nc} cues, {nm} marks, {total} frames ({dur} s at {fps:g} fps)")
    for e in r.errors:
        print(f"ERROR: {asc(e)}")
    for w in r.warnings:
        print(f"WARN: {asc(w)}")
    print(f"check-timeline: {len(r.errors)} errors, {len(r.warnings)} warnings")
    print("FAIL" if r.errors else "PASS")
    return 3 if r.errors else 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
