"""Dependent-asset chains: rebuild what is made from other files, and know when it is stale.

    python scripts/chain.py list
    python scripts/chain.py check [name]          exit 3 if any chain is stale
    python scripts/chain.py run [name | --all]    build, then check, then update the lock

Run from the project root. A chain is anything the film shows that is made from other
files and does not rebuild itself: plates with words baked in, plates cut from frames
of the finished film, a sprite sheet made by a Python painter. Without a chain, a
changed cue or a changed section leaves the old pictures on screen and nothing says so.

data/chains.json declares them:

    { "chains": [
        { "name": "00-open-plates",
          "inputs":  ["data/timeline.json#cues:00-open", "scripts/00-open/**", "work/00-open/src/**"],
          "outputs": ["assets/footage/00-open/seq/*.webp"],
          "build":   ["python scripts/00-open/build.py all"],
          "check":   ["python scripts/flash-check.py out/check/00-open --from 0 --to 8.5"] } ] }

inputs and outputs are globs relative to the project root (** is recursive), or a slice
of a JSON file:
    data/timeline.json#cues:<section>     that section's cues
    data/timeline.json#section:<id>       that section's row, its cues and the
                                          transitions that touch it
Every matched file is hashed by content (sha256); a slice is hashed as canonical JSON.

build and check are commands, one program each, run from the project root in order.
A leading "python" runs this same interpreter. Write paths with forward slashes. A
command with | & < > ; or a backslash goes through the system shell, which is not
portable: prefer a small script.

`run name` always runs that chain. `run` with no name runs every stale chain, in file
order, and repeats until nothing is stale (so a chain whose inputs are another chain's
outputs runs after it). `run --all` runs every chain. The lock, data/chains.lock.json,
records each chain's input and output hashes after a build whose checks passed. `check`
compares the files on disk with the lock: a changed input, a changed or missing output,
or a changed chain definition is STALE.

Exit: 0 fresh / done; 3 stale, a failed command, or an invalid chains.json; 2 bad usage.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path


def project_root() -> Path:
    """The current directory (tools run from the project root), or the folder above
    this script when the current directory is not a film project."""
    cwd = Path.cwd()
    if (cwd / "data").is_dir():
        return cwd
    up = Path(__file__).resolve().parent.parent
    if (up / "data").is_dir():
        return up
    return cwd


ROOT = project_root()
CHAINS = ROOT / "data" / "chains.json"
LOCK = ROOT / "data" / "chains.lock.json"
SKIP_DIRS = {"__pycache__", ".git", "node_modules"}


class ChainError(Exception):
    """chains.json is malformed."""


# ---- loading ---------------------------------------------------------------

def load_chains() -> list[dict]:
    if not CHAINS.exists():
        return []
    try:
        data = json.loads(CHAINS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ChainError(f"data/chains.json is not valid JSON: {e}") from e
    chains = data.get("chains")
    if not isinstance(chains, list):
        raise ChainError('data/chains.json needs a "chains" list')
    seen = set()
    for i, c in enumerate(chains):
        where = f"chains[{i}]"
        if not isinstance(c, dict):
            raise ChainError(f"{where} is not an object")
        name = c.get("name")
        if not isinstance(name, str) or not name:
            raise ChainError(f"{where} has no name")
        if name in seen:
            raise ChainError(f'two chains are named "{name}"')
        seen.add(name)
        for key in ("inputs", "outputs", "build"):
            v = c.get(key)
            if not isinstance(v, list) or not v or not all(isinstance(x, str) and x for x in v):
                raise ChainError(f'chain "{name}": "{key}" must be a non-empty list of strings')
        chk = c.get("check", [])
        if not isinstance(chk, list) or not all(isinstance(x, str) and x for x in chk):
            raise ChainError(f'chain "{name}": "check" must be a list of strings')
        for entry in c["inputs"] + c["outputs"]:
            if "#" in entry:
                _, frag = entry.split("#", 1)
                kind, _, arg = frag.partition(":")
                if kind not in ("cues", "section") or not arg:
                    raise ChainError(f'chain "{name}": unknown slice "#{frag}" (use #cues:<section> or #section:<id>)')
    return chains


def load_lock() -> dict:
    if not LOCK.exists():
        return {}
    try:
        return json.loads(LOCK.read_text(encoding="utf-8")).get("chains", {})
    except (json.JSONDecodeError, AttributeError):
        print("warning: data/chains.lock.json is unreadable; every chain counts as never built")
        return {}


def save_lock(lock: dict) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps({"chains": lock}, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


# ---- hashing ---------------------------------------------------------------

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(1 << 20)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def glob_files(pattern: str) -> list[str]:
    """Files (not folders) matching a project-relative glob, as sorted posix paths."""
    hits = glob.glob(os.path.join(str(ROOT), pattern), recursive=True)
    out = set()
    for h in hits:
        if not os.path.isfile(h):
            continue
        rel = Path(os.path.relpath(h, str(ROOT)))
        parts = rel.parts
        if any(part in SKIP_DIRS for part in parts) or rel.suffix == ".pyc":
            continue
        out.add(rel.as_posix())
    return sorted(out)


def json_slice(entry: str):
    file, frag = entry.split("#", 1)
    kind, _, arg = frag.partition(":")
    path = ROOT / file
    if not path.exists():
        return None, f"{file} does not exist"
    data = json.loads(path.read_text(encoding="utf-8"))
    cues = [c for c in data.get("cues", []) if c.get("section") == arg]
    if kind == "cues":
        return cues, None
    row = next((s for s in data.get("sections", []) if s.get("id") == arg), None)
    if row is None:
        return None, f'{file} has no section "{arg}"'
    trs = [t for t in data.get("transitions", []) if t.get("a") == arg or t.get("b") == arg]
    return {"section": row, "cues": cues, "transitions": trs}, None


def entry_digest(entry: str, content: bool = True) -> dict:
    """{"sha": ..., "files": n} for one input or output entry. content=False hashes
    paths and sizes only (fast; used by doctor --quick). A JSON slice is always
    hashed by content: it is small."""
    if "#" in entry:
        value, problem = json_slice(entry)
        if problem:
            return {"sha": "missing", "files": 0, "problem": problem}
        return {"sha": hashlib.sha256(canonical(value)).hexdigest(), "files": 1}
    files = glob_files(entry)
    h = hashlib.sha256()
    for rel in files:
        p = ROOT / rel
        sig = file_sha(p) if content else str(p.stat().st_size)
        h.update(f"{rel}\0{sig}\n".encode("utf-8"))
    return {"sha": h.hexdigest() if files else "none", "files": len(files)}


def definition_sha(chain: dict) -> str:
    keep = {k: chain.get(k) for k in ("inputs", "outputs", "build", "check")}
    return hashlib.sha256(canonical(keep)).hexdigest()


# ---- state -----------------------------------------------------------------

def state_of(chain: dict, lock: dict, quick: bool = False) -> tuple[bool, list[str]]:
    """(fresh, reasons). quick: files are compared by path and size, not content."""
    name = chain["name"]
    reasons: list[str] = []
    rec = lock.get(name)
    outs = {e: entry_digest(e, content=not quick) for e in chain["outputs"]}
    missing = [e for e, d in outs.items() if d["files"] == 0]
    if missing:
        reasons.append("outputs missing: " + ", ".join(missing))
    if rec is None:
        reasons.append("never built (no entry in data/chains.lock.json)")
        return False, reasons
    if rec.get("definition") != definition_sha(chain):
        reasons.append("the chain's definition in data/chains.json changed")
    changed_in = []
    key = "size" if quick else "sha"
    for e in chain["inputs"]:
        d = entry_digest(e, content=not quick)
        if d.get("problem"):
            reasons.append(f"input {e}: {d['problem']}")
        old = rec.get("inputs", {}).get(e)
        if old is None or old.get(key) != d["sha"]:
            note = ""
            if old is not None and old.get("files") != d["files"]:
                note = f" ({old.get('files')} -> {d['files']} files)"
            changed_in.append(e + note)
    if changed_in:
        reasons.append("inputs changed: " + ", ".join(changed_in))
    changed_out = []
    for e, d in outs.items():
        if e in missing:
            continue
        old = rec.get("outputs", {}).get(e)
        if old is None or old.get(key) != d["sha"]:
            note = ""
            if old is not None and old.get("files") != d["files"]:
                note = f" ({old.get('files')} -> {d['files']} files)"
            changed_out.append(e + note)
    if changed_out:
        reasons.append("outputs differ from the last build: " + ", ".join(changed_out))
    return not reasons, reasons


def signatures(entries: list[str]) -> dict:
    out = {}
    for e in entries:
        full = entry_digest(e)
        quick = entry_digest(e, content=False)
        out[e] = {"sha": full["sha"], "size": quick["sha"], "files": full["files"]}
    return out


def record(chain: dict) -> dict:
    return {
        "built": _dt.datetime.now().isoformat(timespec="seconds"),
        "definition": definition_sha(chain),
        "inputs": signatures(chain["inputs"]),
        "outputs": signatures(chain["outputs"]),
    }


def states(quick: bool = False) -> list[tuple[str, bool, list[str]]]:
    """For doctor.py: [(name, fresh, reasons)] for every chain."""
    lock = load_lock()
    return [(c["name"], *state_of(c, lock, quick)) for c in load_chains()]


# ---- running ---------------------------------------------------------------

def needs_shell(cmd: str) -> bool:
    """True when the command uses shell syntax outside quotes (| & < > ; ( )), or a
    backslash, which shlex would read as an escape."""
    if "\\" in cmd:
        return True
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        tokens = list(lex)
    except ValueError:
        return True
    return any(t and all(ch in "();<>|&" for ch in t) for t in tokens)


def run_command(cmd: str) -> int:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    t0 = time.time()
    if needs_shell(cmd):
        print(f"  $ {cmd}   (through the shell)", flush=True)
        code = subprocess.run(cmd, shell=True, cwd=ROOT, env=env).returncode
    else:
        try:
            argv = shlex.split(cmd)
        except ValueError as e:
            print(f"  cannot parse command: {cmd} ({e})")
            return 2
        if not argv:
            return 0
        exe = argv[0]
        if exe in ("python", "python3", "py"):
            argv[0] = sys.executable
        else:
            found = shutil.which(exe)
            if found:
                argv[0] = found
        print(f"  $ {cmd}", flush=True)
        try:
            code = subprocess.run(argv, cwd=ROOT, env=env).returncode
        except FileNotFoundError:
            print(f"  not found: {exe}")
            return 127
    print(f"    exit {code}, {time.time() - t0:.1f} s", flush=True)
    return code


def run_chain(chain: dict, lock: dict) -> bool:
    name = chain["name"]
    print(f"== run {name}")
    for cmd in chain["build"]:
        if run_command(cmd) != 0:
            print(f"FAIL {name}: build command failed: {cmd}")
            return False
    for cmd in chain.get("check", []):
        if run_command(cmd) != 0:
            print(f"FAIL {name}: check failed: {cmd}  (outputs built but not locked)")
            return False
    missing = [e for e in chain["outputs"] if entry_digest(e, content=False)["files"] == 0]
    if missing:
        print(f"FAIL {name}: the build made no files for: {', '.join(missing)}")
        return False
    lock[name] = record(chain)
    save_lock(lock)
    n = sum(v["files"] for v in lock[name]["outputs"].values())
    print(f"done {name}: {n} output files locked")
    return True


# ---- commands --------------------------------------------------------------

def pick(chains: list[dict], name: str | None) -> list[dict]:
    if name is None:
        return chains
    found = [c for c in chains if c["name"] == name]
    if not found:
        known = ", ".join(c["name"] for c in chains) or "(none)"
        print(f'no chain named "{name}". Known: {known}')
        sys.exit(2)
    return found


def cmd_list(chains: list[dict]) -> int:
    if not chains:
        print("no chains declared (data/chains.json is missing or empty)")
        return 0
    lock = load_lock()
    for c in chains:
        fresh, reasons = state_of(c, lock)
        print(f"{'fresh' if fresh else 'STALE'}  {c['name']}")
        print(f"   inputs:  {', '.join(c['inputs'])}")
        print(f"   outputs: {', '.join(c['outputs'])}")
        print(f"   build:   {' ; '.join(c['build'])}")
        if c.get("check"):
            print(f"   check:   {' ; '.join(c['check'])}")
        if c["name"] in lock:
            print(f"   built:   {lock[c['name']].get('built', '?')}")
        for r in reasons:
            print(f"   - {r}")
    return 0


def cmd_check(chains: list[dict], name: str | None) -> int:
    todo = pick(chains, name)
    if not todo:
        print("no chains declared")
        return 0
    lock = load_lock()
    stale = 0
    for c in todo:
        fresh, reasons = state_of(c, lock)
        if fresh:
            print(f"fresh  {c['name']}")
            continue
        stale += 1
        print(f"STALE  {c['name']}")
        for r in reasons:
            print(f"   - {r}")
        print(f"   fix: python scripts/chain.py run {c['name']}")
    print(f"{len(todo) - stale} fresh, {stale} stale")
    return 3 if stale else 0


def cmd_run(chains: list[dict], name: str | None, run_all: bool) -> int:
    lock = load_lock()
    if name or run_all:
        for c in pick(chains, name):
            if not run_chain(c, lock):
                return 3
        return 0
    ran = 0
    for _ in range(max(1, len(chains))):
        ran_this_pass = 0
        for c in chains:
            fresh, _reasons = state_of(c, lock)
            if fresh:
                continue
            if not run_chain(c, lock):
                return 3
            ran_this_pass += 1
        ran += ran_this_pass
        if ran_this_pass == 0:
            break
    print(f"{ran} chain run(s); every chain is fresh" if ran else "every chain is fresh; nothing to run")
    return 0


def main() -> int:
    # A cue or a path with an accent must not crash a cp1252 console.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        description="Run and check dependent-asset chains declared in data/chains.json.",
        epilog="Exit 0 fresh or done; 3 stale, failed or invalid; 2 bad usage.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="every chain, its files and its state")
    p_check = sub.add_parser("check", help="compare files with the lock; exit 3 if stale")
    p_check.add_argument("name", nargs="?")
    p_run = sub.add_parser("run", help="build, check, update the lock")
    p_run.add_argument("name", nargs="?")
    p_run.add_argument("--all", action="store_true", help="run every chain, stale or not")
    args = ap.parse_args()
    try:
        chains = load_chains()
    except ChainError as e:
        print(f"INVALID {e}")
        return 3
    if args.cmd == "list":
        return cmd_list(chains)
    if args.cmd == "check":
        return cmd_check(chains, args.name)
    return cmd_run(chains, args.name, args.all)


if __name__ == "__main__":
    sys.exit(main())
