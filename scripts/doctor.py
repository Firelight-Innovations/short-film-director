"""Pre-render health check. Run it before every full render.

    python scripts/doctor.py [--quick]

Run from the project root. Each check prints one PASS, WARN or FAIL line, with the
details and the fix under it. A full render takes minutes and a review takes an hour;
these checks take seconds and catch the faults that would waste both:

  timeline   scripts/check-timeline.py exits 0 (the timeline.json rules)
  chains     every chain in data/chains.json is fresh against data/chains.lock.json
             (a baked plate built from old words, plates cut from an old film)
  fonts      every font("X") literal in src/ is in src/kit/fonts.manifest.json, and
             every file the manifest lists exists under assets/
  assets     every staticFile("...") literal in src/ and every board image in
             data/storyboard.json exists under assets/, with the exact case (Windows
             forgives a wrong case; Linux and the cloud do not)
  registry   every id in src/sections/registry.ts is a section in the timeline, and
             every timeline section is registered (an unregistered one renders as a
             test card)
  music      data/beats.json exists when timeline.audio is set
  remotion   the installed remotion and @remotion/* versions equal the pins in
             package.json (a drifted version changes defaults and output)
  props      data/props.final.json turns the dev overlay off
  ffmpeg     ffmpeg and ffprobe are on PATH (the grade and the checks need them)

--quick compares chain files by path and size instead of hashing their content.

Exit: 0 when nothing FAILs (WARN lines do not fail), 3 otherwise.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # importing chain.py must not leave __pycache__ in scripts/
HERE = Path(__file__).resolve().parent


def project_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "data").is_dir():
        return cwd
    up = HERE.parent
    if (up / "data").is_dir():
        return up
    return cwd


ROOT = project_root()
RESULTS: list[tuple[str, str]] = []
SECTION_ID = re.compile(r"^[0-9]{2}-[a-z0-9-]+$")


def report(status: str, name: str, summary: str, details: list[str] | None = None) -> None:
    RESULTS.append((status, name))
    print(f"{status:<4} {name:<9} {summary}")
    for d in details or []:
        print(f"       {d}")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def src_files() -> list[Path]:
    src = ROOT / "src"
    if not src.is_dir():
        return []
    out = []
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", "__pycache__")]
        for f in filenames:
            if f.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs")):
                out.append(Path(dirpath) / f)
    return sorted(out)


def strip_comments(text: str) -> str:
    """Drop // and /* */ comments so an example in a comment is not taken for a use."""
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"(^|[^:\"'`\\])//[^\n]*", r"\1", text)


def literals(pattern: re.Pattern) -> list[tuple[str, str, int]]:
    """(value, file, line) for every match of a call with one string literal."""
    hits = []
    for f in src_files():
        text = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        for m in pattern.finditer(text):
            value = m.group(2)
            if "${" in value:
                continue
            line = text.count("\n", 0, m.start()) + 1
            hits.append((value, f.relative_to(ROOT).as_posix(), line))
    return hits


def exact_case(path: Path) -> str | None:
    """None if the path exists with exactly this case; else what is wrong."""
    cur = ROOT
    for part in path.relative_to(ROOT).parts:
        try:
            names = os.listdir(cur)
        except OSError:
            return "missing"
        if part in names:
            cur = cur / part
            continue
        lower = [n for n in names if n.lower() == part.lower()]
        if lower:
            return f"case differs on disk: {lower[0]}"
        return "missing"
    return None


# ---- checks ----------------------------------------------------------------

