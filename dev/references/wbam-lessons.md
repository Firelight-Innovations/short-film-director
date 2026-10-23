# Lessons from We Built a Mind

*A digest of the first film made the way this skill directs films: a 2:00, 1920x1080, 30 fps music film in Remotion, eight sections in eight art styles, one lead agent plus a crew, finished in about four hours of wall clock on 2026-10-12. Source: the project's brief, build guide, style bible, transitions table, decisions log (143 lines), eight section logs, eight boundary reviews, one final review, and the scripts and kit. Nothing here was re-rendered. Names of people, sources and figures are left out on purpose; where a fact mattered, only its category is given. "The lead" is the Claude session that directed; "S0 to S7" are the sections 00-hook to 07-outro.*

---

## The pipeline as it ran (phases, who did what, which model, how long, numbers)

All clock times are local, 2026-10-12, read from the decisions log. Phase lengths are approximate.

| Phase | Who (model) | Window | What happened | Output |
|---|---|---|---|---|
| 0. Handoff | The human wrote one brief (about 250 lines) | before 11:40 | Non-negotiables ("one shot, no questions", "a film that exists beats a film that is ten percent more beautiful and did not render"), the look of each section, tool menu, four phases, report spec | `docs/HANDOFF-opus-showcase.md` |
| 1. Research, music, bible, kit | Lead (Opus) plus Haiku research agents, one per brief | 11:41 to about 12:45 (1 h) | `git init` and baseline commit (the project had no repo). Eight technique briefs of 10 to 20 references each plus a fact-check, all in `docs/research/`. The lead did the **music analysis itself** (librosa) and **re-timed the whole film** to the measured track at 12:16. Script reworked and facts corrected the same minute. Kit, timeline schema v2, check-render tools, vendored fonts, style bible, transitions table written | `data/beats.json`, `data/timeline.json` v2, `src/kit/`, `docs/style-bible.md`, `docs/transitions.md`, `docs/BUILD-GUIDE.md`, `docs/research/*` |
| 2. Build | Eight named **Opus** builders, one per section, in parallel, one working tree | about 12:45 to 13:50 (1 h wall clock) | Each owned `src/sections/<id>/`, `assets/footage/<id>/`, `scripts/<id>/`, `docs/sections/<id>.md`. S6 had to wait until the other seven were integrated because its plates are frames of the finished film. Lead patched the kit three times while they worked (12:43, 13:19, 13:34) | eight `Section` components, plates, logs; lead rendered a half-size `out/pass1.mp4` |
| 3. Boundary review | Eight **Sonnet** reviewers, one per boundary (7 cuts plus start/end), read-only | 13:58 to 14:24 | Frame dumps around each cut, a fixed review template. Result: 0 blockers; 4 PASS, 4 PASS WITH FIXES. Fix rounds went back to the **same** builders (S0, S4, S7 by 14:18; S6 round 14:25 to 15:10) | `docs/review/transition-*.md` |
| 4. Final | Lead renders and measures; one **fresh Opus** reviewer | 15:22 to 15:40 | Render 2 m 31 s, grade 59 s. Measured checks. Reviewer saw only frames of the graded file. Verdict SHIP WITH FIXES: 1 broken, 8 polish, 1 polish taken. Lead fixed, rebuilt S6 plates from the changed film, rendered again (2 m 13 s, grade 57 s) and re-ran the measured checks. The final review was **not** repeated | `docs/review/final.md` |
| 5. Report | Lead | 15:40 to 15:45 | Session report, TODO with a polish backlog, CLAUDE.md status | `docs/session-report-*.md` |

### Agent roster

| Agent | Count | Model | Job | What it got wrong or could not do |
|---|---|---|---|---|
| Lead | 1 | Opus | Music map, re-time, script and facts, kit, style bible, integration, renders, grade, measured checks, triage, report | Three kit/pipeline bugs (frame snap, colour space, grade gate) were found by **builders**, not by the lead |
| Research | about 9 briefs | Haiku (cheap, fixed doc template and JSON schema) | Technique briefs and a fact-check | The fact-check ran out of web-search budget (the limit was shared by all agents in the turn), could not open several news sites (HTTP 451 and 403), and marked claims "secondary". Four of the script's figures and quotes came back unverifiable or misworded |
| Section builders | 8 | Opus, named so they could be resumed | One section each, with a log | Each wrote its own pass-through check harness because the shared one could not show frames inside a neighbour's window; cue windows drifted from what was drawn; several small type sizes failed on phones |
| Boundary reviewers | 8 | Sonnet | One boundary each, frames only | Judged stills, not motion or sound (as briefed) |
| Final reviewer | 1 | Opus, fresh | Whole graded file as frames | No motion, no sound; sampling every half second missed two seven-frame words; said so honestly |

Standing rule used where the brief was silent: Sonnet for sub-agents. Builders were named agents and not a Workflow so that a fix round could be sent to the same agent with its context intact (four of eight were resumed once).

### Numbers worth knowing

- **Film:** 120.00 s, 3600 frames, 30 fps, 1920x1080, H.264 yuv420p BT.709 limited range, AAC. 8 sections, 9 transition rows (7 named devices plus a start and an end), 38 cues (14 narration, 6 data, 5 slam, 4 stamp, 2 sub, 2 quote, 2 question, 1 each thesis, credit, logo), about 40 named musical marks. Music 102.448 s; the last 17.5 s is silence on purpose.
- **Music map:** tracker tempo 63.0 BPM (beat period 0.952 s) but the real pump period fitted at 0.9585 s over two stretches. The tracker drifted up to 0.1 s on a pad with no drums, so the pump grid was fitted directly to the onset envelope and each pulse snapped to the nearest real onset within 0.06 s.
- **Render speed (ms per frame, wall, 4 tabs, budget 1500):** S0 72, S1 51 to 91, S2 113 to 127, S3 30 to 42 (worst 155 on a blur), S4 116 to 132, S5 55 to 80, S6 45 to 83, S7 32 to 34. Everything heavy was pre-rendered in Python.
- **Final render:** 2 m 13 s to 2 m 31 s; grade 57 to 59 s; 199 to 225 MB.
- **Measured checks on the graded file:** flash-check PASS (29 luminance transitions, 8 flashes, worst second 2, limit 3, no saturated red). Black-check PASS (cut-to-black frames and last frame max luma 0; letterbox bars max luma 5).
- **Cost:** one Max-plan afternoon. The 5-hour window ended at 77 percent used; the weekly all-models limit went from about 15 to 19 percent across the build. No per-agent token accounting was kept.
- **Paper trail:** 143 timestamped decision lines, 8 section logs (about 1,000 lines), 8 boundary reviews, 1 final review, 1 session report.

---

## What worked (and why), 15+ items

