# 3. Storyboard: the skill, panel by panel, and the contract it is built to

How this skill was made, step three. Not loaded by the skill. Part A boards what a
user and the lead see in each phase of a film. Parts B to E are the contract every
build agent works to: names, schemas and command lines here are binding. If a build
agent needs to change one, it says so in its report; it does not silently diverge.

**Part G amends parts A to F after the reference sweep. Where they differ, G wins.**

---

## A. The board

Each panel is one phase of one film. "Lead" is the Claude session running the skill.

| # | Phase | What the user sees | What the lead does | Agents | Artifacts | Gate |
|---|---|---|---|---|---|---|
| P0 | Intake | One round of questions (length, aspect, platform, audio, idea, autonomy, rights, budget). A cost and time estimate. | Scaffolds the project with `new-film.mjs`; writes `docs/brief.md`; logs the first decisions. | none | project folder, `docs/brief.md`, `docs/decisions.md` | the user's answers |
| P1 | Ideation | Three concepts side by side with scores; the chosen treatment and script. | Analyses the music; runs the concept panel; scores against the brief; writes treatment, script and the section map on the music. | 3 concept writers + 1 judge (workflow `concepts.js`) | `data/beats.json`, `docs/concepts/*.md`, `docs/treatment.md`, `docs/script.md` | concept sign-off (checkpoint mode) |
| P2 | References | A reference board per section (contact sheet + linked table), technique briefs, the fact sheet. | Splits research by section style and topic; checks licences; gathers fonts. | 1 researcher per style or topic (workflow `research.js`), cheap model | `refs/manifest.json`, `refs/board-*.jpg`, `refs/BOARD.md`, `docs/research/*.md`, `docs/research/facts.md`, `assets/fonts/` | none |
| P3 | Storyboard | The storyboard sheet, and an **animatic on the real track** with every word at its real time. | Writes the style bible, the transitions table, `timeline.json` v1 and `storyboard.json`; makes board images; renders the animatic; runs `check-timeline.py` and `snap.py`. | optional: 1 board-image agent per section | `docs/style-bible.md`, `docs/transitions.md`, `data/timeline.json`, `data/storyboard.json`, `assets/board/`, `out/animatic.mp4`, `out/storyboard.jpg` | **animatic sign-off** |
| P4 | Build | Progress lines; a half-resolution pass of the whole film. | Adjusts the kit; writes one builder brief per section; launches builders; integrates; renders `pass1`; flash-checks it. | 1 builder per section (named background agents), strong model | `src/sections/<id>/`, `assets/footage/<id>/`, `docs/sections/<id>.md`, `out/pass1.mp4` | the film renders end to end |
| P5 | Review | Verdicts per boundary; what was fixed. | Dumps frames around each cut; runs boundary reviewers; sends fix rounds to the owning builders; re-runs any dependent chain. | 1 reviewer per boundary (workflow `review-boundaries.js`), mid model | `docs/review/transition-*.md` | zero blockers |
| P6 | Final | The graded film, a phone preview, the report, the open items. | Renders, grades, measures; dumps frames from the graded file; runs one fresh final reviewer; fixes what is broken; one polish pass; re-renders; re-measures; writes the report; commits. | 1 final reviewer (workflow `final-review.js`), strong model | `out/<slug>.mp4`, `out/<slug>-graded.mp4`, `out/<slug>-preview.mp4`, `docs/review/final.md`, `docs/report.md` | the user |

Checkpoint mode stops at the P1 and P3 gates. One-shot mode logs the call and goes on.

---

## B. The skill's files

Repo root is the skill folder (clone it into `~/.claude/skills/short-film-director`).

