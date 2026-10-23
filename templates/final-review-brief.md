# Final review: the brief

<!-- Lead: this file is docs/final-review-brief.md. Fill the <placeholders> for the film.
Do not add your own worries or what you fixed: the reviewer's value is that nobody told it
what to expect. Delete this comment. -->

One reviewer, fresh eyes, on the **finished file**. You look and write. You do not render,
edit code, or touch git. Your one output is `docs/review/final.md` (in a second review,
`docs/review/final-2.md`: see the end of this brief).

You have not seen this film being made. That is the point: judge what a viewer gets.

## What you are given

`out/final-review/`, made by `python scripts/film-frames.py` from
`out/__SLUG__-graded.mp4`, the graded deliverable. Every frame in it was read out of that file,
so it carries the final grade, grain, vignette and encode.

- `frames.json`: every sheet with its tiles (frame, time, label, file). Read it first.
- **By clock**, `clock-NN.jpg` (frames in `clock/`): one frame every <0.5> seconds of the whole
  film, in order, 24 tiles a sheet, labelled `f<frame>_t<seconds>`. Read them in order: it is
  the film.
- **By cue**, `cues-NN.jpg` (full-size frames in `cues/`): for every cue in the timeline, its
  first frame plus two (is the line whole when it should be readable?) and its midpoint,
  labelled with the cue id. This is how you check every word, including words on screen for a
  few frames only.
- **By transition**, `transitions-NN.jpg` (full size in `transitions/`): the first and last
  frame of every transition window; for a hard cut, the frame before and the cut frame.
- **The ending**, `last-NN.jpg` (frames in `last/`): every frame of the last <3> seconds before
  <the cut to black at <t> s, and six frames into the black / the end of the film>. Read every
  tile.
- **Key stills**, `full/` at <w>x<h>: first and last frame, the frames around the cut to black,
  every cut frame, every section's midpoint, the midpoint of every data, quote, thesis and logo
  cue. Use them to judge type and detail.
- **Phone sheets**, `phone-NN.jpg`: every cue's midpoint as a 360 px tile, the width of the
  picture on an upright phone. Judge legibility here: that is how most people will see it.

The film is <length> at <fps> fps, <n frames> frames. <The black bars top and bottom are its
letterbox. | It has no letterbox.> The picture carries the final grade up to <where it stops,
and why: "the cut to black; the outro after it is clean on purpose" | the end>.

## Read first

- `<docs/treatment.md>`: what the film is for and its tone arc (<arc in a few words>).
- `docs/style-bible.md`: "Rules for every section" (with the minimum type sizes) and one page
  per section.
- `docs/transitions.md`: "The table": what each boundary is meant to do.
- `data/timeline.json`: `sections` (spans), `cues` (the exact words and when), `transitions`.
  The words on screen must be each cue's `text`, exactly, with its `attribution`, and for
  `data` cues its `source`.
- `docs/research/facts.md`: the verified wording of every fact and quote.

Do not read `docs/sections/`, `docs/review/` (the transition reviews and any earlier final
review), `docs/decisions.md`, `docs/report.md` or any builder brief before you have written
your findings: they would tell you what to expect. (A second review reads
`docs/review/final.md`: see the end of this brief.)

## What to judge

1. **Broken frames.** Anything a viewer would take for a mistake: a test card or placeholder (a
   large section label, the words TEST CARD, safe-area boxes, magenta, a dev read-out of frame
   numbers or timecode), a missing image, a pop of black, white or the wrong picture, a frame
   that jumps for no reason, a section that never arrives.
2. **Words.** For every cue: is it on screen in its span, is the text exact, is it whole on its
   first frame plus two, can it be read at <h>p, and on the phone sheet? Report anything cut off
   by the letterbox or the frame edge, crossed by a moving shape, set over a busy field, or under
   the style bible's minimum size. Facts (`role: "data"`) and quotes must be exact to the
   character, including the attribution and source lines.
3. **Does each picture tell the truth?** A chart, a count or a diagram must read as its fact at a
   glance, on the phone sheet too. A picture that reads as the opposite of its words is broken.