1. **The timeline is data and the single source of timing.** `data/timeline.json` (sections, marks, transitions, cues with exact words) drives every component, the grade gate, the checks and the frame dumps. Re-timing the whole film at 12:16 was a data edit plus rebuilds, not a rewrite. Cue roles (`stamp slam narration sub quote data thesis question credit logo`) let a builder decide how a line looks without editing words.
2. **Cut to a measured track, not an estimated one.** The lead ran its own librosa analysis (beats, onsets, hits, structure novelty, loudness landmarks, per-frame energy by band) and moved every boundary onto a measured event. The old hand-guessed cut missed the real events by 0.5 to 1.5 s. Doing this itself, not delegating, was right: the re-time depended on it being exactly right.
3. **Fit a grid where the tracker drifts.** For a pumped pad the beat tracker was off by up to 0.1 s; fitting period and phase directly against the onset envelope and snapping each pulse to a real peak removed accumulating error. Without that, the last pulse in a stretch would have missed by two frames.
4. **One section = one component = one folder = one agent.** `Section` receives `{from, to, prev?, next?}`. Ownership by path meant eight builders worked in one tree with no merge fights and the lead could swap any section for a test card.
5. **A solo harness per section.** Each section has `entry.ts` registering composition `Solo`, so a compile error in one section cannot break another's check renders, and neighbours appear as labelled test cards in their own palette.
6. **The transition-owner model.** During a window only the owner is mounted and it draws its neighbour's live render as a React node. No pre-render dependency between sections, any mask/filter/transform device possible, and exactly one side responsible for every pixel.
7. **A handshake table of exact pixels and frames.** "S3 holds `#0a0a0a` with one 2 px line `#f4f1e8` at rows 539 and 540 from 48.9 s" was something both builders could build against and a script could assert pixel for pixel. Every one of these "what each side owes the other" lines held in the final film.
8. **Floor first, then depth, then edges, then cost, then stop.** Builders shipped a complete valid range before polishing; the brief said every bold choice gets a working fallback before the bold version is attempted. No section failed to arrive.
9. **"Open the images and look."** The build guide made looking a deliverable: overview sheet, boundaries sheet, three clean full-size stills per section. The best outcomes (S4's horizon, the S7 mark) came from builders iterating on every-frame sequences.
10. **One named device per boundary, none repeated, with a "lands on" column.** It forced seven different ideas, and the reviewers had a concrete promise to check each against ("is it the named device or a generic one?").
11. **Boundary reviews with every frame.** Frame dumps from 12 frames before a window to 12 after, 24 tiles a sheet at 480 px, plus three full-size frames at the cut. Cheap (Sonnet), parallel, and found real problems (a tear that read as web glitch, an angular eyelid, a front-loaded fade).
12. **A fresh final reviewer who is told not to read the logs.** The one broken item in the film (a chart that read as the opposite of its fact) had passed every builder, the lead and eight boundary reviewers. A reviewer with no priors caught it in the first pass.
13. **Measured checks as numbers.** Flash safety, cut to black, last frame, letterbox bars, lossless pixel assertions on the contract frames. "Frame 2996 is pure black" became a number, not an opinion.
14. **Pre-render the per-pixel work, play it back as images.** Interlace, tape chroma, charcoal strokes, gouache and face tracking were done once in Python and played with `<Img>` at 50 to 130 ms a frame. The render stayed under 3 minutes while the visual range stayed wide.
15. **One scene, two renderers.** `scene.py` defined a landscape once; a Python painter and a Three.js wireframe both read it and shared one pinhole camera, so the ridges registered across the tear.
16. **Flash safety as a design input.** The brief asked for strobe; the lead capped it at three flashes a second and no saturated red, then the S6 builder designed the cutting from the measured numbers (level band, torn cuts, a dividing mosaic) instead of testing after the fact.
17. **Truth in data.** Readouts measured the plate under them; counters never counted through unpublished figures; charts were refused where two sources measure different things. The film made no claim that a source did not.
18. **Grade and grain once, at the end, gated by frame number.** Sections own their style's texture; the unifying pass is one ffmpeg call that switches itself off for the silent black outro and repaints the letterbox.
19. **A decision log that costs one shell line.** `scripts/log-decision.sh "who: what, and why"` produced a 143-line audit trail that became the session report. Builders also reported cross-cutting bugs under "Requests to lead", which is how the three pipeline bugs were found.
20. **Fixed log headings and a fixed review template.** What it is, Shots, Transitions, Assets, Decisions, Cost, Known issues, Requests to lead; reviews end with Verdict, Blockers, Should fix, Nice to have, Looked at, and a three-line final message. The lead could triage eight reports in minutes.
21. **Fonts vendored, no network at render time.** 22 Google Fonts families downloaded once into `assets/fonts` and loaded from disk.
22. **Determinism rules stated up front.** "A frame is a pure function of its number" with the banned list (state, `Math.random`, `Date`, CSS animation, `requestAnimationFrame`, `useFrame`) meant parallel tab rendering never produced a flicker. Two renders of the same non-text frames were bit-identical.
23. **Phone-size thinking in the review.** The tagline's x-height was worked out in millimetres on an upright phone; the sizes went up one step. The one broken item was a phone-size failure.
24. **Lifting locks in the open.** When the human lifted the beat-lock and script-lock mid-run, the lead logged it, re-timed, and updated the docs rather than half-obeying both. The facts guardrail stayed locked.
25. **A report that says what was not done.** The session report lists known-and-accepted items, the rights and likeness questions, and that no review used sound. That honesty is what makes the next pass cheap.

---

## Gotchas and their fixes, 25+ items, each: symptom, cause, fix, where it lives in the code

### Time and frames

**G1. A section appears one frame late.**
- Symptom: the cut to black landed a frame late; sections' first frames showed the previous section on frames 158, 2015, 2795 and 2996.
- Cause: `timeline.json` stores seconds to four decimals. 99.8667 is a hair after frame 2996 (2996/30 = 99.86666...), so a comparison in seconds put the frame on the earlier side of the boundary.
- Fix: snap every time to its exact frame when the timeline loads, and compare whole frames in the lookups; do the same in `Grain`.
- Where: `src/timeline/timeline.ts` (`snap`, `frameOf`, `sectionAt`, `cuesAt`, `transitionAt`), `src/components/Grain.tsx` (`amountAt`), BUILD-GUIDE "Compare frames, not typed seconds".

**G2. A literal in a section is one frame late.**
- Symptom: `t >= 5.2667` fires on frame 159, not 158.
- Cause: typed seconds are not frame-aligned.
- Fix: compare `frame >= 158`, `frame >= F(5.2667)`, or use the kit's snapped `cue(id).from` and `mark(name)`. S5 puts every window in a `times.ts` of frame numbers.
- Where: `src/sections/05-build-dread/times.ts`; `docs/BUILD-GUIDE.md`.

**G3. A frame time that is half a frame.**
- Symptom: a mark at 16.0833 s sits between frames.
- Cause: marks were measured in seconds and never audited against the frame grid.
- Fix: snap on load (G1) and move the mark to frame 482; log it.
- Where: `data/timeline.json` marks; decision at 12:43.

**G4. Cue windows and drawn windows disagree.**
- Symptom: a quote cue ended at 28.70 s while its words had to stay to 28.93; a lower-third cue ran to 15.0 s but nothing was allowed on screen from 14.87; a data cue was drawn one frame before its `from`; two words held 3 and 5 frames past `to`.
- Cause: a handshake requirement or a pump bar start won over the cue window, and nothing compared them.
- Fix: change the cue `to` where the handshake is the truth; otherwise log it. Better: separate the "readable window" from the "drawn window" in the schema and assert their relation in a script.
- Where: `data/timeline.json` (`amodei`, `handed`, `invest-us`); `docs/sections/01-recognition.md`, `03-acceleration.md` "Requests to lead".

**G5. A Three.js canvas ignores the film clock.**
- Symptom: a 3D shot froze or ran on the wrong frame when S6 replayed or pinned S5.
- Cause: react-three-fiber renders in its own React root, so the kit's `FilmClockProvider` context does not reach inside `<ThreeCanvas>`.
- Fix: call `useFilmTime()` outside the canvas and pass `frame` in as a prop; drive every object from that prop. S6 replays S5 through `FilmClockOverride`.
- Where: `src/sections/05-build-dread/stage.tsx`, `src/kit/time.tsx` (`FilmClockOverride`), `src/sections/06-reckoning/Seizure.tsx`.

**G6. A neighbour that pins or offsets my clock breaks my picture.**
- Symptom: during a window the owner may freeze or replay a section; a section playing an image sequence from `useCurrentFrame()` showed the wrong plate.
- Cause: the sequence index was tied to a local clock.
- Fix: play plates by the film clock through `Freeze`, one plate frame per film frame.
- Where: `src/sections/01-recognition/Plate.tsx`, `clock.ts`.

### Encode, colour and grade

**G7. Letterbox bars came out grey (RGB 16) against picture black 0.**
- Symptom: bars and true black did not match after the grade; the outro's "pure black" was not.
- Cause: Remotion's default wrote full-range `yuvj420p` tagged `bt470bg`; `grade.sh` then re-tagged it without converting.
- Fix: render with `--color-space=bt709` and `--jpeg-quality=95` (also in config); `grade.sh` first converts to limited-range bt709, and at the end forces the tags with `setparams`.
- Where: `package.json` `render:final`, `remotion.config.ts` (`setColorSpace("bt709")`), `scripts/grade.sh`, `scripts/07-outro/encodecheck.mjs` (proof).

**G8. Grain on the first black frame.**
- Symptom: frame 2996 was not black after the grade.
- Cause: `enable='lt(t,99.8667)'` is still true on frame 2996 (same rounding as G1).
- Fix: gate on the frame number, `lt(n,BLACK_F)`, with `BLACK_F` read from `timeline.json`.
- Where: `scripts/grade.sh` (`BLACK_F`, `ON`), proof in `scripts/07-outro/gradecheck.sh`.

**G9. Grain and lifted gamma over a black outro; grain in the bars.**
- Symptom: black turned to banded grey mush; grain in the letterbox read as a fault.
- Cause: the grade ran over everything.
- Fix: grade, vignette and noise are all `enable`d only before the outro, and the two bars are repainted black after the noise (`drawbox`).
- Where: `scripts/grade.sh`.

**G10. The vignette looked like a dirty lens.**
- Symptom: white fields (S3) and the painted sky (S4) showed a heavy corner.
- Cause: `vignette=PI/5` put the corner at 40 percent.
- Fix: `PI/9` (corner near 80 percent); contrast 1.05, saturation 0.97, gamma 0.985, `noise=alls=5:allf=t+u`.
- Where: `scripts/grade.sh`; decision at 12:31.

**G11. The faintest ember glow disappeared.**
- Symptom: light below about 4/255 was lost and the rest quantised in 8 px blocks.
- Cause: JPEG frames followed by two H.264 passes.
- Fix (not taken): PNG frames for the final render would keep it. Accepted because it is invisible at true brightness.
- Where: `docs/sections/07-outro.md` Known issues; `scripts/07-outro/encodecheck.mjs`.

**G12. Text edges differ between two renders of the same frame.**
- Symptom: 200+ pixels differ by up to 3/255 on text; on four held frames of a scaled image, mean difference 0.5/255.
- Cause: Chromium's rasteriser and image resampling are not bit-stable. The frame functions were pure.
- Fix: determinism checks use a stated tolerance (at most 3/255 on at most 0.05 percent of pixels, reported); assert exactly only on frames that contain no text.
- Where: `scripts/03-acceleration/check_frames.py`; `docs/sections/06-reckoning.md` Known issues.

### Harness and machine

**G13. Two check runs destroyed each other.**
- Symptom: 16 of 22 stills failed on the film target while a builder rendered the same target.
- Cause: the bundle directory was named after the target and wiped at start.
- Fix: `--bundle <name>` gives a private directory `out/.bundle/<name>`. `review-frames.mjs` and `s6-plates.mjs` each pass their own.
- Where: `scripts/shots.mjs` (`bundleDir`), `scripts/review-frames.mjs`, `scripts/s6-plates.mjs`.

**G14. Bundling copied the whole asset tree every time.**
- Symptom: slow starts as `assets/` grew past a gigabyte.
- Cause: `bundle()` copies the public dir.
- Fix: bundle with an empty public dir, then junction `./assets` into the bundle. A `dropJunction` helper removes the junction before any recursive delete so the delete can never walk into `assets/`.
- Where: `scripts/shots.mjs` (`emptyPublic`, `dropJunction`).

**G15. The solo harness cannot show a section inside a neighbour's window.**
- Symptom: frames 130 to 163, 445 to 481, 2003 to 2014 and 2795 to 2823 could not be seen from the section that supplies them.
- Cause: neighbours are test cards, and a test card that owns a transition never draws `prev` or `next`.
- Fix (workaround, written three times by three builders): a pass-through entry that registers owners which draw the live section full-frame in magenta ("nobody drew this"), plus a copy of `shots.mjs` that bundles it. The proper fix is a `--through` option in the main script.
- Where: `src/sections/01-recognition/window.entry.tsx`, `04-bargain/window.entry.tsx`, `05-build-dread/tail.entry.tsx`, `scripts/01-recognition/shots.mjs`, `scripts/04-bargain/shots.mjs` (also adds `--png`), `scripts/05-build-dread/shots.mjs`.

**G16. JPEG stills cannot prove a pixel.**
- Symptom: "pure black", "exactly `#6fd3ff`" and "2 px line at rows 539 to 540" could not be read from JPEG.
- Cause: `shots.mjs` writes JPEG at q88.
- Fix: per-section lossless verifiers that render PNG and assert numbers.
- Where: `scripts/03-acceleration/verify.mjs` + `check_frames.py`; `scripts/07-outro/verify.mjs` + `measure.py --black`.

**G17. Check outputs overwrote each other.**
- Symptom: a `--scale 1` still was replaced by a later `--all` run.
- Cause: file names are `f<frame>_t<sec>.jpg` regardless of options.
- Fix: `--tag`.
- Where: `scripts/shots.mjs`.

**G18. "A delayRender() font was not cleared after 28000ms".**
- Symptom: two builders and the lead each lost a render while other renders ran; a clean re-run passed.
- Cause: a loaded machine took longer than Remotion's 28 s default to hand a tab its fonts.
- Fix: `delayRender(..., {timeoutInMilliseconds: 180000, retries: 3})` in `font()`, and the same global limit in config.
- Where: `src/kit/fonts.ts`, `remotion.config.ts`.

**G19. One render hung for eleven minutes.**
- Symptom: a `--f` render sat on frame 2823 while several others were running; the same frame took 1.4 s on five other runs.
- Cause: unknown; not reproduced. Shared machine.
- Fix: a per-still timeout (120 s) on `renderStill`, and a note to watch frame 2823 in the final render. It rendered fine.
- Where: `scripts/shots.mjs` (`timeoutInMilliseconds`).

**G20. Windows specifics.**
- Symptom: Python crashed reading `timeline.json` (`charmap` codec error); a glyph (the empty-set sign) was missing and a fallback font would have made the render machine-dependent; Pillow could not open woff2.
- Cause: default cp1252 text encoding on Windows; IBM Plex Mono has no U+2205; Pillow reads TTF/OTF only.
- Fix: every script passes `encoding="utf-8"`; draw the glyph as SVG; unpack the kit's woff2 to TTF with fontTools in `work/` (not shipped).
- Where: all `scripts/**/*.py` use `encoding="utf-8"`; `src/sections/01-recognition/ui.tsx`; `scripts/02-human-cost/fonts.py`.

**G21. Dev overlay and letterbox in plates.**
- Symptom: S6 slices, scales and tiles frames of the film; baked-in bars would appear as black bands inside the mosaic.
- Cause: stills were rendered with overlay, grain and letterbox.
- Fix: a `bare` prop on the film composition (no grain, no letterbox, no overlay) and `--bare` in `shots.mjs`; `showDevOverlay` is forced off for the final by `data/props.final.json`.
- Where: `src/config.ts`, `src/kit/frame.tsx` (`bare`), `scripts/s6-plates.mjs`.

**G22. Parallel builders in one tree on one laptop.**
- Symptom: font timeouts (G18), the hang (G19), builders unable to see each other's compile errors.
- Cause: shared Chrome and Python, one `tsc` over everything.
- Fix: rules in the build guide (no installs, no state-changing git, do not kill processes you did not start, limit Python to a few processes); typecheck by `npx tsc --noEmit 2>&1 | grep "sections/<id>"`.
- Where: `docs/BUILD-GUIDE.md`.

### Baked plates and dependency chains

**G23. A plate that no longer matches the timeline.**
- Symptom: change a cue or move a time in S0 or S2 and the film shows old words. S6 would silently show old frames after S0 to S5 changed.
- Cause: S0 and S2 bake their words into WebP sheets; S6 is cut from frames of the finished film.
- Fix: documented rebuild commands (`python scripts/00-hook/build.py all`, `python scripts/02-human-cost/build_all.py`) and, for S6, a guard that fetches each plate and compares its size and a sampled byte sum with what the generator recorded, then calls `cancelRender` with the command to run. S0 and S2 have no such guard (their components clamp to the plates they have).
- Where: `src/sections/06-reckoning/guard.ts`, `plates.gen.json`, `scripts/s6-plates.mjs`, `scripts/06-reckoning/build_plates.py`, `data/s6-plates.json`; CLAUDE.md guardrails.

**G24. A video plate came back one level darker than its PNG.**
- Symptom: a visible step at the hand-off from a video clip to a freeze-frame PNG.
- Cause: `OffthreadVideo` returns BT.709 H.264 about one level darker than the source.
- Fix: for a seamless switch, make the last plates a JPEG sequence (q97, 4:4:4) drawn with `<Img>`, made by the same decode and scale as the PNG (verified to 0.1 of a level).
- Where: `scripts/01-recognition/build_anchor.py`, `src/sections/01-recognition/Plate.tsx`.

**G25. Constants duplicated between Python, TypeScript and `tokens.ts`.**
- Symptom: Python generators hard-code film frames ("keep in step with clock.ts"); `GRAIN` in `tokens.ts` repeats seconds that also live in `timeline.json`.
- Cause: no shared constants file.
- Fix (partly done): Python reads `data/timeline.json` for words and cut points (`hook/common.py`, `02-human-cost/sheet.py`); the rest remains a drift risk.
- Where: `scripts/01-recognition/common.py` (`F_ALIVE`, `F_HIT`, ...), `src/style/tokens.ts` (`GRAIN`).

**G26. Assets are large and the commit question was left open.**
- Symptom: 33 MB of hook WebP, 74 MB of anchor JPEG, 79 MB of charcoal sheets; budget 250 MB per section.
- Cause: baked sequences.
- Fix: scripts regenerate them; `out/` and `work/` are not committed; the commit-or-rebuild decision stayed in "Requests to lead".
- Where: `assets/footage/<id>/`, `docs/sections/00-hook.md`.

### Faults the reviews found

**G27. A tape tear read as a web glitch.**
- Symptom: slices and pixel-sort blocks in frames 137 to 157 looked digital, not like a worn tape; the next section showed black in the gaps.
- Cause: the tear was built from block and sort slices; the next section sat at luma 0.06 underneath.
- Fix: rewrite the tear as one picture with travelling noise bars, line-by-line ragged edges, re-lock, hooked bands and vertical roll; stop block tells at the tear; lift the next section with `filter: brightness(3.0)` easing to exactly 1.0 on the cut frame and no filter after.
- Where: `scripts/00-hook/hook/tear.py`, `dv.py`; `src/sections/00-hook/index.tsx` (`LIFT`).

**G28. An eyelid transition with an angular edge and a one-frame ignition.**
- Symptom: the opening edge looked like a polygon with a screen glow; the thin line took the light in a single frame.
- Cause: 81 points with 21 px noise; a step in weight, brightness and colour.
- Fix: smooth almond sampled every 6 px, a paint rim 3 to 18 px with a broken ochre lip and bristle marks, a 5 px bloom on the burst only; ignition over four frames, each 1.35 to 1.55 times the weight of the one before.
- Where: `src/sections/04-bargain/index.tsx` (`lidEdge`, `RimEdge`, `LidRim`, `PreLine`).

**G29. Torn strips crossed the fact.**
- Symptom: falling paper crossed the key data text on frames 1904 to 1906 and 1926 to 1927.
- Cause: strips swung right about a pivot below the frame.
- Fix: drop straight out of frame, leaning left, never right of where torn.
- Where: `src/sections/04-bargain/index.tsx`.

**G30. A fade that dropped in steps.**
- Symptom: the mark went from full to gone with steps of 80 and 69 levels.
- Cause: a 10-frame cubic fade with a focus pull on top.
- Fix: linear opacity over about 12 frames, no blur on the way out; the ember last.
- Where: `src/sections/07-outro/`.

**G31. A stamp that contradicted its picture, and a cue id that kept the old claim.**
- Symptom: a "Christmas" title over a summer picture with no tree, on a format that did not yet exist in the stated year.
- Cause: the cue was written before the plate existed.
- Fix: reword the cue to match the plate and rebuild the baked sections. The id (`stamp-1962`) was left, so id and text now disagree. Do not put content in ids.
- Where: `data/timeline.json`, `scripts/00-hook/build.py all`.

**G32. A chart said the opposite of its fact (the one broken item).**
- Symptom: 18 lit cells in a framed row of 20, with the other 82 drawn as faint outlines, read on a phone as a meter nine tenths full beside "fewer than 1 in 5".
- Cause: hairline outlines vanish at phone size; a bright framed row looks like a bar.
- Fix: empty cells became grey tiles (fill 0.15, 2 px outline at 0.5) and the frame was removed, so it reads as one hundred with a row of five lit. Counts unchanged.
- Where: `src/sections/03-acceleration/Grid.tsx`.

**G33. Write-ons are not whole on the cue's first frame.**
- Symptom: at the cue's `from` the viewer saw "Disea", "Poverty endec", "The top 1% alre".
- Cause: write-ons started on the cue's first frame.
- Fix (not taken, logged): start 6 to 10 frames early. Cue `from` is "readable by", so start the entrance early.
- Where: `src/sections/04-bargain/`, `05-build-dread/`; `docs/TODO.md` backlog 3.

**G34. The last picture frame was a held card, not the strongest frame.**
- Symptom: the final word sat unchanged for 28 frames over a 4:3 gate with black sides, while the densest frame was one second earlier.
- Cause: the push was 2 percent and the plate kept its aspect.
- Fix (not taken, logged): fill the width or push harder so the cut lands on a moving frame.
- Where: `src/sections/06-reckoning/index.tsx`; `docs/TODO.md` backlog 4.

### Overload and flash safety

**G35. Fast cutting between bone and black fields is a flash per cut.**
- Symptom: three flashes in one second on a deep rewind; a vertical roll and late throw-backs measured three on the real eye.
- Cause: WCAG-style luminance transitions: a quarter of the screen moving by 10 percent in one direction.
- Fix: level each plate's mean luminance into a band (0.10 to 0.42) in linear light; tear violent cuts in horizontal bands dealt over up to five frames by the plate's measured row profile so no frame moves more than 0.16 of the screen; replace faster cutting by a quadtree mosaic that divides from 4x4 to 32x32; cap seizure slips at three frames. Worst second measured at 1 to 2.
- Where: `scripts/06-reckoning/build_plates.py`, `src/sections/06-reckoning/plan.ts`, `Recut.tsx`, `Seizure.tsx`, `Mosaic.tsx`.

**G36. A black word vanished on a dark plate, then a white one sat on the caption.**
- Symptom: black letters disappeared into the black surround; after relighting, two letters overlapped the plate's own caption.
- Cause: the placeholder plate had been the design reference.
- Fix: bone letters lifted by x1.87; the word is fitted to a band that ends 36 px above the caption; the push runs 0.978 to exactly 1.0 so the last frame is the source's framing. `CAPTION_TOP` is measured on plate 0, so it must be re-measured if that plate or the caption moves.
- Where: `src/sections/06-reckoning/index.tsx` (`CAPTION_TOP`).

**G37. Two numbers torn into one.**
- Symptom: frames 2897 to 2899 interleaved bands of two plates that carried different figures, forming a figure in no source; a 11 px colour split made one number read as another.
- Cause: the cut list had two figure plates adjacent and the tear is band-by-band.
- Fix: plates carrying a figure are named in `recut.json` (`numbers`) and are never neighbours; `plan.ts` cuts whole if a later pick makes them so; colour split on a figure plate is capped at 4 px (`FIGURE_SPLIT`). Residual: slices of one figure plate with a plate carrying no figure were accepted and logged.
- Where: `src/sections/06-reckoning/recut.json`, `plan.ts`, `Recut.tsx`.

**G38. Edge blocks in a seizure.**
- Symptom: blocks at the edges on frames 2817 to 2823.
- Cause: slices travelled further than the overscan (240 px); on two frames the blocks were the source's own dark ring gaps dragged in.
- Fix: `PAD` 240 to 420; slipped slices stop where the source's solid light ends on their rows (`roomBeyondEdge`).
- Where: `src/sections/06-reckoning/filters.tsx`, `Seizure.tsx`.

### Facts and data honesty

**G39. Unsourced or misworded facts in the script.**
- Symptom: a headline value-added figure had no source; an adoption percentage was unsupported; a wealth share was stale; a quote was reworded ("erase" for "eliminate", an inserted "all"); a statement's signatory count was unconfirmed; a source caption said "US" where the cue said "private".
- Cause: the script was written before the fact-check.
- Fix: a `facts.md` with a verdict per claim (`verified`, `needs-rewording`, `unverifiable`, `false`), primary source and suggested on-screen wording; cues were rewritten to it; each `data` cue carries a `source` that is drawn on screen; a one-word correction to an attribution was a data edit with no code change because the section reads the cue live.
- Where: `docs/research/facts.md`, `data/timeline.json` (`role: "data"`), decisions at 12:16 and 13:46.

**G40. The fact-check ran out of budget.**
- Symptom: claims were marked secondary; some news sites would not open.
- Cause: the web-search limit is shared across all agents in a turn; some publishers block fetch tools (HTTP 451, 403).
- Fix: the lead spot-checked three primary sources itself; the report tells the human to re-verify on posting day (figures move quarterly).
- Where: `docs/research/facts.md` "limits of this run".

**G41. Charts and counters can invent data.**
- Symptom: a counter that counts up passes through figures nobody published; a bar comparing two dollar figures implies a ratio their sources do not make.
- Cause: motion design habit.
- Fix: the figure is correct and locked on its first frame; the only count is a short reel spin between two cue figures; the second figure is a push into the numeral, not a bar; "decorative" readouts were replaced by measurements of the plate under them.
- Where: `src/sections/03-acceleration/Counter.tsx`; `src/sections/01-recognition/ui.tsx`; decision log 13:45.

### Legibility

**G42. Small type fails on a phone.**
- Symptom: source lines at 20 to 24 px, a 32.5 percent fact at about 36 to 40 px, sixteen names, an attribution label; the outro tagline's x-height was 0.6 mm on a 68 mm-wide frame.
- Cause: sizes were judged on a 1080p still.
- Fix: the outro went up one step (tagline 44 px, credit 48 px, name 66 px); the rest are in the polish backlog.
- Where: `src/sections/07-outro/`; `docs/TODO.md` backlog 5.

**G43. Typeface behaviours.**
- Symptom: Cormorant's old-style figures made "10" look like "1o"; a lit pupil read as a sun.
- Cause: font default numerals; design choice.
- Fix: lining numerals at 74 px; a black pupil that holds the number.
- Where: `src/sections/05-build-dread/`.

**G44. A half-second sample misses a seven-frame event.**
- Symptom: the final reviewer never saw two of the four slam words and had to report "not sampled".
- Cause: `final-review-frames.py` samples every 15 frames and adds only `data`, `quote`, `thesis` and `logo` cue midpoints to the full-size set.
- Fix: the lead looked at the frames itself (they were there). Next time add every cue's first frame plus two and its midpoint to the dump.
- Where: `scripts/final-review-frames.py` (`keys`).

### Rights and likeness

**G45. Music rights, a traced likeness and generated faces were left to the end.**
- Symptom: the closing checklist still has them open; the music is copyrighted and not cleared; a drawing traced from a broadcast interview needs a decision; every face in two sections is generated.
- Cause: they were treated as the human's problem.
- Fix: the report lists them; the film says "generated" on screen.
- Where: `docs/TODO.md` "Before a public post", `docs/footage-log.md`.

---

## What to change next time, 10+ items (e.g. no ideation stage, no storyboard, reviews on stills only, nobody listened with sound, fact-check depth, cost)

1. **Add an ideation stage.** The film started from an existing essay and a track; there were no alternative treatments to choose between and no scoring against the brief. Do: three concepts with a logline, arc, palette idea and a risk each, scored against the brief and the music, then a chosen treatment and script. This was the first thing the style bible lacked.
2. **Storyboard and animatic before any builder starts.** Builders worked from a style-bible page and a timeline; the first time anyone saw the film as a film was the integration pass. The beat and script locks were lifted mid-run and the research files kept stale timestamps ("ignore those"). Do: a storyboard sheet and an animatic on the real track with every word at its real time, signed off, then freeze timing before research timestamps are written.
3. **Review motion, not only stills.** All eight boundary reviews and the final review were frames; no one judged movement. Do: add a motion-energy trace (frame-difference per frame) next to each sheet, short half-rate clips or GIFs for each window, and a script that flags freezes, jumps and one-frame pops.
4. **Someone has to listen with sound.** Sync to the music was set from measured beats and never checked by ear. Do: a standing gate where the human (or a tool) watches the graded file with sound; generalise `pump_check.py` to compute the picture's change against the onset curve for every section and report off-beat moves; write the verdict into the report.
5. **Fact-check as its own phase, earlier, with depth.** Four script claims failed after the script was written; the check hit a shared search limit and blocked sites. Do: run it before storyboard sign-off; two independent checks per `data` or `quote` cue; a verdict enum, an "as of" date and a re-verify date on each claim; on-screen strings must equal the verified wording; give the research agents a search budget per agent, not per turn.
6. **Decide rights and likeness at intake.** Music licence, any traced likeness, generated faces, and font licences were left for the end. Do: a rights register file created at intake, filled by every agent that brings in media, checked at the final gate.
7. **Track cost per phase and per agent.** Only plan-window percentages were recorded. Do: log tokens and wall clock per agent in the report, set a budget per phase, and route simple sections (the pure-code S3 cost 30 to 42 ms a frame) to a cheaper model.
8. **Fold the harness gaps into the main script.** Three builders each copied `shots.mjs` to get a pass-through window and `--png`. Do: add `--through` (owners that draw the live section), `--png`, a per-still timeout, unique default file names for `--all` and `--boundaries`, and a unique default bundle name per process.
9. **A single `doctor` command before any render.** It should check that baked plates match the cues and sources they were built from (a hash in a manifest, generalising `plates.gen.json`), that the S6-style dependent chain is fresh, that fonts are vendored, that no section returns an empty frame in its render range, and that cue windows match what each section draws.
10. **Separate "readable by" from "drawn".** Cue `from` and `to` meant three different things. Do: add `shown: {from, to}` (or assert the relation) and let a verification script print any cue whose drawn window differs from its cue window.
11. **Set minimum type sizes in the style bible.** Five items failed on a phone. Do: put numbers in the rules (for example body 54 px, source lines 32 px at 1080p) and add a phone-size render (360 px wide) to every review input.
12. **Sample the final review by cue, not by clock.** Add every cue's first-frame-plus-two and midpoint, every transition's first and last frame, and phone-size tiles.
13. **Repeat the final review after fixes.** The lead looked at the changed frames itself; a short second pass on a diff-dump (frames that changed between renders) is cheap and would have verified the grid fix on a phone-size render.
14. **Automate dependent chains.** The S6 chain (`s6-plates.mjs`, `build_plates.py`, flash check) is three commands to run by hand after any change to S0 to S5. Do: declare dependents in the timeline (or a `chains.json`) and let one command run the chain and fail loudly.
15. **Use git worktrees or staggered renders for parallel builders.** Font timeouts and a hang came from builders sharing a machine. Do: give each builder its own worktree and private bundle by default, and cap concurrent Chrome tabs.
16. **Do not put content in ids.** `stamp-1962` now says 1966. Use role-based ids (`stamp-1`, `slam-2`).
17. **Make provenance a script.** Builders asked the lead to update the footage log. Do: `scripts/log-asset.sh "<file>: source, URL, licence, how processed"`, like `log-decision.sh`.
18. **Treat "Requests to lead" as a queue.** Some stayed open at the end (commit-or-rebuild for baked sequences, two kit requests). Give each request an owner and a status in the session report.
19. **Name a cut list.** The brief said "ship a simpler version" but did not say what to drop first. Add an ordered cut list per section at storyboard time, so a late squeeze is a decision, not a panic.

---

## The contract: timeline.json schema, frame snapping, absolute film time, transition owner model (prev/next), render ranges, solo harness, private bundles, determinism rules, letterbox, grade-once rule; quote the important types and helper names exactly

### timeline.json (schema v2)

```json
{
  "_schema": "v2 ... (prose description of the schema)",
  "w": 1920, "h": 1080, "fps": 30, "dur": 120.0,
  "audio": { "src": "track.mp3", "duration": 102.448, "note": "free text" },
  "sections":    [ { "id": "01-recognition", "from": 5.2667, "to": 15.3333, "label": "S1 THE RECOGNITION", "style": "free text" } ],
  "marks":       { "reveal-hit": 5.2667 },
  "transitions": [ { "id": "t-00-01", "at": 5.2667, "a": "00-hook", "b": "01-recognition", "owner": "00-hook",
                     "pre": 0.9333, "post": 0.2, "name": "Tracking tear", "device": "prose", "beat": "prose" } ],
  "cues":        [ { "id": "invest-us", "section": "03-acceleration", "role": "data", "from": 28.9667, "to": 32.6,
                     "text": "exact words", "attribution": "label under a number", "source": "where the fact comes from" } ]
}
```

Rules: seconds to four decimals; every boundary is a whole frame (`frame = round(t * 30)`); sections own `[from, to)`; the edges are transitions with `a: null` (start) or `b: null` (end); a hard cut has `pre = post = 0`; on-screen words are the cue's `text` exactly (and `attribution`, and `source` for `data`); `note` is direction and never shown.

### Types (`src/timeline/types.ts`, quoted)

```ts
export interface SectionSpan { id: SectionId; from: number; to: number; label: string; style: string; }

export type CueRole = "stamp" | "slam" | "narration" | "sub" | "quote" | "data" | "thesis" | "question" | "credit" | "logo";

export interface Cue {
  id: string; section: SectionId; role: CueRole;
  from: number; to: number;
  text: string;            // \n = line break; on-screen text is exactly this string
  attribution?: string;    // who said it, or the label under a number
  source?: string;         // where the fact comes from; shown small for `data` cues
  names?: string[];        // extra strings a section may draw
  note?: string;           // direction, never shown
}

export interface Transition {
  id: string; at: number; a: SectionId | null; b: SectionId | null; owner: SectionId;
  pre: number; post: number; name: string; device: string; beat: string;
}

export interface AudioMeta { src: string; duration: number; note?: string; }

export interface Timeline {
  w: number; h: number; fps: number; dur: number; audio?: AudioMeta;
  sections: SectionSpan[]; marks: Record<string, number>; transitions: Transition[]; cues: Cue[];
}
```

`SectionId` is a string-literal union in `src/style/tokens.ts` (`"00-hook" | "01-recognition" | ... | "07-outro"`); it must become `string` in a general kit.

Cue roles as documented in the types file: `stamp` diegetic label inside the picture; `slam` one-beat word hit; `narration` the film's own voice; `sub` a smaller second line; `quote` someone else's words, carries `attribution`; `data` a number that must be exactly right, carries `source`; `thesis` the line the film exists for; `question` outro questions; `credit` removable end credit; `logo` the studio mark.

### Frame snapping (`src/timeline/timeline.ts`, quoted)

```ts
export const FPS = rawTimeline.fps;
const snap = (sec: number): number => Math.round(sec * FPS) / FPS;
const frameOf = (t: number): number => Math.floor(t * FPS + 1e-6);
export function F(sec: number): number { return Math.round(sec * FPS); }   // seconds -> frame
export function T(frame: number): number { return frame / FPS; }            // frame -> seconds
```

At load, `timeline` is built from the raw file with every `sections[].from/to`, `marks`, `cues[].from/to` passed through `snap`; each transition restates `at` as `f / FPS` and `pre`/`post` as whole frames: `pre = (f - a) / FPS`, `post = (b - f) / FPS` where `f = round(at*FPS)`, `a = round((at - pre)*FPS)`, `b = round((at + post)*FPS)`. Lookups compare whole frames.

Exports: `timeline`, `FPS`, `F`, `T`, `section(id)`, `sectionAt(t)`, `cue(id)`, `cuesOf(id)`, `cuesAt(t)`, `mark(name)`, `transitionIn(id)`, `transitionOut(id)`, `transitionAt(t)`, `renderRange(id)`, `formatTimecode(t)`. `section`, `cue`, `mark`, `transitionIn`, `transitionOut` throw on a bad id so typos fail loudly.

### Absolute film time (`src/kit/time.tsx`)

Sections are mounted without a `<Sequence>`, so frame 0 is the first frame of the film. `useFilmTime()` stays absolute inside `<Sequence>`, `<Freeze>` and `<Loop>` because it reads the clock the root provides.

```ts
export const FilmClockProvider: React.FC<{ children }>;                       // mounted once at the root of every composition
export const FilmClockOverride: React.FC<{ frame: number; children }>;       // pin or replay a subtree on one absolute frame
export interface FilmTime { frame: number; t: number; fps: number; }
export function useFilmTime(): FilmTime;
// pure helpers
export const clamp = (v, lo = 0, hi = 1) => ...;   export const lerp = (a, b, k) => ...;
export const ease = { linear, in, out, inOut, outExpo, inExpo, outBack, outQuint, inQuint };
export function prog(t, a, b, easing = ease.linear): number;          // 0..1 progress through [a,b]
export function remap(t, a, b, c, d, easing = ease.linear): number;   // map [a,b] to [c,d], clamped
export function rnd(seed: string | number): number;                   // Remotion random(), same seed same number
export function rndRange(seed, lo, hi): number;
export function hold(frame: number, n: number): number;              // animate "on twos": Math.floor(frame/n)*n
export function envelope(t, from, to, fadeIn = 0.4, fadeOut = 0.4): number;
```

### Section contract (`src/kit/section.ts` and BUILD-GUIDE)

```ts
export interface SectionProps {
  from: number; to: number;          // the section's own span, absolute film seconds
  prev?: React.ReactNode;            // live render of the section before (only for the owner of the transition in)
  next?: React.ReactNode;            // live render of the section after (only for the owner of the transition out)
}
export type SectionComponent = React.FC<SectionProps>;
```

```tsx
// src/sections/<id>/index.tsx
export const Section: SectionComponent = ({ from, to, prev, next }) => {
  const { t, frame } = useFilmTime();           // ABSOLUTE film time
  return <AbsoluteFill>...</AbsoluteFill>;
};
```

Kit exports (`src/kit/index.ts`): `SectionComponent`, `SectionProps`, `FilmClockOverride`, `clamp`, `ease`, `envelope`, `hold`, `lerp`, `prog`, `remap`, `rnd`, `rndRange`, `useFilmTime`, `FilmTime`, `BEATS`, `PULSES`, `PULSE_PERIOD`, `level`, `music`, `pulseEnv`, `pulseFrame`, `pulseIndex`, `pulsesIn`, `sincePulse`, `Band`, `font`, `weightsOf`, `FontFamily`, `F`, `FPS`, `T`, `cue`, `cuesAt`, `cuesOf`, `formatTimecode`, `mark`, `renderRange`, `section`, `sectionAt`, `timeline`, `transitionAt`, `transitionIn`, `transitionOut`, types `Cue CueRole SectionSpan Timeline Transition`, and `CANVAS`, `LETTERBOX_PX`, `PALETTE`, `SAFE`, `WIRE`, `SectionId`, `SectionPalette`.

### Transition owner model (`src/kit/frame.tsx`)

During a window `[at - pre, at + post)` (whole frames) only the **owner** is mounted and it receives the other section's live render as `prev` (owner is the incoming section) or `next` (owner is the outgoing one). The owner places it: under its own layers, in a mask or clip-path, in a CSS or SVG filter, scaled, sliced. If the owner never draws the node, the neighbour is not on screen. A hard cut has `pre = post = 0`: no window, nothing shared, and the cut frame belongs entirely to the incoming section. Edge transitions (`a` or `b` null) never open a window.

```tsx
export type Registry = Record<SectionId, SectionComponent>;
export const FilmStack: React.FC<{ registry: Registry }> = ({ registry }) => {
  const { t } = useFilmTime();
  const render = (id, extra?) => { const s = section(id); const Comp = registry[id]; return <Comp key={id} from={s.from} to={s.to} {...extra} />; };
  const tr = transitionAt(t);
  if (tr && tr.a && tr.b) {
    const other = tr.owner === tr.a ? tr.b : tr.a;
    const neighbour = <AbsoluteFill>{render(other)}</AbsoluteFill>;
    return tr.owner === tr.a ? render(tr.a, { next: neighbour }) : render(tr.b, { prev: neighbour });
  }
  const s = sectionAt(t);
  return s ? render(s.id) : null;
};
```

Consequences: the owner cannot read the neighbour's pixels into WebGL; both sections must draw valid full frames across the whole window including the part outside their own span; the handshake table (below) is the only place two sections must agree on pixels.

**Handshakes** (`docs/transitions.md`): for each boundary, one line of exact obligations, repeated on both sections' style-bible pages. Examples of the form: "S1 holds `anchor-freeze.png` full canvas, untransformed, from 14.8667 to 16.0833, overlays gone by 15.0; S2's drawing is made from that same file." "From 48.9 to 50.2667 S3 is `#0a0a0a` with one 2 px line `#f4f1e8` at y = 540, full width; S4's opening starts as that line." "S6's frame 2995 is bright and full; the outro's frame 2996 is `#000`; nothing from S6 survives the cut."

The table also gives each window in frames (cut frame, frames on which the owner is mounted with the neighbour, first frame the incoming section is alone).

### Render ranges

```ts
export function renderRange(id: SectionId): { from: number; to: number } {
  const s = section(id);
  const tin  = timeline.transitions.find((x) => x.b === id && x.a);
  const tout = timeline.transitions.find((x) => x.a === id && x.b);
  return { from: s.from - (tin?.pre ?? 0), to: s.to + (tout?.post ?? 0) };   // seconds
}
```

A section must draw a valid, full, opaque frame for every `t` in `renderRange(id)`: start the first shot early and keep the last shot running late. Never return null or a transparent frame there. `shots.mjs --all N` renders the section's render range every N seconds; `--boundaries` renders cut-2 to cut+1 and the first, middle and last frame of each window.

### Solo harness (`src/solo.tsx`, `src/sections/<id>/entry.ts`)

```ts
// src/sections/<id>/entry.ts  (do not edit; copy per section)
import { registerRoot } from "remotion";
import { makeSoloRoot } from "../../solo";
import { Section } from "./index";
registerRoot(makeSoloRoot("05-build-dread", Section));
```

`makeSoloRoot(id, Section)` registers composition `"Solo"`: the whole film's timeline with that section real and every other section a `makePlaceholder(id)` test card (a moving, detailed card in the neighbour's palette, labelled with its section label, so a mask or inversion has something to act on). `placeholderRegistry(real)` fills a `Registry`. `Film.tsx` has the same idea through the `debugSolo` prop. Timing, audio, grain, letterbox and transition windows are exactly the film's (same `FilmFrame`). A test card that owns a transition does not draw its neighbour: use a pass-through entry (G15) to see frames inside a neighbour's window. Pass-through owners are one line each: `({ next }) => <AbsoluteFill style={{background:"#f0f"}}>{next ?? null}</AbsoluteFill>`.