```
SKILL.md                         the director's playbook (lead writes)            [lead]
README.md                        for humans: what, install, layout, credits       [lead]
references/
  01-intake-and-ideation.md      intake questions, concept methods, scoring,       [B4]
                                 treatment, script, word budgets, section map
  02-references.md               reference kinds, how many, where from, licences,  [B4]
                                 the board, technique briefs, facts
  03-storyboard.md               style bible, transitions table, timeline v1,      [B4]
                                 storyboard.json, board images, the animatic
  04-architecture.md             the Remotion kit: film time, timeline, owners,    [B3]
                                 render ranges, determinism, assets, fonts, 3D
  05-build.md                    builder briefs, floor first, the check loop,      [B3]
                                 integration, pass1, model routing, ultracode
  06-review.md                   boundary reviews, fix rounds, measured checks,    [B3]
                                 dependent chains
  07-final-and-delivery.md       final render, grade, final review, polish,        [B3]
                                 report, deliverables, phone preview
  music.md                       analysing the track, cutting to it, snap rules    [B4]
  safety-and-rights.md           flash safety, facts, likeness, music, footage,    [B4]
                                 fonts, AI disclosure, public repos
  lessons.md                     gotchas with symptom, cause, fix                  [B5]
  case-study-we-built-a-mind.md  the first film made this way, in numbers          [B5]
templates/                       fill-in documents, copied into docs/ by new-film  [B4 + B3]
  brief.md  concept.md  treatment.md  script.md  style-bible.md  transitions.md
  storyboard.md  section-log.md  builder-brief.md  boundary-review-brief.md
  final-review-brief.md  report.md  decisions.md  CLAUDE.md
scripts/                         tools; new-film copies all but itself into the    [B2]
  new-film.mjs                   project's scripts/
  analyze_music.py  snap.py  check-timeline.py  shots.mjs  sheet.py
  review-frames.mjs  film-frames.py  flash-check.py  black-check.py  grade.py
  preview.py  log-decision.py  fetch-fonts.mjs  plates-from-film.mjs  refboard.py
  workflows/                     Workflow scripts for the fan-outs                 [B5]
    concepts.js  research.js  review-boundaries.js  final-review.js  build-sections.js
assets/template/                 the Remotion starter (new-film copies it)          [B1]
dev/                             how the skill was made (not loaded)               [lead]
```

SKILL.md stays under about 450 lines and points to a reference file at every phase.
Reference files over 300 lines start with a table of contents.

---

## C. The project a film lives in (what `new-film.mjs` makes)

```
<film>/
  CLAUDE.md                      from templates/CLAUDE.md: brief, guardrails, commands
  package.json  tsconfig.json  remotion.config.ts  .gitignore
  data/
    timeline.json                SOURCE OF TRUTH (schema D1)
    beats.json                   from scripts/analyze_music.py; never hand-edited
    storyboard.json              the board (schema D2)
    props.final.json             { "showDevOverlay": false, "grainStrength": 1, "muteAudio": false, "debugSolo": "" }
  docs/
    brief.md  concepts/  treatment.md  script.md  style-bible.md  transitions.md
    storyboard.md  decisions.md  research/ (facts.md + technique briefs)
    sections/<id>.md  review/  report.md
  refs/
    manifest.json                every reference (schema D3)
    img/                         only files whose licence allows it
    board-<section>.jpg  BOARD.md
  assets/                        Remotion publicDir
    audio/<track>  fonts/  board/  footage/<id>/  tex/
  src/                           from assets/template/src
  scripts/                       the tools (B2)
  work/                          sources and intermediates (gitignored)
  out/                           renders (gitignored)
```

---

## D. Data schemas

### D1. `data/timeline.json` (version 3)

