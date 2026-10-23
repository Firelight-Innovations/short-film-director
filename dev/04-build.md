# 4. Build: how the skill was put together

How this skill was made, step four. Not loaded by the skill.

The lead wrote `SKILL.md`, `README.md` and the contract (`03-storyboard.md`). Everything
else was built by sub-agents in Workflow runs, working on disjoint files.

## Run 1: build, verify, fix, re-verify (2026-10-22 and 23)

| Stage | Agents | Model | What |
|---|---|---|---|
| Build | 7 | Opus | B1 the Remotion starter; B2a the render tools; B2b the analysis tools; B3 the build-side references and templates; B4 the front-side references and templates; B5 the Workflow scripts; B6 the lessons and the case study |
| Verify | 5 | Opus | one lens each, report only: end to end (scaffold a film, run every tool), consistency, "could a new director follow it", safety and the public repo, the Workflow scripts |
| Fix | 7 | Sonnet | one per owner, with that owner's findings |
| Re-verify | 2 | Sonnet | end to end and consistency again, report only |

The verifiers found 81 distinct issues (no blockers, 21 major, 60 minor); every lens
returned PASS WITH FIXES. The re-verify found 21 left, 5 of them major. The run paused
twice (the machine slept, and the user needed the usage window for other work) and
resumed from its cache each time.

Fixes were moved from Opus to Sonnet partway through, at the user's request.

## The lead's decisions after run 1

- **Remotion licence.** The first wording counted only the people on the film. Remotion
  counts the whole company, plus any client or studio that operates the project. Fixed
  everywhere.
- **Ask before anything leaves the machine.** A new rule in SKILL.md: a yes before any
  install, download or public action; builders never do any of them.
- **Who judges concepts.** The concept judge runs on a strong model, like the writers.
  It is the film's main creative decision.
- **The one-shot concept gate** takes the judge's winner, with a tie rule when the
  ranking does not hold against the second datum.
- **Stubs before builders.** Every section gets a `makePlaceholder` stub and a registry
  entry before the builders start, so `doctor.py` passes.
- **Web flash check.** For web delivery, also run `flash-check.py --area 0.03`.
- **Anonymised** the first film's traced likeness and its track in `dev/`.

## Run 2: the last fix round (Sonnet only)

One Sonnet fixer per owner with the re-verify findings and the decisions above, then one
Sonnet agent to check the changed points and run a short smoke test. Verdict: PASS WITH
FIXES. Every item held; the smoke test (scaffold, `npm run check`, doctor before and
after stubs, stills, preview sizes, the transition-id error) passed. Six minor doc
leftovers went to one more Sonnet agent and the lead.

New behaviour from this round: `doctor.py` checks the Windows path length, the Python
modules, and a track that is analysed but not wired in; `preview.py` defaults to a 720 px
short side; `check-timeline.py` errors on malformed transition ids; `analyze_music.py`
runs without matplotlib; `research.js` downloads nothing unless `downloads: true`;
`concepts.js` judges on the session model; the kit exports `makePlaceholder` for section
stubs.
