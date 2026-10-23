# Report: __TITLE__

<!-- Lead: this file is docs/report.md. Fill it at the end of Phase 6 from the decisions log,
the reviews, the task notifications and the measured checks. Write for the user and for the
next session. Say what was not done. Delete this comment. -->

**Brief:** `docs/brief.md`. <One or two sentences: what was asked, in the user's terms.>

**Outcome:** <the film exists and it is checked | what is missing>.

| | |
|---|---|
| Deliverable | `out/__SLUG__-graded.mp4` (graded; the one to post) |
| Ungraded master | `out/__SLUG__.mp4` |
| Preview | `out/__SLUG__-preview.mp4` (<n> MB, <height>p; for chat and phones, not for posting) |
| Cover frame | `out/__SLUG__-cover.png` (frame <n>) |
| Format | <w>x<h>, <fps> fps, <frames> frames, <m:ss.cc>, H.264 yuv420p, BT.709 limited range, <AAC 48 kHz stereo / no audio> |
| Size | <n> MB graded, <n> MB ungraded |
| Render | `npm run render:final` <m s>, `npm run grade` <s>, on <machine> |
| Audio | `<assets/audio/...>` from frame 0, untouched; <silence from m:ss / ends with the film> |

`out/` is not in git. The repo reproduces both files: `npm run render:final` then
`npm run grade`.

## What was built

<n> sections, each its own component in `src/sections/<id>/`, reading its words and times from
`data/timeline.json`.

| Section | Span | Style | How it is made |
|---|---|---|---|
| <id> | <m:ss.cc> to <m:ss.cc> | <style> | <code, plates, 3D; what is pre-rendered> |

Transitions (`docs/transitions.md`): <name, name, ...>. During a window only the owning section
is mounted and it draws its neighbour's live render itself.

<Anything that changed from the signed-off animatic, and why: a re-time, a reworded cue, a cut
shot. Each one is in the decisions log.>

## How it was run

| Phase | Who (model) | What | Wall clock |
|---|---|---|---|
| 0 Intake | lead | brief, rights register, scaffold | <hh:mm to hh:mm> |
| 1 Ideation | <n> concept writers + judge (<model>) | <winner, score> | |
| 2 References and facts | <n> researchers (<model>), <n> fact checkers | <n> references; <n> facts verified, <n> corrected, <n> cut | |
| 3 Storyboard | lead | style bible, transitions, timeline v1, animatic; <signed off when, by whom> | |
| 4 Build | <n> builders (<model>) | <n> sections; pass1 | |
| 5 Review | <n> boundary reviewers (<model>) | <n> PASS, <n> PASS WITH FIXES, <n> FAIL; <n> fix rounds | |
| 6 Final | lead; final reviewer (<model>) | <verdict>; <n> broken fixed; <n> polish taken; second review <verdict> | |

Every call is in `docs/decisions.md` (<n> lines).

## Cost

From the task notifications (tokens and wall clock per agent). "Not reported" where a
notification or a workflow result did not carry it.

| Agent | Model | Phase | Rounds | Tokens | Wall clock | Notes |
|---|---|---|---|---|---|---|
| lead | <model> | all | | <n / not reported> | <h m> | |
| <concept-1> | <model> | 1 | 1 | <n> | <m s> | |
| sec-<id> | <model> | 4, 5 | <1 build + 1 fix> | <n> | <m s> | <ms per frame> |
| rev-<t-id> | <model> | 5 | 1 | <n> | <m s> | |
| final reviewer | <model> | 6 | <1 + diff> | <n> | <m s> | |
| **Total** | | | | **<n>** | **<h m>** | |

Usage window: <n> percent before Phase 1, <n> percent at the end (<plan, window>). <Weekly
limit: <n> to <n> percent.>

## Checks on the finished file

All measured on `out/__SLUG__-graded.mp4`, the <first / second> render.

| Check | Tool | Result |
|---|---|---|
| Container | `ffprobe` | <w>x<h>, <fps>/1, <frames> frames, <s> s, yuv420p, bt709 tv; <audio> |
| Types | `npm run typecheck` | <clean> |
| Health | `python scripts/doctor.py` | <exit 0> |
| Chains | `python scripts/chain.py check` | <all fresh> |
| Flash safety, whole film | `python scripts/flash-check.py <mp4>` | <PASS: n transitions, n flashes, worst second n of 3, no saturated red> |
| Flash safety, <dense span> | same, `--from <s> --to <s>` | <...> |
| Black | `python scripts/black-check.py <mp4>` | <frames a to b max luma n; last frame max luma n; bars max luma n> |
| Motion | `python scripts/motion-check.py out/pass1.mp4 --sections` | <freezes, pops: none, or which and why accepted> |
| Sync | `python scripts/sync-check.py out/pass1.mp4 --sections` | <share on the beat per section; off-beat moves kept, and why> |

## Reviews

**Boundaries** (`docs/review/transition-*.md`):

| Transition | Verdict | Blockers | Should fix | Done |
|---|---|---|---|---|
| <t-id> "<name>" | <PASS WITH FIXES> | <n> | <n> | <fixed in round 1 by sec-<id> / accepted: why> |

