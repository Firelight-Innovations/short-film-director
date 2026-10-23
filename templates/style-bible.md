# Style bible: <title>

The builders' shared rulebook (`<skill>/references/03-storyboard.md`, section 5). Times
are film seconds from `data/timeline.json`, which is the authority; research files may
carry older times, so use their techniques and ignore their timestamps. Replace each
`<prompt>`; delete each example line.

## What the film is

<three to five lines: the form, the arc, the line it exists to land>
*Example: A two-minute music film that moves from awe to dread to responsibility, in eight
art styles, and lands one line in silence.*

## Rules for every section

1. **The words are exact.** On-screen text is the cue's `text` (and `attribution`, and
   `source` for `data` cues), character for character. Case styling is allowed. Add no
   factual claim. A decorative label that asserts nothing about the world is fine.
2. **Cut on the music.** Boundaries and shot changes sit on measured events (`marks`,
   `beats.json`). A cue's `from` is the frame it is readable by: start entrances early.
3. **One strong idea per shot.** If a shot has three effects, cut two.
4. **Nothing reads as a slideshow.** Every frame moves: camera, light, boil, grain,
   parallax.
5. **Type is part of the picture.** Each section sets its words in its own material.
6. **The picture area.** Compose inside the letterbox; keep words in the title-safe box and,
   for a vertical feed, inside the platform UI zone below.
7. **Flash safety.** At most three flashes in any one second; no saturated red fields.
8. **Every frame is a pure function of its frame number.** `rnd(seed)` only; no
   `Math.random`, no `Date`, no CSS animation, no state carried between frames.
9. <a rule of this film>
   *Example: Restraint is the tone: reverent, never smug; when in doubt, do less.*

## Minimum type sizes

Pixels at 1080 on the short side; multiply by the kit's `UNIT` for other sizes. Check every
word on the 360 px phone sheets.

| Role | Minimum (px) | This film |
|---|---|---|
| `narration`, body | 54 | <size, or "default"> |
| `thesis` | 64 | <size> |
| `slam` | 120 | <size> |
| `data` numeral | 96 | <size> |
| `quote` (and its `attribution` at 40) | 54 | <size> |
| `sub`, `attribution`, labels | 40 | <size> |
| `source` line | 32 | <size> |
| `credit` | 44 | <size> |
| `stamp`, when it must be read | 32 | <size> |
| chart hairlines | 2 px at 0.5 opacity or more | <size> |
| *Example: `source` line* | *32* | *36, IBM Plex Mono 500* |

## Picture area

- **Letterbox:** <fraction>, bars <px> top and bottom; picture <w x h>
  *Example: 0.06, bars 65 px; picture 1920x950*
- **Title-safe and action-safe boxes:** <from the kit's SAFE, in px>
  *Example: title-safe x 96 to 1824, y 113 to 968*
- **Platform UI zone:** <the x and y range in px where words and anything that must be seen
  stay clear of the platform's own interface, and whose figure it is; "none" for 16:9>
  *Example: x 65 to 1015, y 269 to 1248 (Meta's Reels figure for ads: 14% top, 35% bottom,
  6% sides at 1080x1920; check on the posting day)*
  The kit's `SAFE` does not hold this zone, so the builder brief repeats it and a reviewer
  checks it on the phone sheets (`<skill>/references/03-storyboard.md`, section 5).

## Palette and type at a glance

| Section | Field | Ink | Accent | Type (families in `font()`) |
|---|---|---|---|---|
| <NN-name> | <colour> | <colour> | <colour and what it is for> | <families and weights> |
| *03-acceleration* | *black and white* | *bone* | *acid yellow-green, figures only* | *Archivo Black, Space Grotesk, JetBrains Mono* |

Exact values are the `palette` of each section in `data/timeline.json`.

- **Fonts:** vendor every family in the table before the first style frame and before the
  animatic: `node scripts/fetch-fonts.mjs "<Family>:400,700" ...`. The script downloads
  from Google Fonts, so run it after the user's yes to downloads. Until a family is
  vendored the kit draws a system font and prints a warning.
  *Example: `node scripts/fetch-fonts.mjs "Archivo Black:400" "Space Grotesk:400,700" "JetBrains Mono:400"`*
- **Warmth or coolness of the film:** <which palette fields carry it>. The grade has no
  colour balance or temperature control, so it cannot warm or cool anything; the palettes do.
  *Example: warm: every `bg` leans amber, every `ink` is cream, never pure white.*

## Grain, texture and the grade

- **Each section's own texture:** <paper, tape noise, halftone ...; owned by the section>
  *Example: 02 paper tooth and charcoal boil on twos; 03 halftone and misregistration.*
- **The grade, once, at the end** (`scripts/grade.py`, from `timeline.grade`): <what it does
  and from when it is off>
  *Example: contrast 1.05, saturation 0.97, gamma 0.985, vignette 0.333, grain 5; off from
  the cut to black at 99.867.*

---

## Section pages

Copy this page once per section, in film order.

### <NN-name>: <the look in a few words> (<from> to <to>)

- **Primary style:** <the look>
  *Example: charcoal and ink on paper, animated on twos, with erasure that leaves ghosts.*
- **Clashing secondary:** <a second look that rubs against it, or "none">
  *Example: cut and torn paper for objects: people are drawn, things are pasted.*
- **The job:** <one line: what this section must make the viewer feel or understand>
  *Example: the first human hand in the film; slow down.*

| Shot | Time | Plate or source | What happens |
|---|---|---|---|
| <A> | <from to to> | <file under assets/footage/<id>/, or "live"> | <one or two lines> |
| *A* | *16.08 to 20.30* | *live, over paper-0..2.webp* | *a robot is drawn, then rubbed out; its ghost stays* |

- **Transition in** (`<t-id>`, "<name>"): <who owns it; what this section owes in pixels>
  *Example: owned by this section; the frozen frame from 14.867 is drawn over in ink.*
- **Transition out** (`<t-id>`, "<name>"): <who owns it; what this section owes in pixels>
  *Example: owned by the next section; keep the drawing and the quote steady to 28.933.*
- **Palette:** <bg, ink, accent, and where the accent may not appear>
  *Example: paper cream, charcoal, red oxide only on the torn paper.*
- **Type:** <families, sizes, how the words are set in this material>
  *Example: hand-lettered (Cabin Sketch 64), written on stroke by stroke from 8 frames early.*
- **References:** <manifest ids; refs/board-<id>.jpg>
  *Example: r014, r015, r021; refs/board-02-human-cost.jpg*
- **Research:** <docs/research/<slug>.md files>
  *Example: docs/research/02-ink.md*
- **Style frames:** <assets/board/style-<id>.jpg, or "none">
  *Example: assets/board/style-02-human-cost.jpg (signed off 2026-10-22)*
- **Must not:** <the generic version of this look; the mistakes to avoid>
  *Example: no clean vector lines; no centred caption; never show the source footage itself.*
