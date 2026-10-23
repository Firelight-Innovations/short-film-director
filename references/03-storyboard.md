# Storyboard and animatic

Phase 3: where timing and words lock. Everything built after the animatic gate is built
against what is decided here. Read this with `references/music.md`. Numbers in brackets
point to the sources at the end.

## Contents

1. [The order of work](#1-the-order-of-work)
2. [Thumbnails](#2-thumbnails)
3. [The beat board](#3-the-beat-board)
4. [Style frames](#4-style-frames)
5. [The style bible](#5-the-style-bible)
6. [The transitions table](#6-the-transitions-table)
7. [A catalogue of devices](#7-a-catalogue-of-devices)
8. [Devices in code](#8-devices-in-code)
9. [timeline.json, field by field](#9-timelinejson-field-by-field)
10. [storyboard.json](#10-storyboardjson)
11. [Board images](#11-board-images)
12. [The animatic](#12-the-animatic)
13. [The sign-off](#13-the-sign-off)
14. [The cut list](#14-the-cut-list)
15. [Sources](#15-sources)

---

## 1. The order of work

Motion-design studios run pre-production in about eight steps: idea, outline, moodboard,
storyboard, style frames, animatic, production boards, feedback [3]. Storyboards are
static; animatics add timing and motion [4]. In this skill:

| Step | Here | File |
|---|---|---|
| Idea, outline | Phase 1: concept, treatment, script, section map | `docs/treatment.md`, `docs/script.md` |
| Moodboard | Phase 2: the reference boards | `refs/board-*.jpg`, `refs/BOARD.md` |
| Thumbnails | many small, cheap frames per section | `docs/storyboard.md` (notes), `work/thumbs/` |
| Beat board | one panel per bar or phrase on the real track | `docs/storyboard.md` |
| Style frames | two or three hero moments, full size | `assets/board/` |
| Storyboard | one panel per cue, per transition, every 3 to 4 s | `data/storyboard.json` |
| Animatic | the panels on the real track, every word at its time | `out/animatic.mp4` |
| Production boards | the builders' first stills, checked against the panels | `out/check/<id>/` |
| Feedback | the animatic sign-off, then the reviews | `docs/decisions.md` |

Write the style bible, the transitions table and `data/timeline.json` alongside the beat
board: each one constrains the others. Lock timing at the animatic gate: after it, shot
lengths are fixed, and a shot that needs more time borrows it from a named neighbour and
says so in the decisions log [3][35].

The track is the final audio, not a temp track, so the animatic uses it from the first
board. Temp tracks box in a composer [8]; here there is no composer, but the same logic
says never board to a different piece of music than the one you will cut to.

## 2. Thumbnails

Small, rough, many per beat: framing and sequence, not finish [5]. Commit each idea to a
frame so it can be fixed, and set aside the first obvious one for one more pass [2]. In
code, a thumbnail is a few rectangles and a word: a card drawn by PIL at a quarter of the
film's own size (480x270 for 1920x1080, 270x480 for 1080x1920; read `w` and `h` from
`data/timeline.json`, and never draw a 16:9 card for a vertical film), or the section's
test card with a label. Make a sheet with
`python scripts/sheet.py work/thumbs/sheet.jpg --cols 6 --w 320 work/thumbs/*.jpg` and look
(for a vertical film, `--cols 8 --w 200` keeps the sheet a sensible width).
Keep thumbnails in `work/` (not committed); the beat board and the panels keep what
survived.

## 3. The beat board

A beat board is a condensed set of images for the key moments, used before the full
storyboard [5]. Here it is one row per bar or per phrase of the real track: its time, the
musical event, what we see, the words, the section. It shows at once whether the picture
changes where the music does. Four bars usually make a phrase, and a section change
belongs on a bar's downbeat [10][11].

This prints a skeleton for `docs/storyboard.md` from `data/beats.json`, one row per
phrase of four bars, with the structure points and loudness in each, and the cues that
fall in it (run it from the project root):

```python
import json
from pathlib import Path

beats = json.loads(Path("data/beats.json").read_text(encoding="utf-8"))
tl = json.loads(Path("data/timeline.json").read_text(encoding="utf-8"))
fps = beats["fps"]
downs = beats["downbeats"]
energy = beats["frames"]["energy"]
structure = [s["t"] for s in beats.get("structure", [])]
BARS = 4                                               # bars per phrase; 1 for a bar-by-bar board

starts = downs[::BARS]
ends = starts[1:] + [beats["duration"]]
if downs and downs[0] > 0.5:                           # an intro before the first downbeat
    starts, ends = [0.0] + starts, [downs[0]] + ends

def section_at(t):
    return next((s["id"] for s in tl["sections"] if s["from"] <= t < s["to"]), "-")

print("| # | from | to | bars | section | loudness | structure | cues | we see | words |")
print("|---|---|---|---|---|---|---|---|---|---|")
for i, (a, b) in enumerate(zip(starts, ends), 1):
    seg = energy[int(a * fps):max(int(b * fps), int(a * fps) + 1)]
    loud = sum(seg) / len(seg)
    marks = ", ".join(f"{t:.2f}" for t in structure if a <= t < b)
    cues = ", ".join(c["id"] for c in tl["cues"] if a <= c["from"] < b)
    n_bars = sum(1 for d in downs if a <= d < b)
    print(f"| {i} | {a:.2f} | {b:.2f} | {n_bars} | {section_at(a)} | {loud:.2f} | {marks} | {cues} |  |  |")
```

Fill the last two columns by hand. A row whose loudness jumps from the one before, or
that holds a structure point, is where a section or a shot should change. A long row
with no cue and no change in the picture is where the film will drag.

## 4. Style frames

Get the look signed off before the boarding goes deep: studios deliver style frames
first, for sign-off, before they board [7]. Make one full-size frame, at the film's own
`w` x `h`, for each of the two or three hero moments (the hook, the turn, the ending), in
the section's real style, with the real words.

**Who makes them.** The lead does. No section exists yet in Phase 3 (a section's test
card shows only a label), so a style frame is a plate with the type set over it, not a
render of the film. Do the bible's palette and type first (section 5), vendor the
families it names, then choose one of two routes:

- **The lead draws it.** Take the plate from a technique brief (`references/02-references.md`,
  section 9), or a licensed reference still from `refs/img/` marked as a reference, and set
  the cue's words over it with the script below. A quick job: a few minutes a frame.
- **One style-frame agent per hero moment**, a mid model, when the look needs more than a
  plate and type. Give it five lines and nothing else:

```text
Make one style frame. Write only assets/board/style-<section-id>.jpg, a JPEG at <w>x<h>.
Section <id>: <look, one line>; palette bg <#> ink <#> accent <#>; type <family, weight>, vendored.
Show <the hero moment, one sentence>, with the cue's exact words "<text>" at the bible's sizes.
Use the technique brief <path> for the picture. Keep the words in the title-safe box and out of the platform UI zone.
Change no other file. Reply with the path, the size, and one line on what you drew.
```

The script draws one cue over a flat palette field, or over a plate you name. Save it as
`work/style_frame.py` and run it from the project root; it reads the film's size, the
section's palette and the cue's words from `data/timeline.json`, sizes the words to the
title-safe box, and gives the last word the accent:

```python
"""A style frame: one section's palette, one cue's words, set in the bible's type, at the
film's own size. Save as work/style_frame.py and run from the project root:

    python work/style_frame.py <section-id> <cue-id> <font file> [plate image]

It writes assets/board/style-<section-id>.jpg.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

tl = json.loads(Path("data/timeline.json").read_text(encoding="utf-8"))
W, H = tl["w"], tl["h"]                                      # the film's size, never typed
UNIT = min(W, H) / 1080                                      # the kit's UNIT: 1 at 1080p
sid, cid, font_file = sys.argv[1:4]
plate = sys.argv[4] if len(sys.argv) > 4 else None
sec = next(s for s in tl["sections"] if s["id"] == sid)
cue = next(c for c in tl["cues"] if c["id"] == cid)
pal = sec["palette"]

bars = round(H * tl.get("letterbox", 0))                     # the title-safe box, as the kit's SAFE.title
box_w = round(W * tl["safe"]["title"])
box_h = round((H - 2 * bars) * tl["safe"]["title"])
x0, y0 = (W - box_w) // 2, bars + (H - 2 * bars - box_h) // 2

if plate:
    img = ImageOps.fit(Image.open(plate).convert("RGB"), (W, H))
else:
    img = Image.new("RGB", (W, H), pal["bg"])
draw = ImageDraw.Draw(img)


def load(size):
    try:
        return ImageFont.truetype(font_file, round(size))
    except OSError:                                          # Pillow built without woff2 support
        print("warning: cannot read", font_file, "- using Pillow's default font")
        return ImageFont.load_default(round(size))


def wrap(words, font):
    lines, line = [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if line and draw.textlength(trial, font=font) > box_w:
            lines.append(line)
            line = w
        else:
            line = trial
    return lines + [line]


words = cue["text"].replace("\n", " ").split()
size = 160 * UNIT                                            # biggest first, then down to a floor
while True:
    font = load(size)
    lines = wrap(words, font)
    block = len(lines) * size * 1.1
    fits = block <= box_h and all(draw.textlength(l, font=font) <= box_w for l in lines)
    if fits or size <= 54 * UNIT:
        break
    size *= 0.92

y = H / 2 - block / 2
for i, line in enumerate(lines):
    x = (W - draw.textlength(line, font=font)) / 2
    if i < len(lines) - 1:
        draw.text((x, y), line, font=font, fill=pal["ink"])
    else:                                                    # last line: ink, then the cue's last word in the accent
        head, sep, last = line.rpartition(" ")
        if sep:
            draw.text((x, y), head + " ", font=font, fill=pal["ink"])
            x += draw.textlength(head + " ", font=font)
        draw.text((x, y), last, font=font, fill=pal["accent"])
    y += size * 1.1

out = Path("assets/board") / f"style-{sid}.jpg"
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out, quality=90)
print("wrote", out, W, "x", H)
```

Save the frames as `assets/board/style-<section>.jpg` and point to them from the style
bible's section page. A frame drawn from a built section (`node scripts/shots.mjs
<section-id> --t <s> --clean`) belongs to Phase 4, when the section exists, and is a
check, not a style frame. A style frame the user rejects costs ten minutes; a section
built on it costs an hour.

## 5. The style bible

`docs/style-bible.md` (`templates/style-bible.md`) is the builders' shared rulebook. It
has film-wide rules, then one page per section. The first film's bible was about 200
lines for eight sections and was the document every builder read first.

**Rules for every section** (adapt the wording; keep each reason):

1. **The words are exact.** On-screen text is the cue's `text` (and `attribution`, and
   `source` for `data` cues), character for character. Case styling is allowed. No
   section adds a factual claim. A decorative label that asserts nothing about the world
   is fine.
2. **Cut on the music.** Boundaries and shot changes sit on measured events (`marks`,
   `beats.json`). A cue's `from` is the frame it is readable by; start entrances early.
3. **One strong idea per shot.** If a shot has three effects, cut two.
4. **Nothing reads as a slideshow.** Every frame moves: camera, light, boil, grain,
   parallax.
5. **Type is part of the picture.** Each section sets its words in its own material.
6. **The picture area.** Compose inside the letterbox, keep words inside the title-safe
   area, and, for a vertical film bound for a feed, inside the platform UI zone (both
   below). Words sit where the viewer's screen shows them, not only where the film's
   frame has room.
7. **Flash safety.** At most three flashes in any one second, no saturated red fields
   (`references/safety-and-rights.md`).
8. **Every frame is a pure function of its frame number.** `rnd(seed)` only; no
   `Math.random`, no `Date`, no CSS animation, no state carried between frames.

**Minimum type sizes, as numbers.** Sizes judged on a 1080p still fail on a phone: on the
first film, source lines at 20 to 24 px and a tagline with a 0.6 mm x-height on an
upright phone were the review's commonest finding, and its one broken item was a chart
that read wrong at phone size. Set floors in the bible, in pixels at 1080 on the short
side; for other sizes multiply by the kit's `UNIT` (`min(w, h) / 1080`):

| Role | Minimum (px at 1080) | Notes |
|---|---|---|
| `narration`, body text | 54 | the contract's floor for body text |
| `thesis` | 64 | the line the film exists for gets room |
| `slam` | 120 | a one-word hit should fill a third of the width or more |
| `data` numeral | 96 | the number is the picture |
| `quote` | 54 | with `attribution` at 40 |
| `sub`, `attribution`, labels | 40 | |
| `source` line | 32 | the contract's floor; mono, near the bottom of the safe area |
| `credit` | 44 | the first film raised its credit to 48 after review |
| `stamp` (diegetic date or label) | 32 | if it must be read; smaller only if it is texture |
| hairlines in charts | 2 px, at 0.5 opacity or more | hairlines vanish at phone size |

Body 54 px and source lines 32 px are the contract's floors; the other rows are this
skill's defaults. Check every word on the phone-size sheets (360 px wide tiles) that the
review tools make: a 1920 frame is scaled there by 0.1875, so a 32 px line is 6 px tall. If
a word cannot be read on that sheet, it is too small for a phone.

**Safe areas and the letterbox.** With `letterbox: 0.06` at 1080, the bars are 65 px top
and bottom (`round(1080 x 0.06)`), so the picture is 1920x950. `safe.title` (0.9) and
`safe.action` (0.95) are fractions of the picture inside the bars: words stay inside the
title-safe box, essential picture inside the action-safe box. EBU R 95 defines the two
areas [C32]; its exact margins were not verified, so these fractions are the skill's
default.

**Platform UI zone (vertical social).** Reels and Stories draw their own interface over
the picture, and `safe` cannot hold it, because it is one centred inset. So the bible
carries the zone as one line under "Picture area", in pixels, and the builder brief
repeats it. Default for a 9:16 film bound for Reels or Stories: Meta's guidance for Reels
ads asks for about 14 percent of the top, 35 percent of the bottom and 6 percent of each
side to be free of text and key elements [A1]. At 1080x1920 that is 269, 672 and 65 px,
so words and anything that must be seen stay inside x 65 to 1015, y 269 to 1248 (950x979).
The line reads: `Platform UI zone: x 65 to 1015, y 269 to 1248 (Meta's Reels figure for
ads; check on the posting day)`. Two things follow:

- The title-safe box is larger than the zone (it starts at y 96 at 1080x1920), so a cue
  can be title-safe and still sit under the profile name or the caption. The kit's example
  section and the animatic place words by the title-safe box; check every word against the
  zone by eye on the phone sheets. A full-bleed picture may run outside the zone; words may
  not.
- The figure is Meta's, stated for ads and checked for this skill on one page
  (`references/01-intake-and-ideation.md`, "Platform UI zone"). An organic post, TikTok and
  YouTube Shorts each draw their own overlay. Tell the user which one the bible assumes,
  and write "none" for a 16:9 film.

**Palette logic.** Each section has `bg`, `ink` and `accent` in its timeline entry, so
neighbours can quote each other's colours at a boundary. Say what the accent is for and
where it may not appear. The palette is also where a film's warmth or coolness lives: the
final grade has no colour-balance or temperature control, so a brief that says "warm"
becomes warm backgrounds, inks and accents in each section's palette, not a setting
applied afterwards.

**Grain and texture.** Sections own their style's texture (paper, tape noise, halftone).
The film's unifying grade and grain are applied once at the end by `scripts/grade.py`
from `timeline.grade`; no section grades itself. Say in the bible what the grade will do
(a light contrast lift, a vignette, temporal grain, off from `grade.until`; it controls
contrast, saturation, gamma, vignette and grain, and nothing about colour balance) so
builders do not compensate for it twice.

**Fonts.** Name each section's families (display, body, mono) and weights in the bible.
The moment the bible names them, vendor the set before the first style frame and before
the animatic renders: `node scripts/fetch-fonts.mjs "Family:400,700" ...` (the full rule is
in `references/02-references.md`, section 10). Until a family is vendored the kit draws a
system font and prints a warning, so a frame made earlier would show the wrong type.

**One page per section**: the look and the clashing secondary look, if any; the job in one
line; a shot table (shot, time, plate or source, what happens); the transitions in and
out with what this section owes in pixels; the palette and the type (families, sizes);
references by manifest id and the technique briefs; the style frames; what it must not
do. The first film's pages each ran 15 to 25 lines.

## 6. The transitions table

`docs/transitions.md` (`templates/transitions.md`) gives one **named device** per
boundary, none repeated. The name forces a different idea at every cut, and gives the
reviewer a promise to check ("is it the named device, or a generic dissolve?").

**How a transition is built.** During a window `[at - pre, at + post)` only the **owner**
is mounted, and it receives the other section's live render as a React node: `next` if the
owner is the outgoing section, `prev` if it is the incoming one. The owner draws that node
where it likes (under its own layers, in a mask, a clip-path, a filter, a transform). If it
never draws it, the neighbour is not on screen. Consequences:

- The owner can mask, clip, move, scale, blur, invert or displace the neighbour; it cannot
  read the neighbour's pixels into WebGL.
- Both sections render valid full frames across the whole window, including the part
  outside their own span. That is each section's render range,
  `[from - pre of the way in, to + post of the way out)`.
- A hard cut has `pre = post = 0`: no window, and the frame at `at` belongs entirely to the
  incoming section.
- `t-start` and `t-end` (no `a`, or no `b`) have `pre = post = 0` and name what happens at
  the film's first and last frames.

**The table's columns**: boundary; at (seconds and frame); name; owner; window (seconds
and frames); device (what happens, frame by frame, in one or two sentences); lands on (the
mark or measured event); and the handshake, **what each side owes the other in pixels**.

The handshake is the only place two builders must agree on pixels, so make it exact
enough for a script to assert. Good handshake lines name a colour, a position, a frame
range and what is absent:

- "From 48.900 to 50.267 the outgoing section is `#0a0a0a` with one 2 px line `#f4f1e8` at
  y = 540, full width, and nothing else. The incoming opening starts as that line."
- "From 66.767 to 67.167 the outgoing frame is the wireframe only, tallest tower centred at
  (960, 540); the owner scales it through that point."
- "The last frame before the cut is bright and full; the first frame after it is `#000`."
- "The last frame before the window is a full-frame picture with nothing in the centre
  600 px."

Those lines are the first film's, at 1920x1080. In your film, state positions in the film's
own pixels (read `w` and `h` from `data/timeline.json`), or as fractions of them. Every one
of the first film's handshake lines held in the final film, because both sides built to
the same sentence and the reviewers checked it on the frames.

**Windows in frames.** Seconds are rounded; frames are the truth. The kit snaps at load:
`f = round(at x fps)`, the window opens on `round((at - pre) x fps)` and the incoming
section is alone from `round((at + post) x fps)`. This prints the table for the
transitions file:

```python
import json
import math
from pathlib import Path

tl = json.loads(Path("data/timeline.json").read_text(encoding="utf-8"))
fps = tl["fps"]
F = lambda s: math.floor(s * fps + 0.5)       # the kit's Math.round (Python's round() rounds half to even)
print("| Transition | Cut frame | Owner mounted with the neighbour on frames | First frame the incoming section is alone |")
print("|---|---|---|---|")
for tr in tl["transitions"]:
    f = F(tr["at"])
    a, b = F(tr["at"] - tr["pre"]), F(tr["at"] + tr["post"])
    if not tr.get("a") or not tr.get("b"):
        print(f"| {tr['id']} {tr['name']} | {f} | none (edge) | - |")
    elif a == b:
        print(f"| {tr['id']} {tr['name']} | {f} | none (hard cut) | {f} |")
    else:
        print(f"| {tr['id']} {tr['name']} | {f} | {a} to {b - 1} ({tr['owner']} holds the neighbour) | {b} |")
```

**Internal shifts.** Shot changes inside one section are the section's own business, but
list them in a second table (where, at, device) so no device repeats across the film.

## 7. A catalogue of devices

What each device is, and how it is made under the owner model. The cost is the extra
render time per frame inside the window; the flash note says whether it can trip the
flash check (`references/safety-and-rights.md`).

| Device | What it is | How in code | Cost | Flash |
|---|---|---|---|---|
| Hard cut | the next picture, on a frame | `pre = post = 0`; the incoming owns the cut frame | none | if the two frames differ a lot in brightness, the cut is a luminance transition |
| Smash cut | an abrupt cut where none is expected, for shock or contrast [25] | a hard cut at a pivot: a hit, a drop, a reveal | none | as a hard cut |
| Cut to black | the picture ends; black holds | a section that draws `#000`; list it in `checks.black`; set `grade.until` to its start | none | one transition; fine alone |
| Match cut | shape, position or movement lines up across the cut [23] | both sides draw the anchor at the same pixels on the cut frame (a handshake line), or the owner draws the neighbour until the cut and its own anchor in the same place after | low | low |
| Dissolve | one picture fades through the other | owner draws the neighbour, then itself with opacity rising | low | low |
| Motivated dissolve | a dissolve through a material: ink, light, smoke, paper | the same, through a mask that is a texture (a pre-made noise or ink plate thresholded by progress) | low with a plate | low |
| Dip to black or white | out to a flat field, in from it | owner draws the neighbour fading to a field, then itself fading in | low | white dips are full-frame flashes: count them |
| Wipe | a moving edge brings the new picture in [27] | the owner's picture inside a `clipPath: inset(...)` or a gradient mask that moves | low | low |
| Iris | a circle grows or shrinks [27] | `clipPath: circle(r at x y)` | low | low |
| Clock wipe | a radius sweeps from the centre [27] | a `conic-gradient` mask whose angle follows progress | low | low |
| Barn door | two edges meet at (or open from) the centre [27] | `clipPath: inset(0 X 0 X)` | low | low |
| Matrix wipe | a pattern of cells, revealed in order [27] | a grid of clipped cells, each opening when `rnd(cell) < progress` | medium | many cells flipping at once can count as a pattern: measure |
| Push or slide | the new picture pushes the old out | both translate by the same distance; `@remotion/transitions` has slide in four directions [28] | low | low |
| Whip pan | a pan so fast it streaks, hiding the cut [26] | both pictures side by side on one strip that pans a frame width, under a horizontal blur that peaks mid-window, so direction and speed match by construction (no built-in presentation [28]) | medium (blur) | low |
| Zoom through | push into a point of the old picture and come out in the new | scale the neighbour about the point (`transformOrigin`) until it fills; cut inside | medium (blur) | low |
| Eyelid or line open | the old picture thins to a line; the new opens from it | the handshake fixes the line; the owner opens an ellipse or polygon clip from it | low | low |
| Type as a window | the new picture is seen only through letterforms | an SVG `mask` holding the text, or `backgroundClip: text` | low | low |
| Negative snap | the old picture flips to its negative for a few frames | `filter: invert(1)` on the neighbour | none | an inverted bright frame is a full-frame luminance change: measure |
| Tear, slice, tracking loss | the old picture comes apart in bands | horizontal bands of the neighbour, each clipped and offset by seeded amounts on twos | medium | rapid band cuts count as flashes if bright and dark alternate |
| Glitch, datamosh | compression faults carry one picture into the next | pre-rendered in Python or ffmpeg and played as a plate | plate | measure; fast cuts that make screen areas flash fall under the same limits [W2] |
| Freeze, hold | the neighbour stops on one frame | `<FilmClockOverride frame={F(at)}>{prev}</FilmClockOverride>` pins its clock | none | none |
| Recut from the film | the film's own frames come back | stills of the finished film rendered with `plates-from-film.mjs`, declared in `data/chains.json` | plate | the hardest one to keep under the limit: design from the measured numbers |
| J or L cut | sound leads or trails the picture [24] | only for a voice-over; one continuous music track has nothing to lead | none | none |
| Film burn, morph | (no sourced definition in this skill's research) | build either as a pre-rendered plate and name it in the table | plate | burns are bright: measure |

Remotion's `@remotion/transitions` names fade, slide, wipe, flip, clockWipe and iris
presentations for its `TransitionSeries` [28]. This kit does not use `TransitionSeries`
(the owner model lets one side do anything to the other), but those presentations are a
good list of the simple masks to reach for.

## 8. Devices in code

Owners are ordinary section components. Each snippet below is a whole
`src/sections/<id>/index.tsx`; `Picture` stands for the section's own content
(`./Picture`). The window's progress comes from the kit's snapped transition times, so it
lands on whole frames. Section ids are examples.

No snippet types a frame size. Each reads `CANVAS` (the film's width and height) or `UNIT`
(`min(w, h) / 1080`) from the kit, so the same file works at 1920x1080 and at 1080x1920.
Every pixel constant is derived from `CANVAS`; keep it that way when you copy a snippet or
write a new device, because a `1920` or a `1080` typed into one is the first thing that
breaks when the next film is vertical (an iris of fixed radius never covers a tall frame,
and a tear that stops at row 1080 leaves the rest uncovered). Each device here was
rendered at 1920x1080 and at 1080x1920 when it was written.

An **iris** (the owner is the incoming section; `prev` sits under its growing circle).
From the centre, the radius that covers every corner is half the diagonal:

```tsx
import { AbsoluteFill } from "remotion";
import { CANVAS, ease, prog, transitionIn, useFilmTime } from "../../kit";
import type { SectionComponent } from "../../kit";
import { Picture } from "./Picture";

export const Section: SectionComponent = ({ prev }) => {
  const { t } = useFilmTime();
  const tr = transitionIn("02-rise");       // null only if the file has no transition in
  const p = prev && tr ? prog(t, tr.at - tr.pre, tr.at + tr.post, ease.inOut) : 1;
  const r = (Math.hypot(CANVAS.width, CANVAS.height) / 2) * p;   // half the diagonal: p = 1 covers the frame
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {prev}
      <AbsoluteFill style={{ clipPath: `circle(${r.toFixed(1)}px at ${CANVAS.width / 2}px ${CANVAS.height / 2}px)` }}>
        <Picture />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

A **tracking tear** (the owner is the outgoing section; `next` shows through as bands drop
out in a seeded order and the survivors slip further each frame):

```tsx
import { AbsoluteFill } from "remotion";
import { CANVAS, hold, prog, rnd, transitionOut, useFilmTime } from "../../kit";
import type { SectionComponent } from "../../kit";
import { Picture } from "./Picture";

const BANDS = 18;

export const Section: SectionComponent = ({ next }) => {
  const { t, frame } = useFilmTime();
  const tr = transitionOut("00-open");
  const p = next && tr ? prog(t, tr.at - tr.pre, tr.at + tr.post) : 0;
  const f = hold(frame, 2);                 // slips change on twos, so they jitter, not buzz
  const h = CANVAS.height / BANDS;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {next}
      {Array.from({ length: BANDS }, (_, i) => {
        if (rnd(`tear-gone-${i}`) < p * 1.15) return null;    // gone: next shows through
        const dx = (rnd(`tear-dx-${i}-${f}`) - 0.5) * 0.25 * CANVAS.width * p;
        return (
          <AbsoluteFill key={i} style={{
            clipPath: `inset(${(i * h).toFixed(1)}px 0 ${(CANVAS.height - (i + 1) * h).toFixed(1)}px 0)`,
            transform: `translateX(${dx.toFixed(1)}px)`,
          }}>
            <Picture />
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};
```

Drawing the picture once per band multiplies its cost by the band count; for a heavy
picture, render it to a plate first and clip the plate.

A **zoom through** (incoming owner, window before the cut only: `post = 0`; the old
picture is pushed through its centre and the cut lands inside it; the blur is in `UNIT`
so it reads the same at any size):

```tsx
import { AbsoluteFill } from "remotion";
import { CANVAS, UNIT, ease, prog, transitionIn, useFilmTime } from "../../kit";
import type { SectionComponent } from "../../kit";
import { Picture } from "./Picture";

export const Section: SectionComponent = ({ prev }) => {
  const { t } = useFilmTime();
  const tr = transitionIn("03-fall");
  if (prev && tr && t < tr.at) {
    const p = prog(t, tr.at - tr.pre, tr.at, ease.in);
    return (
      <AbsoluteFill style={{ backgroundColor: "#071019", overflow: "hidden" }}>
        <AbsoluteFill style={{
          transform: `scale(${(1 + 5 * p).toFixed(3)})`, transformOrigin: `${CANVAS.width / 2}px ${CANVAS.height / 2}px`,
          filter: `blur(${(10 * UNIT * p).toFixed(1)}px)`,
        }}>
          {prev}
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }
  return <Picture />;
};
```

A **whip pan** (incoming owner, window across the cut). The two pictures sit side by side
on one strip that pans a full frame width; the speed and the blur peak mid-window, where
the seam between them crosses the frame and hides in the streak. The directional blur is
an SVG filter, because CSS `blur()` blurs both ways. Put the filter on an element that does
not move, and give it a region larger than the frame (a quarter of the width spare on each
side, an eighth of the height above and below), or it clips at a hard edge:

```tsx
import { AbsoluteFill } from "remotion";
import { CANVAS, UNIT, ease, prog, transitionIn, useFilmTime } from "../../kit";
import type { SectionComponent } from "../../kit";
import { Picture } from "./Picture";

export const Section: SectionComponent = ({ prev }) => {
  const { t } = useFilmTime();
  const tr = transitionIn("04-run");
  if (!prev || !tr) return <Picture />;
  const p = prog(t, tr.at - tr.pre, tr.at + tr.post);   // 0 to 1 over the window
  const x = -CANVAS.width * ease.inOut(p);                // the strip pans one frame to the left
  const blur = 90 * UNIT * Math.sin(Math.PI * p);         // follows the speed: 0, most at mid-window, 0
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id="whip" filterUnits="userSpaceOnUse" x={-CANVAS.width / 4} y={-CANVAS.height / 8} width={CANVAS.width * 1.5} height={CANVAS.height * 1.25}>
          <feGaussianBlur stdDeviation={`${blur.toFixed(1)} 0`} />
        </filter>
      </svg>
      <AbsoluteFill style={{ filter: "url(#whip)" }}>
        <AbsoluteFill style={{ transform: `translateX(${x.toFixed(1)}px)` }}>
          <AbsoluteFill>{prev}</AbsoluteFill>
          <AbsoluteFill style={{ transform: `translateX(${CANVAS.width}px)` }}><Picture /></AbsoluteFill>
        </AbsoluteFill>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

Match the direction and the speed on both sides [26]: here both pictures are one strip, so
they cannot disagree. A whip blurs a large area for the whole window, so it is one of the
dearer devices; check its cost with `node scripts/shots.mjs <id> --bench <a>:<b>`.

A **negative snap** and a **soft wipe**, in one file only to save space (a real section
has one device per transition). The snap inverts the neighbour for the whole window, so
give it a window of a few frames before the cut and none after (`pre` 0.1, `post` 0); a
test render of this file with a one-second window measured two full-frame luminance
transitions, which is why the snap stays short:

```tsx
import { AbsoluteFill } from "remotion";
import { CANVAS, prog, transitionIn, useFilmTime } from "../../kit";
import type { SectionComponent } from "../../kit";
import { Picture } from "./Picture";

export const Section: SectionComponent = ({ prev }) => {
  const { t } = useFilmTime();
  const tr = transitionIn("05-press");
  if (prev && tr && tr.name === "Negative snap") {
    return <AbsoluteFill style={{ filter: "invert(1)" }}>{prev}</AbsoluteFill>;
  }
  if (prev && tr) {
    const feather = 0.125 * CANVAS.width;
    const edge = -feather + 1.25 * CANVAS.width * prog(t, tr.at - tr.pre, tr.at + tr.post);   // leading edge, px
    const mask = `linear-gradient(90deg, #000 ${(edge - feather).toFixed(0)}px, transparent ${edge.toFixed(0)}px)`;
    return (
      <AbsoluteFill>
        {prev}
        <AbsoluteFill style={{ maskImage: mask, WebkitMaskImage: mask }}><Picture /></AbsoluteFill>
      </AbsoluteFill>
    );
  }
  return <Picture />;
};
```

Two rules from the first film for every device. Compare frames, not typed seconds: a
literal like `t >= 5.2667` fires a frame late, because 5.2667 is a hair after frame 158;
use the kit's snapped times or `frame >= F(5.2667)`. And keep the neighbour's clock: if
the owner freezes or replays the neighbour, do it with `FilmClockOverride`, and make sure
the neighbour plays its plates by the film clock, or it shows the wrong plate.

## 9. timeline.json, field by field

`data/timeline.json` (version 3) is the source of truth. Everything else reads it.

**Top level**

| Field | Type | Meaning |
|---|---|---|
| `version` | 3 | the schema version |
| `title` | string | the film's title |
| `slug` | string | output file names: `out/<slug>.mp4`, `out/<slug>-graded.mp4` |
| `w`, `h`, `fps` | numbers | frame size and rate |
| `dur` | seconds | composition length is `round(dur x fps)` frames |
| `letterbox` | fraction | bar height as a fraction of `h`, top and bottom; `0` for none |
| `safe` | `{ title, action }` | fractions of the picture inside the bars, one centred inset each; it holds no platform UI zone (that lives in the style bible, section 5) |
| `audio` | `{ src, gain, duration }` or `null` | `src` is under `assets/` (`audio/track.mp3`); `duration` is the measured length |
| `sections` | list | below |
| `marks` | `{ name: seconds }` | musical landmarks taken from `beats.json` (`drop`, `loudest`, `silence`, `hit-1`) |
| `transitions` | list | below |
| `cues` | list | below |
| `checks` | `{ black, lastFrameBlack }` | `black`: `[from, to)` ranges in seconds that must be pure black; `lastFrameBlack`: whether the last frame must be |
| `grade` | object | the one grade pass: `contrast`, `saturation`, `gamma`, `vignette` (0 for none; angle = vignette x PI/3), `grain` (ffmpeg `noise` strength), `until` (seconds; the grade is off from here; `null` for the whole film). There is no colour balance or temperature control: warmth or coolness belongs in the section palettes (section 5) |

**`sections[]`**: `id` (`^[0-9]{2}-[a-z0-9-]+$`), `from`, `to` (seconds, `[from, to)`),
`label` (shown in the dev overlay and the animatic strip), `style` (one line), `palette`
(`{ bg, ink, accent }`, `#rrggbb`; optional `accent2` and `shadow`, which the kit fills in
from `accent` and black when they are missing).

**`transitions[]`**: `id` (`t-00-01` for the boundary between `00-...` and `01-...`;
`t-start`, `t-end` at the edges), `at` (the cut, seconds), `a` (outgoing section, or `null`
at the start), `b` (incoming, or `null` at the end), `owner` (`a` or `b`), `pre`, `post`
(seconds of window before and after `at`), `name` (the device's name), `device` (what
happens, frame by frame), `beat` (a mark name or a short note of the musical event).

**`cues[]`**: `id` (role-based: `data-3`), `section`, `role`, `from` (readable by), `to`
(gone by), `text` (the exact words; `\n` breaks a line), `attribution` (who said it, or the
label under a number), `source` (where a fact comes from; shown small for `data` cues),
`note` (direction; never shown), optionally `names` (extra strings a section may draw,
such as a list of signatories), and optionally `shown: { from, to }` when the words are
drawn over a different window than they are readable (an entrance that starts early, a
handshake that holds them late). Roles: `stamp slam narration sub quote data thesis
question credit logo caption vo`.

**Rules** (`python scripts/check-timeline.py` exits 3 on any error):

- Sections are contiguous, ordered, cover `[0, dur)`, and every boundary is a whole frame.
- Every id is unique; section ids match the pattern.
- Every transition joins two adjacent sections (`a` then `b`), its `owner` is one of them,
  its window `[at - pre, at + post)` stays inside the two sections, and no two windows
  overlap. `t-start` and `t-end` have `pre = post = 0`.
- Every cue has non-empty `text`, a known `section`, `from < to`, and lies inside its
  section's render range, and so does its `shown` window. `data` and `quote` cues have a
  non-empty `source`.
- `checks.black` ranges lie inside `[0, dur]`; `audio.src` exists under `assets/`.

**Warnings** (exit 0, but read them):

- a cue on screen for less than `0.4 s x words + 0.5 s` (never below 0.83 s; for `data`
  and `quote` cues the `attribution` words count too), longer than 7 s, or on more than
  two lines: the reading budget from `references/01-intake-and-ideation.md`;
- a time half a frame from any frame, a cue id that is not role-based, an unknown role, a
  palette colour that is not `#rrggbb`;
- a transition whose `beat` names a mark the cut is not on;
- a `shown` window that starts after or ends before the readable window (the words would
  not be drawn while they should be read);
- a `data` or `quote` cue with no row in `docs/research/facts.md`, a verdict other than
  `verified` or `corrected`, on-screen words that differ from the row, or a re-verify-by
  date that has passed;
- when `beats.json` exists, a boundary more than two frames from a measured event (that is
  `snap.py`'s job; see `references/music.md`).

A complete small film that passes the rules (a 20 s, three-section film at 30 fps):

```json
{
  "version": 3,
  "title": "Paper Weather",
  "slug": "paper-weather",
  "w": 1920, "h": 1080, "fps": 30,
  "dur": 20.0,
  "letterbox": 0.06,
  "safe": { "title": 0.9, "action": 0.95 },
  "audio": { "src": "audio/track.mp3", "gain": 1.0, "duration": 18.4 },
  "sections": [
    { "id": "00-open", "from": 0.0, "to": 6.4, "label": "Open", "style": "charcoal on paper, on twos",
      "palette": { "bg": "#ece4d2", "ink": "#1d1a17", "accent": "#a3402a" } },
    { "id": "01-storm", "from": 6.4, "to": 15.6, "label": "Storm", "style": "kinetic type on the beat",
      "palette": { "bg": "#0b0b0c", "ink": "#f2efe8", "accent": "#c8f04a" } },
    { "id": "02-close", "from": 15.6, "to": 20.0, "label": "Close", "style": "black, silence, one line",
      "palette": { "bg": "#000000", "ink": "#f2efe8", "accent": "#ff8a3d" } }
  ],
  "marks": { "first-note": 0.4, "drop": 6.4, "loudest": 13.2, "last-hit": 15.6, "silence": 18.4 },
  "transitions": [
    { "id": "t-start", "at": 0.0, "a": null, "b": "00-open", "owner": "00-open", "pre": 0, "post": 0,
      "name": "Lamp up", "device": "black; the paper warms in over 12 frames", "beat": "before the first note (0.4)" },
    { "id": "t-00-01", "at": 6.4, "a": "00-open", "b": "01-storm", "owner": "01-storm", "pre": 0.4, "post": 0.2,
      "name": "Ink flood", "device": "ink rises from the bottom edge through the drawing; the storm is under the ink", "beat": "drop" },
    { "id": "t-01-02", "at": 15.6, "a": "01-storm", "b": "02-close", "owner": "02-close", "pre": 0, "post": 0,
      "name": "The cut", "device": "hard cut from the densest frame to pure black", "beat": "last-hit" },
    { "id": "t-end", "at": 20.0, "a": "02-close", "b": null, "owner": "02-close", "pre": 0, "post": 0,
      "name": "Out", "device": "the line fades out from 19.5; the last frames are black", "beat": "silence" }
  ],
  "cues": [
    { "id": "narration-1", "section": "00-open", "role": "narration", "from": 1.2, "to": 4.0,
      "text": "Every map starts\nas weather.", "attribution": "", "source": "", "note": "hand-lettered, written on from 0.9",
      "shown": { "from": 0.9, "to": 4.0 } },
    { "id": "slam-1", "section": "01-storm", "role": "slam", "from": 6.4, "to": 7.4,
      "text": "NOW", "attribution": "", "source": "", "note": "on the drop" },
    { "id": "data-1", "section": "01-storm", "role": "data", "from": 9.0, "to": 13.6,
      "text": "<a figure, exactly as verified>", "attribution": "<label under the number>",
      "source": "<publisher, title, year>", "note": "row data-1 in docs/research/facts.md" },
    { "id": "thesis-1", "section": "02-close", "role": "thesis", "from": 16.0, "to": 19.8,
      "text": "We drew the weather.\nNow it draws us.", "attribution": "", "source": "", "note": "second line 0.8 s after the first" }
  ],
  "checks": { "black": [[15.6, 16.0]], "lastFrameBlack": true },
  "grade": { "contrast": 1.05, "saturation": 0.97, "gamma": 0.985, "vignette": 0.333, "grain": 5, "until": 15.6 }
}
```

Note how it obeys the rules: the `t-00-01` window `[6.0, 6.6)` sits inside `00-open` and
`01-storm`; the narration's early `shown.from` (0.9) is inside its section's render range;
the black check covers the first 12 frames of the close, before its first word; the thesis
holds 3.8 s for its eight words (the budget is 3.7 s); the grade stops where the black
starts.

## 10. storyboard.json

`data/storyboard.json` holds the panels the animatic plays:

| Field | Meaning |
|---|---|
| `id` | `p01`, `p02`, ... in film order |
| `section` | the section it belongs to |
| `at` | seconds; the panel holds the screen from `at` until the next panel's `at` |
| `image` | a file under `assets/` (`board/p01.jpg`), or `null`: the animatic draws a card from the action line |
| `action` | what we see, one or two lines |
| `camera` | optional: "slow push in", "locked", "whip left" |
| `words` | cue ids on screen in this panel (the animatic shows the real cues at their real times regardless) |
| `sound` | optional: the musical event or mark under it |
| `refs` | manifest ids it draws on (`r012`) |
| `note` | anything else |

Panels are sorted by `at`, and the first is at 0. Make one panel per cue, one per
transition window, and at least one every three or four seconds, so a long shot still
shows what moves in it. Copy the words into `words` by id, never by text: the timeline
owns the text. Record the transition into the next panel in `action` when it matters.
The first three panels of the example film in section 9:

```json
{
  "panels": [
    { "id": "p01", "section": "00-open", "at": 0.0, "image": null,
      "action": "Black. A sheet of paper warms in; a charcoal line starts at the left edge.",
      "camera": "locked", "words": [], "sound": "first-note", "refs": ["r001"], "note": "" },
    { "id": "p02", "section": "00-open", "at": 0.9, "image": "board/p02.jpg",
      "action": "The line becomes a coastline; the words write on beside it.",
      "camera": "slow push in", "words": ["narration-1"], "sound": "", "refs": ["r002", "r003"], "note": "" },
    { "id": "p03", "section": "01-storm", "at": 6.0, "image": null,
      "action": "Ink floods up from the bottom edge (t-00-01); the storm's type is under it.",
      "camera": "", "words": ["slam-1"], "sound": "drop", "refs": [], "note": "" }
  ]
}
```

## 11. Board images

A panel's `image` can be any of four things. Each lives in `assets/board/` and is
committed with the film, so its licence must allow that:

1. **A code-drawn card** (`image: null`): the animatic draws the action line on a card in
   the section's palette. Free, honest, and enough for timing. Start here.
2. **A licensed reference still**: a file from `refs/img/` whose licence allows it,
   cropped to the frame, with its manifest id in `refs`. Never a link-only reference.
3. **A quick still**: a Python plate from a technique brief, or a style frame (section 4),
   saved as `assets/board/pNN.jpg`. No section is built at this point, so a still of one
   waits for Phase 4.
4. **A generated image**, only when the user allowed generated media at intake; log it
   with `log-asset.py` and note that it is a board image, not a frame of the film.

Make each board image at the film's own `w` x `h` (1920x1080, or 1080x1920 for 9:16), as
a JPEG at quality 85; the animatic renders at half size. The animatic fills the panel with
the image (`cover`), so a 16:9 image in a vertical film shows only its centre column.

## 12. The animatic

```bash
npm run animatic
```

It runs `remotion render Animatic out/animatic.mp4 --scale=0.5`: the storyboard panels in
order, the real cues at their real times, a strip with the section, the panel and the
timecode, the marks as ticks, the transitions named in their windows, and the music. It
is a boardomatic (stills timed to the track) with the words moving as they will [6][3]:
enough to judge pacing, which is the animatic's job [3].

Then the board sheet, one tile a second:

```bash
node scripts/shots.mjs animatic --all 1 --sheet storyboard
```

The sheet lands in `out/check/animatic/storyboard.jpg`, beside one still per second.
Open it and the mp4 and check, before the user sees them:

- every cue is on screen for its reading time and is readable at half size;
- every section boundary and named transition sits on its mark (the tick and the panel
  change agree);
- no stretch longer than about four seconds shows the same panel with nothing named
  moving;
- the ending lands where the music says it does.

Timecodes on boards, notes and cut lists are non-drop `HH:MM:SS:FF` at the film's frame
rate; drop-frame labels belong to 29.97 material [33].

## 13. The sign-off

In checkpoint mode, send the user `out/animatic.mp4` and the board sheet, with five
questions:

1. Does the arc land: does the end feel the way the brief asked?
2. Is any word wrong, or any line too fast or too slow to read?
3. Is any moment too long or too short?
4. Do the transitions fit, and is any one wrong for its moment?
5. If time runs short, does the cut list (section 14) drop the right things first?

Record each note as a record anchored to a frame, the way review tools anchor comments
to the timeline [34]: frame, cue or panel id, who, the note, status (`open`, `done`,
`declined`). Put them in `docs/storyboard.md` under the sign-off, change the timeline and
panels, render the animatic again, and log the gate:

```bash
python scripts/log-decision.py "user: animatic signed off with notes 1-4 applied; timing locked"
```

Notes here are cheap; notes after the build are not. In one-shot mode, run the checks in
section 12 yourself, fix what fails, and log that you passed the gate.

After the gate, timing is locked. A change that moves a boundary or a cue reopens this
phase for the sections it touches: re-run `check-timeline.py` and `snap.py`, re-render the
animatic, and tell the builders whose windows moved.

## 14. The cut list

For each section, an ordered list of what to drop first if time or budget runs short,
written now, while nobody is attached to anything. The first film's brief said "ship a
simpler version" without saying what; a late squeeze then became a panic instead of a
decision. Shape:

| Section | Drop first | Then | Never drop |
|---|---|---|---|
| 01-storm | the second data chart (keep the figure as type) | the parallax layer | `slam-1` on the drop |
| 02-close | the ember under the mark | the second question | `thesis-1` and the cut to black |

If the film is ever exported as an edit decision list for an editor, state 30 fps (or the
film's rate) explicitly: EDLs carry no frame rate, and the OpenTimelineIO CMX 3600 adapter
assumes 24 [32].

---

## 15. Sources

Plain numbers keep the numbering of the storyboard and music digest
(`dev/references/storyboard-music.md`); `C` and `W` numbers are from the ideation and the
rights digests. Confidence marks are the digests'.

2. Emma Coats, "22 Rules of Storytelling" (repost; medium). https://laughingsquid.com/22-rules-of-storytelling-by-pixar-storyboard-artist/
3. School of Motion, "Guide to Completing a Motion Design Project". https://schoolofmotion.com/blog/guide-completing-motion-design-project
4. Wikipedia, "Previsualization". https://en.wikipedia.org/wiki/Previsualization
5. Gnomon Workshop, "Creating Beatboards for Pre-Production" (low). https://ilm.thegnomonworkshop.com/blog/creating-beatboards-for-pre-production
6. Storyboard Hero, "Boardomatics 101" (vendor; low). https://storyboardhero.ai/boardomatics-101-everything-you-need-to-know
7. Animatic Media, "Boardomatics" (vendor; low). https://animaticmedia.com/boardomatics
8. Wikipedia, "Temp track". https://en.wikipedia.org/wiki/Temp_track
10. Apple, "Edit to the beat in Final Cut Pro". https://support.apple.com/guide/final-cut-pro/ver65b55a2b7/mac
11. Foxi Music, "How to Edit Music for Video in 2026" (vendor heuristics; low). https://www.foximusic.com/blog/?p=597
23. Wikipedia, "Match cut". https://en.wikipedia.org/wiki/Match_cut
24. Wikipedia, "J cut". https://en.wikipedia.org/wiki/J_cut
25. Wikipedia, "Smash cut". https://en.wikipedia.org/wiki/Smash_cut
26. Wikipedia, "Whip pan". https://en.wikipedia.org/wiki/Whip_pan
27. Wikipedia, "Wipe (transition)". https://en.wikipedia.org/wiki/Wipe_(transition)
28. Remotion, "Transitions" and "Presentations". https://remotion.dev/docs/transitions and https://www.remotion.dev/docs/transitions/presentations
32. OpenTimelineIO, otio-cmx3600-adapter. https://github.com/OpenTimelineIO/otio-cmx3600-adapter
33. Wikipedia, "SMPTE timecode". https://en.wikipedia.org/wiki/SMPTE_timecode
34. Adobe, "Add comments on shared projects (Premiere Pro)". https://helpx.adobe.com/premiere-pro-next/export-and-share/collaborate-with-others/add-comments-on-shared-projects.html
35. "The Making of Toy Story" (secondary PDF; low). https://people.uncw.edu/ricanekk/teaching/spring09/csc100/lectures/pattersone/TheMakingOfToyStory.pdf
- [A1] Meta, "Awareness Image Ad Specs on Instagram Reels" (added after review, read on 2026-10-23): leave roughly 14% of the top, 35% of the bottom and 6% on each side free of text. https://www.facebook.com/business/ads-guide/update/image/instagram-reels
- [C32] Wikipedia, "Safe area (television)", citing EBU R 95. https://en.wikipedia.org/wiki/Safe_area_(television)
- [W2] ITU-R BT.1702-3, "Guidance for the reduction of photosensitive epileptic seizures caused by television" (2023). https://www.itu.int/rec/R-REC-BT.1702-3-202311-I/en

The first film's numbers (handshakes that held, sizes that failed on a phone, the cut list
it lacked, frame snapping) come from `dev/references/wbam-lessons.md`.