```jsonc
{
  "version": 3,
  "title": "Untitled film",
  "slug": "untitled-film",            // output file names: out/<slug>.mp4
  "w": 1920, "h": 1080, "fps": 30,
  "dur": 60.0,                        // seconds; composition length = round(dur * fps)
  "letterbox": 0.06,                  // bar height as a fraction of h, top and bottom; 0 = none
  "safe": { "title": 0.9, "action": 0.95 },   // fractions of the picture inside the bars
  "audio": { "src": "audio/track.mp3", "gain": 1.0, "duration": 58.2 },  // or null
  "sections": [
    { "id": "00-open", "from": 0.0, "to": 8.5, "label": "Open", "style": "one line",
      "palette": { "bg": "#0b0b0c", "ink": "#f2efe8", "accent": "#ff5a1f" } }
  ],
  "marks": { "drop": 28.933 },        // musical landmarks, measured (beats.json)
  "transitions": [
    { "id": "t-00-01", "at": 8.5, "a": "00-open", "b": "01-rise", "owner": "01-rise",
      "pre": 0.5, "post": 0.5, "name": "Ink bleed", "device": "what happens, frame by frame",
      "beat": "drop" }                // mark name or a short note
  ],
  "cues": [
    { "id": "title", "section": "00-open", "role": "slam", "from": 1.0, "to": 3.0,
      "text": "THE EXACT WORDS", "attribution": "", "source": "", "note": "" }
  ],
  "checks": {
    "black": [[99.867, 100.9]],       // [from, to) seconds that must be pure black
    "lastFrameBlack": true
  },
  "grade": {
    "contrast": 1.05, "saturation": 0.97, "gamma": 0.985,
    "vignette": 0.35,                 // 0 = none; angle = vignette * PI/3
    "grain": 5,                       // ffmpeg noise alls
    "until": 99.867                   // seconds; grade off from here (null = whole film)
  }
}
```

Rules (enforced by `scripts/check-timeline.py`, exit 3 on any error):
- `sections` are contiguous, ordered, cover `[0, dur)`, and every `from`/`to` is
  frame-aligned after snapping (`round(t * fps)`).
- Every id is unique; section ids match `^[0-9]{2}-[a-z0-9-]+$`.
- Every transition joins two adjacent sections (`a` then `b`), `owner` is `a` or `b`,
  windows `[at - pre, at + post)` stay inside the two sections and do not overlap.
  `t-start` and `t-end` (no `a` or no `b`) are allowed with `pre = post = 0`.
- Every cue has non-empty `text`, a known `section`, `from < to`, and lies inside its
  section's render range. Cues with `role` `data` or `quote` have a non-empty `source`.
