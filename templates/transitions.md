# Transitions: <title>

One named device per boundary, none repeated (`<skill>/references/03-storyboard.md`,
sections 6 to 8). `data/timeline.json` (`transitions`) is the authority for times; this
file is the direction. Replace each `<prompt>`; delete each example line.

## How a transition is built

During a window `[at - pre, at + post)` the film mounts **only the owner** and hands it the
other section's live render: `next` if the owner is the outgoing section, `prev` if it is
the incoming one. The owner draws that node where it likes, under, inside or around its
own layers. If it never draws it, the neighbour is not on screen.

- The owner can mask, clip, move, scale, blur, invert and displace the neighbour; it cannot
  read the neighbour's pixels into WebGL.
- Both sections draw valid full frames across the whole window, including the part outside
  their own span.
- A hard cut has `pre = post = 0`: no window, and the frame at `at` belongs to the
  incoming section.

## Windows in frames

Seconds are rounded; frames are the truth (`f = round(at x fps)`).

| Transition | Cut frame | Owner mounted with the neighbour on frames | First frame the incoming section is alone |
|---|---|---|---|
| <t-id name> | <frame> | <first to last frame (who holds whom), or "none (hard cut)"> | <frame> |
| *t-00-01 Tracking tear* | *158* | *130 to 163 (00-hook holds 01 as `next`)* | *164* |

## The table

| Boundary | At (s / frame) | Name | Owner | Window (s) | Device | Lands on |
|---|---|---|---|---|---|---|
| <start to NN> | <s / frame> | <the device's name> | <section id> | <from to to, or "none"> | <what happens, frame by frame, in one or two sentences> | <the mark or measured event> |
| *00 to 01* | *5.2667 / 158* | *Tracking tear* | *00-hook* | *4.333 to 5.467* | *the archive loses tracking; slices slip, lag and rip open; 01 shows through the gaps* | *the strongest hit of the track, 5.259* |

## What each side owes the other (the handshakes)

The only places two sections must agree on pixels. Write each so a script could assert it:
a colour, a position, a frame range, and what is absent. Repeat each line on both sections'
pages of the style bible.

- **<A> / <B>:** <exact obligations, in pixels and seconds>
  *Example: From 48.900 to 50.267 the outgoing frame is `#0a0a0a` with one 2 px line
  `#f4f1e8` at y = 540, full width, and nothing else; the opening starts as that line.*

## Internal shifts

Shot changes inside one section, listed so no device repeats across the film.

| Where | At | Device |
|---|---|---|
| <section id> | <s, s, ...> | <the device> |
| *05-build-dread* | *73.00, 77.80* | *a match on the ring; a dive through an arch* |

## Render order

<which sections depend on other sections' finished frames, and the chain that rebuilds
them; or "no dependencies">
*Example: 06 is cut from frames of the finished film: render it after 00 to 05 are
integrated, with `python scripts/chain.py run 06-plates`.*