Composition props (`src/config.ts`, zod): `showDevOverlay: boolean`, `grainStrength: number (0..2)`, `muteAudio: boolean`, `debugSolo: string`, `bare?: boolean`. Defaults: overlay on, grain 1, audio on, no solo. `data/props.final.json` is `{showDevOverlay:false, grainStrength:1, muteAudio:false, debugSolo:""}`.

Layer order in `FilmFrame`, bottom to top: `AudioTrack`, `FilmStack` (inside an `overflow: hidden` `AbsoluteFill`), `Grain` (skipped when `bare`), `Letterbox` (skipped when `bare`), `DevOverlay` (only when `showDevOverlay`). The root is `FilmClockProvider` over a `#000` `AbsoluteFill`.

### Private bundles

`shots.mjs` bundles with `publicDir` set to an empty temp dir, then creates a junction `out/.bundle/<name>/public` pointing at `./assets` (so the bundle never copies gigabytes). `<name>` defaults to the target and is set with `--bundle <name>`. Any run that may overlap another on the same target must pass its own name. `dropJunction` unlinks the junction before any recursive delete. Webpack cache is named per target (`cache.name = wbam-<target>`).

### Determinism rules (BUILD-GUIDE, style-bible rule 8)

- A frame is a pure function of its number. Frames render in parallel tabs in any order.
- No state carried between frames, no accumulating `useState`, no `Math.random`, no `Date`, no CSS `transition` or `animation`, no `requestAnimationFrame`, no `useFrame` clock.
- Randomness comes from `rnd("stable-key-" + i)` (Remotion `random(seed)`); Python uses seeds built from string keys (`rng_for`, `rnd(seed, i, ...)`).
- Animate boil and jitter with `hold(frame, 2)` so they hold instead of buzzing.
- Assets load before the frame is taken: `<Img>`, `<OffthreadVideo>`, `staticFile()`; anything loaded by hand is wrapped in `delayRender`/`continueRender`. Fonts through `font("Family")` at module top level.
- SVG filters: `filterUnits="userSpaceOnUse"` with a region larger than the frame or blurs and displacements clip at a hard rectangle. Full-frame `feTurbulence` regenerated every frame is slow; use a pre-made noise plate moved by transforms.
- Three.js: `<ThreeCanvas width={1920} height={1080}>` from `@remotion/three`; read `useFilmTime()` outside and pass the frame in; put text in DOM above the canvas.
- Renders are bit-identical except text anti-aliasing and scaled-image resampling (G12).

