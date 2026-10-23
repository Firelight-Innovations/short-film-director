# 06. Review: boundaries, motion, sync and fix rounds

Phase 5. Every boundary of the integrated film is reviewed by a reviewer who sees only
frames and a brief; motion and sync are measured; findings go back to the section that
owns them for one fix round; the lead checks each fix on frames. Gate: zero blockers.

## Contents

1. [Inputs: review-frames.mjs](#1-inputs-review-framesmjs)
2. [Motion: motion-check.py](#2-motion-motion-checkpy)
3. [Sync: sync-check.py](#3-sync-sync-checkpy)
4. [The boundary reviewers](#4-the-boundary-reviewers)
5. [Verdicts and severity](#5-verdicts-and-severity)
6. [Triage](#6-triage)
7. [Fix rounds](#7-fix-rounds)
8. [Verifying a fix on frames](#8-verifying-a-fix-on-frames)
9. [Chains after a fix](#9-chains-after-a-fix)
10. [The measured checks and what each number means](#10-the-measured-checks-and-what-each-number-means)
11. [Accepted residuals](#11-accepted-residuals)
12. [Sources](#12-sources)

---

## 1. Inputs: review-frames.mjs

```
node scripts/review-frames.mjs [t-ids...] [--margin 12]     default: every transition
```

For each transition it renders the integrated film, clean (no dev overlay), and writes
`out/review/<transition id>/`:

| File | What |
|---|---|
| `frames/` | every frame from `--margin` frames before the window to `--margin` after it, half size; a hard cut (no window) gets 30 before and 14 after |
| `sheet-NN.jpg` | those frames in order, 24 to a sheet (6 x 4, 480 px tiles), labelled `f<frame>_t<sec>` |
| `phone-NN.jpg` | the same frames as 360 px tiles, the width an upright phone gives the picture (a 16:9 1920 frame at 0.1875; a 9:16 1080 frame at 0.333, where every line must also sit inside `SAFE.title`, 972 px); type that fails here fails the post |
| `full_f....jpg` | the frames cut-1, cut and cut+1 at full size |
| `motion.csv`, `motion.png` | the motion trace of `frames/` from `motion-check.py` (section 2) |
| `frames.json` | what is where, for the reviewer |

`t-start` dumps the first 24 frames (and full frames 0 and 6); `t-end` the last 24. The frames
are ungraded; the brief tells reviewers so, so they do not report missing grain.

When a device begins before the margin, the reviewer cannot see its start. On the first film
a boundary reviewer could not see a line of type collapse into the hold the device started
from, because it happened 8 to 16 frames before the window. Read the boundary's row in
`docs/transitions.md`: if a handshake hold or a build-up starts earlier, widen the margin for
that boundary (`node scripts/review-frames.mjs t-03-04 --margin 30`).

## 2. Motion: motion-check.py

```
python scripts/motion-check.py <mp4|dir> [--from s --to s] [--sections]
python scripts/motion-check.py out/pass1.mp4 --sections
```

Every frame is shrunk to a 192 px wide grey copy and compared with the one before: the mean
absolute difference (0 to 255) is that frame's change. It prints the change per section
(median, 95th percentile, share of still frames) and the flags, writes
`out/motion/<name>.csv` (one row per frame) and `out/motion/<name>.png` (the trace in rows of
30 s, sections marked), and exits 3 when it finds a pop or a freeze inside motion.

| Flag | What it is (defaults) | What it usually means |
|---|---|---|
| **Freeze** | 4 or more frames with change under 0.3, with motion on both sides (`--freeze`, `--still`) | a plate sequence that ran out and clamped to its last plate; a clip that ended early; a layer whose `delayRender` never fired; a section that stopped reading the film clock |
| **Jump** | a change of 12 or more and four times the change around it (`--jump`); at a section boundary or a window edge it is listed as a cut | inside a section: a cut where none is planned, a layer that appears or vanishes in one frame, a position or brightness step the device does not explain |
| **Pop** | change in and out both 8 or more while the frames either side are close to each other (`--pop`) | a single wrong frame: a test card, a missing image, a black or white frame, an off-by-one handover between sections |

A held shot with nothing moving around it is not a freeze. The dev overlay's ticking timecode
sits in the bars and averages away at 192 px (measured on a film with bars: with the overlay
on, 92 percent of frames read as still), so pass1 with the overlay is fine for motion and
sync. With `letterbox` 0 the overlay is a strip over the top and bottom of the picture
instead; that case was not measured, so open any flag near an edge on a `--clean` still. The
overlay is not fine for `black-check.py`: it is drawn in the bars or over the edges, so
black-check fails on pass1 by design. Run black-check on the final render
(07-final-and-delivery.md).

How to read it:

- Every flag is a frame number. Open that frame and two either side, full size, before you
  decide anything.
- Expected spikes: planned hard cuts, hits, the cut to black. Check them against the
  section's shot list and `docs/transitions.md`; a spike on the cut frame of a hard cut is
  correct.
- Expected flat stretches: a held card, black between lines, a deliberate freeze-frame.
  The style bible should say so.
- A section animated on twos (`hold(frame, 2)`) shows every second difference near zero.
  That is a pattern, not a freeze; a freeze is a run of them where the style moves.
- A pop at a section boundary is the most common real fault: the incoming section's first
  frame shows the previous section, or a frame inside a window shows nothing. It is the
  symptom of comparing typed seconds instead of frames (04-architecture.md, section 4).

## 3. Sync: sync-check.py

```
python scripts/sync-check.py <mp4> [--sections]
python scripts/sync-check.py out/pass1.mp4 --sections
```

It takes motion-check's change trace, finds its peaks, and matches each to the nearest event
in `data/beats.json` (beat, downbeat, onset, hit, fitted pulse). Per section it prints the
number of peaks, the share within `--tol` frames of an event (default 2: "on the beat"), the
median signed distance (event minus picture: +1 means the music lands a frame after the
picture moved), the correlation between picture change and the onset curve, and the off-beat
moves, biggest first. Peaks after the music has ended are counted apart. It writes
`out/sync/<name>.csv`. Exit 0; it reports, it does not judge. With no track, it says there is
nothing to sync to.

How to read it:

- At 30 fps one frame is 33 ms. A beat tracker's own tolerance in evaluation is 0.07 s
  [1], about two frames, so a peak within two frames of an event is on it.
- A steady median of +1 or -1 across a section means the whole section sits a frame early or
  late against the music: one offset in the section's frame numbers fixes it.
- Judge the share against the section's intent on its style page. A section cut "on the
  pump" should have most of its peaks on events; a slow painted section may have few
  peaks at all, and that is right.
- Read the off-beat list as questions. A big move more than two frames from any event is
  either intended (a move on a phrase the analysis did not mark, a held breath before a
  hit) or late or early. Open the frames; check the cue and the mark it was meant to sit
  on; if it is meant to land on an event, the fix is in the section's frame numbers, or in
  the timeline when the event itself was placed wrong (`python scripts/snap.py`).
- Sync-check reads the picture and the analysis, not the sound. It cannot tell whether the
  cut *feels* on the music. That is the human sound gate (07-final-and-delivery.md).

## 4. The boundary reviewers

One reviewer per boundary, including `t-start` and `t-end` when the timeline has them (the
film's first and last frames are a boundary too). A reviewer looks and writes:
it does not render, edit code or touch git. Its one output is
`docs/review/transition-<t-id without "t-">.md`, named after the transition id, not the
section ids (`t-03-04` writes `transition-03-04.md`, `t-end` writes `transition-end.md`).

Brief: `docs/boundary-review-brief.md` (from `templates/boundary-review-brief.md`). Fill
its placeholders once for the film; the boundary is named in each reviewer's prompt.
Model: mid (for example Sonnet), unless the user's rules say otherwise. Run a boundary when
both of its sections have landed; on the first film six went first and two waited for the
last section.

With workflows:

```
Workflow({ scriptPath: "<skill>/scripts/workflows/review-boundaries.js",
           args: { skill: "<skill>", project: "<project>", transitions: ["t-00-01", "t-01-02"], model: "sonnet" } })
```

`model` defaults to `"sonnet"`. `notes` (optional) is one paragraph every reviewer gets: use
it for facts about the frames (a widened margin, where the sync-check output is), never for
what you expect them to find. It returns each review (verdict, counts, items with frames,
owner and smallest fix, what the reviewer could not judge, file) and totals. Without
workflows, launch one Agent per boundary in one message, each with this prompt:

```
You are reviewing one boundary of a short film: <t-id>, "<name>", between <a> and <b>.
Read <project>/docs/boundary-review-brief.md and follow it exactly. Your frames are in
<project>/out/review/<t-id>/ (start with frames.json). Write
<project>/docs/review/transition-<t-id without "t-">.md and nothing else. Do not read
docs/sections/, docs/decisions.md or other reviews.
```

Why a fresh reviewer with frames only: it is not told what to expect, so it sees what a
viewer sees. On the first film eight boundary reviews found no blockers and four real faults
(a tape tear that read as a web glitch, an eyelid with an angular edge and a one-frame
ignition, a fade that dropped in steps), and each fix round improved the film.

## 5. Verdicts and severity

Boundary verdicts: **PASS** (nothing a viewer would notice), **PASS WITH FIXES** (no
blockers; one or more should-fix items), **FAIL** (one or more blockers). **NOT REVIEWED**
means the reviewer found no frames: run `review-frames.mjs` for that boundary and review it
again. It never counts toward the gate.

| Severity | Means | Examples |
|---|---|---|
| Blocker | broken: a viewer would take it for a mistake, or it is untrue | a test card or placeholder on screen; a one-frame pop of the wrong picture, black or white; a missing image; words cut off, misspelt or not the cue's text; a fact that reads as its opposite; more than three flashes in a second; a saturated red field |
| Should fix | a viewer would notice | a generic dissolve where a named device was promised; a device too short or subtle to see at speed; a weak first image; type too small for a phone; a move that fights the music |
| Nice to have | better, not wrong | a softer edge, a longer hold |

Each finding names the frames, what is wrong, the section that most likely owns it, and the
smallest fix.

## 6. Triage

1. Read every reviewer's final message (three lines each), then the files.
2. Merge findings that are the same fault seen from two boundaries.
3. For each finding decide: **fix** (it goes to the owner), **accept** (a residual, section
   11), or **reject** (the reviewer is wrong). Reject only after you have opened the frames
   yourself, and log why.
4. Every blocker is fixed, or the frames prove it is not one.
5. Findings in the lead's files (kit, timeline, a tool) are yours: fix them before you
   send the section rounds, and tell the builders what changed.
6. Log the triage: `python scripts/log-decision.py "lead: reviews in: <n> PASS, <n> PASS WITH
   FIXES, <n> FAIL; fix rounds to <ids>; accepted <list>; why"`.

## 7. Fix rounds

One round per section, with every finding for that section from every boundary in one
message, blockers first.

**Named builders** (the default): send the round to the same agent, which still holds its
context:

```
SendMessage({ to: "sec-<id>", message: "Fix round 1 for <id>. Findings, blockers first:
1. <frames>: <what is wrong> (from docs/review/transition-<t-id without "t-">.md). Smallest fix: <...>.
2. ...
Do not change any handshake in docs/transitions.md without asking. For each item, re-render
the frames it names, look at them, and write in your log what changed and which frames show
it. Reply with the short final message from your brief and the paths of the after-frames." })
```

**Under workflows**: `build-sections.js` with `fixes: { "<id>": "<path of the review file,
or the findings as text>" }`. A fresh agent reads the section log, the brief and the
findings, and fixes the smallest way.

A finding that belongs to another section goes to that section's round. A finding that
would move a handshake involves both sides: decide the new pixels, write them into
`docs/transitions.md`, and send both rounds together.

## 8. Verifying a fix on frames

Do not take a fix on the builder's word; look.

1. Keep the before frames: rename `out/review/<t-id>/` to `out/review/<t-id>-r0/` before you
   re-run.
2. `node scripts/review-frames.mjs <t-id>` for every boundary the fix touched.
3. Open the frames each finding named, before and after, side by side. Check the
   neighbouring frames too: a fix that moves a fade can open a hole a few frames away.
4. Read the new motion trace for the window: no new pop or freeze.
5. Flash-check the window from its frames: `python scripts/flash-check.py
   out/review/<t-id>/frames`. For a fix away from a boundary, render the span first:
   `node scripts/shots.mjs film --seq a:b --clean --no-sheet --out out/check/flash-<id>`, then
   `python scripts/flash-check.py out/check/flash-<id>`.
6. If the fix touched a boundary's device, send the new frames to a reviewer for a short
   second look, or look at every frame yourself and say so in the log.

## 9. Chains after a fix

A fix in a section can make another section's plates stale: the section's own baked words,
or the frames a recap section cut from the film.

```
python scripts/chain.py check            exit 3 names each stale chain
python scripts/chain.py run <name>       rebuild it, run its checks, update the lock
python scripts/doctor.py                 must exit 0 before the next full render
```

On the first film the recap section was cut from 38 frames of the finished film; every fix
to the sections before it meant re-rendering those plates, rebuilding the section's plates
and flash-checking its span, by hand. Now the chain names the inputs, `chain.py check`
fails loudly, and `doctor.py` refuses a stale chain. After a chain re-runs, look at the
consuming section's frames again: new plates can change a cut that was tuned for flash
safety.

## 10. The measured checks and what each number means

| Tool | Command | What the numbers mean | Pass |
|---|---|---|---|
| flash-check | `python scripts/flash-check.py <mp4\|dir> [--from s] [--to s] [--fps n] [--area 0.25] [--max-flashes 3]` | A **transition** is a rise or fall of 10 percent or more of relative luminance, with the darker state below 0.80, over a quarter of the screen or more; the change accumulates over frames, so a three-frame fade counts like a cut. A **flash** is a pair of opposing transitions. **Worst second** is the most flashes in any one-second window. **Red** counts the same for saturated red (R/(R+G+B) at least 0.8). A saturated red field and a flashing run over five seconds are reported as warnings | exit 0: at most 3 general and 3 red flashes in any second [2] |
| black-check | `python scripts/black-check.py <mp4> [--tol 2] [--bar-tol 12]` | max luma of every frame in `checks.black` (naming the first that is not black) and of the last four frames when `lastFrameBlack`; max luma in the letterbox bars, leaving out the two rows that touch the picture. Luma is read full-range, so 0 is black. A frame is black at max 2 or less; a bar may reach 12 from encoder ringing | exit 0 |
| motion-check | `python scripts/motion-check.py <mp4\|dir> [--from s --to s] [--sections]` | per-frame change (mean absolute difference of a 192 px grey copy, 0 to 255); freezes, jumps and pops by frame (section 2) | exit 0; 3 on a pop or a freeze inside motion |
| sync-check | `python scripts/sync-check.py <mp4> [--sections]` | per section: distance in frames from each change peak to the nearest beat or onset, the share on the beat, the off-beat list | report only |
| check-timeline | `python scripts/check-timeline.py` | the timeline's rules; errors for a cue or its `shown` window outside its section's render range; warnings for cues shorter than their reading time (0.4 s a word plus 0.5 s) | exit 3 on an error, 0 otherwise |
| snap | `python scripts/snap.py [--tol 2]` | each boundary, transition, mark and cue start against the nearest measured event, in frames | exit 0 |
| doctor | `python scripts/doctor.py [--quick]` | one line each: timeline, chains, fonts, assets (`staticFile` paths and board images, exact case), registry, music, Remotion pins, final props, ffmpeg | exit 0 (WARN lines do not fail) |

Notes:

- flash-check approximates WCAG 2.3.1 [2] on downsampled frames. It is a screening tool,
  not a certified analyser, and it ignores viewing distance. Also avoid long flashing
  sequences (over about five seconds) even when each second is under the limit. The first
  film measured 29 transitions, 8 flashes and a worst second of 2 on its graded file.
- A flash count can change after the grade: contrast can push a transition that was just
  under a threshold over it. The numbers that count are on the graded file.
- black-check on the first film: cut-to-black frames and the last frame at max luma 0; the
  bars at max 5 outside the two rows that touch the picture (encoder ringing).

## 11. Accepted residuals

Some findings are real and still not worth fixing, or cannot be fixed without breaking
something that is measured. On the first film: a recap's torn cuts still interleaved slices
of one plate carrying a figure with slices of a plate carrying none, for 2 to 4 frames;
making those cuts whole would have broken flash safety. No numeral was formed from two
sources, so it was accepted.

To accept one:

1. Open the frames yourself and state the residual exactly: frames, what a viewer sees.
2. Say why it stays: what fixing it would break or cost.
3. Log it: `python scripts/log-decision.py "lead: accepted residual on <frames> (<id>):
   <what>; fixing it would <cost>; would fix by <how>"`.
4. Add it to the section log's Known issues and to "Known and accepted" in
   `docs/report.md`, with the file to open.

Never accept a residual that makes a fact read wrong, puts words on screen that are not the
cue's text, or breaks a flash limit.

## 12. Sources

1. mir_eval beat module (F-measure window 0.07 s), https://mir-eval.readthedocs.io/latest/api/beat.html ,
   from `dev/references/storyboard-music.md`.
2. Understanding Success Criterion 2.3.1: Three Flashes or Below Threshold, W3C WAI,
   https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html , from
   `dev/references/storyboard-music.md`.

The review method, the brief and the numbers from the first film come from *We Built a
Mind*: `docs/review/README.md`, the eight boundary reviews and the decisions log.
