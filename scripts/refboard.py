"""Reference boards from refs/manifest.json: one contact sheet per section, and refs/BOARD.md.

    python scripts/refboard.py [--section id] [--cols 4] [--w 384]

For every section (or only --section), refs/board-<section>.jpg tiles the
references whose licence allows a copy and whose `file` exists (images; a
video's first second is grabbed with ffmpeg), each labelled with id, kind,
licence, title, author and year. References that are link-only (copyrighted:
never downloaded) follow as text cards, so the board shows everything the
section draws on without copying what may not be copied. References with no
section, or section "film", go on refs/board-film.jpg.

refs/BOARD.md lists every reference, linked, with its licence, by section, in
the timeline's section order, each board embedded above its table, and a list
of the credits owed (CC BY and other attribution licences on assets, fonts,
music and sound). It is rewritten in full on every run, also with --section.

It warns, without failing, about the things that cause trouble at posting time:
a link-only reference that has a file (delete the copy), a file that is
missing, a reference with no URL, a non-commercial (NC) or no-derivatives (ND)
licence, an unknown kind, a duplicate id, a section that is not in the timeline.
Manifest schema: contract part D3 (refs: id, section, kind, title, by, year,
url, licence, file, take).

Run from the film project root. Exit codes: 0 written, 2 no refs/manifest.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

KINDS = {"look", "technique", "fact", "asset", "font", "music", "sound"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
BG, CARD, INK, DIM = (18, 18, 18), (34, 32, 30), (235, 235, 235), (160, 160, 160)


def sibling(name: str):
    p = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(name.replace("-", "_")[:-3], p)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # no __pycache__ in the project's scripts/
    spec.loader.exec_module(mod)
    return mod


def asc(s: object) -> str:
    table = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u00a0": " "}
    return "".join(table.get(c, c) for c in str(s)).encode("ascii", "backslashreplace").decode("ascii")


def link_only(licence: str) -> bool:
    return licence.strip().lower() in ("link-only", "link only", "copyrighted", "all rights reserved", "")


def cell(s: object) -> str:
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def open_ref(path: Path, tmp: Path) -> Image.Image | None:
    if path.suffix.lower() in IMAGE_EXT:
        try:
            im = Image.open(path)
            im.load()
            return im.convert("RGB")
        except OSError:
            return None
    if path.suffix.lower() in VIDEO_EXT:
        still = tmp / (path.stem + ".jpg")
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(path), "-frames:v", "1", str(still)], capture_output=True)
        if r.returncode != 0 or not still.exists():
            r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-frames:v", "1", str(still)], capture_output=True)
        return Image.open(still).convert("RGB") if still.exists() else None
    return None


def board(out: Path, title: str, items: list[tuple[dict, Image.Image | None]], cols: int, w: int, sheet_mod) -> None:
    h = round(w * 9 / 16)
    lab = 42
    cols = max(1, min(cols, len(items)))
    rows = (len(items) + cols - 1) // cols
    top = 30
    img = Image.new("RGB", (cols * w, top + rows * (h + lab)), BG)
    d = ImageDraw.Draw(img)
    f_title, f_lab, f_card = sheet_mod.font(18), sheet_mod.font(14), sheet_mod.font(15)
    d.text((8, 6), asc(title), fill=INK, font=f_title)
    for i, (r, im) in enumerate(items):
        x, y = (i % cols) * w, top + (i // cols) * (h + lab)
        if im is not None:
            img.paste(sheet_mod.fit(im, w - 4, h - 4), (x + 2, y + 2))
        else:
            d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], fill=CARD)
            body = f"{r.get('title', '')}" + (f" ({r['by']}" + (f", {r['year']}" if r.get("year") else "") + ")" if r.get("by") else "")
            lines = textwrap.wrap(asc(body), width=max(10, w // 9))[:4] + [""] + textwrap.wrap(asc(r.get("take", "")), width=max(10, w // 9))[:4]
            for k, line in enumerate(lines):
                d.text((x + 12, y + 12 + 19 * k), line, fill=INK if k < 4 else DIM, font=f_card)
            d.text((x + 12, y + h - 26), r.get("_why", "no copy"), fill=DIM, font=f_lab)
        line1 = f"{r.get('id', '?')}  {r.get('kind', '')}  {r.get('licence', '')}"
        line2 = asc(f"{r.get('title', '')}" + (f" / {r['by']}" if r.get("by") else "") + (f" / {r['year']}" if r.get("year") else ""))
        d.text((x + 6, y + h + 3), asc(line1), fill=INK, font=f_lab)
        d.text((x + 6, y + h + 21), line2[: max(10, w // 8)], fill=DIM, font=f_lab)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=88)


def main() -> int:
    ap = argparse.ArgumentParser(prog="refboard.py", description="refs/board-<section>.jpg from licensed files, and refs/BOARD.md.")
    ap.add_argument("--section", default=None, help="make only this section's board (BOARD.md is still rewritten whole)")
    ap.add_argument("--cols", type=int, default=4, help="tiles per row (default 4)")
    ap.add_argument("--w", type=int, default=384, help="tile width in px (default 384)")
    a = ap.parse_args()
    mp = Path("refs/manifest.json")
    if not mp.exists():
        print("refboard: no refs/manifest.json here; run from the film project root")
        return 2
    refs = json.loads(mp.read_text(encoding="utf-8")).get("refs") or []
    tlp = Path("data/timeline.json")
    tl = json.loads(tlp.read_text(encoding="utf-8")) if tlp.exists() else {}
    order = [s["id"] for s in tl.get("sections") or []]
    labels = {s["id"]: s.get("label", "") for s in tl.get("sections") or []}
    warn: list[str] = []
    seen: set[str] = set()
    by_sec: dict[str, list[dict]] = {}
    for r in refs:
        rid = str(r.get("id", ""))
        if rid in seen:
            warn.append(f"{rid}: duplicate id")
        seen.add(rid)
        sec = r.get("section") or "film"
        if sec in ("all", ""):
            sec = "film"
        if order and sec != "film" and sec not in order:
            warn.append(f"{rid}: section {sec!r} is not in data/timeline.json")
        if r.get("kind") not in KINDS:
            warn.append(f"{rid}: kind {r.get('kind')!r} is not one of {' '.join(sorted(KINDS))}")
        lic = str(r.get("licence") or "")
        if not lic:
            warn.append(f"{rid}: no licence; treat it as link-only")
        if re.search(r"\bNC\b", lic, re.IGNORECASE):
            warn.append(f"{rid}: licence {lic} is non-commercial; a brand or promotional film is a commercial use")
        if re.search(r"\bND\b", lic, re.IGNORECASE):
            warn.append(f"{rid}: licence {lic} allows no derivatives; cutting it into a film is one")
        if not r.get("url"):
            warn.append(f"{rid}: no url; a reference nobody can find again cannot be checked")
        f = r.get("file")
        if f:
            if link_only(lic):
                warn.append(f"{rid}: link-only but has a file ({f}); delete refs/{f} and set file to null")
            elif not (Path("refs") / f).exists():
                warn.append(f"{rid}: file refs/{f} not found")
        by_sec.setdefault(sec, []).append(r)
    secs = [s for s in order if s in by_sec] + sorted(s for s in by_sec if s not in order and s != "film") + (["film"] if "film" in by_sec else [])
    sheet_mod = sibling("sheet.py")
    made = []
    with tempfile.TemporaryDirectory(prefix="refboard-") as tmp:
        for sec in secs:
            if a.section and sec != a.section:
                continue
            items: list[tuple[dict, Image.Image | None]] = []
            texts = []
            for r in by_sec[sec]:
                f = r.get("file")
                if f and not link_only(str(r.get("licence") or "")) and (Path("refs") / f).exists():
                    im = open_ref(Path("refs") / f, Path(tmp))
                    if im is not None:
                        items.append((r, im))
                        continue
                    warn.append(f"{r.get('id')}: could not open refs/{f} as an image or video")
                lic = str(r.get("licence") or "")
                why = ("link-only: not copied" if link_only(lic) else
                       "file missing" if f and not (Path("refs") / f).exists() else
                       "not an image or video" if f else "no file")
                texts.append(({**r, "_why": why}, None))
            all_items = items + texts
            if not all_items:
                continue
            n_img = len(items)
            title = f"{sec}{(' ' + labels[sec]) if labels.get(sec) else ''}: {len(all_items)} references, {n_img} with a licensed copy, {len(texts)} link-only or text"
            out = Path("refs") / f"board-{sec}.jpg"
            board(out, title, all_items, a.cols, a.w, sheet_mod)
            made.append(out.as_posix())

    md = ["# Reference board", "",
          "Generated by `python scripts/refboard.py` from `refs/manifest.json`. Do not edit; change the manifest and re-run.", "",
          f"{len(refs)} references: {sum(1 for r in refs if r.get('file') and not link_only(str(r.get('licence') or '')))} with a licensed copy, "
          f"{sum(1 for r in refs if link_only(str(r.get('licence') or '')))} link-only.", ""]
    if warn:
        md += ["## Problems", ""] + [f"- {w}" for w in warn] + [""]
    for sec in secs:
        md += [f"## {sec}" + (f": {labels[sec]}" if labels.get(sec) else ""), ""]
        if (Path("refs") / f"board-{sec}.jpg").exists():
            md += [f"![board {sec}](board-{sec}.jpg)", ""]
        md += ["| id | kind | reference | by | year | licence | copy | take |", "|---|---|---|---|---|---|---|---|"]
        for r in by_sec[sec]:
            ref = f"[{cell(r.get('title') or r.get('url') or '?')}]({r['url']})" if r.get("url") else cell(r.get("title"))
            copy = f"[{cell(r['file'])}]({r['file']})" if r.get("file") and not link_only(str(r.get("licence") or "")) else ""
            md.append(f"| {cell(r.get('id'))} | {cell(r.get('kind'))} | {ref} | {cell(r.get('by'))} | {cell(r.get('year'))} | "
                      f"{cell(r.get('licence'))} | {copy} | {cell(r.get('take'))} |")
        md.append("")
    owed = [r for r in refs if r.get("kind") in ("asset", "font", "music", "sound")
            and re.search(r"BY|attribution", str(r.get("licence") or ""), re.IGNORECASE)]
    md += ["## Credits owed", ""]
    md += ([f"- {cell(r.get('id'))}: {cell(r.get('title'))}" + (f" by {cell(r.get('by'))}" if r.get("by") else "")
            + f", {cell(r.get('licence'))}, {cell(r.get('url'))}" for r in owed] or ["- none (no attribution-licensed assets)"])
    Path("refs/BOARD.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"refboard: {len(refs)} references in {len(secs)} groups -> refs/BOARD.md")
    for m in made:
        print(f"  {m}")
    for w in warn:
        print(f"WARN: {asc(w)}")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