### Letterbox, safe area, palette (`src/style/tokens.ts`)

```ts
export const CANVAS = { width: 1920, height: 1080, fps: 30 } as const;
export const LETTERBOX_RATIO = 0.06;
export const LETTERBOX_PX = Math.round(CANVAS.height * LETTERBOX_RATIO);   // 65
export const SAFE = { top: 65, bottom: 1015, height: 950, centerY: 540,
                      text: { left: 150, right: 1770, top: 125, bottom: 955 } } as const;
export const WIRE = "#6fd3ff";
export const PALETTE: Record<SectionId, { bg; ink; accent; accent2; shadow }>;   // one record per section so neighbours can quote colours at a boundary
export const GRAIN: Array<{ start: number; end: number; amount: number }>;       // film-wide in-comp grain schedule, seconds
export const DEV = { font, color, size };
```

Rules: the letterbox covers y < 65 and y > 1015; compose for 1920x950; words stay inside `SAFE.text`. `Letterbox` is two `#000` bars; the dev overlay is drawn inside the bars so it never covers picture. Builders do not add their own letterbox or audio.

### Music (`src/kit/music.ts`)

`music` is `data/beats.json`; `PULSES` is every pulse in the pumped regions, ascending; `BEATS` is the tracked grid; `PULSE_PERIOD = 0.96`; `level(frame, band: Band = "energy")` returns 0..1 per frame for `"energy" | "low" | "mid" | "high" | "onset" | "perc"`, interpolating fractional frames and returning 0 past the end; `pulsesIn(a, b)`, `pulseIndex(t)`, `sincePulse(t)` (Infinity before the first pulse or more than 1.5 s after one), `pulseEnv(t, decay = 0.35)` (1 on a pulse, `exp(-3 d / decay)` after), `pulseFrame(p) = Math.floor(p * FPS + 0.25)`.