4. **<The styles | The look>.** <Each in its own style: does each section read as the style on
   its page, and as different from its neighbours? Name the weakest section and say why. | One
   look throughout: does every section hold the look on the style bible's page, and does the
   film still develop (pace, scale, light, what is on screen) rather than repeat one image?
   Name the section that drifts furthest from the look, or the one that adds least, and say
   why.>
5. **Boundaries.** Each cut: does it read as the named device, and does the incoming section
   start on a strong image?
6. **The ending.** Frame by frame: what is on screen, does it build, is the last picture frame
   the strongest, <is the first black frame truly black and are the frames after it black | does
   the fade go evenly to black | is the held mark whole and held long enough, and does the last
   frame cut cleanly back to the first, for a film that loops>. Is anything left on screen by
   mistake?
7. **The grade.** Crushed blacks that eat detail, clipped highlights, banding, grain too heavy
   for the type or missing, a vignette that reads as a dirty lens, grade where it should be off.
8. **<The end card / the mark / the credit>.** Timing, legibility, does it end.
9. **The arc.** <The intended arc, e.g. "awe, then dread, then responsibility; not a horror
   trailer">. Does the film earn its last line?

Flash safety is measured by the lead with `scripts/flash-check.py`; report only what looks like
a strobe or a saturated red field. You cannot judge motion, sync or sound from stills: do not
pretend to. Where they matter, say what you could not settle and name the frames.

Say what you see with frame numbers. **Do not guess**: if a frame cannot settle a point, name it
and say so. A short honest review is worth more than a long one.

## The file you write

```
# Final review

**Verdict:** SHIP | SHIP WITH FIXES | DO NOT SHIP
**File:** out/__SLUG__-graded.mp4

What this review rests on: (which samples, how many full-size stills; what you could not judge.)

## The film in ten lines
(What a viewer sees, start to end, with frame ranges.)

## Broken
(Must fix before this is shown. One bullet each: frames; what is wrong; which section owns it;
the smallest fix. "None." if none.)

## Polish, in order of worth
(At most eight. Same form. The one that would improve the film most first.)

## Not settled
(Frames the lead must look at, and what to look for: a word between samples, a motion, an exact
entry frame. "None." if none.)

## Words
| Cue | On screen | Exact | <h>p | Phone | Note |
|---|---|---|---|---|---|
(Every cue in the timeline, one row each, frame numbers in the note.)

## Section by section
(Two to four lines each: does it read as its style, its best frame, its weakest.)

## The ending
(Frame ranges and what happens; the last picture frame; the black or the fade.)

## Looked at
(The sheets and stills you opened.)
```

SHIP: nothing broken. SHIP WITH FIXES: broken items that are small and clear, or polish worth
doing. DO NOT SHIP: broken items that change what the film says, or that a fix cannot settle
quickly.

## Your final message

To the lead, six lines at most:

```
Verdict: <VERDICT>
Broken: <n>  <one line for the worst, with frames>
Polish 1: <...>
Polish 2: <...>
Polish 3: <...>
Not settled: <n> (<frames>)
```

## If this is the second review (diff mode)

The lead fixed what the first review found and rendered again. You review **only what changed**.

- Inputs: `out/diff/`, made by `python scripts/diff-frames.py <old> <new>`: `frames.json` (the
  frame ranges that changed between the two graded files, with their sections), one
  `sheet-NN.jpg` per group of ranges (rows: old, new, and the difference x4), and the full-size
  frames in `old/`, `new/` and `delta/`. And `docs/review/final.md`, the first review: read its
  Broken and Polish lists; you may read that file.
- Judge: is each broken item fixed, on the frames it named, at full size and on the phone? Did a
  fix break anything nearby? Is every changed range one the lead meant to change (a range that
  matches no finding is a finding)?
- Write `docs/review/final-2.md`:

```
# Final review, second pass

**Verdict:** SHIP | SHIP WITH FIXES | DO NOT SHIP
**Files:** <old> -> <new>

## Each item from the first review
| Item | Frames | Fixed? | Note |

## Changed ranges
| Frames | Expected (which item) or unexpected | What changed |

## New problems
(Same form as Broken. "None." if none.)

## Looked at
```

Final message: the verdict, the number of items fixed and not fixed, and any new problem, in
four lines at most.
