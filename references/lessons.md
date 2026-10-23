# Lessons: gotchas from the first film, and what prevents them now

Every gotcha met on *We Built a Mind* (Firelight Innovations, 2026-10-12), the first
film made the way this skill directs films. Read this file when something breaks in a
way that looks familiar, and before you change a tool or a rule: most tools and rules
in this skill exist because of an entry below. A few entries (L13, L45, L46, L82) are
gotchas the first film did not meet; each says so.

Each entry has four parts:

- **Symptom**: what you see.
- **Cause**: why it happens.
- **Fix**: what was done on the first film, or what should have been done when it was
  left.
- **Now**: what in this skill prevents it: a tool in `scripts/`, a field in `data/`, a
  template, or a rule in SKILL.md. "Rule" means nothing checks it for you.

Numbers are from the first film unless a source is cited as [n]; the sources are listed
at the end, with the digest in `dev/references/` each came from. Frames are at 30 fps.
S0 to S7 are the first film's sections 00-hook to 07-outro; the map is in
`case-study-we-built-a-mind.md`. Paths are relative to a film's project root.

<!-- TOC -->
## Contents

- [Rendering](#rendering) (L1 to L13)
  - [L1. Two check runs deleted each other's bundle](#l1-two-check-runs-deleted-each-others-bundle)
  - [L2. Bundling slowed down as the assets grew](#l2-bundling-slowed-down-as-the-assets-grew)
  - [L3. A builder could not see its own frames inside a neighbour's window](#l3-a-builder-could-not-see-its-own-frames-inside-a-neighbours-window)
  - [L4. JPEG stills could not prove a pixel](#l4-jpeg-stills-could-not-prove-a-pixel)
  - [L5. Check stills overwrote each other](#l5-check-stills-overwrote-each-other)
  - [L6. A font's delayRender timed out under load](#l6-a-fonts-delayrender-timed-out-under-load)
  - [L7. One still hung for eleven minutes](#l7-one-still-hung-for-eleven-minutes)
  - [L8. A Three.js canvas ignored the film clock](#l8-a-threejs-canvas-ignored-the-film-clock)
  - [L9. A pinned or replayed clock showed the wrong plate](#l9-a-pinned-or-replayed-clock-showed-the-wrong-plate)
  - [L10. Text edges differed between two renders of one frame](#l10-text-edges-differed-between-two-renders-of-one-frame)
  - [L11. Overlay, grain and letterbox were baked into plates cut from the film](#l11-overlay-grain-and-letterbox-were-baked-into-plates-cut-from-the-film)
  - [L12. Edge blocks from a distortion filter](#l12-edge-blocks-from-a-distortion-filter)
  - [L13. WebGL fails without the right GL backend](#l13-webgl-fails-without-the-right-gl-backend)
- [Timing and frames](#timing-and-frames) (L14 to L22)
  - [L14. A section appeared one frame late](#l14-a-section-appeared-one-frame-late)
  - [L15. A literal in a section fired one frame late](#l15-a-literal-in-a-section-fired-one-frame-late)
  - [L16. A mark sat between two frames](#l16-a-mark-sat-between-two-frames)
  - [L17. A cue landed a frame late in a section drawn on twos](#l17-a-cue-landed-a-frame-late-in-a-section-drawn-on-twos)
  - [L18. Cue windows and drawn windows disagreed](#l18-cue-windows-and-drawn-windows-disagreed)
  - [L19. Write-ons were not whole on the cue's first frame](#l19-write-ons-were-not-whole-on-the-cues-first-frame)
  - [L20. The guessed cut missed the music](#l20-the-guessed-cut-missed-the-music)
  - [L21. The beat tracker drifted on a pad with no drums](#l21-the-beat-tracker-drifted-on-a-pad-with-no-drums)
  - [L22. Frame constants retyped in generators drifted from the timeline](#l22-frame-constants-retyped-in-generators-drifted-from-the-timeline)
- [Assets and fonts](#assets-and-fonts) (L23 to L29)
  - [L23. A baked plate no longer matched the timeline](#l23-a-baked-plate-no-longer-matched-the-timeline)
  - [L24. A plate was designed against a placeholder](#l24-a-plate-was-designed-against-a-placeholder)
  - [L25. A glyph was missing from the vendored font](#l25-a-glyph-was-missing-from-the-vendored-font)
  - [L26. Pillow could not read the vendored fonts](#l26-pillow-could-not-read-the-vendored-fonts)
  - [L27. Old-style figures read wrong](#l27-old-style-figures-read-wrong)
  - [L28. Generated clips at 24 fps juddered at 30](#l28-generated-clips-at-24-fps-juddered-at-30)
  - [L29. Baked assets were large and the commit question stayed open](#l29-baked-assets-were-large-and-the-commit-question-stayed-open)
- [Colour and encoding](#colour-and-encoding) (L30 to L35)
  - [L30. Letterbox bars came out grey against picture black](#l30-letterbox-bars-came-out-grey-against-picture-black)
  - [L31. Grain and lifted gamma over a black outro; grain in the bars](#l31-grain-and-lifted-gamma-over-a-black-outro-grain-in-the-bars)
  - [L32. The vignette looked like a dirty lens](#l32-the-vignette-looked-like-a-dirty-lens)
  - [L33. The faintest glow disappeared](#l33-the-faintest-glow-disappeared)
  - [L34. A video plate came back one level darker than its PNG](#l34-a-video-plate-came-back-one-level-darker-than-its-png)
  - [L35. Encoder ringing at the edge of the bars](#l35-encoder-ringing-at-the-edge-of-the-bars)
- [ffmpeg](#ffmpeg) (L36 to L40)
  - [L36. A time gate graded the first black frame](#l36-a-time-gate-graded-the-first-black-frame)
  - [L37. Filter order decided what the bars and the tags looked like](#l37-filter-order-decided-what-the-bars-and-the-tags-looked-like)
  - [L38. A long frame list broke ffmpeg's expression parser](#l38-a-long-frame-list-broke-ffmpegs-expression-parser)
  - [L39. A comma inside a filter expression split the filter graph](#l39-a-comma-inside-a-filter-expression-split-the-filter-graph)
  - [L40. A tool held the whole film in memory](#l40-a-tool-held-the-whole-film-in-memory)
- [Windows](#windows) (L41 to L46, and L82)
  - [L41. Python crashed reading timeline.json](#l41-python-crashed-reading-timelinejson)
  - [L42. The console could not print what the film says](#l42-the-console-could-not-print-what-the-film-says)
  - [L43. Tools that need bash](#l43-tools-that-need-bash)
  - [L44. A recursive delete can walk through a junction into assets/](#l44-a-recursive-delete-can-walk-through-a-junction-into-assets)
  - [L45. Inline JSON props fail on Windows](#l45-inline-json-props-fail-on-windows)
  - [L46. A generated ffmpeg command over 8192 characters](#l46-a-generated-ffmpeg-command-over-8192-characters)
  - [L82. A deep project folder made every render fail](#l82-a-deep-project-folder-made-every-render-fail)
- [Agents in one tree](#agents-in-one-tree) (L47 to L53)
  - [L47. Pipeline bugs were found by builders, not by the lead](#l47-pipeline-bugs-were-found-by-builders-not-by-the-lead)
  - [L48. Requests to lead stayed open at the end](#l48-requests-to-lead-stayed-open-at-the-end)
  - [L49. A shared machine made renders fail](#l49-a-shared-machine-made-renders-fail)
  - [L50. A section was built against test cards for its neighbours](#l50-a-section-was-built-against-test-cards-for-its-neighbours)
  - [L51. One section had to wait for all the others](#l51-one-section-had-to-wait-for-all-the-others)
  - [L52. Builders could not watch their section play](#l52-builders-could-not-watch-their-section-play)
  - [L53. A builder improvised around a missing tool](#l53-a-builder-improvised-around-a-missing-tool)
- [Reviews](#reviews) (L54 to L68)
  - [L54. Reviews judged stills, not motion](#l54-reviews-judged-stills-not-motion)
  - [L55. A half-second sample missed seven-frame words](#l55-a-half-second-sample-missed-seven-frame-words)
  - [L56. The final review was not repeated after the fixes](#l56-the-final-review-was-not-repeated-after-the-fixes)
  - [L57. A review dump did not reach the neighbour's first line](#l57-a-review-dump-did-not-reach-the-neighbours-first-line)
  - [L58. Nobody listened with sound](#l58-nobody-listened-with-sound)
  - [L59. 480 px tiles could not settle fine detail](#l59-480-px-tiles-could-not-settle-fine-detail)
  - [L60. Reviewers would have reported what was not built yet](#l60-reviewers-would-have-reported-what-was-not-built-yet)
  - [L61. A tape tear read as a web glitch](#l61-a-tape-tear-read-as-a-web-glitch)
  - [L62. A painted eyelid had an angular edge and a one-frame ignition](#l62-a-painted-eyelid-had-an-angular-edge-and-a-one-frame-ignition)
  - [L63. Falling paper crossed the fact](#l63-falling-paper-crossed-the-fact)
  - [L64. A chart said the opposite of its fact](#l64-a-chart-said-the-opposite-of-its-fact)
  - [L65. Small type failed on a phone](#l65-small-type-failed-on-a-phone)
  - [L66. The line that sets up the thesis was the thinnest](#l66-the-line-that-sets-up-the-thesis-was-the-thinnest)
  - [L67. The last picture frame was a held card](#l67-the-last-picture-frame-was-a-held-card)
  - [L68. A fade dropped in steps](#l68-a-fade-dropped-in-steps)
- [Facts, rights and flash safety](#facts-rights-and-flash-safety) (L69 to L76)
  - [L69. Script facts failed after the script was written](#l69-script-facts-failed-after-the-script-was-written)
  - [L70. The fact-check ran out of search budget](#l70-the-fact-check-ran-out-of-search-budget)
  - [L71. Charts and counters can invent data](#l71-charts-and-counters-can-invent-data)
  - [L72. Two figures were torn into one](#l72-two-figures-were-torn-into-one)
  - [L73. A stamp contradicted its picture, and its id kept the old claim](#l73-a-stamp-contradicted-its-picture-and-its-id-kept-the-old-claim)
  - [L74. Rights were left to the end](#l74-rights-were-left-to-the-end)
  - [L75. Fast cuts between light and dark fields were a flash per cut](#l75-fast-cuts-between-light-and-dark-fields-were-a-flash-per-cut)
  - [L76. The grade can push a near transition over the line](#l76-the-grade-can-push-a-near-transition-over-the-line)
- [Cost](#cost) (L77 to L81)
  - [L77. No per-agent cost was recorded](#l77-no-per-agent-cost-was-recorded)
  - [L78. A pure-code section was built by the strongest model](#l78-a-pure-code-section-was-built-by-the-strongest-model)
  - [L79. Cheap research was fine for technique, not for facts](#l79-cheap-research-was-fine-for-technique-not-for-facts)
  - [L80. The render stayed fast because heavy work was pre-rendered](#l80-the-render-stayed-fast-because-heavy-work-was-pre-rendered)
  - [L81. A standing model rule and the brief disagreed](#l81-a-standing-model-rule-and-the-brief-disagreed)
- [What to change next time, and where this skill does it](#what-to-change-next-time-and-where-this-skill-does-it)
- [Sources](#sources)

<!-- /TOC -->

---

## Rendering

### L1. Two check runs deleted each other's bundle

- **Symptom.** 16 of 22 stills failed on the `film` target while a builder was
  rendering the same target.
- **Cause.** The bundle folder was named after the target and wiped at the start of
  every run.
- **Fix.** A private bundle folder per run (`--bundle <name>`).
- **Now.** `scripts/shots.mjs` gives every process its own bundle by default. Pass
  `--bundle <name>` only to reuse one.

### L2. Bundling slowed down as the assets grew

- **Symptom.** Every check run started slowly once `assets/` passed a gigabyte of baked
  plates.
- **Cause.** Remotion's `bundle()` copies the public folder into each bundle.
- **Fix.** Bundle with an empty public folder, then link `assets/` into the bundle (a
  junction on Windows).
- **Now.** `shots.mjs` bundles this way. Read L44 before you delete a bundle by hand.

### L3. A builder could not see its own frames inside a neighbour's window

- **Symptom.** Frames 130 to 163, 445 to 481, 2003 to 2014 and 2795 to 2823 could not be
  seen from the section that supplies them. Three builders each wrote their own
  pass-through entry and their own copy of `shots.mjs`.
- **Cause.** In the `Solo` composition the neighbours are test cards, and a test card
  that owns a transition never draws `prev` or `next`.
- **Fix.** A pass-through owner that draws the live section full frame over magenta, so
  any pixel nobody drew shows.
- **Now.** `node scripts/shots.mjs <id> --through` and the `Solo` composition's
  `through` prop. Check every window you supply, not only the ones you own.

### L4. JPEG stills could not prove a pixel

- **Symptom.** "Pure black", "exactly `#6fd3ff`" and "a 2 px line on rows 539 and 540"
  could not be read off the check stills. Two builders wrote lossless verifiers of
  their own.
- **Cause.** `shots.mjs` wrote JPEG at quality 88.
- **Fix.** Render PNG and assert numbers.
- **Now.** `shots.mjs --png` for pixel asserts; `black-check.py` measures black and the
  letterbox on the finished mp4.

### L5. Check stills overwrote each other

- **Symptom.** A full-size still was replaced by a later `--all` run that rendered the
  same frame.
- **Cause.** Stills are named `f<frame>_t<sec>.jpg` whatever the options.
- **Fix.** A tag in the file name.
- **Now.** `shots.mjs` gives the `--all` and `--boundaries` sheets unique default names.
  Put a set of stills you want to keep in its own folder with `--out <dir>`.

### L6. A font's delayRender timed out under load

- **Symptom.** `A delayRender() "font Anton" was called but not cleared after
  28000ms`. Two builders and the lead each lost a render while other renders ran; a
  clean re-run passed.
- **Cause.** On a loaded machine a tab took longer than Remotion's default limit to load
  its fonts. The docs give 30 s; their sample error reads 28000 ms [1][2].
- **Fix.** A 180 s limit with 3 retries in `font()`, and the same global limit in the
  config.
- **Now.** The template sets both: `delayRender(..., { timeoutInMilliseconds: 180000,
  retries: 3 })` in `src/kit/fonts.ts` and a 180 s limit in `remotion.config.ts`. Load
  every font through `font()`. Do not raise the limit further: a very long limit hides
  a stuck render [3].

### L7. One still hung for eleven minutes

- **Symptom.** A `--f` render sat on frame 2823 while several other renders ran. The same
  frame took 1.4 s on five other runs.
- **Cause.** Unknown; a shared machine. It did not happen again.
- **Fix.** A 120 s timeout per still, and a note to watch that frame in the final render
  (it rendered fine).
- **Now.** `shots.mjs --timeout <s>` turns a hang into an error. Run `npx remotion browser
  ensure` before the first render (SKILL.md, Phase 0; it downloads Chromium, so the user
  says yes first): Remotion traces most stalled renders to a browser mismatch [3].

### L8. A Three.js canvas ignored the film clock

- **Symptom.** A 3D shot froze, or ran on the wrong frame, when S6 replayed or pinned S5
  inside a transition window.
- **Cause.** react-three-fiber renders in its own React root, so the kit's clock context
  does not reach inside `<ThreeCanvas>`. `ThreeCanvas` also runs no frame loop of its
  own; animation must come from the frame [4].
- **Fix.** Call `useFilmTime()` outside the canvas, pass `frame` in as a prop, and drive
  every object from that prop.
- **Now.** Rule; the kit cannot enforce it. `FilmClockOverride` replays a subtree on one
  absolute frame, and it reaches a canvas only through that prop. See "Three.js" in
  `references/04-architecture.md`.

### L9. A pinned or replayed clock showed the wrong plate

- **Symptom.** A section playing an image sequence showed the wrong plate when its
  neighbour froze or replayed it inside a window.
- **Cause.** The plate index came from a local clock (`useCurrentFrame()` inside a
  `Sequence`).
- **Fix.** Index plates by the film clock, one plate frame per film frame.
- **Now.** Rule: read time only through `useFilmTime()`. It is absolute, and it follows
  `FilmClockOverride`.

### L10. Text edges differed between two renders of one frame

- **Symptom.** 200 or more pixels differed by up to 3/255 on text. On held frames of a
  scaled image the mean difference was 0.5/255.
- **Cause.** Chromium's text rasteriser and image resampling are not bit-stable. The
  frame functions were pure.
- **Fix.** Determinism checks with a stated tolerance (at most 3/255 on at most 0.05
  percent of the pixels); exact asserts only on frames with no text. Frames without text
  were bit-identical across renders.
- **Now.** `diff-frames.py <old.mp4> <new.mp4>` has a `--threshold` (default 2.0) below
  which a frame counts as unchanged, so this noise does not read as a change. Keep exact
  pixel asserts for frames without text.

### L11. Overlay, grain and letterbox were baked into plates cut from the film

- **Symptom.** S6 slices, scales and tiles frames of the film. Bars baked into those
  frames would have shown as black bands inside its mosaic.
- **Cause.** The stills were rendered with the dev overlay, the grain and the letterbox.
- **Fix.** A `bare` prop on the `Film` composition and `--bare` in `shots.mjs`.
- **Now.** `Film` takes `bare`; `shots.mjs --bare`; `plates-from-film.mjs <plates.json>`
  renders bare stills. `data/props.final.json` turns the overlay off for the final.

### L12. Edge blocks from a distortion filter

- **Symptom.** Black and coloured blocks at the frame edge on frames 2817 to 2823 of S6's
  seizure.
- **Cause.** Slices travelled further than the filter's overscan (240 px). On two frames
  they also dragged in the source picture's own dark gaps.
- **Fix.** Overscan of 420 px, more than the furthest a slice travels (372 px); slipped
  slices stop where the solid light ends on their rows.
- **Now.** Rule: give an SVG filter a region (`filterUnits="userSpaceOnUse"`) larger
  than the frame by more than its largest displacement, or blurs and slips clip at a
  hard rectangle ("SVG filters and other slow CSS" in `references/04-architecture.md`).
  Boundary reviewers look at the frame edges.

### L13. WebGL fails without the right GL backend

- **Symptom.** Not met on the first film. A render fails with "Failed to acquire WebGL2
  context", or 3D is very slow.
- **Cause.** Remotion 4 lets Chrome choose the GL backend. `angle` needs a GPU; a machine
  without one needs `swangle` [5].
- **Fix.** Set the backend for the machine.
- **Now.** The template sets `angle` in `remotion.config.ts`; pass `--gl=swangle` on a
  machine without a GPU. `npx remotion gpu --gl=angle` prints Chrome's GPU status [5].

---

## Timing and frames

### L14. A section appeared one frame late

- **Symptom.** The cut to black landed a frame late. On frames 158, 2015, 2795 and 2996
  the previous section was still mounted.
- **Cause.** `timeline.json` stored seconds to four decimals. 99.8667 is a hair after
  frame 2996 (2996 / 30 = 99.86666...), so a comparison in seconds put that frame on
  the wrong side of the boundary.
- **Fix.** Snap every time to its frame when the timeline loads, compare whole frames in
  every lookup, and do the same in the grain schedule.
- **Now.** The kit snaps every time it reads at load. `check-timeline.py` expects
  frame-aligned times (it warns when one is more than a quarter of a frame off).
  `black-check.py` fails if a frame in `checks.black` is not black.

### L15. A literal in a section fired one frame late

- **Symptom.** `t >= 5.2667` fired on frame 159, not 158.
- **Cause.** Typed seconds are not frame-aligned.
- **Fix.** Compare frames: `frame >= F(5.2667)`, or use the kit's snapped
  `cue(id).from` and `mark(name)`. One builder kept every window as a frame number in a
  `times.ts`.
- **Now.** Rule: never compare typed seconds. Read every time from the kit.

### L16. A mark sat between two frames

- **Symptom.** A measured mark at 16.0833 s fell halfway between frames 482 and 483.
- **Cause.** Marks were measured in seconds and never checked against the frame grid.
- **Fix.** Snap on load (L14), move the mark to frame 482, log it.
- **Now.** The kit snaps marks at load. `snap.py` reports every mark, boundary and cue
  start in frames against the nearest measured event.

### L17. A cue landed a frame late in a section drawn on twos

- **Symptom.** A cue that starts on frame 609 first appeared on 610, in a section whose
  drawings change on even frames.
- **Cause.** The drawing schedule was phased to frame 0, not to the cue.
- **Fix.** Re-phase the twos at the cue, so its first frame is its own drawing (one
  sheet then showed for a single frame).
- **Now.** Rule: phase a hold from the event it serves, for example
  `F(c.from) + hold(frame - F(c.from), 2)`.

### L18. Cue windows and drawn windows disagreed

- **Symptom.** A quote cue ended at 28.70 s while its words had to stay to 28.93. A lower
  third's cue ran to 15.0 s while nothing could be on screen after 14.87. A data cue was
  drawn one frame before its `from`. Two cues' words held 3 and 5 frames past `to`.
- **Cause.** A handshake or a bar start won over the cue window, and nothing compared
  the two.
- **Fix.** Move the cue's `to` where the handshake was the truth; otherwise log the
  difference.
- **Now.** A cue may carry `"shown": { "from": s, "to": s }` when what is drawn differs
  from the readable window. `check-timeline.py` reports a `shown` that runs outside its
  section's render range. Nothing compares `shown` with the pixels: look at the frames.

### L19. Write-ons were not whole on the cue's first frame

- **Symptom.** On a cue's `from` frame the viewer saw "Disea", "Poverty endec", "The top
  1% alre".
- **Cause.** The write-ons started on the cue's first frame.
- **Fix.** Not taken (polish backlog): start the entrance 6 to 10 frames early.
- **Now.** Rule: a cue's `from` means "readable by". Start entrances early and record
  the drawn span in `shown`. `film-frames.py` samples every cue's first frame + 2, so
  the final review sees a late entrance.

### L20. The guessed cut missed the music

- **Symptom.** The hand-placed boundaries missed the track's real events by 0.5 to 1.5 s.
  The whole film was re-timed mid-run: all seven boundaries moved. Research files then
  carried stale timestamps that builders were told to ignore.
- **Cause.** Timing was set before the track was measured, and the beat and script locks
  were lifted during the run.
- **Fix.** Measure the track (beats, onsets, hits, structure, loudness, energy per frame
  by band), move every boundary onto a measured event, and log every lifted lock. The
  re-time was a data edit plus plate rebuilds, not a rewrite.
- **Now.** Music comes first in Phase 1 (`analyze_music.py`). `snap.py` exits 3 when a
  boundary is more than `--tol` frames (default 2) from a measured event. Times live
  only in `data/timeline.json` and freeze at the animatic sign-off. Log any lift with
  `log-decision.py`.

### L21. The beat tracker drifted on a pad with no drums

- **Symptom.** The tracker said 63.0 BPM (a beat every 0.952 s), but the pump fitted at
  0.9585 s. The tracked grid drifted up to 0.1 s, so the last pulse of a stretch would
  have missed by two frames.
- **Cause.** A tracker such as librosa's `beat_track` estimates one global tempo and fits
  the beats to it [6]. A pad with soft attacks gives it little to lock to.
- **Fix.** Fit period and phase directly against the onset envelope over the pumped
  stretch, then snap each pulse to the nearest real onset within 0.06 s.
- **Now.** `snap.py` measures against onsets and structure points as well as the beat
  grid, so a drifting grid shows up as boundaries far from onsets. Cutting to the track
  is in `references/music.md`. No agent can hear the result; the human watch with sound
  is the last check (L58).

### L22. Frame constants retyped in generators drifted from the timeline

- **Symptom.** Python plate generators hard-coded film frames ("keep in step with
  clock.ts"). A grain schedule in the style tokens repeated seconds that also lived in
  the timeline.
- **Cause.** No single place for constants outside `timeline.json`.
- **Fix.** Partly done: generators read their words and cut points from
  `data/timeline.json`.
- **Now.** Rule: generators read times from `data/timeline.json`, sections from the kit;
  neither retypes them. A chain's `inputs` can name `data/timeline.json#cues:<section>`
  or `#section:<id>`, so `chain.py check` marks its plates stale when those words or
  times change.

---

## Assets and fonts

### L23. A baked plate no longer matched the timeline

- **Symptom.** Change a cue or a time in S0 or S2, and the film still showed the old
  words. S6 would have shown old frames after any change upstream.
- **Cause.** S0 and S2 baked their words into WebP sheets; S6 was cut from frames of the
  finished film. Only S6 had a guard (a checksum per plate that cancelled the render and
  named the command to run).
- **Fix.** A documented rebuild command per section, and the guard.
- **Now.** Every baked section declares a chain in `data/chains.json` (inputs, outputs,
  build, check). `python scripts/chain.py run <name>` rebuilds it. `chain.py check` and
  `doctor.py` (before every full render) fail on a stale chain.

### L24. A plate was designed against a placeholder

- **Symptom.** S6's last word was set in black letters on a placeholder plate. On the
  real plate the letters vanished into its black surround. Relit in bone, two letters
  then sat on the plate's own caption.
- **Cause.** The placeholder was the design reference, and a measured constant (the
  caption's top edge) came from one plate.
- **Fix.** Bone letters over a lifted plate, fitted to a band that ends 36 px above the
  caption; a note to re-measure if that plate or caption moves.
- **Now.** Design a frame you inherit against the real one: `shots.mjs <id> --through`,
  or the plates `plates-from-film.mjs` renders. Put the plate a constant was measured on
  in the chain's `inputs`, so a change upstream marks it stale.

### L25. A glyph was missing from the vendored font

- **Symptom.** IBM Plex Mono has no U+2205 (the empty-set sign). A fallback font would
  have made the render depend on the machine.
- **Cause.** The face does not have the glyph.
- **Fix.** Draw it as SVG.
- **Now.** Rule: check every special character against the vendored face before the
  storyboard locks. `doctor.py` checks that every `font("X")` is vendored, not that
  every glyph exists.

### L26. Pillow could not read the vendored fonts

- **Symptom.** A Python generator that letters its own plates could not open the kit's
  fonts.
- **Cause.** The fonts were vendored as woff2; Pillow reads TTF and OTF only.
- **Fix.** Unpack the woff2 to TTF with fontTools, into `work/`.
- **Now.** Rule: unpack into `work/<id>/fonts/`. Never put converted fonts in `assets/`
  or in git.

### L27. Old-style figures read wrong

- **Symptom.** Cormorant's default figures made "10" look like "1o".
- **Cause.** The face's default numerals are old-style.
- **Fix.** Lining numerals (`font-variant-numeric: lining-nums`).
- **Now.** Rule for the style bible: name the figure style of every face that sets a
  number, and look at every figure at phone size.

### L28. Generated clips at 24 fps juddered at 30

- **Symptom.** A slow drift on a generated face juddered faintly.
- **Cause.** Two generated clips were 24 fps, conformed to 30 by repeating every fifth
  frame.
- **Fix.** Not done: flow interpolation on a face risks worse artefacts than a held
  frame.
- **Now.** Ask for generated footage at the film's fps, and record each clip's frame
  rate with `log-asset.py`. A repeated frame every fifth frame shows as a regular dip to
  zero in the `motion-check.py` trace.

### L29. Baked assets were large and the commit question stayed open

- **Symptom.** 33.7 MB of hook WebP, 74 MB of JPEG plates, 79 MB of charcoal sheets,
  against a budget of 250 MB a section. Whether to commit them was still an open request
  at the end.
- **Cause.** Baked image sequences.
- **Fix.** Scripts regenerate them; `work/` and `out/` were never committed.
- **Now.** Chains make every baked asset rebuildable. Decide commit-or-rebuild in Phase 4
  (`references/07-final-and-delivery.md`, section 11: commit large plates, or ignore them
  and record the rebuild command) and keep it in the report's Requests-to-lead queue with
  an owner (`templates/report.md`). Media whose licence does not allow a copy stays out
  of git (SKILL.md, Phase 6, step 6).

---

## Colour and encoding

### L30. Letterbox bars came out grey against picture black

- **Symptom.** After the grade the bars were RGB 16 while the picture's black was 0.
- **Cause.** Remotion's default colour space wrote full-range `yuvj420p` tagged
  `bt470bg`. The grade re-tagged it as bt709 without converting the pixels.
- **Fix.** Render with `--color-space=bt709 --jpeg-quality=95`. The grade first converts
  to limited-range bt709, and forces the tags at the end.
- **Now.** The template's `remotion.config.ts` sets bt709 and JPEG quality 95.
  `grade.py` writes bt709 limited range and repaints the bars; `black-check.py`
  measures them; probe both files with `ffprobe` (SKILL.md, Phase 6). Remotion's pages
  disagree on what the default will be in 5.0, so keep setting it explicitly [7][8].

### L31. Grain and lifted gamma over a black outro; grain in the bars

- **Symptom.** True black turned into banded grey. Grain in the letterbox read as a
  fault.
- **Cause.** The grade ran over every frame.
- **Fix.** Grade, vignette and noise switched on only before the outro; the two bars
  painted black after the noise.
- **Now.** `timeline.grade.until` switches the grade off (null means the whole film);
  `grade.py` repaints the letterbox last; `black-check.py` measures `checks.black` and
  `checks.lastFrameBlack`.

### L32. The vignette looked like a dirty lens

- **Symptom.** White fields and a painted sky showed heavy dark corners.
- **Cause.** `vignette=PI/5` put the corner at about 40 percent.
- **Fix.** `PI/9` (corner near 80 percent), with contrast 1.05, saturation 0.97, gamma
  0.985 and `noise=alls=5:allf=t+u`.
- **Now.** Those are the example values in `timeline.grade`. Its `vignette: 0.35` gives
  an angle of 0.35 x PI/3, about PI/8.6. Look at the lightest frames after the grade.

### L33. The faintest glow disappeared

- **Symptom.** Light below about 4/255 was lost, and the rest of an ember's glow broke
  into 8 px blocks.
- **Cause.** JPEG frames, then two H.264 passes (render, then grade).
- **Fix.** Not taken: PNG frames for the final render would keep it. Accepted, because
  it is invisible at true brightness.
- **Now.** When a film's look lives in near-black, render the final with PNG frames
  (Remotion's `--image-format=png`; its docs recommend PNG frames where colour matters
  [7]) and
  compare a frame against a `shots.mjs --png` still.

### L34. A video plate came back one level darker than its PNG

- **Symptom.** A visible step where a video clip handed over to a freeze-frame PNG.
- **Cause.** `OffthreadVideo` returned a BT.709 H.264 plate about one level darker than
  the same frame drawn by `<Img>` (mean -1.0, -1.4 and -0.9 per channel).
- **Fix.** Make the last plates a JPEG sequence (quality 97, 4:4:4) drawn with `<Img>`,
  made by the same decode and scale as the PNG. It matched to 0.1 of a level.
- **Now.** Rule: do not switch between a video element and an image at a seam; if you
  must, measure the switch frame with `shots.mjs --png`.

### L35. Encoder ringing at the edge of the bars

- **Symptom.** The two bar rows that touch the picture read a few levels above black.
  Elsewhere the bars were at most 5 to 9 of 255.
- **Cause.** H.264 rings at a hard edge.
- **Fix.** The first film's bar check skipped the two rows that touch the picture and
  allowed 12 of 255 on the rest; black frames were allowed at most 2.
- **Now.** `black-check.py` measures the bars and the black ranges on the finished file.
  Read its numbers before you call a bar grey.

---

## ffmpeg

### L36. A time gate graded the first black frame

- **Symptom.** Frame 2996, the first frame of the cut to black, carried grain after the
  grade.
- **Cause.** `enable='lt(t,99.8667)'` is still true on frame 2996 (t = 99.86666...): the
  same rounding as L14.
- **Fix.** Gate on the frame number, `lt(n,2996)`, with the frame read from the
  timeline. A builder proved both gates on a test clip.
- **Now.** `grade.py` switches off at `grade.until`; that gate must compare frame
  numbers (`n`), not times. `black-check.py` fails if any `checks.black` frame is not
  black, so a wrong gate cannot pass unseen.

### L37. Filter order decided what the bars and the tags looked like

- **Symptom.** Grain in the bars (L31); wrong colour tags (L30).
- **Cause.** The order of the filters.
- **Fix.** One pass, in this order: convert to limited-range bt709
  (`scale=out_range=tv:out_color_matrix=bt709`, `format=yuv420p`); `eq` (contrast,
  saturation, gamma); `vignette`; `noise`; one `drawbox` per bar; `setparams` to force
  bt709 tags last. Then libx264 with `-movflags +faststart`, and `-c:a copy` so the
  music is never re-encoded.
- **Now.** `grade.py <in.mp4> <out.mp4>` does the grade from `timeline.grade`, repaints
  the letterbox, tags bt709 limited range and copies the audio.

### L38. A long frame list broke ffmpeg's expression parser

- **Symptom.** ffmpeg failed to parse a `select` expression of a few hundred terms.
- **Cause.** Its expression parser gives up on a long sum.
- **Fix.** Deal the frames into several `select` expressions of about 25 terms each.
- **Now.** `film-frames.py`, `black-check.py` and the other frame-dumping tools split
  long frame lists.

### L39. A comma inside a filter expression split the filter graph

- **Symptom.** ffmpeg rejects a filter graph, or reads half an expression as a new
  filter, when an expression contains a comma, for example `select='eq(n,12)'`.
- **Cause.** A comma separates filters. Inside an expression it must be escaped as `\,`,
  which a normal Python string writes as `"\\,"`.
- **Fix.** Escape it.
- **Now.** Every tool writes it that way. Pass ffmpeg's arguments as a list to
  `subprocess`, never through a shell, so no second layer of quoting applies.

### L40. A tool held the whole film in memory

- **Symptom.** A frame tool that decodes every frame first runs out of memory: 3600
  frames of 1920 x 1080 x 3 bytes are about 22 GB.
- **Cause.** Decoding the film into one array.
- **Fix.** Stream frames from ffmpeg's stdout one at a time.
- **Now.** Every tool in `scripts/` streams frames. Write per-section tools the same way.

---

## Windows

### L41. Python crashed reading timeline.json

- **Symptom.** `UnicodeDecodeError: 'charmap' codec can't decode byte ...` on a file
  with curly quotes.
- **Cause.** Python's default text encoding on Windows is the ANSI code page (cp1252),
  not UTF-8.
- **Fix.** `encoding="utf-8"` on every `open()`, or run `python -X utf8`.
- **Now.** Every tool in `scripts/` opens text as UTF-8. Do the same in per-section
  generators.

### L42. The console could not print what the film says

- **Symptom.** Printing a curly apostrophe, a dash or the empty-set sign raises
  `UnicodeEncodeError` or prints garbage.
- **Cause.** The Windows console is not UTF-8.
- **Fix.** Print ASCII; keep the exact strings in files.
- **Now.** Every tool prints plain ASCII lines. Write exact on-screen strings to files,
  not to the console.

### L43. Tools that need bash

- **Symptom.** The first film's `grade.sh`, `log-decision.sh` and a grade-gate proof
  needed Git Bash. The build guide's `| grep "sections/<id>"` filter does not exist in
  PowerShell.
- **Cause.** Tools written for a POSIX shell.
- **Fix.** None needed there: Git Bash was installed.
- **Now.** Every tool is Python or Node (`grade.py`, `log-decision.py`, `log-asset.py`).
  Filter typecheck output with `Select-String` in PowerShell, `grep` in Git Bash.

### L44. A recursive delete can walk through a junction into assets/

- **Symptom.** Prevented, not suffered: deleting a bundle folder that holds a junction to
  `assets/` would delete the film's assets.
- **Cause.** Some recursive deletes follow junctions.
- **Fix.** Unlink the junction before any recursive delete (`dropJunction`).
- **Now.** `shots.mjs` removes its junction first. Never delete an `out/.bundle/` folder
  by hand with `rm -rf` or `Remove-Item -Recurse` while its link to `assets/` exists.

### L45. Inline JSON props fail on Windows

- **Symptom.** Not met on the first film. `--props='{...}'` fails on Windows.
- **Cause.** The CLI does not support inline JSON props on Windows [9].
- **Fix.** Pass a file.
- **Now.** `npm run render:final` passes `data/props.final.json` as a file.

### L46. A generated ffmpeg command over 8192 characters

- **Symptom.** Not met on the first film. On Windows, a render with many audio layers
  fails with ENAMETOOLONG [10].
- **Cause.** Windows limits a command line to 8192 characters, and Remotion builds one
  long ffmpeg command [10].
- **Fix.** Mute silent clips, keep audio to a few tracks, or render in parts with
  `--frames` and join the parts with ffmpeg's concat [10].
- **Now.** The template has one `AudioTrack`. A voice-over film with many clips will meet
  this; plan its audio as few tracks.

### L82. A deep project folder made every render fail

- **Symptom.** Not met on the first film; met while testing this skill on Windows. Every
  render, still and animatic failed with an `ENOENT` spawn error. The error never
  mentions the path length.
- **Cause.** Remotion keeps its headless Chrome inside the project, under
  `node_modules/.remotion/`. The path of its executable adds 105 characters to the project
  path (call it about 110). Windows stops most programs at 260 characters, so a project
  path over about 150 fails. In the test, a 163-character project path gave a
  268-character Chrome path.
- **Fix.** Move the film to a short path, for example `C:\films\<slug>`, or scaffold it
  there.
- **Now.** SKILL.md, Phase 0 says to keep the path short, and `new-film.mjs` repeats it.
  `doctor.py` fails on Windows when the project path plus 110 characters passes 259.

---

## Agents in one tree

### L47. Pipeline bugs were found by builders, not by the lead

- **Symptom.** The frame-snap bug (L14), the colour-space bug (L30) and the grade-gate
  bug (L36) were all found by section builders measuring their own edges losslessly.
- **Cause.** The lead integrated at half size and judged by eye; builders measured exact
  pixels on the frames they owed.
- **Fix.** Every log had a "Requests to lead" heading. The lead fixed the kit three
  times while builders worked, and told all eight each time.
- **Now.** `templates/section-log.md` keeps "Requests to lead". `black-check.py` now
  catches all three by number on the finished file; the logs still matter, because they
  find what no check knows to look for.

### L48. Requests to lead stayed open at the end

- **Symptom.** Commit-or-rebuild for baked sequences, a pass-through harness request,
  cue-window corrections and footage-log edits were still open after the report.
- **Cause.** Requests were free text in eight logs.
- **Fix.** None; the report listed some.
- **Now.** `templates/report.md` keeps a Requests-to-lead queue with an owner and a
  status for each. Provenance no longer waits for the lead: any agent appends to
  `docs/rights.md` with `log-asset.py`.

### L49. A shared machine made renders fail

- **Symptom.** Font timeouts (L6), the eleven-minute hang (L7), and builders unable to
  find their own compile errors among seven others'.
- **Cause.** Eight builders and the lead shared one laptop: its Chrome renders, its
  Python processes, and one `tsc` over the whole tree.
- **Fix.** Build-guide rules: no installs, no state-changing git, do not kill processes
  you did not start, a few Python processes at most; a typecheck filtered to the
  builder's own folder.
- **Now.** SKILL.md's crew rules; a private bundle per process (L1), `--timeout` (L7),
  the 180 s font limit (L6). Builders still share one tree, so stagger heavy renders.

### L50. A section was built against test cards for its neighbours

- **Symptom.** S0's tear, S2's ink and S5's fall-through were first seen over the real
  neighbour at integration. S5 assumed S4's tallest tower sat at (960, 540) on frames
  2003 to 2014.
- **Cause.** Solo renders show neighbours as test cards.
- **Fix.** A handshake table of exact pixels and frames. Every promise in it held in the
  final film.
- **Now.** `docs/transitions.md` (from `templates/transitions.md`) says what each side
  owes the other in pixels. `shots.mjs <id> --through` shows a window you supply.
  Integrate each section as it lands with `shots.mjs film --f <frames>` (SKILL.md,
  Phase 4).

### L51. One section had to wait for all the others

- **Symptom.** S6 could not start until the other seven were integrated, and every later
  fix to S0 to S5 meant three commands run by hand.
- **Cause.** Its plates were frames of the finished film.
- **Fix.** A manifest of plate times, a renderer for them, and a guard.
- **Now.** `plates-from-film.mjs <plates.json>` plus a chain in `data/chains.json`; run
  `chain.py run <name>` after any upstream fix (SKILL.md, Phase 5, step 4).

### L52. Builders could not watch their section play

- **Symptom.** Logs say motion was judged from stills and frame sequences, not from
  playback (a charcoal boil, the outro's held beat).
- **Cause.** Agents have no playback and no ears.
- **Fix.** Every-frame sheets.
- **Now.** `motion-check.py` (freezes, jumps, one-frame pops) and `sync-check.py`
  (picture change against onsets) turn motion into numbers. The user watches with sound
  at the end (L58).

### L53. A builder improvised around a missing tool

- **Symptom.** No face-landmark model was installed and installs were banned, so a
  builder wrote a face tracker from corners and optical flow. Blender was installed in
  the background during setup, with a 20-minute cap on the decision.
- **Cause.** The tool set was decided during the run.
- **Fix.** The improvised tracker worked; Three.js stayed the baseline for 3D.
- **Now.** Decide the tool set at intake (SKILL.md, Phase 0) and say in each builder
  brief what is installed. Builders do not install (crew rules), and the lead installs
  nothing without the user's yes (SKILL.md, rule 11).

---

## Reviews

### L54. Reviews judged stills, not motion

- **Symptom.** All eight boundary reviews and the final review read frames. Nobody judged
  movement, and the final reviewer said so.
- **Cause.** Briefed that way; the inputs were contact sheets.
- **Fix.** None on the first film.
- **Now.** `review-frames.mjs` adds a motion trace (from `motion-check.py`) and a
  phone-size sheet to every window. In Phase 5 run `motion-check.py out/pass1.mp4
  --sections` and `sync-check.py out/pass1.mp4 --sections`. Not adopted: short clips
  or GIFs per window.

### L55. A half-second sample missed seven-frame words

- **Symptom.** The final reviewer never saw two of the four slam words and reported "not
  sampled". The lead found them on the graded file.
- **Cause.** One frame every 15, plus the midpoints of `data`, `quote`, `thesis` and
  `logo` cues only.
- **Fix.** The lead looked at the frames itself.
- **Now.** `film-frames.py` adds every cue's first frame + 2 and its midpoint, every
  transition's first and last frame, and phone-size sheets.

### L56. The final review was not repeated after the fixes

- **Symptom.** The chart fix (L64) and a heavier line (L66) were checked only by the
  lead's own look.
- **Cause.** Time; one review was planned.
- **Fix.** None.
- **Now.** Keep the first graded file; run `diff-frames.py <old.mp4> <new.mp4>`, then
  `final-review.js` with `mode: "diff"`, which writes `docs/review/final-2.md`.

### L57. A review dump did not reach the neighbour's first line

- **Symptom.** The Fall-through reviewer's frames ended on 2026, two frames before the
  incoming section's first line (2028). The Horizon-opens reviewer's frames began on
  1466, after the outgoing type had collapsed (1458 to 1465).
- **Cause.** A fixed margin of 12 frames either side of the window.
- **Fix.** The lead looked at the frames the reviewers named.
- **Now.** Before the review, read the boundary's row in `docs/transitions.md`: when a
  hold or a build-up starts before the margin, or the incoming section's first line
  lands just after it, widen the window for that boundary with
  `node scripts/review-frames.mjs <t-id> --margin <n>` (`references/06-review.md`,
  section 1). The final review's by-cue samples include every cue's first frame.

### L58. Nobody listened with sound

- **Symptom.** Sync to the music was set from measured beats and never checked by ear.
  The report said so.
- **Cause.** Agents cannot hear.
- **Fix.** None on the first film.
- **Now.** `sync-check.py` lists picture changes that miss the music's onsets. The last
  gate is a human watch of the graded file with the sound on, with the verdict in the
  report (`templates/report.md`; SKILL.md, Phase 6, step 6).

### L59. 480 px tiles could not settle fine detail

- **Symptom.** Reviewers wrote "the lead should look at f140 to f150 full size" and
  similar, for example whether the next section showed in the gaps at all.
- **Cause.** 24 tiles to a sheet at 480 px.
- **Fix.** Three full-size frames at each cut, and an evidence rule: name the frame, do
  not guess.
- **Now.** The evidence rule is in `templates/boundary-review-brief.md`. Check every
  frame a reviewer names yourself, on frames from the graded file (SKILL.md, Phase 6,
  step 4).

### L60. Reviewers would have reported what was not built yet

- **Symptom.** Avoided: boundary reviews ran before the grade, and a missing grain would
  have been reported as a fault.
- **Cause.** Reviewers judge what they see.
- **Fix.** The brief said that there was no grade yet, what the grade would add later,
  and not to report the absence of grain.
- **Now.** Rule: say in every review brief what is applied later (grade, grain,
  vignette, audio).

### L61. A tape tear read as a web glitch

- **Symptom.** On frames 137 to 157 the tear was clean slices, each carrying a different
  clip, with coloured block noise in the gaps. The next section was black in the gaps
  for 20 frames.
- **Cause.** The tear was built from block and pixel-sort slices, and the next section
  sat at luma 0.06 under it.
- **Fix.** One picture losing tracking (noise bars, ragged line edges, re-lock, hooked
  bands, vertical roll), fine grey snow; the next section lifted with `brightness(3.0)`
  easing to exactly 1.0 on the cut frame.
- **Now.** The transitions table names each device, and reviewers judge "the named
  device, or a generic one?" Board style frames for the hero moments (SKILL.md, Phase 3).

### L62. A painted eyelid had an angular edge and a one-frame ignition

- **Symptom.** The opening edge read as a polygon with a screen glow; a thin line took
  the light in a single frame.
- **Cause.** 81 points with 21 px of noise; a one-frame step in weight, brightness and
  colour.
- **Fix.** A smooth almond sampled every 6 px, a paint rim 3 to 18 px thick, a 5 px
  bloom on the burst only; the ignition spread over four frames, each 1.35 to 1.55 times
  the weight of the one before.
- **Now.** `motion-check.py` on the window shows a one-frame step as a spike in its
  trace. Look at edges full size.

### L63. Falling paper crossed the fact

- **Symptom.** Torn strips crossed the key data line on frames 1904 to 1906 and 1926 to
  1927.
- **Cause.** The strips swung right, about a pivot below the frame.
- **Fix.** Drop straight out of frame, leaning left, never right of where torn.
- **Now.** Rule: nothing moves across a `data` or `quote` cue while it is up. The final
  review's Words table checks every cue for crossings.

### L64. A chart said the opposite of its fact

- **Symptom.** The one broken item in the film: 18 lit cells in a framed row of 20, with
  the other 82 as faint outlines, read on a phone as a meter nine tenths full beside
  "fewer than 1 in 5".
- **Cause.** Hairline outlines vanish at phone size, and a bright framed row reads as a
  bar.
- **Fix.** Empty cells as grey tiles (fill 0.15, 2 px outline at 0.5), no frame. The
  counts did not change.
- **Now.** Phone-size sheets (360 px tiles) in every review input (`review-frames.mjs`,
  `film-frames.py`), and a fresh final reviewer (SKILL.md, rule 6). The chart had passed
  its builder, the lead and eight boundary reviewers.

### L65. Small type failed on a phone

- **Symptom.** Source lines at 20 to 24 px, a key fact at 36 to 40 px, sixteen names and
  an attribution label were too small on a phone. The closing tagline's x-height was
  0.6 mm on a phone held upright (the frame is about 68 mm wide).
- **Cause.** Sizes were judged on 1080p stills.
- **Fix.** The outro went up one step (tagline 44 px, credit 48 px, name 66 px); the
  rest went to the backlog.
- **Now.** The style bible states minimum type sizes as numbers, for example body 54 px
  and source lines 32 px at 1080p, scaled with height (`templates/style-bible.md`).
  Every review input has phone-size sheets.

### L66. The line that sets up the thesis was the thinnest

- **Symptom.** The final reviewer put "Then we told it what we wanted." first among the
  polish items: thin capitals over floor glare, marginal on a phone.
- **Cause.** Type weight was set per section, not by the line's job in the film.
- **Fix.** Heavier and larger (weight 700 at 62 px), with a second scrim over the glare.
- **Now.** Rule for the style bible: rank lines by what they carry, the `thesis` and its
  set-up first. The final review judges the arc.

### L67. The last picture frame was a held card

- **Symptom.** The last word sat unchanged for 28 frames over a 4:3 gate with black
  sides; the densest frame of the film was a second earlier.
- **Cause.** A 2 percent push, and a plate kept at its own aspect.
- **Fix.** Not taken (backlog): fill the width or push harder, so the cut lands on a
  frame that still moves.
- **Now.** Board the last frame before the cut as a hero style frame (SKILL.md,
  Phase 3). The final review brief asks whether the last picture frame is the strongest.

### L68. A fade dropped in steps

- **Symptom.** The closing mark went from full to gone in about 8 frames, with steps of 80
  and 69 levels.
- **Cause.** A 10-frame cubic fade with a focus pull on top; blur lowers the peaks faster
  than the opacity does.
- **Fix.** Linear opacity over 13 frames, no blur on the way out, the ember last.
- **Now.** `motion-check.py` on the window shows the step. When a fade matters, write its
  peak value per frame in the section log.

---

## Facts, rights and flash safety

### L69. Script facts failed after the script was written

- **Symptom.** A headline figure had no source. An adoption figure was unsupported. A
  wealth share was stale. A quote was reworded ("erase" for "eliminate", an inserted
  "all"). A signatory count was unconfirmed. A caption said "private" where the source
  did not.
- **Cause.** The script was written before the fact-check.
- **Fix.** A `facts.md` with a verdict per claim and the primary source; cues rewritten
  to it; every `data` cue carries a `source` drawn on screen. A one-word attribution fix
  was a data edit with no code change, because the section read the cue live.
- **Now.** Facts are their own step before the storyboard gate (SKILL.md, Phase 2,
  step 4): `fact-check.js`; the `docs/research/facts.md` table (verdict, as of,
  re-verify by, check A, check B); on-screen words equal to the verified wording.
  `check-timeline.py` warns when a `data` or `quote` cue has no row, or a verdict other
  than `verified` or `corrected`.

### L70. The fact-check ran out of search budget

- **Symptom.** Claims came back marked "secondary". Several publishers' pages would not
  open (HTTP 451 and 403).
- **Cause.** The web-search limit was shared by every agent in the turn. Some publishers
  block fetch tools.
- **Fix.** The lead spot-checked three primary sources itself. The report told the user
  to re-verify on the day of posting, because the figures move quarterly.
- **Now.** `fact-check.js` runs two independent checkers with different search
  approaches, then a reconciler, and gives each checker its own search budget (its
  `searches` argument). Every row has a re-verify-by date, and the report lists what to
  re-verify.

### L71. Charts and counters can invent data

- **Symptom.** A counter that counts up passes through figures nobody published. A bar
  between two dollar figures implies a ratio their sources do not make. A decorative
  readout looks like a claim.
- **Cause.** Motion-design habit.
- **Fix.** The figure correct and locked on its first frame; the only count a short reel
  spin between two cue figures; a push into the numeral instead of a bar; readouts that
  measure the plate under them.
- **Now.** Rule (SKILL.md, rule 9; `references/safety-and-rights.md`). The test is the UK
  statistics code's: a number on screen must not be materially misleading [11].

### L72. Two figures were torn into one

- **Symptom.** Frames 2897 to 2899 interleaved bands of two plates that carried different
  figures, making a figure that is in no source. An 11 px colour split made "10 to 20"
  read "110 to 20".
- **Cause.** Two figure plates were neighbours in the cut list, and the tear works band
  by band.
- **Fix.** Plates that carry a figure are named in the cut list and never neighbours; a
  cut between two figure plates is whole; a colour split on a figure plate is capped at
  4 px.
- **Now.** Rule for any section that reuses the film's frames: list the plates that carry
  figures and keep them apart. The final review's Words table checks every figure.

### L73. A stamp contradicted its picture, and its id kept the old claim

- **Symptom.** A "Christmas 1962" title sat over a summer picture with no tree, on a
  format (Super 8) that went on sale in 1965. The cue was reworded to "Summer 1966",
  but its id `stamp-1962` stayed, so the id and the text disagreed.
- **Cause.** The cue was written before the plate existed, and the id carried content.
- **Fix.** Reword the cue to match the plate; rebuild the baked plates.
- **Now.** Ids are role-based (`stamp-1`, `slam-2`, `data-3`), never content, and
  `check-timeline.py` warns on a cue id that is not. Give a dated or period claim a row in
  `facts.md` even when its role is `stamp`, and check generated stills against their
  captions.

### L74. Rights were left to the end

- **Symptom.** At the end the music was not cleared, a drawing traced from a broadcast
  interview needed a decision, and every face in two sections was generated.
- **Cause.** Rights were treated as the user's problem after the film.
- **Fix.** The report listed them; the film says "generated" on screen.
- **Now.** `docs/rights.md` from intake (`templates/rights.md`), filled by every agent
  with `log-asset.py`, its state in the report; the rights stance is an intake question
  (SKILL.md, Phase 0). Why it matters: a rights holder can block, mute or monetise a
  matched upload [12]; a traced likeness is a derivative, and a commercial use with the
  same purpose as its source weighs against fair use [13]; the EU AI Act asks for
  disclosure of generated media that could pass as real, from 2 August 2026 [14].

### L75. Fast cuts between light and dark fields were a flash per cut

- **Symptom.** Three flashes in one second on a deep rewind. A vertical roll and late
  throw-backs measured three on the real eye.
- **Cause.** A flash is a pair of opposing changes in relative luminance of 10 percent or
  more, the darker state below 0.80, over more than a quarter of the screen; more than
  three in any one second fails [15][16]. A hard cut between a bone field and a black one
  is one such change on its own.
- **Fix.** Level each plate's mean luminance into a band (0.10 to 0.42, linear light).
  Tear violent cuts into horizontal bands dealt over up to five frames, so no frame moves
  more than 0.16 of the screen one way. Past a plate every other frame, divide the frame
  (a quadtree mosaic) instead of cutting faster. Cap seizure slips at three frames. The
  worst second measured 1 to 2 flashes. The brief had asked for strobe; the cap held.
- **Now.** `flash-check.py <mp4|dir>` (exit 3 on FAIL) on each section's frames and on
  the graded film. Design from its numbers, not after them. Avoid long flashing
  stretches (over five seconds) even under the limit [16].

### L76. The grade can push a near transition over the line

- **Symptom.** A boundary reviewer measured per-frame changes of 0.20 and 0.21 on tiles,
  close to the threshold, before the grade.
- **Cause.** The grade adds contrast after the section's own check.
- **Fix.** Flash-check the graded file.
- **Now.** SKILL.md, Phase 6, step 2: `flash-check.py out/<slug>-graded.mp4` must pass.
  Its default area is the broadcast reading (a quarter of the screen); for web delivery
  also run it with `--area 0.03` and judge each region that fails
  (`references/safety-and-rights.md`, section 2).

---

## Cost

### L77. No per-agent cost was recorded

- **Symptom.** Only plan-window percentages: the 5-hour window ended at 77 percent used;
  the weekly all-models limit went from about 15 to 19 percent.
- **Cause.** Nobody logged tokens or wall clock per agent.
- **Fix.** None.
- **Now.** `templates/report.md` has a cost table: tokens and wall clock per agent, from
  the task notifications. Say what a film costs at intake, and read the usage window
  before each fan-out (SKILL.md, "Before you start").

### L78. A pure-code section was built by the strongest model

- **Symptom.** S3 (type only, no assets, 30 to 42 ms a frame) used the same strong model
  as the 3D and baked sections.
- **Cause.** One model for every builder.
- **Fix.** None.
- **Now.** Route simple sections to a mid model (`references/05-build.md`, section 5;
  SKILL.md, rule 10).

### L79. Cheap research was fine for technique, not for facts

- **Symptom.** The cheap research briefs made good technique references. The fact-check,
  on the same tier and the same shared search budget, came back with four claims
  unverifiable or misworded.
- **Cause.** Facts need depth and primary sources; a technique brief does not.
- **Fix.** The lead re-checked against primary sources.
- **Now.** A cheap model for `research.js`; facts through `fact-check.js` (two checkers
  and a reconciler, on a mid model; SKILL.md, rule 10).

### L80. The render stayed fast because heavy work was pre-rendered

- **Symptom.** The good case: against a budget of 1.5 s a frame, sections cost 30 to 132
  ms a frame (worst 155 ms, on a blur filter), and the full render took 2 m 13 s to
  2 m 31 s for 3600 frames.
- **Cause.** Everything per-pixel (interlace, tape chroma, charcoal, gouache, face
  tracking) was done once in Python and played back with `<Img>`.
- **Fix.** Keep doing it.
- **Now.** A speed budget in every builder brief; `shots.mjs <id> --bench a:b` to measure
  it. Choose render concurrency with `npx remotion benchmark`. GPU-heavy CSS (blur,
  shadows, gradients) is slow: pre-render it [17].

### L81. A standing model rule and the brief disagreed

- **Symptom.** The user's standing rule (a mid model for sub-agents) and the brief
  (strong builders and a strong final reviewer) differed. Research moved to the
  cheapest tier at the user's request during setup.
- **Cause.** Model routing was not settled before the run.
- **Fix.** The lead logged which rule applied where.
- **Now.** Intake asks for the user's model rules (SKILL.md, Phase 0). Log the routing
  with `log-decision.py`.

---

## What to change next time, and where this skill does it

The first film's digest ends with nineteen changes for the next film. Each is marked
with where this skill now makes it: **Done**, **Partly** (what is still missing), or
**Not adopted**.

1. **Add an ideation stage.** Done: SKILL.md, Phase 1. About eight one-line options, then
   three concepts and a wildcard (`concepts.js`), scored with a Pugh matrix against two
   datums, Murch's order as the tiebreak, a concept gate in checkpoint mode
   (`references/01-intake-and-ideation.md`).
2. **Storyboard and animatic before any builder starts.** Done: SKILL.md, Phase 3.
   Thumbnails, a beat board, `data/storyboard.json`, `npm run animatic`, and the
   animatic sign-off as the gate. Timing lives only in `data/timeline.json`; research,
   which runs before the storyboard, carries no times.
3. **Review motion, not only stills.** Partly: `motion-check.py`, and a motion trace in
   every `review-frames.mjs` window (L54). Not adopted: half-rate clips or GIFs.
4. **Someone has to listen with sound.** Done: `sync-check.py` generalises the first
   film's pump check to every section; the human sound gate is in the report (L58).
5. **Fact-check as its own phase, earlier, with depth.** Done: Phase 2, step 4,
   `fact-check.js`, the `facts.md` table, `check-timeline.py` warnings (L69), and a
   search budget per checker instead of one shared by the turn (L70).
6. **Decide rights and likeness at intake.** Done: `docs/rights.md` from
   `templates/rights.md`, `log-asset.py`, the Remotion licence check, the register's
   state in the report (SKILL.md, Phase 0).
7. **Track cost per phase and per agent.** Done: the cost estimate at intake, the usage
   check before each fan-out, the cost table in `templates/report.md` (L77). Simple
   sections go to a cheaper model (L78).
8. **Fold the harness gaps into the main script.** Done: `shots.mjs --through`, `--png`,
   `--timeout`, unique default sheet names for `--all` and `--boundaries`, a unique
   bundle per process (L1, L3, L4, L5, L7).
9. **One `doctor` command before any render.** Partly: `doctor.py` checks the timeline,
   chain freshness, vendored fonts, `staticFile()` paths, registry against timeline (it
   fails until Phase 4 gives every section a stub), `beats.json`, the pinned Remotion
   version, the Python modules and, on Windows, the project path length (L82). It does
   not check for empty frames in a render range or compare cue windows with what is
   drawn: use `shots.mjs <id> --all 1` and `shown` (L18).
10. **Separate "readable by" from "drawn".** Partly: cues take `shown`, and
    `check-timeline.py` reports a `shown` outside its render range. No script compares
    `shown` with the pixels (L18).
11. **Minimum type sizes in the style bible, and a phone-size render in every review.**
    Done: `templates/style-bible.md`; phone-size sheets in `review-frames.mjs` and
    `film-frames.py` (L64, L65).
12. **Sample the final review by cue, not by clock.** Done: `film-frames.py` (L55).
13. **Repeat the final review after fixes.** Done: `diff-frames.py` and
    `final-review.js` with `mode: "diff"` (L56).
14. **Automate dependent chains.** Done: `data/chains.json`, `chain.py`, `doctor.py`
    (L23, L51).
15. **Worktrees or staggered renders for parallel builders.** Partly: private bundles,
    per-still timeouts and the 180 s font limit; builders still share one working tree,
    and nothing caps concurrent Chrome tabs (L49).
16. **No content in ids.** Done: role-based ids (L73), and `check-timeline.py` warns on a
    cue id that is not role-based.
17. **Provenance as a script.** Done: `log-asset.py` appends to `docs/rights.md` (L48).
18. **Requests to lead as a queue.** Done: owner and status for each request in
    `templates/report.md` (L48).
19. **Name a cut list.** Done: an ordered cut list per section in `docs/storyboard.md`
    at storyboard time (SKILL.md, Phase 3), so a late squeeze is a decision.

One more from the digest's note on the first film's brief: **say which locks may be
lifted, and by whom.** Partly: the autonomy choice at intake and the animatic sign-off
are the locks; log any lift with `log-decision.py` (L20).

---

## Sources

From the digests in `dev/references/` (read 2026-10-22). Everything not cited comes from
the first film's own records, digested in `dev/references/wbam-lessons.md`.

1. Remotion, "delayRender() and continueRender()", https://www.remotion.dev/docs/delay-render (remotion-technical.md [11])
2. Remotion, "Debugging timeouts", https://www.remotion.dev/docs/timeout (remotion-technical.md [12])
3. Remotion, "Stuck renders", https://www.remotion.dev/docs/troubleshooting/stuck-render (remotion-technical.md [27])
4. Remotion, "ThreeCanvas" and "@remotion/three", https://www.remotion.dev/docs/three-canvas ; https://www.remotion.dev/docs/three (remotion-technical.md [20])
5. Remotion, "GL options" and "gpu" command, https://www.remotion.dev/docs/gl-options ; https://www.remotion.dev/docs/cli/gpu (remotion-technical.md [25])
6. librosa, "librosa.beat.beat_track" (docs v0.10.2), https://librosa.org/doc/0.10.2/generated/librosa.beat.beat_track.html (storyboard-music.md [13])
7. Remotion, "Encoding guide" and the "colorSpace" option, https://www.remotion.dev/docs/encoding/ ; https://www.remotion.dev/docs/options/color-space (remotion-technical.md [23])
8. Remotion, "Remotion 5.0 migration guide", https://www.remotion.dev/docs/5-0-migration (remotion-technical.md [31])
9. Remotion, "Configuration file" and "CLI render", https://www.remotion.dev/docs/config ; https://www.remotion.dev/docs/cli/render (remotion-technical.md [24])
10. Remotion, "ENAMETOOLONG on Windows", https://www.remotion.dev/docs/enametoolong (remotion-technical.md [28])
11. Office for Statistics Regulation (UK), "Code of Practice for Statistics", https://osr.statisticsauthority.gov.uk/publications/the-code-of-practice-for-statistics/pages/2/ (rights-safety-sourcing.md [35])
12. YouTube Help, "How Content ID works", https://support.google.com/youtube/answer/2797370 (rights-safety-sourcing.md [20])
13. U.S. Copyright Office, summary of *Andy Warhol Foundation for the Visual Arts v. Goldsmith* (2023), https://www.copyright.gov/fair-use/summaries/Andy-Warhol-Found-for-the-Visual-Arts-Inc-v-Goldsmith-143-S-Ct-1258-2023.pdf (rights-safety-sourcing.md [27])
14. Article 50, Regulation (EU) 2024/1689 (AI Act), https://artificialintelligenceact.eu/article/50/ (rights-safety-sourcing.md [29])
15. W3C, "Understanding Success Criterion 2.3.1: Three Flashes or Below Threshold" (WCAG 2.2), https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html (rights-safety-sourcing.md [1])
16. ITU-R BT.1702-3, "Guidance for the reduction of photosensitive epileptic seizures caused by television" (11/2023), https://www.itu.int/rec/R-REC-BT.1702-3-202311-I/en (rights-safety-sourcing.md [2])
17. Remotion, "Performance guide", https://www.remotion.dev/docs/performance (remotion-technical.md [29])