### Grade-once rule (`scripts/grade.sh`, `remotion.config.ts`)

- The render is clean: no per-section grade. `Grain` is light and scheduled by `GRAIN`; each section brings its own texture.
- One ffmpeg pass over the render: `scale=out_range=tv:out_color_matrix=bt709, format=yuv420p, eq=contrast=1.05:saturation=0.97:gamma=0.985:enable='lt(n,BLACK_F)', vignette=PI/9:enable=..., noise=alls=5:allf=t+u:enable=..., drawbox (top 65 px black), drawbox (bottom 65 px black), setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709`; `libx264 -crf 17 -preset slow -maxrate 40M -bufsize 80M -pix_fmt yuv420p`, tags forced to bt709 tv, `-movflags +faststart`, `-c:a copy`.
- `BLACK_F` is the outro's `from` as a frame, read from the timeline, and the gate uses the frame number (G8).
- `render:final`: `remotion render Film out/<name>.mp4 --codec=h264 --crf=16 --color-space=bt709 --jpeg-quality=95 --props=./data/props.final.json`. Config sets jpeg frames, overwrite, angle GL, bt709, jpeg quality 95, public dir `assets`, h264, and a 180 s `delayRender` limit.
- Flash safety: at most three full-frame luminance flashes in any one second, no saturated red fields; measure with `flash-check.py` on the graded file, because the grade's contrast can move a 0.24 transition over 0.25.

