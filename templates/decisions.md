# Decisions: __TITLE__

One line per call, timestamped, newest at the bottom. Append with
`python scripts/log-decision.py "who: what, and why"`; it writes
`- [YYYY-MM-DD HH:MM] who: what, and why` at the end of this file. Never rewrite an earlier
line: to change a call, add a new line that says what it supersedes.

**Who** is `lead`, `user` (a call the user made: quote their words), `sec-<id>` (a builder), or
a reviewer's name. **Why** is the part that matters: the next session, or the next person,
picks the film up from this file.

What to log: every gate (signed off, and by whom); every lock lifted, and by whom; every change
to timing or words after the animatic; every fact corrected or cut; model routing and the user's
rules; every fan-out (what, how many, which model); every fix round and residual accepted; every
measured check on a final file, with its numbers; every yes or no the user gave to an install, a
download or anything public (quote their words, and say which class of files a yes covers).

The form of a good line:

> - [2026-10-12 12:43] lead: timeline loader snaps every time to its frame and lookups compare
>   whole frames. Why: 99.8667 is a hair after frame 2996, so the cut to black landed a frame
>   late; found by the outro builder.
> - [2026-10-12 15:10] lead: accepted residual on frames 2864-2872: torn cuts interleave slices
>   of one figure plate with a plate that has no figure. Making them whole would break flash
>   safety; no numeral is formed from two sources.

## Log

