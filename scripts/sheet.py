"""Labelled contact sheet: tile images in order, each labelled with its file name.

    python scripts/sheet.py <out.jpg> [--cols 6] [--w 480] [--title TEXT] <images...>

Images may be files, directories (every image inside, sorted by name) or glob
patterns such as "out/check/film/*.jpg" (expanded here, because PowerShell and
cmd do not expand them). Each tile keeps its image's aspect ratio inside a cell
as tall as the first image at the tile width. The label is the file stem, so the
f<frame>_t<seconds> names written by shots.mjs and film-frames.py read as the
frame and time.

Other tools import make_sheet() from this file (film-frames.py, diff-frames.py).

Exit codes: 0 written, 2 bad arguments or no images.
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
BG = (18, 18, 18)
INK = (235, 235, 235)
LABEL_H = 22

# Monospace fonts to try on Windows, macOS and Linux; Pillow's own font is the fallback.
FONT_CANDIDATES = [
    "consola.ttf", "cour.ttf", "Menlo.ttc", "Monaco.ttf",
    "DejaVuSansMono.ttf", "LiberationMono-Regular.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]


def font(size: int = 15) -> ImageFont.ImageFont:
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow older than 10.1
        return ImageFont.load_default()


def expand(items: list[str]) -> list[Path]:
    """Files, directories and glob patterns -> image paths, in the order given."""
    out: list[Path] = []
    for it in items:
        p = Path(it)
        if any(c in it for c in "*?["):
            out += [Path(g) for g in sorted(glob.glob(it)) if Path(g).suffix.lower() in IMAGE_EXT]
        elif p.is_dir():
            out += sorted(q for q in p.iterdir() if q.suffix.lower() in IMAGE_EXT)
        else:
            out.append(p)
    return out


def fit(im: Image.Image, w: int, h: int) -> Image.Image:
    """Scale to fit inside w x h, keeping the aspect ratio, centred on the background."""
    im = im.convert("RGB")
    k = min(w / im.width, h / im.height)
    nw, nh = max(1, round(im.width * k)), max(1, round(im.height * k))
    im = im.resize((nw, nh), Image.LANCZOS)
    if (nw, nh) == (w, h):
        return im
    cell = Image.new("RGB", (w, h), BG)
    cell.paste(im, ((w - nw) // 2, (h - nh) // 2))
    return cell


def make_sheet(out: Path | str, files: list[Path | str], cols: int = 6, width: int = 480,
               title: str | None = None, labels: list[str] | None = None, quality: int = 88) -> Path:
    """Write one contact sheet and return its path. labels default to the file stems."""
    files = [Path(f) for f in files]
    if not files:
        raise ValueError("no images")
    out = Path(out)
    cols = max(1, min(cols, len(files)))
    with Image.open(files[0]) as first:
        height = max(1, round(width * first.height / first.width))
    rows = (len(files) + cols - 1) // cols
    top = LABEL_H + 6 if title else 0
    sheet = Image.new("RGB", (cols * width, top + rows * (height + LABEL_H)), BG)
    draw = ImageDraw.Draw(sheet)
    fnt = font(15)
    if title:
        draw.text((8, 4), title, fill=INK, font=font(17))
    for i, f in enumerate(files):
        x, y = (i % cols) * width, top + (i // cols) * (height + LABEL_H)
        with Image.open(f) as im:
            sheet.paste(fit(im, width, height), (x, y + LABEL_H))
        label = labels[i] if labels and i < len(labels) else f.stem
        draw.text((x + 6, y + 3), label, fill=INK, font=fnt)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=quality)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="sheet.py",
        description="Tile images into a labelled contact sheet (labels are the file stems).",
        epilog="Example: python scripts/sheet.py out/check/s1.jpg --cols 6 --w 480 \"out/check/01-x/*.jpg\"",
    )
    ap.add_argument("out", help="the sheet to write (.jpg)")
    ap.add_argument("images", nargs="+", help="image files, directories or glob patterns, in order")
    ap.add_argument("--cols", type=int, default=6, help="tiles per row (default 6)")
    ap.add_argument("--w", type=int, default=480, help="tile width in px (default 480)")
    ap.add_argument("--title", default=None, help="a line of text above the tiles")
    a = ap.parse_args()
    files = expand(a.images)
    missing = [f for f in files if not f.exists()]
    if missing:
        print(f"sheet: not found: {', '.join(str(m) for m in missing[:5])}")
        return 2
    if not files:
        print("sheet: no images")
        return 2
    out = make_sheet(a.out, files, a.cols, a.w, a.title)
    print(f"sheet: {len(files)} images -> {out.as_posix()}")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