---

## Tool inventory: for EACH script and kit module: what it does, its CLI, what is specific to this film and what is generic, and exactly what to parameterise to make it reusable

Run everything from the project root. `python` is Python 3.13; use `-X utf8` or explicit `encoding="utf-8"` on Windows.

### Root scripts

**`scripts/analyze_music.py`**
- Does: converts the mp3 to a mono 22.05 kHz wav with ffmpeg, then with librosa measures tempo (beat tracker plus tempogram second opinion), beat grid, bar phase (which beat of four carries the most low-band and onset energy), onsets with strength, the 40 strongest "hits", structure boundaries (4 s before/after novelty over MFCC and chroma plus loudness novelty, refined to the strongest onset within 0.6 s), loudness landmarks (loudest, fade below -40 dB, silence from, sudden drops and rises), per-video-frame curves (`energy low mid high onset perc` at 30 fps), and a "legacy snap" table. Fits an exact pulse grid in two hand-given "pumped" stretches. Writes `data/beats.json` (compact) and five plots to `out/research/`.
- CLI: `python scripts/analyze_music.py` (no arguments). Deterministic.
- Specific: the mp3 path (`assets/solitude_short_cut.mp3`); the `LEGACY` dict of the old timeline's times; the two pumped windows `fit_grid(28.5, 46.7)` and `fit_grid(66.9, 100.2)` and the period search range 0.940 to 0.981 s; the plot windows (0 to 34, 28 to 68, 64 to end, 92 to end) and their cyan/lime annotation of legacy times; `FPS = 30`.
- Generic: everything else.
- Parameterise: take `--audio`, `--fps`, `--out`; drop `LEGACY` (or take `--legacy file.json`); detect pumped or periodic regions automatically (search windows where a single period/phase explains the onset envelope with a score above a threshold) instead of hand windows; emit candidate cut points (ranked hits, structure peaks, downbeats) as `marks` suggestions; add a short text "music brief" (tempo, sections by loudness, where the quiet is) for ideation; make the plots optional.

**`scripts/shots.mjs`**
- Does: bundles a target once (section solo or the film) and renders stills with Remotion's renderer in one browser; optional contact sheet; optional full-res benchmark.
- CLI: `node scripts/shots.mjs <section-id|film> [--t 15.4,16.08] [--f 460,461] [--range a:b:step] [--seq a:b] [--boundaries] [--all N] [--out dir] [--sheet name] [--cols 6] [--scale 0.5] [--clean] [--bare] [--tag v2] [--bundle name] [--bench a:b]`. Names files `f<frame>_t<sec>.jpg`. Exit 2 if any frame failed. JPEG quality 88; per-still timeout 120 s; GL `angle`; `--bench` renders at full res with 4 tabs and prints ms per frame.
- Specific: composition ids `Film` and `Solo`; `src/sections/<id>/entry.ts` convention; `FPS = 30`; "1920x1080" in the bench message; `wbam-` names for the webpack cache and the temp public dir; `muteAudio: true` in the input props.
- Generic: the whole mechanism (junctioned public dir, private bundles, one browser).
- Parameterise: read `fps`, `w`, `h` from the timeline; project name for cache names; composition ids from a config; entry path template; add `--through` (pass-through owners), `--png`, `--timeout`; make `--all`/`--boundaries` write to a tagged subfolder by default; accept a `--frames-file`.

**`scripts/sheet.py`**
- Does: tiles images into a labelled contact sheet.
- CLI: `python scripts/sheet.py out.jpg [--cols 6] [--w 480] img1 img2 ...`. Labels are the file stems (frame and time).
- Specific: font `consola.ttf` (Windows) with PIL default fallback; tile label height 22; dark grey background.
- Generic: all of it.
- Parameterise: font path or a bundled font; `--label` template; `--bg`; optional timecode strip or waveform row under each sheet.

**`scripts/review-frames.mjs`**
- Does: for each transition in the timeline (or the ones named) renders every frame from 12 before the window to 12 after (a hard cut: 30 before, 14 after) at half size into 24-tile sheets (6 x 4, 480 px), plus the frames cut-1, cut, cut+1 at full size, plus `frames.json`. A special job `t-start-end` dumps the first and last 24 frames and four full-size frames.
- CLI: `node scripts/review-frames.mjs [t-00-01 t-04-05 ...]` (default: all). Output `out/review/<id>/`. Calls `shots.mjs film --bundle review --clean`, then `sheet.py`.
- Specific: the `t-start-end` job and its frames; target `film`; bundle name `review`; `--clean` only.
- Generic: the margin logic and the sheet building.
- Parameterise: `--margin 12`, `--per-sheet 24`, `--tile 480`; skip the start/end job if the timeline has no edge transitions; add a motion-energy strip and a phone-size (360 px) tile set; allow a `--through` flag.

