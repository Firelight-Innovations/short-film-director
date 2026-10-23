# <id>: <label>, <from> to <to> s, frames <F(from)> to <F(to) - 1>

**Status:** not started | in progress | floor only | done | blocked
**Builder:** sec-<id> (<model>)   **Dates:** <YYYY-MM-DD>
**Render range:** <a> to <b> s, frames <first> to <last>
**Brief:** `docs/sections/<id>.brief.md`

<!-- Builder: this is your log and your handover. Keep it current as you go, so someone else
could pick the section up from it. Keep these headings; the lead and the fix-round agents read
them in this order. Delete this comment. -->

## What it is

(Three sentences: what a viewer sees, the style, how it is made.)

## From the board

What the storyboard and the animatic show in this span, and what the build keeps, changes or
adds. Every change from the board says why.

| Panel | At | The board | The build |
|---|---|---|---|
| <p01> | <s> | <action, words> | <kept / changed: how and why> |

## Shots

All times are film time. "Readable" is the first frame a line can be read in the every-frame
sheets.

| Time (frames) | On screen | How it is made |
|---|---|---|
| <s to s (f to f)> | <what, which cue, readable from frame n> | <code, plate, 3D; file> |

Type sizes: <role: px, font, weight>. Ink bounds measured on lossless frames: <inside SAFE.text:
yes, or where not>.

## Transitions

For each boundary: what you did, and whether each handshake in `docs/transitions.md` is met, with
the frames you checked and how (eye on a full-size still, or numbers on a `--png` frame).

**In, <t-id> "<name>" (cut frame <f>, window <a> to <b>, owner <id>).** <What happens. Handshake:
met / not met.>

| Frame | Result |
|---|---|
| <f> | <what was measured> |

**Out, <t-id> "<name>" (cut frame <f>, window <a> to <b>, owner <id>).** <...>

## Assets

Every file you added: source, URL, licence, how processed (also logged with
`python scripts/log-asset.py`). "None" if the section is all code.

| File | Source and URL | Licence | Processing |
|---|---|---|---|
| `assets/footage/<id>/...` | <...> | <...> | <script that made it> |

Code and scripts:

| File | What |
|---|---|
| `src/sections/<id>/index.tsx` | `Section` |
| `scripts/<id>/...` | <generator; its command> |

Chain: <none | `<name>` in `data/chains.json`: inputs, build and check commands>.

Check renders in `out/check/<id>/`: <overview sheet, boundaries sheet, phone sheet, full-size
clean stills of the best frames, lossless frames>.

## Decisions

Each call you made and why. Also append each one with
`python scripts/log-decision.py "sec-<id>: what, and why"`.

- <decision, and why>

<!-- Fix rounds append here: "### Fix round <n> (<date>)", one bullet per finding: the frames,
what changed, which frames show it. -->

## Cost

| Span | ms per frame (`--bench`, full resolution) | Note |
|---|---|---|
| <a:b> | <n> | <heaviest shot> |

Plates: <n> MB in `assets/footage/<id>/`. Build time of the plates: <n> min.

## Known issues

Be honest; say what you would fix next, and where.

- <frames; what; why it stays; file>

## Requests to lead

One per line, with an id the lead can answer. This is also where you ask for anything to be
installed or downloaded, or for anything public: what, from where, under which licence. You do
not do it yourself.

| # | Request | Why | Status |
|---|---|---|---|
| <id>-R1 | <what to change, in which lead-owned file> | <the cause, with frames or a proof> | open |
