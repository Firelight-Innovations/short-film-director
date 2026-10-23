"""Record where a piece of media came from: one line under "Assets" in docs/rights.md.

    python scripts/log-asset.py "<file>: source, URL, licence, how processed"

Example:
    python scripts/log-asset.py "assets/footage/02-ink/paper.jpg: Wikimedia Commons, https://commons.wikimedia.org/wiki/File:X.jpg, CC0, cropped and greyed"

Every agent that brings media into the film (a still, a clip, a font, a texture,
a generated image, the track) runs this, so the rights register is filled while
the work happens, not reconstructed at the end. The line goes at the end of the
"Assets" section of docs/rights.md (any heading level). If there is no such
section it is added at the end; if there is no file it is created. The read and
write happen under docs/.rights.lock (an exclusive lock file, retried every
50 ms), because researchers and builders log in parallel and an unlocked
read-insert-write loses lines. A lock older than 30 s is taken as left by a
killed run and removed.

It warns, without failing, when the file does not exist, when no URL or origin
word is given, or when no licence is recognisable, because a line that cannot be
checked later is the line that causes trouble at posting time.

Run from the film project root. Exit codes: 0 appended, 2 no text.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import time
from pathlib import Path

REGISTER = Path("docs") / "rights.md"
LOCK = Path("docs") / ".rights.lock"
STALE_S = 30.0
NEW_FILE = "# Rights register\n\nMusic, likenesses, generated media, footage, fonts: owner, licence, use, status.\n\n## Assets\n\n"
LICENCE_WORDS = re.compile(
    r"\b(CC0|CC[- ]?BY[\w.-]*|public domain|PD|OFL|SIL|MIT|Apache|licen[cs]ed|licen[cs]e|royalty[- ]free|"
    r"own work|own|generated|made in code|code|commissioned|permission|all rights reserved|link-only)\b",
    re.IGNORECASE,
)
ORIGIN_WORDS = re.compile(r"(https?://|\bgenerated\b|\bcode\b|\bown\b|\bshot\b|\brecorded\b|\buser\b|\bclient\b)", re.IGNORECASE)


def insert_under_assets(body: str, line: str) -> str:
    lines = body.splitlines()
    head = None
    level = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^(#+)\s+Assets\b", ln.strip(), re.IGNORECASE)
        if m:
            head, level = i, len(m.group(1))
            break
    if head is None:
        text = body.rstrip("\n")
        return (text + "\n\n" if text else "") + "## Assets\n\n" + line + "\n"
    end = len(lines)
    for j in range(head + 1, len(lines)):
        m = re.match(r"^(#+)\s", lines[j])
        if m and len(m.group(1)) <= level:
            end = j
            break
    k = end
    while k > head + 1 and not lines[k - 1].strip():
        k -= 1  # place it after the last non-blank line of the section
    lines.insert(k, line)
    if k == head + 1:
        lines.insert(k, "")  # a blank line after the heading
    out = "\n".join(lines)
    return out + "\n"


def lock() -> int:
    """Take docs/.rights.lock; wait while another run holds it, clear it when stale."""
    while True:
        try:
            return os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (FileExistsError, PermissionError):  # Windows gives PermissionError while the lock is being deleted
            try:
                if time.time() - LOCK.stat().st_mtime > STALE_S:
                    LOCK.unlink()
                    print(f"log-asset: warning: removed a stale {LOCK.as_posix()}")
                    continue
            except OSError:
                pass
            time.sleep(0.05)


def main() -> int:
    ap = argparse.ArgumentParser(prog="log-asset.py", description='Append "<file>: source, URL, licence, how processed" to docs/rights.md under Assets.')
    ap.add_argument("text", nargs="+", help='"<file>: source, URL, licence, how processed"')
    a = ap.parse_args()
    text = " ".join(" ".join(a.text).split())
    if not text:
        print("log-asset: no text")
        return 2
    name, sep, rest = text.partition(": ")
    if not sep:
        print('log-asset: warning: write "<file>: source, URL, licence, how processed" (no "<file>: " found)')
        rest = text
    elif not Path(name).exists():
        print(f"log-asset: warning: {name} does not exist (from the project root)")
    if not ORIGIN_WORDS.search(rest):
        print("log-asset: warning: no URL or origin (generated, code, own, shot, user) in the line")
    if not LICENCE_WORDS.search(rest):
        print("log-asset: warning: no licence recognised (CC0, PD, CC-BY-4.0, OFL, licensed, generated, ...)")
    line = f"- {dt.date.today().isoformat()} {text}"
    REGISTER.parent.mkdir(parents=True, exist_ok=True)
    fd = lock()
    try:
        body = REGISTER.read_text(encoding="utf-8") if REGISTER.exists() else NEW_FILE
        REGISTER.write_text(insert_under_assets(body, line), encoding="utf-8", newline="\n")
    finally:
        os.close(fd)
        try:
            LOCK.unlink()
        except OSError:
            pass
    print(f"log-asset: {REGISTER.as_posix()} <- {line}")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