**`scripts/final-review-frames.py`**
- Does: reads frames out of the delivered mp4 itself: one frame every half second (`half/`, 960 px), every frame of the 3 s before the cut to black plus 6 after (`last/`), and key full-size frames (`full/`: first, last, the cut to black and its neighbours, every transition's cut frame, every section midpoint, and the midpoint of every `data`, `quote`, `thesis` and `logo` cue), contact sheets `sheet-NN.jpg` and `last-NN.jpg`, and `frames.json`.
- CLI: `python scripts/final-review-frames.py [graded.mp4]` (default the graded file). Output `out/final-review/`.
- Specific: the default path; `BLACK` taken from section id `07-outro`; the 3-second window; the four cue roles.
- Generic: the ffmpeg `select` dealing (25 terms per expression because the parser gives up on a long sum), the frame naming, the sheet building.
- Parameterise: `--black-frame` or read the final-cut frame from a `finish` block in the timeline (and cope with films that fade out); `--every 0.5`; include every cue's first frame + 2 and midpoint; add `--phone 360`; add waveform and motion-energy strips; take the section for the "last seconds" from the timeline.

**`scripts/flash-check.py`**
- Does: approximates WCAG 2.3.1 general flash. Downsamples to 96x54; a "transition" is a frame-to-frame change where at least 25 percent of the picture moves by at least 0.10 relative luminance in the same direction with the darker state below 0.80; a "flash" is two opposing transitions; more than three flashes in any one second is FAIL. Also counts saturated-red changes (R > 200 and R minus max(G, B) > 110, at least 25 percent of the screen changing). Prints counts, worst one-second window and flash times.
- CLI: `python scripts/flash-check.py <video.mp4 | dir of frames> [--from 93.0] [--to 100.0] [--fps 30]`. Exit 0 PASS, 3 FAIL.
- Specific: nothing (it is film-agnostic).
- Generic: all of it. Known limits: screening tool, not a certified analyser; ignores viewing distance and gradual changes.
- Parameterise: `--max-flashes`, `--area`, `--step`, `--json` output; a mode that takes a `timeline.json` and checks each section separately; run it on the graded file, not only on renders.

**`scripts/black-check.py`**
- Does: measures the cut to black (frames BLACK-3 to BLACK+4), a 30-frame black hold, the last four frames, and the letterbox bars (every 7th frame; the two bar rows touching the picture are skipped). Luma read through ffmpeg gray (full range, 0 is black). Tolerances: black frames max Y at most 2; bars at most 12.
- CLI: `python scripts/black-check.py <graded.mp4>`. Exit 3 on any failure.
- Specific: `BLACK` is the start of section `07-outro`; `BAR = 65`.
- Generic: the streaming ffmpeg select and the checks.
- Parameterise: black frame from a `finish.cutToBlack` entry (skip if none); bar px from the timeline or tokens; optional checks for first frame black, fade-out duration and monotonic fade; tolerances as flags.

**`scripts/grade.sh`**
- Does: the single unifying pass (see "Grade-once rule"). Converts to limited bt709 first, grades, vignettes and adds temporal noise only before the outro frame, repaints the bars, forces tags, copies audio.
- CLI: `scripts/grade.sh <in.mp4> <out.mp4>` (`npm run grade`). Needs ffmpeg and node on PATH.
- Specific: the grade numbers, `BAR=65`, the section id `07-outro` used to find where to switch off.
- Generic: the structure and the frame-number gate.
- Parameterise: a `grade` block in the timeline or a `grade.json` (contrast, saturation, gamma, vignette, noise, crf, maxrate); `finish.gradeOffFrom`; letterbox px (zero for none); in/out aspect from the timeline.

**`scripts/log-decision.sh`**
- Does: appends `- [YYYY-MM-DD HH:MM] <text>` to `docs/decisions.md`.
- CLI: `bash scripts/log-decision.sh "who: what, and why"`.
- Specific: the file path. Generic: everything.
- Parameterise: the log path and a `--who` default from an environment variable; create the file with a header if missing. Make a twin `log-asset.sh` for provenance.

**`scripts/s6-plates.mjs`**
- Does: re-renders the frames of the finished film listed in `data/s6-plates.json` (bare: no letterbox, grain or overlay; scale 1) and writes them over the files the manifest names.
- CLI: `node scripts/s6-plates.mjs` (no arguments). Uses `shots.mjs film --bundle s6-plates --bare`.
- Specific: the manifest name, the destination folder, S6 itself (all plate times are before S6 starts so S6 never renders itself).
- Generic: the idea "a section cut from the finished film".
- Parameterise: `--manifest data/plates.json`; the film target; assert every plate time is before the consuming section; call the consuming section's own plate builder afterwards.

**`scripts/fetch-fonts.mjs`**
- Does: vendors Google Fonts into `assets/fonts/` (latin subset of each listed weight and style) using `@remotion/google-fonts` metadata, and writes `src/kit/fonts.manifest.json` for `font()`. Existing files are kept. Missing weights set exit code 1.
- CLI: `node scripts/fetch-fonts.mjs` (`npm run fonts`).
- Specific: the `FAMILIES` map (22 families).
- Generic: the download and manifest.
- Parameterise: read families from a `fonts.json` produced at storyboard time; add `--add "Family:400,700"`; also generate the `FontFamily` union and the `KIND` fallback map in `fonts.ts` from the manifest; write licences into the rights register.

### Per-section scripts (film-specific; keep as technique references, copy the pattern)

Every one of these reads `data/timeline.json` (or should) for words and cut points, takes no arguments unless stated, is deterministic (seeded by string keys), and writes plates into `assets/footage/<id>/` with intermediates in `work/<id>/`.

- **`scripts/00-hook/build.py`** (+ `hook/common.py`, `plates.py`, `scene.py`, `video.py`, `film8.py`, `vhs.py`, `hi8.py`, `dv.py`, `tear.py`): `proof` (draw polygons over stills), `prev 0-12 20 47` (single frames), `sheet a 0:48:2` (contact sheet of a span), `cache [frames]` (render the four eras), `seq [frames]` (cache, tear, write `NNNN.webp`), `all`. Specific: the four stills, the four formats, the stamps. Generic pattern: era-true degradation at native raster then scale last (video.py), a still treated as a scene with a depth map and a virtual camera (scene.py), a `proof` command that draws your own masks back onto the source. Parameterise: source list and per-source format module from the storyboard; cut points from the timeline (already done); output folder.
- **`scripts/01-recognition/build_ungen.py`, `build_face.py`, `build_anchor.py`, `latent.py`, `common.py`**: `--preview f1,f2,...` renders stills; each writes a plate and a JSON of measurements (noise level per tile, face mesh per frame, face box per frame) that the TS section reads so the on-screen readouts are true. Specific: the four tiles, the face, the anchor, frame constants `F_ALIVE` etc. Generic: the latent "un-generate" sampler `x_t = sqrt(a) x0 + sqrt(1-a) eps`, tracked mesh from Shi-Tomasi + Lucas-Kanade (no landmark model), JPEG-sequence plates for seam-free hand-offs. Parameterise: read frame constants from the timeline.
- **`scripts/01-recognition/shots.mjs`**, **`scripts/04-bargain/shots.mjs`** (adds `--png`), **`scripts/05-build-dread/shots.mjs`**: copies of `shots.mjs` bundling a pass-through entry. Replace by `--through` in the main script.
- **`scripts/02-human-cost/build_all.py`** (runs `build_c.py`, `build_ab.py`, `manifest.py` in that order; about 6 minutes on one core), `build_c.py [a b | --test 730,790,860]`, `charcoal.py` (stroke engine: traced contour strokes with taper and wobble, hatching along a bent direction field, tooth-broken mass, smudge, rubbing-out with ghosts), `roto.py` (one drawing from one moment of a clip, cropped above the broadcast lower third), `sheet.py` (shared timeline, lettering, cut paper), `fonts.py` (woff2 to TTF), `montage.py out.jpg cols scale a.jpg ...`, `manifest.py` (joins frame lists into `plates.json`, fails if any frame in the render range has no sheet or a file is missing, prunes unlisted sheets). Generic pattern: a manifest that fails loudly on a gap. Parameterise: the section's frame range and plate directory from the timeline.
- **`scripts/03-acceleration/verify.mjs [--keep] [--out dir]`** + **`check_frames.py <dir>`**: lossless PNG renders of the contract frames and pixel assertions (negative of `prev`, a light field with dark numerals, a 2 px line, determinism re-render with a stated tolerance). **`pump_check.py <seq dir>`**: measures frame-to-frame change against the pump pulses and the bass curve, listing big moves that are off the pulse. **`strip.py <dir> <first> <last> <out.jpg> [--step --cols --w]`**: contact sheet of consecutive frames. **`measure_fonts.py`**: hmtx advances and bounds from the vendored woff2 into `metrics.json`, so layout never depends on when a font finished loading. Generic: `pump_check.py` (generalise to every section against `beats.json`), `measure_fonts.py` (generalise to any font list). Specific: the asserted values and frame numbers.
- **`scripts/04-bargain/scene.py`** (the landscape as numbers, one description for two renderers, with a pinhole camera `F = 1483.6` for a 40 degree vertical field of view), **`paint.py [--only sky,fg] [--variants 1]`** (gouache layers as 2240x1260 WebP with alpha, three boil variants, plus `scene.json` and a preview), **`gouache.py`** (seeded gouache toolkit). Generic pattern: one scene file, two renderers, a shared camera.
- **`scripts/06-reckoning/build_plates.py`** (levels each plate's mean luminance into a band in linear light, builds thumbnails and two mosaic sprites, measures every cut with `flash-check`'s arithmetic, writes `plates.gen.json` that the guard reads), **`cutlist.mjs`** (bundles `plan.ts` with esbuild and prints the cut list: which plate, from which frame, for how long, how it is cut and the largest part of the screen any frame moves), **`transitions.py <dir> [first-frame]`** (lists every frame moving 12 percent of the screen or more, to trace a FAIL to its cut). Generic: all three, if "plates" and "plan" become parameters.
- **`scripts/07-outro/verify.mjs [--f ... --t ... --seq a:b --step n --comp Direct|Solo|NoCredit --out dir --black --keep]`** + **`measure.py [--black] frames.png...`** (brightest value, non-black pixel count and bounding box, mean, ink offset from the vertical axis; `--black` exits 2 unless every pixel is `#000`), **`encodecheck.mjs`** (renders a second through Remotion's own encoder twice, once with the default colour space and once with bt709, passes it through the active part of the grade, and measures black, bars and ember against the lossless frame), **`gradecheck.sh`** (proves a time gate lands grain on the first black frame and a frame gate does not). Generic: `measure.py`, `verify.mjs`'s `--black` assertion, and the encode/grade pipeline proof. Parameterise: composition ids and frame numbers from the timeline.

### Kit and application modules

| Module | What it does | Specific to this film | Parameterise |
|---|---|---|---|
| `src/timeline/types.ts` | The schema types (quoted above) | `SectionId` union; the cue-role list is generic | `SectionId = string`; roles as a config list |
| `src/timeline/timeline.ts` | Loads `data/timeline.json`, snaps to frames, lookups, `renderRange` | Imports `../../data/timeline.json` | Path from a config; `FPS` from the file (already) |
| `src/kit/time.tsx` | Film clock, override, `useFilmTime`, pure helpers | None | None |
| `src/kit/section.ts` | `SectionProps`, `SectionComponent` | None | None |
| `src/kit/frame.tsx` | `FilmStack`, `FilmFrame` (layer order, `bare`) | `Registry` is keyed by `SectionId` | Let the layer list be configured (letterbox on/off, grain on/off) |
| `src/kit/music.ts` | `PULSES`, `BEATS`, `level`, `pulseEnv`, `sincePulse`, `pulseFrame` | `PULSE_PERIOD = 0.96`, comments about a pad with no drums, band list | Derive the period from `beats.json`; a film with a drum track would use `BEATS` and `downbeats` more |
| `src/kit/fonts.ts` | `font(family)`, `weightsOf`, 180 s `delayRender` with retries | `FontFamily` union (22), `KIND` fallback map | Generate from `fonts.manifest.json` |
| `src/kit/placeholder.tsx` | `makePlaceholder(id)`: labelled moving test card in the section's palette | Palette lookup by `SectionId` | Palette from the storyboard |
| `src/kit/index.ts` | The only import surface for sections | None | None |
| `src/style/tokens.ts` | `CANVAS`, `LETTERBOX_RATIO`, `LETTERBOX_PX`, `SAFE`, `PALETTE`, `WIRE`, `GRAIN`, `DEV` | All of the values; `GRAIN` repeats timeline seconds | Generate from the storyboard's `film.config.json`; derive `GRAIN` from section style; letterbox optional for 9:16 and 1:1 |
| `src/config.ts` | zod input props and defaults | None | None |
| `src/solo.tsx` | `placeholderRegistry`, `makeSoloRoot` | Composition id `Solo` | None |
| `src/Film.tsx`, `src/Root.tsx`, `src/index.ts` | The film composition from the timeline's duration, fps, size; registers the root; `debugSolo` | Composition id `Film` | None |
| `src/sections/registry.ts` | `SECTIONS`: `SectionId` to `Section`, the only file importing all of them | Eight sections | Generate from the timeline |
| `src/sections/<id>/entry.ts` | Solo entry per section | The section id string | Scaffold from a template |
| `src/components/AudioTrack.tsx` | `<Audio src={staticFile(timeline.audio.src)}>`, never trimmed or shifted | Comment about silence after 1:42 | Support a voice-over track and per-track gain, with ducking declared in the timeline |
| `src/components/Grain.tsx` | One 2304x1296 noise plate moved and flipped by seeded randoms each frame, `mixBlendMode: overlay`, opacity min(0.3, amount*0.22) | `assets/tex/grain.jpg`, the schedule | Generate the plate; schedule from the timeline |
| `src/components/Letterbox.tsx` | Two `#000` bars of `LETTERBOX_PX` | 65 px | Zero for none |
| `src/components/DevOverlay.tsx` | Section, open transition, cue ids, timecode and frame, drawn in the bars | None | None |
| `remotion.config.ts` | jpeg, overwrite, angle, bt709, jpeg quality 95, public dir `assets`, h264, 180 s delayRender | None | None |
| `package.json` scripts | `studio`, `render`, `render:final`, `still`, `grade`, `typecheck`, `shots`, `fonts`, `music` | Output file names | Name from the project |

### Hard-coded values to lift into one `film.config.json` (or the timeline) when making the skill

- Section id `07-outro` as the "black from here" marker: `grade.sh`, `black-check.py`, `final-review-frames.py`. Replace with `finish: { cutToBlackFrame, gradeOffFrom, endFade }`.
- Letterbox 65 px: `grade.sh`, `black-check.py`, `tokens.ts`, `Letterbox.tsx`.
- 30 fps: `shots.mjs`, `review-frames.mjs`, `s6-plates.mjs`, `flash-check.py` default.
- Composition ids `Film` and `Solo`, the `src/sections/<id>/entry.ts` convention, the `wbam-` cache names.
- File names `f%04d_t%06.2f`: used by `shots.mjs`, `review-frames.mjs`, `final-review-frames.py`, `sheet.py` labels; keep one shared helper.
- Frame constants in Python and TS that repeat timeline values (`scripts/01-recognition/common.py`, `src/sections/01-recognition/clock.ts`, `tokens.ts` `GRAIN`).
- Music file name in `analyze_music.py`; the hand windows for pumped regions.

---

## Briefs that worked: what the builder brief, boundary-review brief and final-review brief asked for, and why each part was there

### The builder brief (`docs/BUILD-GUIDE.md`, about 110 lines, given to each of eight builders with its style-bible page and transitions row)

| Part | What it asked | Why it was there |
|---|---|---|
| Identity paragraph | "You are building one section... seven other builders are working in this same working tree. The lead integrates." Format and tech in one line | Makes concurrency and ownership explicit so a builder does not edit what it does not own |
| Read order | Style bible, transitions, timeline, research files named on its page, tone file; "their timestamps are from an old cut: ignore those" | Prevents building to stale timing (the timeline had been re-cut after research was written) |
| Ownership table | Paths owned (section folder, plates, scripts, log, check renders); everything else read-only; changes requested under "Requests to lead" | One tree, eight writers: no conflicts. The requests became the lead's bug list |
| Process bans | No installs, no state-changing git, do not kill other people's processes | Shared laptop |
| The contract with a skeleton | Absolute time; compare frames not seconds; draw a valid frame across `renderRange`; handle `prev`/`next` as the owner or be placed; root `AbsoluteFill`; determinism; assets; Three.js; SVG filters | Each line is a failure the lead had already hit or expected; the "hard requirements" in the transitions doc are "not optional... the builder on the other side cannot see your code" |
| Kit table | Every helper with a one-line meaning | So nobody rebuilds a clock, a random or an envelope |
| The loop | Exact `shots.mjs` commands for stills, sheets, sequences, boundaries, full-res, bench, private bundle; "Open the images with the Read tool and look at them. A frame you have not looked at is not done"; what to look for | Makes looking a step, with a checklist (beautiful? legible at phone size? clipped by the letterbox? reads as the style? text exact?) |
| Typecheck line | `npx tsc --noEmit 2>&1 | grep "sections/<id>"` prints nothing | Other builders' errors scroll past; only your folder counts |
| Speed budget | 1.5 s per frame at full res; over budget means pre-render in Python, Blender or ffmpeg and play back from `assets/footage/<id>/`, with the tool list | Keeps the final render short and gives the escape hatch |
| Media policy | Code first; public-domain or CC0 through the stock MCP; record URL and licence; no paid generation | Rights |
| Order of work | Floor, depth, edges, cost, stop. "A film that exists beats a film that is ten percent more beautiful and did not render" | The single most important process rule; every section arrived |
| Deliverables | The component, plates and scripts, check stills (overview, boundaries, three clean full-size), and a log with fixed headings: What it is (three sentences), Shots (table), Transitions (with frame numbers checked), Assets (source, URL, licence, processing), Decisions (also appended with `log-decision.sh`), Cost (ms per frame), Known issues ("be honest; say what you would fix next"), Requests to lead | Makes the log the handover and the lead's triage input |

Keep for the skill: all of it. Add: an animatic frame for each shot (what the board said), a minimum type size, and a line telling the builder how to do a pass-through window check.

### The boundary-review brief (`docs/review/README.md`)

| Part | What it asked | Why |
|---|---|---|
| Role | "A reviewer looks and writes; it does not render, edit code, or touch git. Its one output is `docs/review/transition-NN-MM.md`" | Cheap, parallel, no side effects |
| Inputs | Frame dump: every frame from 12 before the window to 12 after, 24 to a sheet at 480 px labelled `f<frame>_t<sec>`, plus three full-size frames; `frames.json` | The reviewer sees the whole device, not a cherry-picked frame |
| Pre-empt false positives | "There is no grade yet... Do not report the absence of grain" | The grade is applied later; this cut reviewer noise |
| Read first | The row of the transitions table for this boundary and its handshake line; the style bible's rules and the two section pages | The reviewer judges against the promise |
| Six judgements | Does it do what the table says on the frames it says; broken frames (pop of black/white/wrong picture, a test card, missing image, a jump the device does not explain, a frozen frame where there should be motion); words (cut off, overlapped, crossed, too small); flash safety; named device or generic dissolve; does the incoming section start on a strong image | Covers the fault classes that actually occurred |
| Evidence rule | "Say what you see with frame numbers. Do not guess; if a 480 px tile cannot settle a point, name the frame and say the lead should look at it full size" | Avoids hallucinated detail; routes doubt to the lead |
| Output template | Verdict (PASS, PASS WITH FIXES, FAIL); cut frame, window, owner; What I saw (8 to 15 lines in frame order); Blockers; Should fix; Nice to have (each: frames, what is wrong, likely owner, smallest fix); Looked at | Triageable in seconds; fixes name an owner and a smallest change |
| Final message | Verdict and counts, three lines at most | Lets the lead read eight results at a glance |

Result: 0 blockers; four fix rounds that each improved a real fault (G27, G28, G30). Missing from it: motion, sound and phone-size tiles.

### The final-review brief (`docs/review/final-brief.md`)

| Part | What it asked | Why |
|---|---|---|
| Role | One fresh reviewer, on the finished file; "You have not seen this film being made. That is the point: judge what a viewer gets." Looks and writes | Fresh eyes found the one broken item |
| Inputs | Frame dumps from the **graded mp4**: half-second sheets (240 frames), every frame of the last three seconds and the first six of black, key full-size frames (section midpoints, cut frames, every fact, quote and thesis line, the frames either side of the cut to black, the mark) | The reviewer judges grade, grain, vignette and encode, not renders |
| Withheld | "Do not read transition reviews or section logs before you have written your findings: they would tell you what to expect." | Avoids priming |
| Read first | The tone file, the style bible's rules, the transitions table, the timeline cues | So it can check words and styles |
| Eight judgements | Broken frames; Words for every cue (on screen, exact, 1080p, phone), facts and quotes exact to the character including the attribution; eight styles distinct, name the weakest; boundaries; the last three seconds and the cut to black frame by frame; the grade; the outro and the mark; the arc (awe, dread, responsibility; not a horror trailer; does the film earn its last line) | Each maps to a risk the lead cared about |
| Not its job | "Flash safety is measured by the lead; report only what looks like a strobe or a saturated red field" | Measured things are measured |
| Output template | Verdict (SHIP, SHIP WITH FIXES, DO NOT SHIP); the film in ten lines; Broken; Polish in order of worth (at most eight); a Words table with every cue; Section by section; The last three seconds; Looked at | The "film in ten lines" proves the reviewer understood it; the Words table is the audit |
| Final message | Verdict, number of broken items and the top three polish items, six lines | Fast triage |

Result: SHIP WITH FIXES; one broken, eight polish. It also said honestly what it could not judge (motion, sync, exact entry frames), which is what the next version of the brief must cover.

### The handoff brief (the lead's own, `docs/HANDOFF-opus-showcase.md`), in one paragraph

Non-negotiables first (one shot and no questions; audio is the music only; deliverable is a finished watchable mp4; do not break the data architecture; keep the thesis), then "what showcase means" by section with starting-point looks, a tools menu with "check what is installed before deciding" and a 20-minute cap on the Blender decision, the research phase as one agent per brief with a fixed output (a paragraph, 10 to 20 references with links, what makes it read as that style, how to fake it in code), the style-bible and transitions-table the lead writes from the research, the build phase with ownership and a hard budget ("if an effect isn't working after a reasonable push, ship a simpler version that does work and note what was cut"), the review phase, the final phase with "don't loop forever", and the report spec (what was built, the agent roster and what each got wrong, what was cut, render stats). It worked because it fixed the order, the stop conditions and the report in advance; it cost the film a locked timeline that had to be lifted, so the next brief should say which locks may be lifted and by whom.
