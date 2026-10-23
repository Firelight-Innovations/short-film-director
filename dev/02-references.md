# 2. References: what the skill was built from

How this skill was made, step two. Not loaded by the skill. The skill's own
`references/` folder is written from these digests and cites their sources.

Five research agents ran in one Workflow (2026-10-22): four web digests on a cheap
model and one deep read of the first film's project on a mid model. About 136 web
sources in all, each with what to take from it and a confidence mark.

| Digest | Covers | Sources | Feeds |
|---|---|---|---|
| [craft-ideation.md](references/craft-ideation.md) | loglines, essay films, music-video treatments, divergent concept methods (Crazy Eights, Pugh matrix), tone arcs, on-screen reading speed (DCMP, BBC, Netflix, research), title sequences (Bass, Cooper, Elastic) | 32 | `references/01-intake-and-ideation.md` |
| [remotion-technical.md](references/remotion-technical.md) | determinism, Sequence and calculateMetadata, delayRender, fonts, media components, audio, Three.js, render flags, GL backends, Windows limits, memory, Lambda, **the licence**, Remotion's own agent skills, alternatives | 35 entries, 54 URLs | `references/04-architecture.md`, intake licence check |
| [storyboard-music.md](references/storyboard-music.md) | thumbnails, beat boards, animatics, style frames, shot lists; cutting to music, Murch's rule of six; librosa, madmom, Essentia and their failure modes; a transitions catalogue; timecoded review notes | 34 | `references/03-storyboard.md`, `references/music.md`, `references/06-review.md` |
| [rights-safety-sourcing.md](references/rights-safety-sourcing.md) | open collections and their terms, stock licences, font licences, music licensing and Content ID, fair use, likeness, AI disclosure by platform and the EU AI Act, flash safety (WCAG 2.3.1, ITU-R BT.1702), captions, fact-checking | 35 | `references/02-references.md`, `references/safety-and-rights.md` |
| [wbam-lessons.md](references/wbam-lessons.md) | the first film's pipeline in numbers, 25 things that worked, 45 gotchas with symptom, cause and fix, 19 changes for next time, the contract, the tool inventory, the briefs | the project itself | `references/lessons.md`, the case study, every tool |

## What changed in the skill because of them

The storyboard's Part G (`03-storyboard.md`) lists every change; the main ones:

- **Intake** checks the Remotion licence (free for a collaborating group of up to three
  people), pins the version, and starts a rights register.
- **Ideation** diverges (about eight one-liners) before it converges (three concepts and
  a wildcard), scored with a Pugh matrix against two datums.
- **Words on screen** default to 150 words a minute or slower, 5/6 s to 7 s per text event,
  two lines at most.
- **Facts** get two independent checks and a verdict before the storyboard gate.
- **Storyboard** goes thumbnails, beat board, animatic, and writes a cut list.
- **Reviews** add motion and sync traces, phone-size sheets, sampling by cue, and a short
  second final review on the frames that changed.
- **Tools** gain `doctor`, `chain` (dependent-asset rebuilds), `motion-check`,
  `sync-check`, `diff-frames`, `log-asset`, and `shots.mjs` gains `--png`, `--through`, a
  per-still timeout and a private bundle per run.
- **The report** records cost per agent and a human watch with the sound on.

## Caveats the digests raised

- Some pages were blocked or read only through search excerpts (Smithsonian, the Met,
  the Art Institute of Chicago, Artlist, TikTok and LinkedIn policies); those entries are
  marked medium or low confidence, and the skill hedges them.
- Netflix's English characters-per-second figure could not be confirmed; the skill uses
  the more conservative 150 words a minute.
- Only the emotion weight (51 percent) of Murch's rule of six was seen in a source; the
  skill uses the order, not the other weights.
- Remotion's LICENSE says "up to 3 employees" and its FAQ says "up to 3 people" and adds
  collaborators; the skill takes the stricter reading.
