# __TITLE__: project brief and working notes

A code-rendered short film, directed with the short-film-director skill. Every session
that works on this film reads this file first. Keep it current: the status at the end is
how the next session (or person) picks up the work.

## What the film is

<two to four lines: length, aspect, platform, the idea, the feeling at the end; copied
from docs/brief.md once the concept is signed off>
*Example: A 2:00, 16:9 music film for LinkedIn about where AI is taking us, in eight art
styles cut to the measured track; it moves from awe to dread to responsibility and lands
one line in silence.*

- **Thesis:** <the line the film exists to land>
- **Audio:** <the track, from frame 0; or voice-over; or silence>
- **Brief and decisions:** `docs/brief.md`, `docs/decisions.md`; rights in `docs/rights.md`.

## Tech stack

- **Remotion 4 (React 19, TypeScript)**, pinned in `package.json` (4.0.410). Three.js
  through `@remotion/three`, SVG filters, Canvas 2D where a section needs them. Chromium
  renders with `--gl=angle` on a machine with a GPU (`swangle` without one).
- **Python** (numpy, scipy, OpenCV, Pillow, scikit-image, librosa) and **ffmpeg** for the
  music analysis, pre-rendered plates and the final grade.
- Tools are cross-platform Python and Node in `scripts/`; each prints its usage with
  `--help`.

## Layout

```
CLAUDE.md                     this file
package.json  tsconfig.json  remotion.config.ts  .gitignore
data/
  timeline.json               SOURCE OF TRUTH: sections, cues (exact words), marks, transitions, checks, grade
  beats.json                  the track, measured by scripts/analyze_music.py; never hand-edited
  storyboard.json             the board the animatic plays
  chains.json                 dependent-asset chains (baked plates, plates cut from the film)
  props.final.json            export props: dev overlay off
docs/
  brief.md  concepts/  treatment.md  script.md  style-bible.md  transitions.md
  storyboard.md  decisions.md  rights.md
  research/                   technique briefs and facts.md (the fact-check table)
  sections/<id>.md            one log per section; <id>.brief.md is its builder brief
  review/                     boundary reviews, the final review
  report.md                   the delivery report
refs/
  manifest.json               every reference; img/ holds only files whose licence allows it
  board-<section>.jpg  BOARD.md
assets/                       Remotion publicDir: audio/, fonts/, board/, footage/<id>/, tex/
src/                          the kit (src/kit, src/timeline, src/components) and src/sections/<id>/
scripts/                      the tools
work/                         sources and intermediates (gitignored)
out/                          renders (gitignored)
```

## The timeline is the source of truth

`data/timeline.json` (version 3) holds every section `[from, to)`, every word on screen
and when (`cues`), every musical landmark (`marks`), every transition (owner, window,
device), the frames that must be black (`checks`) and the grade. Sections read their words
and times from it; the animatic renders it; reviewers check against it. Change the film by
changing the data first, then `npm run check`.

- On-screen words are the cue's `text` exactly (and `attribution`, and `source` for `data`
  cues). Cue ids are role-based (`slam-2`, `data-3`), never content.
- Cue `from` is the frame the words are readable by; `shown` records a different drawn
  window.
- During a transition window only the owner is mounted; it receives the neighbour's live
  render as `prev` or `next`. What each side owes the other is in `docs/transitions.md`.

## Guardrails

- **Timing comes from the music.** Boundaries and cues sit on measured events in
  `data/beats.json`. Move one only to a better measured event (`python scripts/snap.py`),
  and log it.
- **Facts on screen are exact and sourced.** Every `data` and `quote` cue has a `verified`
  or `corrected` row in `docs/research/facts.md`, and its words equal the verified wording.
  Do not reword a factual cue without re-checking it.
- **Keep the timeline as data.** No words or times typed into components; compare frames,
  not typed seconds.
- **Grade and unifying grain once, at the end** (`npm run grade`, from `timeline.grade`).
  Sections own their style's texture, never the film's grade.
- **Every frame is a pure function of its frame number.** `rnd(seed)` only; no
  `Math.random`, no `Date`, no CSS animation, no state carried between frames.
- **Flash safety.** At most three flashes in any one second, no saturated red fields.
  Measure the graded file: `python scripts/flash-check.py out/__SLUG__-graded.mp4`.
- **Dev overlay off for the final** (`data/props.final.json`); keep the toggle.
- **Never commit** `work/`, `out/`, keys, tokens or `.env` files, or media whose licence does
  not allow it. Assume the repository may become public.
- **Rebuild chains after changes.** A change to a section that bakes words into plates, or
  to a frame another section reuses, makes a chain stale: `python scripts/chain.py check`,
  then `python scripts/chain.py run <name>`; `python scripts/doctor.py` fails on a stale one.
- **One owner per file.** The lead owns `src/kit/`, `src/timeline/`, `src/components/`,
  `data/`, `scripts/` and the registry; each builder owns its `src/sections/<id>/`,
  `assets/footage/<id>/`, `scripts/<id>/` and `docs/sections/<id>.md`.
- **Rights.** Every file brought into `assets/` or `refs/img/` gets a line:
  `python scripts/log-asset.py "<file>: source, URL, licence, how processed"`.
- **Log every call:** `python scripts/log-decision.py "who: what, and why"`.

## Commands

| Command | Does |
|---|---|
| `npm run studio` | Remotion Studio (dev overlay on) |
| `npm run check` | typecheck and `check-timeline.py` |
| `python scripts/doctor.py` | pre-render health check; run before every full render |
| `python scripts/analyze_music.py assets/audio/<track>` | the track, measured, to `data/beats.json` |
| `python scripts/snap.py` | boundaries against the measured events |
| `npm run animatic` | the storyboard on the track, to `out/animatic.mp4` |
| `node scripts/shots.mjs <section-id\|film\|animatic> --t 12.3,45.6` | check stills (`--seq`, `--all`, `--boundaries`, `--sheet`, `--through`, `--png`) |
| `node scripts/review-frames.mjs` | every frame around each transition, for review |
| `npm run render:final` | the film, dev overlay off, to `out/__SLUG__.mp4` |
| `npm run grade` | the one grade pass, to `out/__SLUG__-graded.mp4` |
| `python scripts/flash-check.py <mp4>` and `python scripts/black-check.py <mp4>` | the measured checks on a finished file |
| `python scripts/film-frames.py out/__SLUG__-graded.mp4` | frames from the graded file, for the final review |
| `python scripts/preview.py out/__SLUG__-graded.mp4 out/__SLUG__-preview.mp4` | a small copy for phones and chat |

## Status

- [ ] **P0 Intake:** brief, rights register, scaffold, licence check. <date>
- [ ] **P1 Ideation:** music analysed; concepts scored; treatment and script; section map. <date>
- [ ] **P2 References and facts:** boards, technique briefs, fonts; every fact verified or cut. <date>
- [ ] **P3 Storyboard:** style bible, transitions, timeline, panels; **animatic signed off**. <date>
- [ ] **P4 Build:** every section landed; `out/pass1.mp4` renders end to end and passes the flash check. <date>
- [ ] **P5 Review:** every boundary reviewed; zero blockers. <date>
- [ ] **P6 Final:** graded, measured, final review, report; the human sound gate. <date>

**Next:** <the one thing the next session should do first>
*Example: send the animatic to the user and wait for notes.*
