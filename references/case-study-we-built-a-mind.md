# Case study: We Built a Mind

*We Built a Mind* is the first film made the way this skill directs films. Firelight
Innovations made it on 2026-10-12, in one afternoon, with one lead agent and a crew of
sub-agents. Read this file to know what a full build looks like and costs, and why the
rules in SKILL.md exist. The gotchas it met, one by one, are in `lessons.md`.

Everything here comes from the film's own records: its brief, its decisions log (about
140 timestamped lines), eight section logs, eight boundary reviews, one final review,
the session report and the to-do list. They are digested in
`dev/references/wbam-lessons.md`. Nothing was re-rendered for this file. People's names
are left out, and so are the film's figures and their publishers: the figures were
dated, and they move.

<!-- TOC -->
## Contents

- [The film](#the-film)
- [The eight sections](#the-eight-sections)
- [The transitions](#the-transitions)
- [The phases as they ran](#the-phases-as-they-ran)
- [The crew and the models](#the-crew-and-the-models)
- [Numbers](#numbers)
- [Review outcomes](#review-outcomes)
- [What went right](#what-went-right)
- [What it lacked](#what-it-lacked)
- [What this skill changed because of it](#what-this-skill-changed-because-of-it)
- [Where the rules in SKILL.md came from](#where-the-rules-in-skillmd-came-from)
- [Open at the end](#open-at-the-end)

<!-- /TOC -->

---

## The film

| | |
|---|---|
| Title | *We Built a Mind* |
| Made by | Firelight Innovations: an essay film for LinkedIn that doubles as a quiet signature for the studio |
| Made | 2026-10-12, about 11:40 to 15:45 local time |
| Thesis | Misalignment as doing what was asked. The film's own line: "It won't hate us. It will simply do exactly what we asked." |
| Arc | Awe, then dread, then responsibility. Not a horror trailer. |
| Length | 2:00.00: 3600 frames at 30 fps, 1920x1080, a 6 percent letterbox (65 px bars) |
| Audio | Music only, from frame 0, untouched: a copyrighted commercial track used for reference, not cleared. 102.448 s long, so the last 17.5 s of the film are silent on purpose. No voice-over, no sound effects. |
| The track, measured | Beat tracker 63.0 BPM; the real pump fitted at 0.9585 s a pulse; about 40 named musical marks |
| Words | 38 cues: 14 narration, 6 data, 5 slam, 4 stamp, 2 sub, 2 quote, 2 question, and one each of thesis, credit and logo |
| Deliverable | H.264 yuv420p, BT.709 limited range, AAC 48 kHz stereo, 225 MB graded |
| Stack | Remotion 4 (React 19, TypeScript), Three.js through `@remotion/three`, SVG filters, Canvas2D, GLSL; Python (numpy, OpenCV, Pillow, scikit-image, librosa) for plates and the music analysis; ffmpeg for the grade |

The brief was one document of about 250 lines, written by the person who commissioned
the film. It fixed the non-negotiables first ("one shot, no questions"; music only; a
finished, watchable mp4; keep the data architecture; keep the thesis), then the look of
each section, a menu of tools, four phases, stop conditions, and what the report must
say. Its rule of thumb became this skill's first rule: a film that exists beats a film
ten percent more beautiful that did not render.

---

## The eight sections

Every section is a different art style, built as its own component by its own agent.

| Id | Span (s) | Frames | Style | How it was made | ms a frame |
|---|---|---|---|---|---|
| 00-hook | 0.00 to 5.27 | 0 to 157 | A family archive that never existed: Super-8, VHS, Hi8, MiniDV | Four generated stills aged in Python, each at its format's native raster, scaled up last; baked to 164 WebP frames; the component is a player. The last second is a tracking tear with real holes in it. | 72 |
| 01-recognition | 5.27 to 15.33 | 158 to 459 | Synthetic media under forensic inspection | The archive made from noise and unmade again by a simulated diffusion sampler; a tracked face mesh (corners, Delaunay, optical flow; no landmark model); readouts that measure the plate under them | 51 to 91 |
| 02-human-cost | 15.33 to 28.93 | 460 to 867 | Hand-drawn: charcoal, ink, erasure, cut paper | Every frame a baked sheet from a Python stroke engine, on twos, with the words drawn in; a charcoal rotoscope of a public figure from a broadcast interview | 113 to 127 |
| 03-acceleration | 28.93 to 49.40 | 868 to 1481 | Kinetic type and data on the pump | Pure code, no assets: five bars of music, five typographic ideas, every move driven by the measured kick and bass | 30 to 42 |
| 04-bargain | 49.40 to 67.17 | 1482 to 2014 | Warm gouache utopia against a cold wireframe of the same land | One scene file, two renderers (a Python gouache painter and a Three.js wireframe) sharing one pinhole camera, so the ridges register across a paper tear | 116 to 132 |
| 05-build-dread | 67.17 to 93.17 | 2015 to 2794 | Procedural 3D: factory, ouroboros, tower, nave, wall of names, the eye | Six Three.js shots with hard cuts on the music; no plates | 55 to 80 |
| 06-reckoning | 93.17 to 99.87 | 2795 to 2995 | Overload: every style back at once, four words, hard cut to black | The film recut backwards from 38 plates rendered out of the finished film, levelled for flash safety; a mosaic that divides to about a thousand cells | 39 to 83 |
| 07-outro | 99.87 to 120.00 | 2996 to 3599 | Silence, type, the Firelight mark | Serif type on true black and a per-pixel ember; frames 2996 and 3599 pure black by construction | 32 to 34 |

Render cost is wall time per frame at full resolution with four tabs, against a budget
of 1500 ms. The worst single span was 155 ms, a blur filter during a reel spin in S3.

Baked assets: S0 33.7 MB, S1 about 100 MB, S2 78.9 MB, S4 4.2 MB, S6 23 MB; S3, S5 and
S7 none. The budget was 250 MB a section. Plate builds took about 90 s (S0), about 5
minutes in three scripts (S1), about 6 minutes on one core (S2), under a minute (S4)
and about 10 s (S6).

---

## The transitions

Seven named devices joined the eight sections, none used twice, plus an opening and a
closing. During a window only the owner is mounted, and it draws its neighbour's live
render itself. Each boundary sits on a measured event in the track.

| Id | Name | Owner | Window (frames) | Cut frame | Lands on |
|---|---|---|---|---|---|
| t-start | Projector start | 00-hook | none | 0 | the first frame |
| t-00-01 | Tracking tear | 00-hook | 130 to 163 | 158 | the strongest transient in the track (5.27 s) |
| t-01-02 | The hand takes it back | 02-human-cost | 445 to 481 | 460 | a structure change (15.33 s) |
| t-02-03 | Negative snap | 03-acceleration | 865 to 867 | 868 | the drop (28.93 s) |
| t-03-04 | Horizon opens | 04-bargain | 1478 to 1507 | 1482 | a bright burst (49.40 s) |
| t-04-05 | Fall-through | 05-build-dread | 2003 to 2014 | 2015 | a hit (67.17 s) |
| t-05-06 | Seizure | 06-reckoning | 2795 to 2823 | 2795 | the overload (93.17 s) |
| t-06-07 | The cut | 07-outro | none (hard cut) | 2996 | the last pulse (99.87 s) |
| t-end | Ember out | 07-outro | none | 3599 | the last frame |

Every boundary also had a line of exact obligations, repeated on both sections' pages
of the style bible. Three examples: from 48.9 s S3 holds `#0a0a0a` with one 2 px
`#f4f1e8` line on rows 539 and 540, and S4's opening starts as that line. S5's eye is
centred on (960, 540) with no words after frame 2787, because S6 seizes it. S6's frame
2995 is bright and full; the outro's frame 2996 is `#000`. Every one of these promises
held in the final film, and several were asserted pixel for pixel on lossless frames.

---

## The phases as they ran

| Phase | Clock | Who | What happened |
|---|---|---|---|
| 0. Handoff | before 11:40 | the commissioner | The brief above |
| 1. Research, music, bible, kit | 11:41 to about 12:45 | lead, cheap research agents | `git init` and a baseline commit (the project had no repository). About nine technique briefs of 10 to 20 references each, and a fact-check. The lead ran the music analysis itself and re-timed the whole film to the measured track at 12:16; the script was reworked and the facts corrected the same minute. Then the kit, the timeline schema, the check-render tools, 22 vendored font families, the style bible, the transitions table and a build guide. |
| 2. Build | about 12:45 to 13:50 | eight builders, one per section, in one working tree | Each owned its section folder, plates, scripts and log. S6 waited until the other seven were integrated, because its plates are frames of the finished film. The lead patched the kit three times while they worked (12:43 frame snapping, 13:19 colour space and the grade gate, 13:34 private bundles) and raised the font timeout at 13:46. Then a half-size pass of the whole film. |
| 3. Boundary review | 13:58 to 14:24 | eight reviewers, one per boundary, read-only | Frame dumps around each cut and a fixed template. Fix rounds went back to the same builders: S0, S4 and S7 by 14:18; S6 from 14:25 to 15:10. |
| 4. Final | 15:22 to 15:40 | lead, one fresh reviewer | Full render 2 m 31 s, grade 59 s, measured checks. The reviewer saw only frames of the graded file. After the fixes: S6's plates rebuilt from the changed film, render 2 m 13 s, grade 57 s, checks re-run. The final review was not repeated. |
| 5. Report | 15:40 to 15:45 | lead | Session report, a to-do list with the polish backlog, the project's status notes |

About four hours of wall clock from first decision to report. The parallel build itself
took about an hour.

---

## The crew and the models

| Agent | Count | Model | Job | What it got wrong or could not do |
|---|---|---|---|---|
| Lead | 1 | Opus | Music map and re-time, script and facts, kit, style bible, integration, renders, grade, measured checks, triage, report | Three kit and pipeline bugs (frame snapping, colour space, grade gate) were found by builders, not by the lead |
| Research | about 9 briefs | Haiku, with a fixed document template and a JSON schema | Technique briefs and a fact-check | The fact-check ran out of web-search budget (shared by every agent in the turn) and could not open several news sites; four of the script's figures and quotes came back unverifiable or misworded |
| Section builders | 8 | Opus, named background agents | One section each, with a log | Each of three wrote its own pass-through check harness; cue windows drifted from what was drawn; several small type sizes failed on a phone |
| Boundary reviewers | 8 | Sonnet | One boundary each, frames only | Judged stills, not motion or sound, as briefed |
| Final reviewer | 1 | Opus, fresh, told not to read the logs | The graded file, as frames | No motion and no sound; sampling every half second missed two seven-frame words. It said so. |

In all, about 26 sub-agents worked for the lead. Builders were named agents, not a
Workflow, so that a fix round could go to the same agent with its context intact; four
of the eight were resumed once. The commissioner's standing rule (a mid model for
sub-agents wherever the brief was silent) and the brief (strong builders and a strong
final reviewer) were reconciled in the decisions log; research moved to the cheapest
tier at the commissioner's request during setup.

---

## Numbers

| What | Value |
|---|---|
| Final render | 2 m 31 s, then 2 m 13 s after the fixes (about 42 and 37 ms a frame over 3600 frames) |
| Grade | 59 s, then 57 s |
| File sizes | ungraded 199 MB, then 201 MB; graded 223 MB, then 225 MB |
| Flash check, whole graded film | PASS: 29 luminance transitions, 8 flashes, worst one-second window 2, limit 3, no saturated red. This used the broadcast area rule (a quarter of the screen); the small-area reading for the web (`--area 0.03`) was not run. |
| Flash check, S6 (92.0 to 100.6 s) | PASS: 3 flashes, worst second 2 |
| Black check | PASS: frames 2996 to 3026 and frame 3599 at luma 0; letterbox bars at most 9 (first render) and 5 (second) of 255, outside the two rows that touch the picture |
| Determinism | Two renders of the same frames without text were bit-identical; text edges differed by at most 3/255 |
| Paper trail | about 140 decision lines, 8 section logs (about 1,000 lines), 8 boundary reviews, 1 final review, 1 session report |
| Fonts | 22 Google Fonts families vendored; the render needed no network |
| Cost | One Max-plan afternoon. The 5-hour usage window ended at 77 percent used; the weekly all-models limit went from about 15 to 19 percent. No per-agent tokens were recorded. |

---

## Review outcomes

### The boundary reviews

Zero blockers. Four PASS, four PASS WITH FIXES, five should-fix items in all, each fixed
by the owning builder in one round.

| Boundary | Verdict | What the review found | What was done |
|---|---|---|---|
| Start and end | PASS WITH FIXES | The closing fade was front-loaded: full, then gone in about 8 frames, with steps of 80 and 69 levels | Linear over 13 frames, the ember last; small type up one step for phones |
| Tracking tear | PASS WITH FIXES | S1 read as black in the gaps for 20 frames; from frame 137 the tear read as a web glitch, not tape | Rebuilt as one picture losing tracking; S1 lifted in the gaps |
| The hand takes it back | PASS | Nice-to-haves only | none |
| Negative snap | PASS | The numerals come within 2 to 8 px of the bar on the hit frame; left as intended | none |
| Horizon opens | PASS WITH FIXES | The eyelid edge read as an angular polygon with a screen glow | A wet brush edge; the ignition spread over four frames; falling strips kept off the fact |
| Fall-through | PASS | The visible fall is about 8 frames; the dump ended two frames before the next line | none |
| Seizure | PASS | Nice-to-have: blocks at the frame edge on frames 2817 to 2823 | Fixed in S6's round (wider overscan) |
| The cut | PASS WITH FIXES | The last word fused with the plate's own caption | Fitted above the caption; the push ends on the hook's own framing |

### The final review

Verdict: SHIP WITH FIXES. One broken item, eight polish items.

- **Broken, fixed by the lead.** A grid of 100 cells over "fewer than 1 in 5" lit 18
  cells in a framed row of 20 and drew the other 82 as faint outlines. On a phone it read
  as a meter nine tenths full: the opposite of the fact. It had passed its builder, the
  lead and eight boundary reviewers. The empty cells became grey tiles and the frame
  went; the count did not change.
- **Three open checks, settled by the lead** on frames of the graded file: two slam words
  that fell between the reviewer's samples were there; the three inverted frames of the
  negative snap were there; the mark faded evenly to black.
- **Polish: one of eight taken.** The line that sets up the thesis was made heavier and
  larger. The other seven went to the backlog with the file to open for each, because
  each was a design call, a re-layout, or tied to a cut list tuned for flash safety.
- The reviewer also reported every word on screen exact to its cue, attributions and
  sources included; no test card or dev read-out on any frame; the weakest stretch a line
  about people over identical pictograms; the best boundary the horizon opening; and that
  the film earns its last line.

---

## What went right

1. **The film was data.** `data/timeline.json` drove every section, the grade gate, the
   checks and the frame dumps. Re-timing the whole film was a data edit plus rebuilds.
2. **The cut followed the measured track.** The guessed cut had missed the real events
   by 0.5 to 1.5 s; after the analysis every boundary sat on a measured event.
3. **One section, one component, one folder, one agent.** Eight builders worked in one
   tree with no merge fights, and the lead could swap any section for a test card.
4. **The transition owner model and a handshake of exact pixels.** Exactly one side owned
   every pixel of every window, and every promise in the table held.
5. **Floor first.** Builders shipped a complete, valid range before they polished. Every
   section arrived.
6. **Looking was a deliverable.** Overview sheets, boundary sheets and clean full-size
   stills per section. The best results came from builders iterating on every-frame
   sequences.
7. **One named device per boundary, none repeated.** It forced seven different ideas,
   and gave reviewers a promise to check against.
8. **Boundary reviews with every frame.** Cheap, parallel, and they found real faults.
9. **A fresh final reviewer.** It caught the only broken item in the film, which every
   earlier pair of eyes had passed.
10. **Measured checks as numbers.** "Frame 2996 is pure black" was a measurement, not an
    opinion.
11. **Heavy work pre-rendered.** Per-pixel looks were made once in Python and played
    back as images, so the render stayed under three minutes.
12. **Flash safety as a design input.** The brief asked for strobe. The lead capped it at
    three flashes a second and no saturated red, and the S6 builder designed its cutting
    from the measured numbers.
13. **Truth in data.** Readouts measured the picture under them, counters never counted
    through unpublished figures, and no chart compared things its sources do not.
14. **Grade once, at the end, gated by frame.** One ffmpeg pass, off for the black outro,
    with the letterbox repainted.
15. **A decision log that costs one line,** and a "Requests to lead" heading in every
    section log. The requests are how the three pipeline bugs were found.
16. **A report that said what was not done:** the open rights questions, the backlog, and
    that no review used sound.

---

## What it lacked

**No ideation stage.** The film started from an existing essay and a track. There were
no alternative treatments to choose between and no scoring against the brief; the style
bible was the first creative document.

**No storyboard or animatic.** Builders worked from a style-bible page and a timeline.
The first time anyone saw the film as a film was the integration pass. The beat and
script locks were lifted during the run, and research written before the re-time kept
stale timestamps.

**Reviews on stills.** All nine reviews read frames. Nobody judged movement, rhythm, or
how a transition feels at speed.

**No listen with sound.** Sync was set from measured beats and never checked by ear. No
agent can hear, and no person watched the graded film with sound before the report.

**A late fact-check.** The script was written before the facts were checked. Four claims
failed; the check hit a shared search limit and blocked sites; the lead spot-checked
three primary sources itself.

**No cost tracking.** Only usage-window percentages were recorded: no tokens and no wall
clock per agent, no budget per phase.

Also missing: rights and likeness were decided at the end; three builders each patched
the same harness gaps; the final review sampled by the clock, not by cue, and was not
repeated after the fixes; there was no cut list, so "ship a simpler version" did not say
what to drop first.

---

## What this skill changed because of it

| The first film lacked | This skill does | Where |
|---|---|---|
| An ideation stage | About eight one-line options, then three concepts and a wildcard, scored with a Pugh matrix against two datums, ties broken in Murch's order; a treatment and a script with reading times; a concept gate | SKILL.md, Phase 1; `scripts/workflows/concepts.js`; `references/01-intake-and-ideation.md` |
| A storyboard and an animatic | A style bible with minimum type sizes, a transitions table, timeline v1, thumbnails, a beat board, `data/storyboard.json`, a cut list, the animatic on the real track (`npm run animatic`), and the animatic sign-off as the gate before any build | SKILL.md, Phase 3; `references/03-storyboard.md` |
| Review of motion | `motion-check.py` (freezes, jumps, one-frame pops), a motion trace and a phone-size sheet in every `review-frames.mjs` window | SKILL.md, Phase 5 |
| A listen with sound | `sync-check.py` (picture change against onsets), and a human watch with the sound on as the last gate, its verdict in the report | SKILL.md, Phases 5 and 6; `templates/report.md` |
| An early, deep fact-check | Facts as their own step before the storyboard gate: two independent checks per `data` or `quote` cue, a verdict, an as-of date and a re-verify-by date | SKILL.md, Phase 2; `scripts/workflows/fact-check.js`; `docs/research/facts.md` |
| Cost tracking | A cost estimate at intake, the usage window read before each fan-out, tokens and wall clock per agent in the report | SKILL.md, "Before you start"; `templates/report.md` |
| Rights at the start | A rights register from intake, filled with `log-asset.py`; the Remotion licence check | SKILL.md, Phase 0; `templates/rights.md` |
| A harness that shows every frame | `shots.mjs --through`, `--png`, `--timeout`, and a private bundle per process | SKILL.md, Phase 4 |
| Plates that know they are stale | `data/chains.json`, `chain.py`, and `doctor.py` before every full render | SKILL.md, Phases 4 and 5 |
| A final review by cue, repeated after fixes | `film-frames.py` samples every cue and transition and adds phone-size sheets; `diff-frames.py` and `final-review.js` in `diff` mode | SKILL.md, Phase 6 |
| Drawn windows apart from readable ones | `shown` on a cue | `references/03-storyboard.md` (timeline schema) |
| Ids without content | Role-based cue ids (`stamp-1`, `slam-2`); `check-timeline.py` warns on any other | `references/03-storyboard.md` |
| Installs, downloads and publishing with no yes | Ask the user before any install, download or public step; one yes at intake can cover a named class | SKILL.md, rule 11 and Phase 0 |
| A queue for requests | Requests to lead with an owner and a status | `templates/report.md` |
| A cut list | An ordered cut list per section at storyboard time | `docs/storyboard.md` (`templates/storyboard.md`) |

---

## Where the rules in SKILL.md came from

1. **Floor first.** The brief's own line, and it held: every section arrived, and the
   fallbacks were built before the bold versions.
2. **Cut to measured music.** The guessed cut missed by up to 1.5 s; the measured one
   put the reveal, the drop, the overload and the cut to black on real events.
3. **One owner per file.** Eight builders in one tree with no conflicts; anything outside
   a builder's paths went to the lead as a request.
4. **Look at every frame you claim.** The build guide made looking a deliverable, and the
   best frames in the film came from builders reading every-frame sequences.
5. **Measure what can be measured.** All three pipeline bugs were found by measuring
   pixels, not by looking at stills.
6. **Fresh eyes review.** The one broken item passed its builder, the lead and eight
   boundary reviewers, and the first reader with no priors caught it.
7. **Every frame is a pure function of its frame number.** Parallel tabs never produced a
   flicker; frames without text were bit-identical across renders.
8. **Log every call.** About 140 one-line decisions became the session report and let
   any later session pick the film up.
9. **Rights and safety are craft.** The facts rework, flash safety designed from numbers,
   and the rights questions that were still open at the end.
10. **Spend where it shows.** Cheap research, strong builders and judges, mid reviewers;
    the fact-check that needed more than the cheap tier it got; and the pure-code section
    that a cheaper model could have built.
11. **Ask before anything is installed, downloaded or made public.** The brief said "one
    shot, no questions". Blender was installed in the background during setup (L53), and
    the questions about the track and a traced likeness reached the commissioner only in
    the report (L74).

---

## Open at the end

What the report left for the commissioner before a public post:

- **Music rights.** The track is copyrighted and not cleared; a public upload may be
  muted or flagged.
- **A traced likeness.** S2's charcoal head is traced from a broadcast interview. The
  source clip stayed out of the repository and was never shown, but whether a drawn
  likeness traced from broadcast footage is acceptable for a company post was left to
  the commissioner. A typographic fallback was planned and not built.
- **Figures to re-verify on the day of posting.** One of them moves every quarter.
- **Generated faces.** Every face in the hook and S1 is generated, and the film says so
  on screen.
- **A watch with the sound on.** Nobody had done it.
- **A polish backlog** of twelve items, each with the file to open.
