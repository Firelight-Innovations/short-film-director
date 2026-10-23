# 1. Ideation: what this skill is

How this skill was made, step one. Not loaded by the skill.

## Logline

A director for code-rendered short films. Claude takes a brief to a finished, graded,
checked mp4 by running a small film crew of sub-agents through seven phases:
intake, ideation, references, storyboard, build, review, final.

## Where it comes from

*We Built a Mind* (Firelight Innovations, October 2026): a 2:00 music film rendered in
Remotion, eight sections in eight art styles, joined by named transitions, cut to a
measured track. One lead agent; Haiku research agents; eight Opus section builders;
eight Sonnet boundary reviewers; one fresh Opus final reviewer. It shipped in one
afternoon.

What it did not have, and what this skill adds at the front: a real **ideation**
stage, a **reference board** worth the name, and a **storyboard with an animatic**
signed off before anyone builds.

## Who uses it, and when

Anyone who wants a short film made in code: a music film, an essay film, a title
sequence, a product or launch film, a data story, a social cut. Usually under five
minutes, 16:9, 9:16 or 1:1. Music-driven by default; voice-over allowed.

It should trigger on: "make a short film / video / music video / promo / explainer /
title sequence / animated essay", "turn this script (or track, or idea) into a film",
"Remotion video", "storyboard this", "animatic", "cut this to the music", and on
resuming such a project ("continue the film", "re-render the film", "the transition
at 0:40 is off").

It should not trigger on: editing a user's camera footage in an NLE, a single still
image, a slide deck, a GIF, a one-line Remotion API question.

## The seven phases (per film)

| # | Phase | Output | Gate |
|---|---|---|---|
| 0 | Intake | brief.md: length, aspect, audio, audience, platform, deliverables, rights, budget, autonomy | the user answers once |
| 1 | Ideation | three divergent concepts, scored; a treatment; the script; a section map on the music | concept sign-off (checkpoint mode) |
| 2 | References | per section: look references, technique briefs with code, facts with sources, licensed assets, fonts | none: it feeds 3 |
| 3 | Storyboard | timeline.json v1, style bible, transitions table, board frames, an animatic on the real track | **animatic sign-off** |
| 4 | Build | scaffolded project; one builder per section; integration pass | the film renders end to end |
| 5 | Review | boundary reviews; measured checks; fix rounds | zero blockers |
| 6 | Final | render, grade, measured checks, a fresh final review, at most one polish pass, report, deliverables | the user |

## Design principles (each one learned on *We Built a Mind*)

1. **The film is data.** From the storyboard on, `data/timeline.json` holds every
   section, cue (the exact words), musical mark and transition. Sections read it; the
   animatic renders it; reviewers check against it.
2. **Cut to measured music.** The track is analysed once into `data/beats.json`; every
   boundary and cue sits on a measured event. Ears are not available to agents; numbers
   are.
3. **One owner per file.** The lead owns the kit, data and scripts; each builder owns
   one section folder. Contracts between neighbours live in the transitions table.
4. **Look at every frame you claim.** Every agent renders, opens and reads its stills,
   sequences and contact sheets. A frame you have not looked at is not done.
5. **Measure what can be measured.** Flash safety, true black, colour tags, duration,
   letterbox, fps, audio: scripts with exit codes, not opinions.
6. **Fresh eyes review.** Reviewers get a brief and frames, not the builders' logs, so
   they are not told what to expect.
7. **Floor first.** A film that exists beats a film ten percent more beautiful that did
   not render. Every phase ends with something that plays.
8. **Every call is logged** with its reason, so the next session (or person) can pick
   it up.
9. **Rights and safety are part of the craft:** facts sourced to the character, flash
   limits, likeness, music rights, footage licences, AI disclosure.
10. **Spend where it shows.** Cheap models research, strong models build and judge,
    mid models review. One fan-out per phase. Check the usage window before a big one.

## Orchestration

- **Fan-outs that return documents** (concept panel, research, boundary reviews):
  Workflow scripts (ultracode) when the user has opted in, else parallel Agent calls.
- **Builders** are named background agents, one per section, so a fix round resumes
  the same agent with its context. Under ultracode a builder may run inside a workflow;
  its fix round is then a fresh agent that reads the section log.
- **The lead** never builds a section. It writes the brief, the kit, the data and the
  contracts, integrates, renders, measures and decides.

## What ships in the skill

- `SKILL.md`: the director's playbook, phase by phase, with gates.
- `references/`: one file per phase, plus architecture, music, safety and rights,
  lessons learned, and the *We Built a Mind* case study.
- `templates/`: fill-in documents (brief, concept, treatment, style bible, transitions,
  storyboard, builder brief, reviewer briefs, report).
- `scripts/`: cross-platform tools (Python and Node) that read the project's
  `timeline.json`: scaffold, music analysis, check renders, contact sheets, review
  frames, flash check, black check, grade, preview encode, decision log, plus Workflow
  scripts for the fan-outs.
- `assets/template/`: a Remotion starter that already has the kit: absolute film time,
  frame-snapped timeline, transition owners, solo harness, test cards, letterbox, grain,
  dev overlay, an animatic composition.

## Not in scope

Long-form (over about five minutes), live-action editing of camera footage, music
generation, posting to social platforms.

## Risks

- Remotion and Chromium versions drift: pin versions in the template, say which.
- Windows, macOS and Linux differ (shell quoting, ffmpeg filter escaping, console
  encodings): tools are Python and Node, not bash.
- A full build is costly (hours, a large share of a usage window): the skill says so up
  front and offers a short test film first.
- The repo is public: no media under rights, no keys, no personal data in it.
