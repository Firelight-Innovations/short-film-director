# 05. Build: from the signed-off animatic to pass1

Phase 4. The lead prepares the kit and the briefs, launches one builder per section,
integrates them as they land, and ends with a half-resolution pass of the whole film that
renders end to end. Builders read this file too: sections 8 to 11 are theirs.

## Contents

1. [What the phase delivers](#1-what-the-phase-delivers)
2. [Before you start](#2-before-you-start)
3. [Your kit work first](#3-your-kit-work-first)
4. [Writing a builder brief](#4-writing-a-builder-brief)
5. [Model routing](#5-model-routing)
6. [Launching the builders: named agents or build-sections.js](#6-launching-the-builders-named-agents-or-build-sectionsjs)
7. [One working tree, or a worktree per builder](#7-one-working-tree-or-a-worktree-per-builder)
8. [How a builder works: floor, depth, edges, cost, stop](#8-how-a-builder-works-floor-depth-edges-cost-stop)
9. [The check loop: shots.mjs](#9-the-check-loop-shotsmjs)
10. [Typecheck and the determinism checks](#10-typecheck-and-the-determinism-checks)
11. [Requests to lead](#11-requests-to-lead)
12. [Integration as builders land](#12-integration-as-builders-land)
13. [doctor, pass1 and the first flash check](#13-doctor-pass1-and-the-first-flash-check)
14. [Status lines, usage checks, cost records](#14-status-lines-usage-checks-cost-records)
15. [Sources](#15-sources)

---

## 1. What the phase delivers

- `src/sections/<id>/` for every section, type-clean, drawing a valid frame on every frame
  of its render range.
- Plates in `assets/footage/<id>/` and the scripts that make them in `scripts/<id>/`, with a
  chain in `data/chains.json` for anything that depends on the timeline or on other
  sections.
- A log per section, `docs/sections/<id>.md` (from `templates/section-log.md`).
- `out/pass1.mp4`: the whole film at half resolution, dev overlay on, flash-checked.

**Gate:** the film renders end to end. A section that is not good enough yet still
renders; a section that does not render is the only thing that stops the phase.

## 2. Before you start

- The animatic is signed off (or, in one-shot mode, logged). Timing and words are frozen:
  a builder who wants a cue moved asks; the lead moves it in the timeline and logs it.
- `python scripts/check-timeline.py` exits 0 and `python scripts/snap.py` exits 0 (or every
  boundary off the grid has a logged reason).
- Every `data` and `quote` cue is `verified` or `corrected` in `docs/research/facts.md`.
- `npx remotion browser ensure` has run once on this machine.
- `npx remotion benchmark` has given you a concurrency for this machine (04-architecture.md,
  section 20).
- Usage: read where the window stands and say it to the user (section 14).

## 3. Your kit work first

Builders read the kit; they do not change it. Every change you make while they work costs
each of them a message and a re-check, so do it now:

1. **Tokens and fonts.** Check `CANVAS`, `LETTERBOX_PX`, `SAFE` and each section's palette in
   the timeline. Vendor every family the style bible names:
   `node scripts/fetch-fonts.mjs "Family:400,700" ...`.
2. **Shared pieces.** Anything two sections must share goes in the kit or in
   `assets/footage/shared/` now: a still both sides of a handshake use, a scene file two
   renderers read, a helper two builders would each write. **A film with one look
   throughout** (the choice made at ideation) needs more: the look is the shared piece.
   Before the builders launch, put the type system (families, sizes, weights), the palette,
   the texture and the components every section reuses (a title card, a lower third, the
   frame treatment) in `src/kit/` or `src/style/`, and point each brief's Style row at them.
   Builders who work in parallel from a description read it differently; code in the kit
   gives them one look to build on, and the section's own page then says only what that
   section adds.
3. **Folders and registry.** Builders do not own the registry, and the `Solo` harness
   renders a section for real only when the registry has it (an id with no entry plays as a
   labelled test card). So before launch, give each section a stub and register it:

   ```tsx
   // src/sections/<id>/index.tsx (the builder replaces it)
   import { AbsoluteFill } from "remotion";
   import { PALETTE } from "../../kit";
   import type { SectionComponent } from "../../kit";
   export const Section: SectionComponent = () => <AbsoluteFill style={{ background: PALETTE("<id>").bg }} />;
   ```

   Add `import { Section as S<nn> } from "./<id>";` and `"<id>": S<nn>,` to
   `src/sections/registry.ts`. Remove the template's worked example `00-open` (folder and
   registry entry) unless the film has a section by that id; `doctor.py` checks the registry
   and the timeline against each other.
4. **Logs.** Copy `docs/section-log.md` (from `templates/section-log.md`) to
   `docs/sections/<id>.md` with the header filled in.
5. **Chains you already know.** A section that bakes its words or reuses the film's frames
   gets its chain entry in `data/chains.json` now, even if the build command is a
   placeholder the builder will fill.
6. **Check.** `npm run check` (typecheck and `check-timeline.py`), then
   `python scripts/doctor.py --quick`, then a few stills of the film:
   `node scripts/shots.mjs film --all 5 --sheet kit`. Look at the sheet.
7. **Commit** the kit, data and briefs, so each builder starts from a known state.

On the first film the lead patched the kit three times while eight builders worked (a frame
snap fix, a colour-space fix, a private bundle flag). Two of the three were found by
builders. Each patch meant a message to every builder. Expect some of this; keep it rare.

## 4. Writing a builder brief

One brief per section, from `templates/builder-brief.md`, saved as
`docs/sections/<id>.brief.md`. The brief is the builder's whole world: it does not see
this conversation. Fill every `<placeholder>`:

| Part | What goes in | Why |
|---|---|---|
| Identity | the film, its format, how many builders work at once and where, the agent's name | a builder that knows others share the tree does not edit what it does not own |
| Span and render range | seconds and frames | the section must draw every frame of the render range |
| Cues | id, role, from, to, text, copied from the timeline | the timeline wins if they differ; the copy saves a lookup |
| Shots from the board | each panel's time, action, words, camera, refs and board image | the builder builds what was signed off, not a fresh idea |
| Style page | the heading of its page in `docs/style-bible.md`, the palette, the minimum type sizes as numbers; in a one-look film, the shared kit pieces that carry the look | five items failed on phones on the first film; numbers stop that |
| References | `refs/board-<id>.jpg`, the ref ids, the technique briefs in `docs/research/` | look and method, with code that runs |
| Transitions | each boundary it touches: cut frame, window frames, owner, device, what lands on it | the owner draws the neighbour itself |
| Handshakes | the exact pixels and frames it owes and is owed | the other builder builds against them and cannot see this code |
| Budgets | speed (1.5 s a frame at full resolution), plates (about 250 MB) | keeps the final render short; gives the escape hatch |
| Cut list | what to drop first if time runs short, from `docs/storyboard.md` | a late squeeze becomes a decision, not a panic |
| Media and rights | what it may bring in, and `log-asset.py` for each file | the rights register is filled as media arrives |
| Deliverables and final message | the files, the check stills, the log headings, a short final message | the lead triages eight reports in minutes |

Write the brief so the builder can start without asking. Say which locks may not be lifted
(timing, words, facts) and who may lift them (the lead, after asking the user in checkpoint
mode). On the first film the brief's locks were lifted mid-run; the research files kept
stale timestamps, and the build guide had to say "ignore those".

## 5. Model routing

The user's own rules come first: a model they named, a standing rule in their CLAUDE.md or
memory ("Sonnet for sub-agents"), a budget. Follow them, and log the routing. Where they say
nothing:

| Job | Tier | Example | Why |
|---|---|---|---|
| Research, reference gathering | cheap | Haiku (`research.js` default) | volume work against a fixed template and schema |
| Fact checks: two checkers and a reconciler per cue | mid | Sonnet (`fact-check.js` default) | the first film's cheap fact pass let four misworded or unverifiable claims through; a fact on screen is where a film is wrong in public. Give each checker its own search budget |
| Concept writers | strong | Opus (`concepts.js`: the session's model) | ideas are the product |
| Concept judge | mid | Sonnet (`concepts.js` default) | scores against a fixed Pugh matrix; raise it to strong when the concepts are close |
| Section builders | strong | Opus | the film is made here; a weak section shows |
| A simple section (type on a plain field, pure code, no plates) | mid | Sonnet | the first film's pure-code section rendered at 30 to 42 ms a frame and needed no plates |
| Boundary reviewers | mid | Sonnet | frames and a fixed template; parallel and cheap |
| Final reviewer | strong, fresh | Opus | found the one broken item that a builder, the lead and eight reviewers had passed |
| The lead | the session itself | | |

The first film ran Haiku research, eight Opus builders, eight Sonnet boundary reviewers
and one fresh Opus final reviewer, and spent 77 percent of one five-hour Max window in an
afternoon.

## 6. Launching the builders: named agents or build-sections.js

**Named background agents (the default).** One Agent call per section, all in one message,
each `run_in_background: true`, `name: "sec-<id>"`, on the strong model, with a prompt like:

```
You are the builder of section <id> of the film in <project>.
Read <project>/docs/sections/<id>.brief.md first, then <skill>/references/04-architecture.md
and <skill>/references/05-build.md (sections 8 to 11). Build the section as the brief says.
Your log is <project>/docs/sections/<id>.md. When done, reply with the short final
message the brief asks for.
```

A fix round later goes to the same agent with `SendMessage({ to: "sec-<id>", message })`,
and the builder still holds its context: its code, its measurements, why it made each call.
The lead can also message a running builder ("the kit's frame snap changed; re-check
frames 158 and 2015"). Cost: each builder's context stays alive until its last round, and
each fix round adds to it. On the first film four of eight builders were resumed once.

**`build-sections.js` (under ultracode, or when the user asked for workflows).**

```
Workflow({ scriptPath: "<skill>/scripts/workflows/build-sections.js",
           args: { skill: "<skill>", project: "<project>", sections: ["00-open", "01-rise"], model: "opus" } })
```

One builder per section, brief from `docs/sections/<id>.brief.md`, at most `maxParallel`
at once (default 8; more run in later waves), on `model` (default: the session's). It
returns each builder's report: status (`done`, `floor only`, `blocked`), summary, log, stills,
ms per frame, known issues, requests. A fix round is the same script with
`fixes: { "<id>": "<findings, or the path of a review file>" }`: a fresh agent that reads the
section log, the brief and the findings. Cost: a builder inside a workflow cannot be messaged
while it runs, so a kit change mid-build reaches it only through its next round; and every
fix round pays again to read the brief, the log and the code. It is the better choice when
builds are independent and unlikely to need a second round, or when the session cannot hold
many background agents.

Either way the briefs are the same. Sections that reuse the film's frames go last: launch
them with the others on placeholder plates, and tell them the placeholders are not design
references, or launch them after the sections they sample have landed.

## 7. One working tree, or a worktree per builder

**One tree** works because ownership is by path: on the first film eight builders shared
one tree with no conflicts. Its costs: one `tsc` over everything (a builder filters for its
own folder), and a syntax error or broken import in one section stops every bundle, the
film's and every builder's solo renders, until it is fixed (the registry imports every
section). `shots.mjs` bundles into a unique folder per process, so check runs no longer
delete each other's bundles.

**A git worktree per builder** isolates the code: a builder's typecheck and film bundle see
only its section and the kit. Use it when the machine has the disk (each worktree is a full
checkout, and plates are large) and you are willing to merge. Set it up before launching:

```
git worktree add ../<film>-sec-<id> -b sec/<id>
```

then link the shared, uncommitted folders into the worktree instead of copying them:
`node_modules` always, and `assets/audio` or `assets/fonts` if they are not committed. On
Windows: `New-Item -ItemType Junction -Path ..\<film>-sec-<id>\node_modules -Target
.\node_modules`; on macOS and Linux: `ln -s "$PWD/node_modules" ../<film>-sec-<id>/node_modules`.
Name the worktree in the brief. Builders still run no state-changing git: when a builder
lands, the lead commits in its worktree (`git -C ../<film>-sec-<id> add src/sections/<id>
assets/footage/<id> scripts/<id> docs/sections/<id>.md` and `commit`) and merges `sec/<id>`;
paths are disjoint, so the merge is clean. A kit change means merging the main branch into
each worktree and telling each builder. Remove the worktree after the last round
(`git worktree remove`).

A worktree does not make the machine faster. Font timeouts and the eleven-minute hang on
the first film came from many renders sharing one CPU and one GPU. Stagger heavy benches,
keep Python jobs to a few processes per builder, and do not render the full film while
builders bench.

## 8. How a builder works: floor, depth, edges, cost, stop

1. **Floor first.** Build the simplest complete version of the whole render range: every
   shot present, every cue on screen and readable on its `from` frame, both boundaries
   valid, every handshake met. Render `--all 1` and `--boundaries` and look. A film that
   exists beats a film that is ten percent more beautiful and did not render. Every bold
   choice gets a working fallback before the bold version is attempted.
2. **Then depth.** Take the shots in order of how much they matter and make each worth
   pausing on. Re-render and look after every change.
3. **Then the edges.** `--seq` across both boundaries, every frame of each window, with
   `--through` for the frames a neighbour owns.
4. **Then cost.** `--bench` the heaviest span. Pre-render anything over budget.
5. **Stop** when the section is whole and you have looked at it end to end. Leave it
   rendering cleanly; do not start a rewrite you cannot finish.

Keep the log current as you go, so someone else could pick the section up from it. Append
each call to the decisions log too: `python scripts/log-decision.py "sec-<id>: what, and
why"`.

## 9. The check loop: shots.mjs

```
node scripts/shots.mjs <section-id|film|animatic> [options]
```

A section id renders the `Solo` composition: the section real, its neighbours as labelled
test cards in their palettes, timing, audio, grain, letterbox and windows exactly as in the
film. `film` renders the integrated film; `animatic` the animatic. Stills go to
`out/check/<target>/f<frame>_t<sec>.jpg`, and the script prints what each still cost.

All times are film seconds and all frames film frames.

| Option | Does | Use it to |
|---|---|---|
| `--t a,b` | stills at these times | look at moments named in the brief |
| `--f a,b` | stills at these frames | look at exact frames (cut frames, handshake frames) |
| `--range a:b:step` | stills from a to b every step seconds | a pacing strip of one shot |
| `--seq a:b` | every frame from a to b | judge motion, entrances, every frame of a window |
| `--all n` | every n seconds over the target's render range (the whole film for `film` and `animatic`) | the overview |
| `--boundaries` | frames cut-2 to cut+1 of each boundary, plus the first, middle and last frame of each window the section takes part in | check both edges at once |
| `--sheet [name]` | also a contact sheet `<out>/<name>.jpg`; `--all` and `--boundaries` make one by default, named from the options, so two kinds of run never overwrite each other | read many frames in one image |
| `--no-sheet` | no sheet, even for `--all` or `--boundaries` | stills only |
| `--cols n`, `--tile px` | sheet columns and tile width | wider sheets; `--tile 360` for a phone-size sheet |
| `--scale s` | render scale (default 0.5; 1 is full size) | judge detail and type at `--scale 1` |
| `--png` | lossless PNG stills | prove a pixel: true black, an exact colour, a 2 px line |
| `--quality q` | JPEG quality (default 88) | |
| `--clean` | no dev overlay (default: on, drawn in the bars; over the top and bottom 34 px of picture when `letterbox` is 0) | stills to judge edges, or to show |
| `--bare` | picture only: no overlay, grain or letterbox | plates; pixel checks |
| `--through` | section target only: a test-card neighbour that owns a transition with this section draws this section live, full-frame (magenta behind it means nobody drew that pixel) | see your frames inside a window your neighbour owns |
| `--tag v2` | suffix on file names | keep a re-render from overwriting the first |
| `--out dir` | output folder (default `out/check/<target>`) | keep a before set while you make an after set |
| `--bundle name` | keep and reuse `out/.bundle/<name>`, rebuilt only when sources change; default is a private bundle per run, deleted at the end | speed up repeated runs; never share a name with a run that may overlap yours |
| `--timeout s` | seconds per still (default 120); a slower still fails and the browser restarts | survive a hung still on a loaded machine |
| `--gl angle\|swangle` | GL backend | `swangle` on a machine without a GPU |
| `--logs` | print the browser console | debug a still that fails or comes out blank |
| `--bench a:b [--concurrency n]` | render that span at full size and print ms per frame | measure against the speed budget |

Exit 0 when every still rendered, 1 when one failed or the arguments are wrong. The loop a
builder repeats:

```
node scripts/shots.mjs <id> --all 1 --sheet overview          the whole range, every second
node scripts/shots.mjs <id> --boundaries                       both edges
node scripts/shots.mjs <id> --seq 15.0:16.2 --sheet in         every frame of an entrance
node scripts/shots.mjs <id> --seq 66.7:67.2 --through          frames inside the neighbour's window
node scripts/shots.mjs <id> --t 24.5 --scale 1 --clean         full size: detail and type
node scripts/shots.mjs <id> --f 1478,1482 --png --scale 1 --clean   lossless, for a handshake assert
node scripts/shots.mjs <id> --bench 20:22                      speed
node scripts/shots.mjs film --f 2003,2014                      the integrated film
```

**Open the images with the Read tool and look at them.** A frame you have not looked at is
not done. For every sheet and still, ask:

- Is it beautiful, and does it read as the style on the section's page?
- Is every word exactly the cue's text, whole on the cue's `from` frame, and legible at phone
  size? Make a phone sheet to judge it: `node scripts/shots.mjs <id> --all 1 --tile 360
  --sheet phone`. Text below the style bible's minimum sizes is a fault.
- Is anything clipped by the letterbox or outside `SAFE.text`?
- Does any frame read as a mistake: a test card, a missing image, a pop of black or white, a
  jump the device does not explain?
- Are the handshake frames exactly what `docs/transitions.md` says? Prove pixel claims on
  `--png` frames with a few lines of Python (numpy, Pillow), not by eye.

## 10. Typecheck and the determinism checks

Type-check your own folder; other builders' errors are not yours:

```
npx tsc --noEmit 2>&1 | grep "sections/<id>"                  (Git Bash, macOS, Linux)
npx tsc --noEmit | Select-String "sections/<id>"               (PowerShell)
```

It must print nothing. Then run the four determinism checks in 04-architecture.md, section 9:
the search for banned clocks and randomness, a repeat render compared with the first, and an
out-of-order render compared with a sequence. A minimal compare of two lossless frames of
the same frame number (render once, then again with `--png --out <other dir>`):

```python
import sys, numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(int)
d = np.abs(a - b).max(axis=2)
print("max diff", d.max(), "share over 3/255", round((d > 3).mean() * 100, 4), "percent")
```

Pass: max 0 on frames without text or scaled images; otherwise at most 3/255 on at most 0.05
percent of pixels.

## 11. Requests to lead

A builder writes only inside what it owns. Anything else (a kit helper, a cue time, a
`shown` window, a font, a change to a handshake, a bug in a tool) goes under "Requests to
lead" in its log, with an id, and the builder works around it locally meanwhile. The lead
reads requests first when a builder lands, answers each (done, declined with the reason, or
open with an owner) and carries the open ones into the report's queue.

Why it matters: on the first film the three pipeline bugs (frame snapping, colour space, the
grade gate) were all reported this way, by builders, with the cause and a proof.

## 12. Integration as builders land

After each builder lands:

1. Read its final message, then its log: Requests to lead first, then Known issues.
2. `npm run typecheck`.
3. Stills across its boundaries in the integrated film:
   `node scripts/shots.mjs film --f <cut-1>,<cut>,<cut+1>` for each cut, plus the first,
   middle and last frame of each window. Look at them.
4. Check each handshake it owes on the frames named in `docs/transitions.md`.
5. Answer its requests; log what you decided.
6. Commit its files (in its worktree, then merge, if it has one).
7. Tell the user one status line (section 14).

A boundary is ready for review when both of its sections have landed.

## 13. doctor, pass1 and the first flash check

When every builder has landed:

```
python scripts/chain.py run                                      rebuild every stale chain
python scripts/doctor.py                                         must exit 0
npx remotion render src/index.ts Film out/pass1.mp4 --scale=0.5   the whole film, dev overlay on
python scripts/flash-check.py out/pass1.mp4                      PASS (0) or FAIL (3)
```

Run `chain.py` first when a section reuses the film's frames: its plates must be cut from
the integrated sections, not from test cards. Look at pass1 as frames: one per second,
30 to a sheet, straight from the file (it takes seconds):

```
ffmpeg -v error -i out/pass1.mp4 -vf "fps=1,scale=320:-1,tile=6x5" out/pass1-sheet-%02d.jpg
```

(`film-frames.py` also reads a finished file, but writes `out/final-review/` by default,
which the final reviewer reads; give it `--out out/pass1-frames` if you use it here.) A flash
FAIL here goes straight to the owning builder; the flash numbers on
the graded file are the ones that count (07-final-and-delivery.md).

The gate is met when pass1 renders end to end and every section is real.

## 14. Status lines, usage checks, cost records

**Status lines.** The user may be away from the screen. One line at each event, plain:

```
Build: launched 7 builders (Opus) for 00 to 06; 07 waits for its plates.
Build 3/7: 04-bargain landed, 120 ms a frame, 2 requests (both answered), typecheck clean.
Build: pass1 rendered (2 m 40 s at half size); flash-check PASS, worst second 2 of 3.
```

**Usage before each fan-out.** Read the usage window before launching builders (and before
each review fan-out): with a usage tool if the session has one, otherwise ask the user to
look. Say where it stands and what the fan-out will cost. If the window is short: launch
fewer builders at once, route simple sections to a mid model, take items off the cut list,
or wait for the reset. Say which, and log it.

**Cost records.** Each background agent's task notification reports its tokens and its
wall-clock time. Copy them into the cost table of `docs/report.md` as they arrive (agent,
model, phase, tokens, wall clock, rounds), and add each fix round to the same row. A
workflow's result may or may not carry usage; if not, write "not reported". The first film
kept only plan-window percentages, so nobody could say afterwards which agent cost what.

## 15. Sources

From *We Built a Mind*: its build guide (`docs/BUILD-GUIDE.md`), decisions log and session
report; the routing and cost numbers are from that session. The determinism rules and the
speed advice are cited in 04-architecture.md. The tolerance for comparing renders was
measured on that film's frames.
