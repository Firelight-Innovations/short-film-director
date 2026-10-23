# short-film-director

A Claude skill for directing **code-rendered short films**: music films, essay films,
title sequences, product films, kinetic-type pieces and data stories, made in
[Remotion](https://www.remotion.dev) with Python and ffmpeg, from an idea to a graded,
checked mp4.

Claude acts as the director. It runs a small crew of sub-agents through seven phases:

| # | Phase | What comes out |
|---|---|---|
| 0 | Intake | the brief; a scaffolded film project |
| 1 | Ideation | three concepts, scored; a treatment; the script; a section map on the music |
| 2 | References | a reference board per section, technique briefs, a fact sheet, licensed assets |
| 3 | Storyboard | the style bible, the transitions table, the timeline, board panels, **an animatic on the real track** |
| 4 | Build | one builder agent per section; the whole film rendering end to end |
| 5 | Review | one reviewer per cut; measured flash, black and colour checks; fix rounds |
| 6 | Final | final render, grade, a fresh final review, one polish pass, the report, a phone preview |

The film is data: `data/timeline.json` holds every section, every word on screen and
when, every musical mark and every transition. Sections read it, the animatic renders
it, reviewers check against it.

## Install

Clone it into your skills folder:

```bash
git clone https://github.com/Firelight-Innovations/short-film-director ~/.claude/skills/short-film-director
```

The skill asks before it installs, downloads or publishes anything. Then ask Claude Code
for a film: "make a 45-second launch film for our product, cut to
this track", "storyboard this script and make an animatic", "turn this essay into a
kinetic-type film".

## What you need

- Node 18+ and npm (Remotion 4, React 19, TypeScript; versions are pinned in the template)
- Python 3.11+ with numpy, scipy, Pillow, OpenCV and librosa (music analysis, checks,
  contact sheets); matplotlib is optional, for the music and motion plots
- ffmpeg and ffprobe on the PATH
- Optional: Blender for pre-rendered 3D plates

Remotion is free for individuals, for non-profits, and for a for-profit company whose
total headcount, plus any client or studio that operates or co-develops the project, is
three or fewer. Count whole companies, not only the people on the film. Four or more need
a Company License: check [remotion.dev/license](https://www.remotion.dev/license) before
you use it at work. The skill asks at intake.

## Cost

A full multi-style two-minute film runs for hours and uses a large share of a usage
window: 35 to 55 agents, with strong models building and judging. The skill says so
before it starts and offers a 15-second test film first.

## Layout

```
SKILL.md          the director's playbook, phase by phase
references/       one file per phase, plus architecture, music, safety and rights,
                  lessons learned and a case study
templates/        fill-in documents copied into each film's docs/
scripts/          the tools (scaffold, music analysis, check renders, flash and black
                  checks, grade, preview) and Workflow scripts for the agent fan-outs
assets/template/  the Remotion starter every film begins from
dev/              how this skill was made (not loaded by the skill)
```

## Where it comes from

Built from the pipeline that made *We Built a Mind* (Firelight Innovations, 2026), a
two-minute music film in eight art styles. `references/case-study-we-built-a-mind.md`
has the numbers; `references/lessons.md` has what went wrong and how it was fixed.