def check_timeline() -> None:
    tool = ROOT / "scripts" / "check-timeline.py"
    if not tool.exists():
        report("FAIL", "timeline", "scripts/check-timeline.py is missing")
        return
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    res = subprocess.run([sys.executable, str(tool)], cwd=ROOT, env=env, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    lines = [ln.strip() for ln in (res.stdout + res.stderr).splitlines() if ln.strip()]
    warns = [ln for ln in lines if ln.upper().startswith("WARN")]
    if res.returncode == 0:
        report("PASS", "timeline", f"check-timeline.py exit 0, {len(warns)} warning(s)", warns[:12])
    else:
        errors = [ln for ln in lines if not ln.upper().startswith("WARN")]
        report("FAIL", "timeline", f"check-timeline.py exit {res.returncode}",
               errors[:20] + ["fix: python scripts/check-timeline.py, then edit data/timeline.json"])


def load_chain_module():
    path = HERE / "chain.py"
    if not path.exists():
        path = ROOT / "scripts" / "chain.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("sfd_chain", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_chains(quick: bool) -> None:
    if not (ROOT / "data" / "chains.json").exists():
        report("PASS", "chains", "no data/chains.json (no dependent assets declared)")
        return
    mod = load_chain_module()
    if mod is None:
        report("FAIL", "chains", "scripts/chain.py is missing")
        return
    try:
        sts = mod.states(quick=quick)
    except mod.ChainError as e:
        report("FAIL", "chains", f"data/chains.json is invalid: {e}")
        return
    stale = [(n, r) for n, fresh, r in sts if not fresh]
    if not stale:
        report("PASS", "chains", f"{len(sts)} chain(s), all fresh" + (" (by size)" if quick else ""))
        return
    details = []
    for name, reasons in stale:
        details.append(f"{name}: " + "; ".join(reasons))
        details.append(f"  fix: python scripts/chain.py run {name}")
    report("FAIL", "chains", f"{len(stale)} of {len(sts)} chain(s) stale", details)


def manifest_entries(data) -> list[dict]:
    """Every file entry, with its family, in any shape src/kit/fonts.ts reads:
    { "Family": [ {style, weight, file} ] }, { "Family": { kind, files: [...] } },
    { "fonts": [ {family, ...} ] } or that list alone."""
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    if not isinstance(data, dict):
        return []
    if isinstance(data.get("fonts"), list):
        return [e for e in data["fonts"] if isinstance(e, dict)]
    out = []
    for family, block in data.items():
        files = block if isinstance(block, list) else (block.get("files", []) if isinstance(block, dict) else [])
        for e in files:
            if isinstance(e, dict):
                out.append({"family": e.get("family", family), **{k: v for k, v in e.items() if k != "family"},
                            "file": e.get("file") or e.get("path") or e.get("url")})
    return out


def check_fonts() -> None:
    man_path = ROOT / "src" / "kit" / "fonts.manifest.json"
    used = literals(re.compile(r"\bfont\(\s*([\"'`])([^\"'`\n]+)\1\s*[,)]"))
    entries = []
    if man_path.exists():
        try:
            entries = manifest_entries(read_json(man_path))
        except json.JSONDecodeError as e:
            report("FAIL", "fonts", f"src/kit/fonts.manifest.json is not valid JSON: {e}")
            return
    elif used:
        report("FAIL", "fonts", "src/kit/fonts.manifest.json is missing but src/ calls font()",
               ['fix: node scripts/fetch-fonts.mjs "Family:400,700"'])
        return
    families = {str(e.get("family")) for e in entries}
    problems = []
    for family, file, line in used:
        if family not in families:
            problems.append(f'{file}:{line} font("{family}") is not vendored. fix: node scripts/fetch-fonts.mjs "{family}:400"')
    for e in entries:
        rel = str(e.get("file", ""))
        if not rel:
            problems.append(f"manifest entry for {e.get('family')} has no file")
            continue
        p = ROOT / "assets" / rel
        why = exact_case(p)
        if why:
            problems.append(f"assets/{rel}: {why}")
    n_used = len({u[0] for u in used})
    if problems:
        report("FAIL", "fonts", f"{len(problems)} problem(s)", problems[:30])
    else:
        report("PASS", "fonts", f"{n_used} family(ies) used in src/, {len(entries)} file(s) vendored")


def check_assets() -> None:
    used = literals(re.compile(r"\bstaticFile\(\s*([\"'`])([^\"'`\n]+)\1\s*\)"))
    problems = []
    seen = set()
    for value, file, line in used:
        rel = value.lstrip("/")
        if rel in seen:
            continue
        seen.add(rel)
        why = exact_case(ROOT / "assets" / rel)
        if why:
            problems.append(f'{file}:{line} staticFile("{value}"): assets/{rel} {why}')
    # The animatic reads its board images through staticFile(panel.image).
    board = ROOT / "data" / "storyboard.json"
    n_board = 0
    if board.exists():
        try:
            panels = read_json(board).get("panels", [])
        except (json.JSONDecodeError, AttributeError):
            panels = []
            problems.append("data/storyboard.json is not valid JSON")
        for p in panels:
            img = p.get("image") if isinstance(p, dict) else None
            if isinstance(img, str) and img:
                n_board += 1
                why = exact_case(ROOT / "assets" / img.lstrip("/"))
                if why:
                    problems.append(f'data/storyboard.json panel {p.get("id", "?")}: image assets/{img} {why}')
    if problems:
        report("FAIL", "assets", f"{len(problems)} missing or mis-cased file(s)", problems[:30])
    else:
        report("PASS", "assets", f"{len(seen)} staticFile() literal path(s) and {n_board} board image(s), all present")


def check_registry(tl: dict | None) -> None:
    reg = ROOT / "src" / "sections" / "registry.ts"
    if tl is None:
        report("FAIL", "registry", "data/timeline.json could not be read")
        return
    if not reg.exists():
        report("FAIL", "registry", "src/sections/registry.ts is missing")
        return
    text = strip_comments(reg.read_text(encoding="utf-8"))
    registered = []
    for m in re.finditer(r"([\"'])([0-9]{2}-[a-z0-9-]+)\1\s*:", text):
        if m.group(2) not in registered:
            registered.append(m.group(2))
    timeline_ids = [s.get("id") for s in tl.get("sections", [])]
    extra = [i for i in registered if i not in timeline_ids]
    missing = [i for i in timeline_ids if i not in registered]
    details = [f"{i}: registered but not a section in data/timeline.json" for i in extra]
    details += [f"{i}: in the timeline but not registered (plays as a labelled test card; register a stub before a full render: the skill's references/05-build.md section 3)" for i in missing]
    for i in registered:
        folder = ROOT / "src" / "sections" / i
        if not any((folder / n).exists() for n in ("index.tsx", "index.ts")):
            details.append(f"{i}: src/sections/{i}/index.tsx is missing")
    if details:
        report("FAIL", "registry", f"{len(registered)} registered, {len(timeline_ids)} in the timeline", details)
    else:
        report("PASS", "registry", f"{len(registered)} section(s), registry and timeline agree")


def check_music(tl: dict | None) -> None:
    if tl is None:
        return
    audio = tl.get("audio")
    if not audio:
        report("PASS", "music", "no audio in the timeline")
        return
    beats = ROOT / "data" / "beats.json"
    src = str(audio.get("src", ""))
    if not beats.exists():
        report("FAIL", "music", f"timeline.audio is {src} but data/beats.json is missing",
               [f"fix: python scripts/analyze_music.py assets/{src}"])
        return
    try:
        b = read_json(beats)
    except json.JSONDecodeError:
        report("FAIL", "music", "data/beats.json is not valid JSON")
        return
    named = None
    for key in ("audio", "src", "source", "file", "track"):
        v = b.get(key) if isinstance(b, dict) else None
        if isinstance(v, dict):
            v = v.get("src") or v.get("file") or v.get("path")
        if isinstance(v, str) and v:
            named = v
            break
    if named and Path(named).name.lower() != Path(src).name.lower():
        report("FAIL", "music", f"data/beats.json was measured from {Path(named).name}, the timeline plays {Path(src).name}",
               [f"fix: python scripts/analyze_music.py assets/{src}"])
        return
    report("PASS", "music", f"data/beats.json present for {src}")


def check_remotion() -> None:
    pkg_path = ROOT / "package.json"
    if not pkg_path.exists():
        report("FAIL", "remotion", "package.json is missing")
        return
    pkg = read_json(pkg_path)
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    pinned = {k: v for k, v in deps.items() if k == "remotion" or k.startswith("@remotion/")}
    if "remotion" not in pinned:
        report("FAIL", "remotion", "package.json does not depend on remotion")
        return
    if not (ROOT / "node_modules").exists():
        report("FAIL", "remotion", "node_modules is missing", ["fix: npm install"])
        return
    problems, loose = [], []
    exact = re.compile(r"^\d+\.\d+\.\d+$")
    for name, spec in sorted(pinned.items()):
        meta = ROOT / "node_modules" / Path(*name.split("/")) / "package.json"
        if not meta.exists():
            problems.append(f"{name} {spec} is not installed. fix: npm install")
            continue
        have = read_json(meta).get("version", "?")
        if exact.match(spec):
            if have != spec:
                problems.append(f"{name}: package.json pins {spec}, installed {have}. fix: npm install")
        else:
            loose.append(f"{name}: '{spec}' is not an exact pin (installed {have})")
    want = pinned["remotion"]
    if problems:
        report("FAIL", "remotion", f"installed versions differ from the pins (remotion {want})", problems)
    elif loose:
        report("WARN", "remotion", f"remotion {want} installed; some packages are not pinned exactly", loose)
    else:
        report("PASS", "remotion", f"remotion {want}, {len(pinned)} package(s) match their pins")


def check_props() -> None:
    p = ROOT / "data" / "props.final.json"
    if not p.exists():
        report("FAIL", "props", "data/props.final.json is missing (render:final reads it)")
        return
    try:
        props = read_json(p)
    except json.JSONDecodeError:
        report("FAIL", "props", "data/props.final.json is not valid JSON")
        return
    if props.get("showDevOverlay") is not False:
        report("FAIL", "props", "data/props.final.json must set showDevOverlay to false")
        return
    report("PASS", "props", "final props turn the dev overlay off")


def check_ffmpeg() -> None:
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        report("FAIL", "ffmpeg", f"not on PATH: {', '.join(missing)} (the grade and the measured checks need them)")
    else:
        report("PASS", "ffmpeg", "ffmpeg and ffprobe on PATH")


def main() -> int:
    # A cue or a path with an accent must not crash a cp1252 console.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Pre-render health check for a film project.",
                                 epilog="Exit 0 when nothing fails, 3 otherwise.")
    ap.add_argument("--quick", action="store_true", help="compare chain files by size, not content")
    args = ap.parse_args()
    print(f"doctor: {ROOT}")
    tl = None
    tl_path = ROOT / "data" / "timeline.json"
    if tl_path.exists():
        try:
            tl = read_json(tl_path)
        except json.JSONDecodeError:
            tl = None
    check_timeline()
    check_chains(args.quick)
    check_fonts()
    check_assets()
    check_registry(tl)
    check_music(tl)
    check_remotion()
    check_props()
    check_ffmpeg()
    fails = [n for s, n in RESULTS if s == "FAIL"]
    if fails:
        print(f"FAIL: {len(fails)} of {len(RESULTS)} checks ({', '.join(fails)}). Fix them before a full render.")
        return 3
    print(f"PASS: {len(RESULTS)} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
