# Storyboard: <title>

The working notes of the storyboard phase (`<skill>/references/03-storyboard.md`). The
panels themselves are `data/storyboard.json`; the animatic is `out/animatic.mp4`. Replace
each `<prompt>`; delete each example line.

## Thumbnails

<where the thumbnail sheets are, and what each round settled>
*Example: work/thumbs/sheet-1.jpg: the hook needs four eras, not six; the outro is one
line, not three.*

## Beat board

One row per phrase (or per bar) of the real track. Print the skeleton with the snippet in
`references/03-storyboard.md`, section 3, then fill the last two columns.

| # | From | To | Bars | Section | Loudness | Structure | Cues | We see | Words |
|---|---|---|---|---|---|---|---|---|---|
| <n> | <s> | <s> | <n> | <section id> | <0 to 1> | <structure points inside> | <cue ids> | <the picture, in a few words> | <the words, short> |
| *3* | *16.08* | *31.29* | *4* | *02-human-cost* | *0.71* | *28.65* | *narration-2, quote-1* | *desks empty one by one; a face drawn as it speaks* | *"... half of entry-level ..."* |

## Panels

- **Count:** <panels>, <one per cue, one per transition window, at least one every 3 to 4 s>
  *Example: 46 panels; the longest hold is 3.6 s (p31).*
- **Images:** <how many code-drawn cards, licensed stills, quick stills, generated images>
  *Example: 30 cards, 9 quick stills, 7 licensed stills; no generated images (not allowed).*

## Style frames

| Moment | File | Status |
|---|---|---|
| <the hero moment> | <assets/board/style-<id>.jpg> | <open, approved, or changed: what> |
| *the eyelid opening at 49.40* | *assets/board/style-04-bargain.jpg* | *approved 2026-10-22* |

## Cut list

What to drop first, per section, if time or budget runs short. Write it now, before
anyone is attached to anything.

| Section | Drop first | Then | Never drop |
|---|---|---|---|
| <section id> | <the first thing to go> | <the second> | <what the section exists for> |
| *03-acceleration* | *the second chart (keep the figure as type)* | *the halftone pass* | *the six figures, exact, and the collapse to one line* |

## Animatic checks

- [ ] Every cue is on screen for its reading time and readable at half size.
- [ ] Every section boundary and named transition sits on its mark.
- [ ] No stretch longer than about four seconds shows one panel with nothing named moving.
- [ ] The ending lands where the music says it does.
- [ ] `python scripts/check-timeline.py` exits 0; `python scripts/snap.py` flags nothing
      without a logged reason.
- [ ] Every `data` and `quote` cue is `verified` or `corrected` in `docs/research/facts.md`.

## Sign-off

Notes anchored to a frame (non-drop timecode at the film's frame rate).

| Frame | Timecode | Cue or panel | Who | Note | Status |
|---|---|---|---|---|---|
| <frame> | <HH:MM:SS:FF> | <id> | <user or lead> | <the note> | <open, done, declined> |
| *1482* | *00:00:49:12* | *p27* | *user* | *the eyelid opens too fast; hold the line a beat longer* | *done* |

- **Gate:** <date; signed off by whom; what changed after the notes; "timing locked">
  *Example: 2026-10-22; signed off by the user with notes 1 to 4 applied; timing locked.*