**Final** (`docs/review/final.md`): <verdict>. <n> broken, <n> polish.

- **Broken, fixed:** <frames; what; the fix; how it was checked>.
- **Not settled by the reviewer, checked by the lead:** <frames; what was seen>.
- **Polish taken:** <item; why this one>.
- **Polish not taken:** listed under "Known and accepted".

**Second review** (`docs/review/final-2.md`, diff mode): <verdict>; <n> items fixed; <changed
ranges all expected / unexpected range at frames ...>. <Or: not run, and why.>

## Requests to lead

Every request from every builder and reviewer, as a queue. Status: `done`, `declined` (with the
reason) or `open` (with an owner).

| # | From | Request | Owner | Status | Resolution |
|---|---|---|---|---|---|
| <id>-R1 | sec-<id> | <what and why> | lead | done | <what was done, when> |
| <id>-R2 | sec-<id> | <...> | <user / next session> | open | <what is needed> |

## Rights

The state of `docs/rights.md` at delivery. Every item is `cleared`, `own work`, `licensed`,
`open` or `not used`.

| Item | Kind | Owner | Licence or basis | Use in the film | Status |
|---|---|---|---|---|---|
| <track> | music | <holder> | <licence / none> | <frame 0 to end> | <open: not cleared for public posting> |
| <person> | likeness or quote | <...> | <...> | <section, frames> | <...> |
| <generated images> | generated media | <tool> | <terms> | <sections> | <disclosed on screen: yes / no> |
| <fonts> | fonts | <foundries> | <OFL / Apache> | all | cleared |
| Remotion | software | Remotion | <free (up to 3 people) / company licence> | render | <recorded in the brief> |

## The sound gate

No agent has heard this film. Beats and onsets were measured; whether the cut lands on the music
is a human judgement.

| | |
|---|---|
| Watched by | <name or role> |
| When | <YYYY-MM-DD HH:MM> |
| File | `out/__SLUG__-graded.mp4` (<n> MB) |
| Device | <screen; speakers or headphones> |
| Verdict | <PASS / NOTES / NOT RUN> |
| Notes | <timecodes and what was heard; what was done about each> |

## Delivery checks

Checked on the posting day, from the platform's own help page (the skill states no platform
number; `references/07-final-and-delivery.md`, section 12). "Not run" is an honest answer.

| Check | Result |
|---|---|
| Platform and date | <platform, YYYY-MM-DD> |
| Limits (size, length, frame size, codec) | <the platform's limits; this file's values> |
| Cover frame and crops | <frame n; crops checked: 1:1 / 4:5 / 9:16 / none; anything cut> |
| Overlay zones | <the margin the platform gives; any word near an edge> |
| Sound off | <do the first three seconds hold and the words carry with no sound> |
| Loudness | <integrated n LUFS, true peak n dBFS from `ebur128`; the level the platform states, if any> |
| Loop seam | <not a loop / clean / a jump cut, meant: frames> |

## Before posting

The user decides these; nothing in the build settles them.

1. **Music rights:** <state; what happens on the platform without a licence>.
2. **Likenesses:** <any real person drawn, traced, quoted or generated; any generated face>.
3. **Facts to re-verify on the day:** <cue ids, figures, their re-verify-by dates in
   `docs/research/facts.md`>.
4. **AI disclosure:** <what is generated; what the film says on screen; the platform's label>.
5. **Licences:** <the Remotion licence answer; codec patents for H.264 and AAC are the user's
   responsibility; open rights items>.
6. **Flash safety:** measured on the graded file with a screening tool, not certified.
7. **The platform:** <delivery checks above: what was checked, what was not>.

## Known and accepted

Not broken; left as they are, in rough order of worth for another pass. Each with the file to
open.

1. <frames; what a viewer sees; why it stayed; `src/sections/<id>/<file>`>
2. <...>

Also known: <anything no review covered: motion, sound, a platform's crop>.

## How to work on it

```
npm run studio                                                 Remotion Studio, dev overlay on
node scripts/shots.mjs <section-id> --all 1 --sheet overview   one section, solo
node scripts/shots.mjs film --f <frames>                       the integrated film
node scripts/review-frames.mjs <t-id>                          every frame around a boundary
python scripts/doctor.py                                       before any full render
npm run render:final                                           the ungraded master
npm run grade                                                  the graded deliverable
python scripts/flash-check.py out/__SLUG__-graded.mp4
python scripts/black-check.py out/__SLUG__-graded.mp4
python scripts/film-frames.py out/__SLUG__-graded.mp4            frames for a review of the finished file
```

- **Words and times** live in `data/timeline.json`. <Sections that draw words into baked plates,
  and their chains: change a cue there, then `python scripts/chain.py run <name>`.>
- **Sections made from the film:** <which; their chain; what triggers a rebuild>.
- **Uncommitted inputs:** <the track, source clips: where they are and how to put them back>.
- Each section's log, `docs/sections/<id>.md`, says how it is built and what its builder would
  fix next.
