# Boundary review: the brief

<!-- Lead: this file is docs/boundary-review-brief.md. Fill the <placeholders> once for the
film; each reviewer's prompt names its boundary. Delete this comment. -->

You review one boundary of *__TITLE__*, a <length> code-rendered film (<w>x<h>, <fps> fps,
<n> sections, <each in its own style | one look throughout>). Your boundary is named in your
prompt: a transition id such as `t-03-04`, its name, and the two sections it joins.

A reviewer **looks and writes**. You do not render, edit code, touch git, or install, download
or publish anything (if you need something, say so in your file). Your one output
is `docs/review/transition-<a>-<b>.md`: the transition id without `t-` (`t-03-04` writes
`transition-03-04.md`; `t-start` writes `transition-start.md`, `t-end` writes
`transition-end.md`). Do not read `docs/sections/`, `docs/decisions.md` or other reviews:
they would tell you what to expect.

## What you are given

`out/review/<transition id>/`, made by `node scripts/review-frames.mjs`:

- `frames.json`: the cut frame, the window, and which file holds which frames. Read it first.
- `sheet-NN.jpg`: **every** frame from a margin before the window to a margin after it, in
  order, 24 to a sheet, each tile labelled `f<frame>_t<seconds>`. Read them in order, every
  tile.
- `full_f....jpg`: the frame before the cut, the cut frame, the frame after, at full size.
- `phone-NN.jpg`: the same frames as 360 px tiles, the width of the picture on an upright
  phone. Judge legibility here: that is how most people will see it.
- `motion.csv` (and `motion.png`): the mean absolute difference between each frame and the one
  before. A lone spike with quiet neighbours is a one-frame pop; a run of zeros inside motion
  is a freeze.
- `frames/`: the frames one by one at half size, when a tile is too small.

If the folder is missing or empty, do not review from imagination: write your file saying so,
with the verdict NOT REVIEWED.

The frames are the film's clean output at <fps> fps. <The black bars top and bottom are the
film's letterbox. | The film has no letterbox.> There is no grade yet: <a gentle contrast
grade, a little grain and a soft vignette> go over the film at the end<, except <where>>. Do
not report the absence of grain or grade.

## Read first

- `docs/transitions.md`: the row for your boundary in the table (name, owner, window, device,
  what it lands on), its line under "What each side owes the other", and "How a transition is
  built". During the window only the **owner** section is mounted, and it draws its
  neighbour's live picture itself.
- `docs/style-bible.md`: "Rules for every section" (including the minimum type sizes) and the
  pages of your two sections.
- `data/timeline.json`: the transition (time, window, owner, device, beat) and the cues of
  your two sections near the boundary (`cues`, by `section`). Words on screen must be each
  cue's `text`, exactly.
- `data/storyboard.json`: the panels for this moment: what the board promised.

## What to judge

1. **Does it do what the table says, on the frames it says?** The cut frame, the device, what
   it lands on, and every pixel promised in the handshake line.
2. **Broken frames.** Anything that reads as a mistake: a one-frame pop of black, white or the
   wrong picture; a test card (a large section label on stripes, the words TEST CARD, safe-area
   boxes, magenta); a missing image; a neighbour visible where it should be gone; a jump in
   position, scale or brightness that the device does not explain; a frame identical to its
   neighbours where there should be motion, or the reverse. Use the motion trace to find them,
   then the tiles to see them.
3. **Words.** Cut off, overlapping other words, crossed by a moving shape so they cannot be
   read, not whole on the cue's first frame, not the cue's exact text, too small or too low in
   contrast at <h>p, or unreadable on the phone sheet.
4. **Flash safety.** More than three flashes (light-dark-light pairs) in any one second over a
   quarter of the frame or more (name smaller strobing areas too), or any saturated red field.
5. **Is it the named device, or a generic one?** A plain cut or dissolve where a device was
   promised is a finding. So is a device that is there but too short or too subtle to be seen
   at speed (<fps> frames is one second).
6. **Does the incoming section start well?** Its first frames after the window: is the first
   image strong; is the first line readable when it arrives?
7. **Motion.** From consecutive tiles and the trace: does the device move as described (an
   even ease, a build, a hit), or does it step, stall or snap?

Say what you see with frame numbers. **Do not guess.** If a tile cannot settle a point, name
the frame and say the lead should look at it full size. If something you need is not in your
frames (the device starts before the first tile), say so under "Looked at".

## The file you write

```
# Transition <a> to <b>: <name>

**Verdict:** PASS | PASS WITH FIXES | FAIL | NOT REVIEWED
**Cut frame:** <n>   **Window:** <first> to <last>   **Owner:** <section id>

## What I saw
(8 to 15 lines, in frame order, with frame numbers.)

## Blockers
(Broken things. One bullet each: frames; what is wrong; which section most likely owns it;
the smallest fix you can think of. "None." if none.)

## Should fix
(Same form. Things a viewer would notice.)

## Nice to have
(Same form. Short.)

## Looked at
(Every sheet and still you opened, and anything you could not see.)
```

PASS: nothing a viewer would notice. PASS WITH FIXES: no blockers, one or more should-fix
items. FAIL: one or more blockers. NOT REVIEWED: no frames to review.

## Your final message

To the lead, three lines at most:

```
<transition id>: <VERDICT>
Blockers: <n>   Should fix: <n>   Nice to have: <n>
<the one thing the lead must look at, or "nothing open">
```
