# 07. Final and delivery

Phase 6. Render the film, grade it once, measure the graded file, have it reviewed by fresh
eyes from frames of that file, fix what is broken, take at most one polish pass, re-render
and re-measure, write the report, commit, deliver. The last gate is a person watching with
the sound on.

## Contents

1. [Render: npm run render:final](#1-render-npm-run-renderfinal)
2. [Grade: once, at the end](#2-grade-once-at-the-end)
3. [Probe both files](#3-probe-both-files)
4. [Measure the graded file](#4-measure-the-graded-file)
5. [Frames from the graded file: film-frames.py](#5-frames-from-the-graded-file-film-framespy)
6. [The final reviewer](#6-the-final-reviewer)
7. [What the reviewer could not settle](#7-what-the-reviewer-could-not-settle)
8. [Broken, polish, and the one polish pass](#8-broken-polish-and-the-one-polish-pass)
9. [Re-render, re-measure, diff, second review](#9-re-render-re-measure-diff-second-review)
10. [The report](#10-the-report)
11. [Commit](#11-commit)
12. [Deliverables and platform checks](#12-deliverables-and-platform-checks)
13. [The sound gate](#13-the-sound-gate)
14. [What to tell the user before posting](#14-what-to-tell-the-user-before-posting)
15. [Sources](#15-sources)

---

## 1. Render: npm run render:final

Before it: `python scripts/chain.py check` and `python scripts/doctor.py` both exit 0; Studio
and other renders are closed; the dev overlay is off in `data/props.final.json`. Then:

```
npm run render:final
```

It runs `node scripts/render-final.mjs`, which prints and runs

```
remotion render src/index.ts Film out/<slug>.mp4 --codec=h264 --crf=16 --color-space=bt709 --jpeg-quality=95 --props=data/props.final.json
```

`data/props.final.json` turns the dev overlay off; the slug comes from the timeline. CRF 16
because the master is re-encoded once more by the grade. Props go in as a file because
Windows does not accept inline JSON props [1]. For a quick check of the same thing:
`node scripts/render-final.mjs --scale 0.25 --out out/quick.mp4`; for a part:
`--frames 0-299`; anything after `--` goes to Remotion as it is (`-- --concurrency=4`,
`-- --gl=swangle`). On the first film a 2:00 film (3600 frames, 1920x1080) rendered in
2 m 13 s to 2 m 31 s.

If it dies on a timeout, the label in the error names the `delayRender` that did not clear
(a font, a plate, a texture); see 04-architecture.md, sections 10 and 20. If the OS kills it,
lower the concurrency. If it fails with a long command line on Windows, see
04-architecture.md, section 21.

## 2. Grade: once, at the end

```
npm run grade                      the same as: python scripts/grade.py out/<slug>.mp4 out/<slug>-graded.mp4
python scripts/grade.py [<in.mp4> <out.mp4>] [--crf 17] [--preset slow]
```

`grade.py` is one ffmpeg pass over the whole render, from the `grade` block in the timeline
(missing values default to contrast 1.05, saturation 0.97, gamma 0.985, vignette 0.35,
grain 5):

1. converts the input to limited-range BT.709 and yuv420p, whatever it was tagged;
2. applies `contrast`, `saturation` and `gamma`, a vignette (angle = `vignette` x pi/3) and
   temporal grain (`grain`, ffmpeg `noise` strength), each gated by frame number: off from
   `until` on (by default the start of the first `checks.black` range), and off inside every
   `checks.black` range;
3. repaints the letterbox bars black after the grain;
4. encodes H.264, forces the BT.709 limited-range tags, copies the audio untouched, and moves
   the index to the front for the web.

Why once, and at the end:

- Each section owns its style's texture (film grain, paper tooth, tape noise). The grade is
  the single surface that makes separately built sections one film (eight styles on the
  first); a grade per section would make them eight films again, and would be graded twice
  where sections overlap in a window.
- Reviewers before this phase judge clean frames. The boundary brief tells them there is no
  grade yet, so they do not report missing grain.
- A gate in seconds misses by a frame (99.8667 s is a hair after frame 2996), and grain or a
  lifted gamma over a black outro turns black into banded grey. On the first film both
  happened before the gate moved to the frame number and `until`.
- Grain in the bars reads as a fault, hence the repaint.
- The first film's values, as a starting point: contrast 1.05, saturation 0.97, gamma 0.985,
  vignette near pi/9 (a stronger pi/5 put the corners at 40 percent and read as a dirty lens
  on white fields), grain 5. The template's `vignette: 0.35` is pi/8.6.

## 3. Probe both files

```
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,profile,width,height,pix_fmt,color_range,color_space,color_primaries,color_transfer,r_frame_rate,nb_frames,sample_rate,channels,duration -of default=nw=1 out/<slug>-graded.mp4
```

Run it on `out/<slug>.mp4` and on `out/<slug>-graded.mp4`. Check:

| Field | Expected | The first film's graded file |
|---|---|---|
| video `codec_name`, `profile` | `h264`, `High` | h264, High |
| `width`, `height` | the timeline's `w`, `h` | 1920, 1080 |
| `r_frame_rate` | `<fps>/1` | 30/1 |
| `nb_frames` | `round(dur x fps)` | 3600 |
| video `duration` | `dur` | 120.000000 |
| `pix_fmt` | `yuv420p` (not `yuvj420p`) | yuv420p |
| `color_range` | `tv` | tv |
| `color_space`, `color_primaries`, `color_transfer` | `bt709` each | bt709 |
| audio `codec_name`, `sample_rate`, `channels` | `aac`, `48000`, `2`; Remotion writes a silent AAC track even when the timeline's `audio` is null | aac, 48000, 2 |
| audio `duration` | the video's plus up to about a twentieth of a second (AAC pads its last 1024-sample frame; a 20 s test film measured 20.053) | 120.021333 |
| `size` | plausible for the length | 225 MB graded, 201 MB ungraded |

Both files have the same frame count and duration. A `yuvj420p` or `pc` file means the render
ran without `--color-space=bt709`, and its black and bars will not match (04-architecture.md,
section 18).

## 4. Measure the graded file

```
python scripts/flash-check.py out/<slug>-graded.mp4
python scripts/black-check.py out/<slug>-graded.mp4
```

Both must exit 0, **on the graded file**: the grade's contrast can push a transition over a
flash threshold, and only the graded file shows whether the grade stayed off the black and
out of the bars. For a dense section, also check its span on its own with `--from` and
`--to`. What the numbers mean: 06-review.md, section 10.

**For web delivery** (LinkedIn, YouTube, a site) also run
`python scripts/flash-check.py out/<slug>-graded.mp4 --area 0.03` and judge each region that
fails (safety-and-rights.md, section 2). The default `--area 0.25` is the broadcast reading, so
a PASS there is not a WCAG 2.3.1 claim and not enough to call a web film flash-safe. Record
both results in the report.

- flash-check FAIL: find the flashes it lists, open the frames, and fix the section (level the
  plates, tear a hard cut over several frames, slow the cutting). Lowering the grade's contrast
  fixes only a transition the grade itself pushed over.
- black-check FAIL on a black range: check `grade.until` and the frame gate; on the bars: the
  colour space and the repaint; on the last frame: the section that owns the end.

**A film that ends on its mark.** The template ends in black: `checks.black` names the black
range and `checks.lastFrameBlack` is true. A film for a feed that loops, or one that closes
on a held logo or end card, ends on a picture instead. Decide that at the storyboard and
write it in the timeline: `checks.black: []`, `checks.lastFrameBlack: false`,
`grade.until: null` (the grade then covers the whole film, the mark included). Run on such a
file, `black-check.py` prints "no checks.black ranges", lists the last four frames without
failing on them, and still tests the bars; `film-frames.py` runs `last/` to the end of the
film. The last frames are then judged as a picture, not as black: the mark whole, held at
least its reading time (0.4 s a word plus 0.5 s, the rule `check-timeline.py` warns on), and
the last frame one you would put on a poster. A held card is not a fault in itself; the
fault in lessons.md L67 was a card that sat unchanged while a stronger frame came before it.
On a loop, also check the seam from the last frame to the first (section 12).

Log the numbers: `python scripts/log-decision.py "lead: final render <time>, grade <time>;
flash-check PASS (<n> transitions, <n> flashes, worst second <n>; web, --area 0.03: <PASS / what
was judged>); black-check PASS (<...>)"`.

## 5. Frames from the graded file: film-frames.py

```
python scripts/film-frames.py out/<slug>-graded.mp4 [--every 0.5] [--last 3] [--out out/final-review]
```

It reads frames out of the finished file itself (decoding it once), so the reviewer judges
grade, grain, vignette and encode, not renders. It writes `out/final-review/`:

| Folder and sheets | What |
|---|---|
| `clock/`, `clock-NN.jpg` | one frame every `--every` seconds, in order, 960 px |
| `cues/`, `cues-NN.jpg` | every cue's first frame plus two and its midpoint, full size, labelled with the cue id |
| `transitions/`, `transitions-NN.jpg` | every window's first and last frame (a hard cut: the frame before and the cut frame) |
| `last/`, `last-NN.jpg` | every frame of the last `--last` seconds before the first `checks.black` range and six frames into it (or the end of the film) |
| `full/` | key stills: first and last frame, the frames around the cut to black, every cut frame, every section's midpoint, the midpoint of every data, quote, thesis and logo cue |
| `phone-NN.jpg` | every cue's midpoint as a 360 px tile |
| `frames.json` | every sheet with its tiles |

Sheets are 24 tiles of 480 px, labelled `f<frame>_t<seconds>`.

Why by cue as well as by clock: on the first film a half-second sample missed two slam words
that were on screen for seven frames each, and the reviewer had to report them as "not
seen". Choose `--every` at half the length of the shortest thing that is not a cue (a flash
of an image, a hit) if you want the clock samples to catch it. For a film that fades out
instead of cutting to black, `--last` covers the fade.

## 6. The final reviewer

One reviewer, a strong model, fresh: it has not seen the film being made. That is the point.
On the first film the one broken item, a chart that read as the opposite of its fact on a
phone, had passed its builder, the lead and eight boundary reviewers; the fresh reviewer
caught it in its first pass.

- Brief: `docs/final-review-brief.md` (from `templates/final-review-brief.md`), placeholders
  filled for the film.
- Inputs: `out/final-review/` from the graded file; the brief points it at the tone document,
  the style bible's rules, the transitions table and the timeline's cues.
- Withheld: section logs, boundary reviews, the decisions log, and the lead's worries. Do
  not tell it what you fixed or what you suspect. Check your own suspicions yourself
  (section 7).

With workflows:

```
Workflow({ scriptPath: "<skill>/scripts/workflows/final-review.js",
           args: { skill: "<skill>", project: "<project>", mode: "full" } })
```

It writes `docs/review/final.md` and returns the verdict, the broken list and the top polish
items. `model` defaults to the session's (a strong model). `notes` is one paragraph the
reviewer gets: the measured check results are fine there; your suspicions are not. Without
workflows, one Agent on the strong model:

```
You are the final reviewer of a short film. You have not seen it being made.
Read <project>/docs/final-review-brief.md and follow it exactly. Your frames are in
<project>/out/final-review/ (start with frames.json). Write <project>/docs/review/final.md
and nothing else.
```

Verdicts: **SHIP**, **SHIP WITH FIXES**, **DO NOT SHIP**.

## 7. What the reviewer could not settle

A good reviewer says what it could not judge: words between its samples, motion, sync, the
exact frame a cue arrives. Settle each one yourself on frames from the graded file, never on
a fresh render:

```
ffmpeg -v error -i out/<slug>-graded.mp4 -vf "select=eq(n\,2852)" -frames:v 1 out/final-review/check/f2852.png
ffmpeg -v error -i out/<slug>-graded.mp4 -vf "select=between(n\,2852\,2858)" -fps_mode passthrough out/final-review/check/r%02d.png
```

The second writes `r01.png` for the first selected frame (2852 here), `r02.png` for the next,
and so on. `select` decodes from the start of the file, which takes a few seconds for a short
film. Create `out/final-review/check/` first. Open the frames, write down what you saw, and
log it. Do the same for anything you suspected and kept from the reviewer.

## 8. Broken, polish, and the one polish pass

**Broken** is anything a viewer would take for a mistake, anything untrue (a fact that reads
wrong, words that are not the cue's text, a misattributed quote), and any failed measured
check. Fix all of it. Send each item to the section's builder (`SendMessage` to `sec-<id>`, or
a fresh agent with the section log). A one-line constant change the lead can make itself, and
logs.

**Polish** makes the film better. Take **at most one polish pass**: the items worth most that
stay local and cheap. Do not take, at this stage:

- anything that moves a cue or a boundary time (it ripples into baked plates, chains, recap
  sections, reading times and the music);
- anything inside a tuned cut list (on the first film the recap's word holds were tied to a
  cut list tuned for flash safety and figure separation; lengthening them meant re-tuning it);
- re-layouts, new shots, new assets;
- a change to a section that a recap section samples, unless you will re-run its chain and
  re-measure;
- anything you cannot verify on frames before the deadline.

List every polish item not taken, with the file to open and the reason, in the report's
"Known and accepted". On the first film one polish item of eight was taken.

## 9. Re-render, re-measure, diff, second review

1. Keep the first graded file: rename `out/<slug>-graded.mp4` to `out/<slug>-graded-r1.mp4`
   (`render:final` and `grade` overwrite).
2. `python scripts/chain.py check`; re-run any stale chain. Then `python scripts/doctor.py`.
3. `npm run render:final`, `npm run grade`.
4. Probe, flash-check and black-check the new graded file again (sections 3 and 4).
5. `python scripts/diff-frames.py out/<slug>-graded-r1.mp4 out/<slug>-graded.mp4 [--threshold 2.0]`
   lists the frame ranges that changed, by section, and writes `out/diff/` (sheets with rows
   old, new and the difference x4; full-size `old/`, `new/`, `delta/` frames;
   `frames.json`). A frame's score is the largest mean difference of any 20 x 20 block at
   320 px, so one changed word counts as much as a changed sky. Read the ranges: each should
   be a fix you made. An unexpected range (a chain changed plates, a fix moved something
   elsewhere) is a finding. Frames next to a real change can differ a little because the
   encoder codes neighbouring frames against each other; the 2.0 threshold sits above that.
   On a 20 s test, a type-size change showed as exactly the cue's drawn window (f220 to f317)
   and nothing else.
6. A short second review on only the frames that changed:

   ```
   Workflow({ scriptPath: "<skill>/scripts/workflows/final-review.js",
              args: { skill: "<skill>", project: "<project>", mode: "diff" } })
   ```

   A fresh reviewer reads `out/diff/` against `docs/review/final.md` and writes
   `docs/review/final-2.md`: is each broken item fixed, did anything new break. Without
   workflows, one strong Agent with the "second review" part of the brief. On the first film
   this pass was skipped and the lead looked at the changed frames itself; the second review
   is cheap and would have checked the fixed chart at phone size.

Stop there. Do not loop: a third round is only for a new broken item.

## 10. The report

`docs/report.md` from `templates/report.md`. It is written for the user and for the next
session. It holds:

- what was made, with the deliverable's path, format, size and render times;
- how it was run: phases, agents, models;
- **the cost table**: tokens and wall clock per agent, from the task notifications, and the
  usage window before and after;
- the checks on the finished file, as numbers;
- what the reviews found and what was done, including the second review;
- **the Requests-to-lead queue**: every request from every builder, with owner and status;
- **the rights register's state**, from `docs/rights.md`, with every open item;
- **the sound gate**: who watched, when, which file, the verdict;
- **the delivery checks**: the cover frame and its crops, the platform's limits, loudness and
  the loop seam, or "not run" (section 12);
- what the user must decide before posting (section 14);
- known and accepted items, with the file to open for each;
- how to work on the film: the commands.

Say what was not done. On the first film the report said no review had used sound; that
honesty is what makes the next pass cheap.

## 11. Commit

Commit everything the template does not ignore: `out/`, `work/` and `assets/audio/*` stay
local, and so does any media whose licence does not allow a copy in the repo. Before you do:

- `git status --porcelain` and read every path. No keys or tokens, nothing from `work/`.
- Media whose licence does not allow redistribution stays out of git: a copyrighted track, a
  source clip, a traced reference. Add such paths to `.gitignore` and say in the report how
  to put them back. Assume the repo may become public.
- Large plates that scripts can regenerate: commit them, or ignore them and record the
  rebuild command. Decide, log it, and say which in the report.

Then commit with a message that says what the film is and its state. The commit is local.
Do not push, upload or share a link until the user says yes (SKILL.md rule 11).

## 12. Deliverables and platform checks

1. **The graded mp4**, `out/<slug>-graded.mp4`: the one to post.
2. **A preview** small enough for chat and phones:

   ```
   python scripts/preview.py out/<slug>-graded.mp4 out/<slug>-preview.mp4 --max-mib 28 [--height N]
   ```

   Two-pass H.264 to a size, then measured and re-encoded smaller if it is still over (exit 3
   if it never fits). With no file arguments it reads `out/<slug>-graded.mp4` and writes
   `out/<slug>-preview.mp4`. By default the SHORT side is 720 px, so a 16:9 film comes out at
   1280 x 720 and a 9:16 film at 720 x 1280. You do not need a flag for either. `--height N`
   is an explicit override: it sets the picture height in lines, and it never scales up. Set
   `--max-mib` under the limit of wherever the preview will go (a chat attachment, a
   messenger); 28 is the default. The first film's 720p preview
   was 22 MB for two minutes. The preview is for watching, not for posting.
3. **A cover frame**, `out/<slug>-cover.png`: one still at the film's `w` x `h`, read out of
   the graded file, for the platforms that show a poster before play or let you pick one.
   Pick a frame that holds up alone: a strong picture, any words whole, not black, not in
   the middle of a dissolve. Then crop it the ways the platform shows it (see the table
   below):

   ```
   ffmpeg -v error -i out/<slug>-graded.mp4 -vf "select=eq(n\,<frame>)" -frames:v 1 -fps_mode passthrough out/<slug>-cover.png
   ffmpeg -v error -i out/<slug>-cover.png -vf "crop=ih*4/5:ih" out/cover-4x5.png
   ```

   `crop=ih*A/B:ih` is the centre crop of a frame wider than the shape A:B (width:height);
   for a frame taller than the shape use `crop=iw:iw*B/A`. A 16:9 frame cropped to 1:1,
   4:5 and 9:16 keeps the middle 56, 45 and 32 percent of its width. Open each crop with
   the Read tool: if the face, the title or the mark is cut, choose another frame, or move
   the picture's weight to the centre third.
4. **The report**, `docs/report.md`.

Send the preview, the cover frame and the report to the user (for example with
SendUserFile), and give the path of the graded file, which may be too large to send.

**Platform checks, on the posting day.** Platforms change their limits and their crops, and
the sources this skill rests on gave no reliable platform numbers (01-intake-and-ideation.md,
"Safe areas"). So the skill states none: the table says what to check and how, and the
platform's own help page gives the number. Record what you checked, and the numbers, in the
report ("Delivery checks").

| Check | Why | How |
|---|---|---|
| Limits | file size, length, frame size, frame rate and codec limits differ by platform and move | the platform's help page; compare with the `ffprobe` table (section 3) and the file size. The graded file is H.264 and AAC in an mp4 with the index at the front |
| Cover and crops | feeds show a poster and often a centre crop of a wide film before play | the cover frame above, cropped to each shape the platform shows |
| Overlay zones | captions, buttons and the account name sit over part of the picture | the platform's help page for the margins; then look at the phone sheets for words near an edge. A 9:16 film keeps its lines inside `SAFE.title` |
| Sound off | feeds often start a film muted (01-intake-and-ideation.md, "Sound off": 50 to 85 percent of one platform's views were silent in 2016, self-reported) | read `clock-01.jpg` and the first cues as a viewer with no sound: do the first three seconds hold, and do the words carry? If not, a different cover or captions |
| Loudness | a platform may turn a loud file down, and a quiet one is not turned up | measure the track as delivered: `ffmpeg -hide_banner -nostats -i out/<slug>-graded.mp4 -af ebur128=peak=true -f null -` and read `I` (integrated, LUFS) and `Peak` (true peak, dBFS). The film's audio is the user's track, untouched: a change is the user's call, logged |
| Loop | a feed that loops plays the last frame into the first | for a film that ends on its mark: the seam check below |

The seam check, for a film that ends on its mark and will loop. `N` is `nb_frames` from the
probe:

```
mkdir out/seam
ffmpeg -v error -i out/<slug>-graded.mp4 -vf "select=gte(n\,<N-6>)" -fps_mode passthrough out/seam/a_%02d.png
ffmpeg -v error -i out/<slug>-graded.mp4 -vf "select=lt(n\,6)" -fps_mode passthrough out/seam/b_%02d.png
python scripts/motion-check.py out/seam
```

The files sort `a_` then `b_`, so the trace runs from the last six frames into the first
six. The row for frame 6 in `out/motion/seam.csv` is the change across the seam. A seam as
quiet as the rows around it is a clean loop; a spike is a jump cut. A jump from the mark
to the film's first image is fine if you meant it and the first image is strong; it is a
fault if not. Open `a_06.png` and `b_01.png` and look at both.

## 13. The sound gate

No agent has heard the film. Beats and onsets are numbers, and `sync-check.py` compares
numbers; nobody has judged whether a cut lands. So the last gate is a person: someone watches
the graded file (not the preview), start to end, with the sound on, on the kind of screen it
will be posted to. Ask them to note, with timecodes:

- any cut or hit that feels early or late against the music;
- any word that arrives after its musical moment or leaves before it can be read;
- the ending: does the silence or the last note sit right with the last picture;
- the level: too quiet or too loud against other posts on the platform.

Record the verdict in the report: who, when, which file (name and size), **PASS** or **NOTES**,
and the notes. A note at a timecode becomes a frame (`round(t x fps)`), a section, a fix, a
re-render, a re-measure and a diff (section 9). If the user will not watch it, record that the
gate was not run, in those words.

## 14. What to tell the user before posting

Say these plainly, in the report and in your last message. Details:
`references/safety-and-rights.md`.

- **Music rights.** Whether the track is licensed for this use on this platform. An unlicensed
  track may be muted, flagged or taken down; nothing in the build solves that.
- **Likenesses.** Any real person drawn, traced, quoted or generated; any generated face. What
  the film says on screen about it.
- **Facts.** Every figure has a re-verify-by date in `docs/research/facts.md`. Figures move;
  re-check them on the day of posting.
- **AI disclosure.** What in the film is generated, and the platform's rules for labelling
  AI-generated or altered media.
- **Flash safety.** Measured on the graded file with a screening tool, not certified. The
  default check is the broadcast reading; for web delivery the `--area 0.03` result is
  reported too (section 4).
- **The platform.** Its limits, crops, loudness handling and loop behaviour were not
  verified at build time; section 12 lists what to check on the posting day.
- **Licences.** The Remotion licence answer recorded in the brief [2]. Remotion is free for
  individuals, for non-profits, and for a for-profit company whose total headcount, plus any
  client or studio that operates or co-develops the project, is 3 or fewer. Count whole
  companies, not only the people on the film. A client that only receives the mp4 does not
  count. Four or more combined need a Company License. Codec patent licensing for H.264 and
  AAC is the user's own responsibility [2]; the rights register's open items.

## 15. Sources

1. remotion.config.ts and the CLI render command (props as a file on Windows),
   https://www.remotion.dev/docs/cli/render , from `dev/references/remotion-technical.md`.
2. Remotion License FAQ and licence pricing FAQ, https://www.remotion.dev/docs/license/faq ,
   https://www.remotion.dev/docs/license-pricing-compliance/faq , from
   `dev/references/remotion-technical.md`.

The grade values, render times, file sizes, check numbers and the review history come from
*We Built a Mind* (session report, decisions log, final review, `ffprobe` of its files). The
`ffmpeg` frame commands were run on that film's graded file for this page.
