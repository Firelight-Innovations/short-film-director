"""Append one timestamped line to docs/decisions.md.

    python scripts/log-decision.py "who: what was decided, and why"

Writes "- [YYYY-MM-DD HH:MM] who: what, and why" at the end of docs/decisions.md
(created with a heading if it does not exist). Start the text with who decided
("lead:", "sec-03-data:", "user:") and give the reason: the log is how the next
session, or the next person, picks the film up. Several arguments are joined with
spaces, so the quotes are optional in a shell that keeps them together.

Run from the film project root. Exit codes: 0 appended, 2 no text.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

LOG = Path("docs") / "decisions.md"
HEADER = "# Decisions\n\nOne line per call: `- [time] who: what, and why`. Append with `python scripts/log-decision.py`.\n\n"


def main() -> int:
    ap = argparse.ArgumentParser(prog="log-decision.py", description="Append a timestamped line to docs/decisions.md.")
    ap.add_argument("text", nargs="+", help='"who: what, and why"')
    a = ap.parse_args()
    text = " ".join(a.text).strip()
    if not text:
        print("log-decision: no text")
        return 2
    text = " ".join(text.split())  # one line, whatever the shell passed
    if ":" not in text.split()[0] and ": " not in text[:40]:
        print('log-decision: warning: start with who decided, e.g. "lead: ..."')
    if not LOG.exists():
        LOG.parent.mkdir(parents=True, exist_ok=True)
        LOG.write_text(HEADER, encoding="utf-8")
    body = LOG.read_text(encoding="utf-8")
    line = f"- [{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}] {text}\n"
    with LOG.open("a", encoding="utf-8", newline="\n") as f:
        if body and not body.endswith("\n"):
            f.write("\n")
        f.write(line)
    print(f"log-decision: {LOG.as_posix()} <- {line.strip()}")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