- `checks.black` ranges lie inside `[0, dur]`; `audio.src` exists under `assets/`.
- Warnings (exit 0): a cue shorter than its reading time (see music.md / ideation:
  about 3 words a second, plus 0.5 s), a boundary more than 2 frames from a measured
  event (that is `snap.py`'s job; check-timeline only warns if beats.json exists).

Cue roles (open set; these have meaning in the kit): `stamp slam narration sub quote
data thesis question credit logo caption vo`.

### D2. `data/storyboard.json`

```jsonc
{
  "panels": [
    { "id": "p01", "section": "00-open", "at": 0.0,
      "image": "board/p01.jpg",       // under assets/, or null: the animatic draws a card
      "action": "What we see, one or two lines",
      "camera": "slow push in",       // optional
      "words": ["title"],             // cue ids on screen in this panel (the animatic shows the real cues at their real times anyway)
      "sound": "first note",          // optional
      "refs": ["r012", "r031"],       // refs/manifest.json ids
      "note": "" }
  ]
}
```

A panel holds the screen from `at` until the next panel's `at`. Panels are sorted by
`at`; the first is at 0.

### D3. `refs/manifest.json`

```jsonc
{
  "refs": [
    { "id": "r012", "section": "02-ink", "kind": "look",   // look | technique | fact | asset | font | music | sound
      "title": "…", "by": "…", "year": 1965, "url": "https://…",
      "licence": "CC0" ,                // CC0 | PD | CC-BY-4.0 | … | "link-only" (copyrighted: never downloaded)
      "file": "img/r012.jpg",           // only when the licence allows a copy; else null
      "take": "what to take from it, one line" }
  ]
}
```

---

## E. The template (assets/template) and the tool command lines

### E1. Kit surface (`src/kit/index.ts`), kept from *We Built a Mind*, generalised

Time: `useFilmTime() -> { frame, t, fps }` (absolute film time), `FilmClockOverride`,
`F(sec)`, `T(frame)`, `clamp lerp ease prog remap envelope hold rnd rndRange`.
Timeline: `timeline section(id) sectionAt(t) cue(id) cuesOf(id) cuesAt(t) mark(name)
transitionIn(id) transitionOut(id) transitionAt(t) renderRange(id) formatTimecode(t)`.
Times read through the kit are snapped to frames at load.
Music: `music BEATS DOWNBEATS ONSETS level(frame, band) beatIndex(t) sinceBeat(t)
beatEnv(t, decay) beatsIn(a, b)` (generic names; band: energy | low | mid | high | onset).
Fonts: `font(family)`, `weightsOf(family)`; vendored by `scripts/fetch-fonts.mjs`.
Tokens: `CANVAS LETTERBOX_PX SAFE PALETTE(id)` read from timeline.json.
Types: `SectionComponent SectionProps { from, to, prev?, next? } Cue CueRole SectionSpan
Timeline Transition`.
`SectionId` is `string`: sections come from timeline.json. The registry maps ids to
components; an id with no component renders as a labelled test card in its palette, so a
new section in the timeline plays at once.

Compositions: `Film` (props: showDevOverlay, grainStrength, muteAudio, debugSolo, bare),
`Solo` (one section for real, neighbours as test cards, its render range only),
`Animatic` (storyboard.json panels + the real cues at their real times + section, panel
and timecode strip + marks as ticks + transition names in their windows + the music).

Layers in `FilmFrame`, bottom to top: AudioTrack, FilmStack (one section, or a
transition owner holding its neighbour as `prev`/`next`), Grain, Letterbox, DevOverlay.

npm scripts: `studio`, `typecheck`, `check` (typecheck + check-timeline), `animatic`
(`remotion render Animatic out/animatic.mp4 --scale=0.5`), `render:final` (Film, crf 16,
bt709, jpeg-quality 95, props.final.json, to `out/<slug>.mp4` via a small node wrapper
that reads the slug), `grade`, `preview`, `shots`, `music`, `fonts`.

Pinned: remotion and @remotion/* 4.0.410, react and react-dom 19.0.0, typescript 5.6.3,
zod 3.22.3, three 0.170. remotion.config.ts: jpeg, overwrite, `--gl=angle`, bt709,
jpeg quality 95, publicDir `assets`, delayRender timeout 180 s.

### E2. Tool command lines (run from the project root)

| Tool | Command | Does | Exit |
|---|---|---|---|
| new-film | `node <skill>/scripts/new-film.mjs <dir> [--title T] [--w 1920 --h 1080 --fps 30] [--dur 60]` | copies assets/template, templates/ to docs/, scripts/ (minus itself) to scripts/; writes slug and title; `git init` | 0 / 2 bad args / 1 dir not empty |
| analyze_music | `python scripts/analyze_music.py <audio> [--fps 30]` | beats, downbeats, onsets, hits, structure, per-frame energy bands, loudest, silence → `data/beats.json`; plot → `out/research/music.png` | 0 |
| snap | `python scripts/snap.py [--tol 2]` | each section boundary, transition, mark and cue start vs the nearest beat, downbeat, onset, structure point, in frames; flags beyond tol | 0, or 3 if any boundary is off |
| check-timeline | `python scripts/check-timeline.py` | the D1 rules | 0 / 3 |
| shots | `node scripts/shots.mjs <section-id\|film\|animatic> [--t a,b] [--f a,b] [--seq a:b] [--all n] [--boundaries] [--sheet name] [--cols n] [--scale s] [--clean] [--bare] [--bench a:b] [--bundle name] [--out dir]` | check stills to `out/check/<target>/f<frame>_t<sec>.jpg`, contact sheets, speed bench | 0 / 1 |
| sheet | `python scripts/sheet.py <out.jpg> [--cols 6] [--w 480] <images…>` | labelled contact sheet | 0 |
| review-frames | `node scripts/review-frames.mjs [t-ids…]` | every frame around each transition window, sheets + full-size cut frames + frames.json → `out/review/<id>/` | 0 |
| film-frames | `python scripts/film-frames.py <mp4> [--every 0.5] [--last 3]` | frames from a FINISHED file: every N s, every frame of the last N s before the first `checks.black` range (or the end), key stills; sheets + frames.json → `out/final-review/` | 0 |
| flash-check | `python scripts/flash-check.py <mp4\|dir> [--from s] [--to s] [--fps n]` | general and red flash counts per second; default `--area 0.25` is the broadcast reading, and web delivery also runs `--area 0.03` (amended after review) | 0 PASS / 3 FAIL |
| black-check | `python scripts/black-check.py <mp4>` | `checks.black` ranges and last frame are black; letterbox bars carry no picture | 0 / 3 |
| grade | `python scripts/grade.py <in.mp4> <out.mp4>` | ffmpeg grade from `timeline.grade`, off from `until`; repaints the letterbox black; bt709 tv; audio copied | 0 |
| preview | `python scripts/preview.py <in.mp4> <out.mp4> [--max-mib 28] [--height N]` | small copy for phones and chat (two-pass to a size; default a 720 px short side, amended after review) | 0 |
| log-decision | `python scripts/log-decision.py "who: what, and why"` | appends a timestamped line to `docs/decisions.md` | 0 |
| fetch-fonts | `node scripts/fetch-fonts.mjs "Family:400,700" …` | vendors Google Fonts into `assets/fonts/` + `src/kit/fonts.manifest.json` | 0 |
| plates-from-film | `node scripts/plates-from-film.mjs <plates.json>` | renders bare film stills at listed times to listed files (a section that reuses the film's own frames) | 0 |
| refboard | `python scripts/refboard.py [--section id]` | `refs/board-<section>.jpg` from licensed files, and `refs/BOARD.md` (every ref, linked, licence shown) | 0 |

Every tool reads `data/timeline.json` from the current directory, prints plain lines,
and avoids bash. ffmpeg filter expressions escape commas as `\,` inside Python strings
written as `"\\,"`. Long frame lists are split (ffmpeg's expression parser fails on
hundreds of terms). Frames are streamed, never held whole in memory.

### E3. Workflows (scripts/workflows/*.js)

Run with the Workflow tool: `Workflow({ scriptPath: "<skill>/scripts/workflows/<name>.js", args: {...} })`.
Scripts cannot read files, so every prompt names absolute paths the agent must read.

| Script | args | Agents | Writes | Returns |
|---|---|---|---|---|
| concepts.js | `{ project, n: 3, angles?: [..] }` | n concept writers (different angles), then 1 judge | `docs/concepts/<k>.md`, `docs/concepts/scores.md` | scores and the winner |
| research.js | `{ project, topics: [{ slug, prompt, model? }] }` | one per topic | `docs/research/<slug>.md`, rows in `refs/manifest.json` (via a per-topic `refs/<slug>.json` the lead merges) | short summaries |
| build-sections.js | `{ project, sections: [ids], model? }` | one builder per section, brief from `docs/sections/<id>.brief.md` | the section's files | each builder's report |
| review-boundaries.js | `{ project, transitions: [ids], model? }` | one reviewer per boundary | `docs/review/transition-<a>-<b>.md` | verdict, blockers, should-fix counts (schema) |
| final-review.js | `{ project }` | one fresh reviewer | `docs/review/final.md` | verdict, broken list, top polish (schema) |

---

## F. Build plan (step four)

One workflow, five writers in parallel on disjoint files, then one fresh verifier:

- **B1 template**: `assets/template/` (src, data examples, config). Verifies it with
  `tsc --noEmit`, `check-timeline.py`, three stills and a short animatic render, using a
  scratch copy linked to an existing node_modules.
- **B2 tools**: everything in `scripts/` except `workflows/`. Tests each against the
  *We Built a Mind* project (read-only) and against a scaffolded scratch film.
- **B3 build-side docs**: references 04 to 07, templates builder-brief,
  boundary-review-brief, final-review-brief, report, section-log, decisions.
- **B4 front-side docs**: references 01 to 03, music, safety-and-rights; templates
  brief, concept, treatment, script, style-bible, transitions, storyboard, CLAUDE.md.
- **B5 orchestration and lessons**: `scripts/workflows/*.js`, references lessons and
  case study.
- **V verifier**: fresh eyes over the whole skill: names and paths agree with this
  contract, every reference is reachable from SKILL.md, the scaffold runs end to end.

The lead writes SKILL.md and README.md meanwhile, then fixes what V finds, then
commits and pushes.

---

## G. Amendments after the reference sweep (binding; G wins over A to F)

Sources: `dev/references/*.md`, above all `wbam-lessons.md` "What to change next time".

### G1. Phase changes

- **Intake** also creates `docs/rights.md` (the rights register, `templates/rights.md`):
  music, likenesses, generated media, footage, fonts, each with owner, licence, use,
  status. It runs the **Remotion licence check** (free for individuals, non-profits, and a
  for-profit company whose total headcount plus any client or studio that operates the
  project is 3 or fewer; count whole companies; a client that only receives the mp4 does
  not count; a Company License above that; corrected after the safety review) and records
  the answer. It pins the Remotion version in the brief. It offers the official
  Remotion agent skills (`npx skills add remotion-dev/skills`) as a complement, only with
  the user's yes.
- **Ideation** diverges before it converges: about eight one-line options first (a Crazy
  Eights style burst), then three developed concepts plus one wildcard slot, scored with a
  Pugh matrix (about ten criteria from the brief; a datum concept; + S -; re-run with a
  second datum to check the ranking holds). Murch's order (emotion, story, rhythm, eye
  trace, screen plane, depth) is the tiebreak. A keep-and-kill list from the user when
  they have one.
- **Facts are their own step, before the storyboard gate**, with depth: every `data` or
  `quote` cue gets two independent checks (workflow `fact-check.js`), a verdict
  (`verified | corrected | unverified | cut`), an as-of date and a re-verify-by date in
  `docs/research/facts.md` (table format G4). On-screen words must equal the verified
  wording.
- **Storyboard** runs thumbnails, then a **beat board** (one panel per bar or phrase on
  the real track), then the animatic; style frames for the two or three hero moments. It
  writes a **cut list** per section (what to drop first if time runs short) into
  `docs/storyboard.md`. The style bible carries **minimum type sizes** as numbers (for
  example body 54 px, source lines 32 px at 1080p; scale with height).
- **Build** runs `python scripts/doctor.py` before every full render.
- **Review** adds motion and sync: `motion-check.py` (freezes, jumps, one-frame pops) and
  `sync-check.py` (picture change against the music's onsets) per section, plus a
  phone-size sheet (360 px wide) in every review input.
- **Final review** samples by clock AND by cue (every cue's first frame + 2 and its
  midpoint; every transition's first and last frame) and adds phone-size tiles. After the
  fixes, a **short second final review** on the frames that changed (`diff-frames.py`,
  `final-review.js` with `mode: "diff"`).
- **Report** records tokens and wall clock per agent (from task notifications), a
  Requests-to-lead queue with owner and status, the rights register's state, and the
  **human sound gate**: someone watches the graded file with the sound on; the verdict
  goes in the report.

### G2. Data additions

- `timeline.json` cues may carry `"shown": { "from": s, "to": s }` when what is drawn
  differs from the readable window; `check-timeline.py` reports any cue whose `shown`
  extends outside its section's render range. **Ids are role-based** (`stamp-1`,
  `slam-2`, `data-3`), never content (`stamp-1962` once said 1966).
- `data/chains.json`, dependent-asset chains (baked plates, plates cut from the film):

  ```jsonc
  { "chains": [
      { "name": "00-open-plates",
        "inputs": ["data/timeline.json#cues:00-open", "scripts/00-open/**", "work/00-open/src/**"],
        "outputs": ["assets/footage/00-open/seq/*.webp"],
        "build": ["python scripts/00-open/build.py all"],
        "check": ["python scripts/flash-check.py out/check/00-open --from 0 --to 8.5"] } ] }
  ```

  `inputs` are globs, or `data/timeline.json#cues:<section>` (that section's cues,
  hashed) or `#section:<id>`. `chain.py` writes `data/chains.lock.json` (input and output
  hashes).

### G3. Tool additions and changes (all in `scripts/`, run from the project root)

| Tool | Command | Does | Exit |
|---|---|---|---|
| doctor | `python scripts/doctor.py [--quick]` | pre-render health: timeline valid (runs check-timeline), every chain fresh against its lock, every `font("X")` used in src/ vendored, every `staticFile("…")` literal path exists under assets/, every registered section id is in the timeline and the other way round, beats.json present when audio is set, installed Remotion version matches the pin in package.json | 0 / 3 |
| chain | `python scripts/chain.py list \| check [name] \| run [name\|--all]` | runs a chain's build then check commands and updates the lock; `check` fails loudly on stale outputs | 0 / 3 |
| motion-check | `python scripts/motion-check.py <mp4\|dir> [--from s --to s] [--sections]` | per-frame mean absolute difference; flags freezes (N identical frames inside motion), jumps, one-frame pops (a frame far from both neighbours that are close to each other); writes `out/motion/<name>.csv` and `.png` | 0; 3 when a pop or an unexpected freeze is found |
| sync-check | `python scripts/sync-check.py <mp4> [--sections]` | picture-change peaks per section against beats.json onsets and beats: distance in frames to the nearest event, share on the beat, off-beat moves listed | 0 |
| diff-frames | `python scripts/diff-frames.py <old.mp4> <new.mp4> [--threshold 2.0]` | which frames changed between two renders (ranges), before and after sheets → `out/diff/` | 0 |
| log-asset | `python scripts/log-asset.py "<file>: source, URL, licence, how processed"` | appends to `docs/rights.md` under "Assets" | 0 |
| shots (changes) | adds `--png` (lossless PNG instead of JPEG, for pixel asserts), `--through` (in a solo render, neighbour owners place the live section full-frame instead of a test card, so a section can be checked through a window it does not own), `--timeout <s>` per still, unique default sheet names for `--all` and `--boundaries`, and a **unique default bundle per process** (so `--bundle` is only for reuse) | | |
| film-frames (changes) | adds the by-cue and by-transition samples and phone-size sheets (`phone-*.jpg`, 360 px tiles) | | |
| review-frames (changes) | adds a phone-size sheet per window and runs `motion-check.py` on the window, writing its CSV next to the sheets | | |

The `Solo` composition takes a `through: boolean` prop for `shots.mjs --through`.

### G4. `docs/research/facts.md` table (parsed by `check-timeline.py`)

```
| cue | on screen | source | url | published | exact wording at source | verdict | as of | re-verify by | check A | check B |
```

One row per `data` or `quote` cue (cue id in the first column). `check-timeline.py` warns
when such a cue has no row, or a verdict other than `verified` or `corrected`.

### G5. Workflows (scripts/workflows/), additions

| Script | args | Agents | Writes | Returns |
|---|---|---|---|---|
| fact-check.js | `{ skill, project, cues?: [ids] }` | two independent checkers per data or quote cue (different search approaches), then one reconciler | `docs/research/facts.md` rows | per-cue verdicts (schema) |
| final-review.js | adds `mode: "full" \| "diff"` | `diff` reviews only the `out/diff/` sheets against the earlier review | `docs/review/final-2.md` in diff mode | as before |

Every workflow takes `args.skill` (the skill folder) and `args.project` (the film).

### G6. Templates, additions

`templates/rights.md` (the rights register). `templates/report.md` gains the cost table,
the Requests-to-lead queue and the sound gate. `templates/storyboard.md` gains the beat
board and the cut list. `templates/style-bible.md` gains minimum type sizes.

### G7. Numbers to carry (from the digests; cite them in the reference files)

- On-screen text: 150 words a minute or less (about 0.4 s a word, 2.5 words a second) as
  the default reading budget; each text event on screen at least 5/6 s and at most 7 s;
  at most two lines; a line within about 68 percent of the frame width at 16:9.
  `check-timeline.py` warns below `0.4 s x words + 0.5 s` (minimum 0.83 s).
- Flash: at most three general or red flashes in any one-second window; a general flash
  is an opposing luminance change of 10 percent or more with the darker state below 0.80,
  over more than a quarter of the screen; any saturated-red transition counts as a red
  flash; avoid long flashing sequences (over five seconds) even under the limit.
- Remotion: pin 4.x; `npx remotion browser ensure` before the first render; `--gl=angle`
  with a GPU, `swangle` without; on Windows keep the ffmpeg command under 8192 characters
  (props as a file); choose concurrency with `npx remotion benchmark`.
