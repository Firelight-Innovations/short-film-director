# Script: <title>

Every word that will be on screen or spoken, in film order
(`<skill>/references/01-intake-and-ideation.md`, sections 14 and 15). The words in
`data/timeline.json` must end up equal to the **Text** column, and for `data` and `quote`
cues equal to the verified wording in `docs/research/facts.md`.

**Reading budget:** 0.4 s a word plus 0.5 s, never under 0.83 s; at most 7 s an event
(`logo` and `credit` cues are exempt); two lines at most; each line within about 68 percent
of the frame width (1306 px at 1920; 972 px, the title-safe width, for 9:16).
Every text shot works with the sound off. Ids are role-based (`slam-1`, `data-3`), never
content.

| Cue id | Section | Role | Text (exact; `\n` for a line break) | Words | Minimum (s) | Window (s) | Sound off? | Claimed source |
|---|---|---|---|---|---|---|---|---|
| <role-n> | <NN-name> | <role> | <the exact words> | <n> | <0.4 n + 0.5> | <from to to> | <yes, or why not> | <for data and quote: publisher, title, year> |
| *narration-1* | *00-open* | *narration* | *Every frame is a function of time.* | *7* | *3.3* | *2.8 to 6.4* | *yes* | |

## Checks

- **Read aloud against the track:** <date; what did not fit and what was cut>
  *Example: 2026-10-22; narration-4 cut from 19 to 12 words.*
- **Events over 16 words (split them):** <cue ids, or "none">
  *Example: none*
- **Fact-check:** <date run; verified, corrected, unverified, cut counts; lines changed>
  *Example: 2026-10-22; 4 verified, 3 corrected, 1 cut (data-5 removed).*
