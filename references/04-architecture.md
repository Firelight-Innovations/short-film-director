# 04. Architecture: the Remotion kit and the rules behind it

Read this before Phase 4, and give it to every section builder. It describes the code a
film lives in (copied from `<skill>/assets/template/` by `new-film.mjs`), what the kit
gives a section, and the rules every section follows. Each rule says why it exists:
almost every one is a failure that happened on *We Built a Mind*, the first film made
this way (`references/case-study-we-built-a-mind.md`, `references/lessons.md`).

Pinned versions: remotion and every `@remotion/*` package 4.0.410, react and react-dom
19.0.0, typescript 5.6.3, zod 3.22.3, three 0.170. Remotion 5.0 changes defaults that
alter output (colour space, GL backend, audio visualisation), so stay on 4.x until a film
is finished [1].

## Contents

1. [The code a film lives in](#1-the-code-a-film-lives-in)
2. [The kit surface](#2-the-kit-surface)
3. [Absolute film time](#3-absolute-film-time)
4. [Frames, not seconds](#4-frames-not-seconds)
5. [Sections, the registry and test cards](#5-sections-the-registry-and-test-cards)
6. [Transitions: the owner model](#6-transitions-the-owner-model)
7. [Render ranges](#7-render-ranges)
8. [The compositions and the solo harness](#8-the-compositions-and-the-solo-harness)
9. [Determinism](#9-determinism)
10. [Assets: images, video, plates](#10-assets-images-video-plates)
11. [Fonts](#11-fonts)
12. [Three.js](#12-threejs)
13. [SVG filters and other slow CSS](#13-svg-filters-and-other-slow-css)
14. [Heavy looks: pre-render them as plates](#14-heavy-looks-pre-render-them-as-plates)
15. [Sections with baked words](#15-sections-with-baked-words)
16. [Sections that reuse the film's frames](#16-sections-that-reuse-the-films-frames)
17. [Chains, the lock and doctor](#17-chains-the-lock-and-doctor)
18. [Colour: limited-range BT.709](#18-colour-limited-range-bt709)
19. [GL backends](#19-gl-backends)
20. [Memory, concurrency and a shared machine](#20-memory-concurrency-and-a-shared-machine)
21. [The Windows command-line limit](#21-the-windows-command-line-limit)
22. [The speed budget](#22-the-speed-budget)
23. [Sources](#23-sources)

---

## 1. The code a film lives in

```
data/timeline.json        the film as data: sections, cues, marks, transitions, checks, grade
data/beats.json           the measured track (scripts/analyze_music.py); never hand-edited
data/chains.json          dependent-asset chains (section 17)
src/index.ts  Root.tsx    registers the compositions Film, Solo, Animatic
src/kit/                  everything a section may import (src/kit/index.ts)
src/timeline/             the typed loader and lookups for timeline.json
src/style/tokens.ts       canvas, letterbox, safe areas, palettes, all read from the timeline
src/components/           film-wide layers: AudioTrack, Grain, Letterbox, DevOverlay
src/sections/registry.ts  section id -> component; the only file that imports every section
src/sections/<id>/        one folder per section, owned by its builder; index.tsx exports Section
assets/                   Remotion's public dir: audio/, fonts/, board/, footage/<id>/, tex/
scripts/<id>/             a section's plate generators
work/<id>/                a section's sources and intermediates (gitignored)
```

Ownership is by path. The lead owns `src/kit/`, `src/timeline/`, `src/style/`,
`src/components/`, the registry, `data/` and `scripts/` (except `scripts/<id>/`). A
builder owns `src/sections/<id>/`, `assets/footage/<id>/`, `scripts/<id>/`, `work/<id>/`
and `docs/sections/<id>.md`. Why: eight builders worked in one tree on the first film
with no merge conflict, because no two of them ever wrote the same file.

## 2. The kit surface

Sections import only from `src/kit` (and from their own folder). If something is
missing, the builder writes a local version in its folder and asks for it under
"Requests to lead" in its log.

| Group | Names | Why it is in the kit |
|---|---|---|
| Time | `useFilmTime() -> { frame, t, fps }`, `FilmClockOverride`, `F(sec)`, `T(frame)` | One clock for the whole film, so a section, its neighbour and the dev overlay agree on the frame (section 3) |
| Pure helpers | `clamp lerp ease prog remap envelope hold rnd rndRange` | Motion as a function of time; seeded randomness. Nobody rebuilds a clock, an easing or a random |
| Timeline | `timeline section(id) sectionAt(t) cue(id) cuesOf(id) cuesAt(t) mark(name) transitionIn(id) transitionOut(id) transitionAt(t) renderRange(id) formatTimecode(t)` | Words and times come from the data, snapped to frames at load (section 4). `section`, `cue` and `mark` throw on a bad id, so a typo fails loudly |
| Music | `music BEATS DOWNBEATS ONSETS level(frame, band) beatIndex(t) sinceBeat(t) beatEnv(t, decay) beatsIn(a, b)`; band is `energy`, `low`, `mid`, `high` or `onset` | Motion that answers the track reads the measured track, not a timer |
| Fonts | `font(family)`, `weightsOf(family)` | Vendored fonts that hold the frame until loaded (section 11) |
| Tokens | `CANVAS LETTERBOX_PX SAFE PALETTE(id)` | Size, bars, safe areas and each section's palette, read from the timeline, so neighbours can quote each other's colours without importing each other's code |
| Types | `SectionComponent`, `SectionProps { from, to, prev?, next? }`, `Cue`, `CueRole`, `SectionSpan`, `Timeline`, `Transition` | The contract between the film and a section |

Notes on a few of them:

- `prog(t, a, b, easing?)` is 0..1 progress through `[a, b]`, clamped. `remap(t, a, b, c,
  d, easing?)` maps `[a, b]` to `[c, d]`, clamped. `envelope(t, from, to, fadeIn,
  fadeOut)` is 0 -> 1 -> 0 over a span. They take seconds or frames alike.
- `hold(frame, n)` is `Math.floor(frame / n) * n`. Use it as the seed for boil and jitter
  ("on twos"), so a texture holds for n frames instead of buzzing every frame.
- `rnd(seed)` is Remotion's `random(seed)`: the same seed gives the same number in every
  render tab [2]. Build seeds from stable strings: `rnd("dust-" + i + "-" + hold(frame, 2))`.
- `level(frame, band)` is 0..1 per frame from `beats.json`; `beatEnv(t, decay)` is 1 on a
  beat and decays after it; `sinceBeat(t)` is seconds since the last beat.
- `transitionIn(id)` and `transitionOut(id)` return `null` when the timeline has none.
- The template also exports `UNIT` (the short side of the frame over 1080; write sizes as
  `54 * UNIT` so they keep their share of the frame at 4K or 9:16), `shownOf(cue)` (the
  drawn window, section 4), `mustBeBlack(frame)` (true on frames `checks` says must be pure
  black: draw `#000` and mount nothing else there, because a layer at a tiny opacity is
  not 0), `DURATION_FRAMES` and `SYSTEM_FONTS`.

## 3. Absolute film time

Sections are mounted without a `<Sequence>`, so frame 0 is the first frame of the film.
`useFilmTime()` reads the clock the root provides (`FilmClockProvider`), so it stays
absolute even inside a `<Sequence>`, `<Freeze>` or `<Loop>` a section adds itself. Use it
instead of `useCurrentFrame()`.

Why: a section's cue times, marks and its neighbour's windows are all in film time. A
section clock that started at zero would need every time translated, and one mistake
puts a word on the wrong beat.

`FilmClockOverride` pins the clock for a subtree. An owner uses it to freeze a neighbour
on one frame or to replay it:

```tsx
// hold the outgoing picture on the frame before the cut while ink covers it
<FilmClockOverride frame={cut - 1}>{prev}</FilmClockOverride>
```

Consequence for every section: never tie a plate index or an animation to a local
counter. On the first film a section that played its image sequence from
`useCurrentFrame()` showed the wrong plate when its neighbour pinned it. Play plates by
film frame (section 10).

## 4. Frames, not seconds

`timeline.json` stores seconds to a few decimals. A typed second is not a frame:

- `5.2667` is a hair after frame 158 (158 / 30 = 5.266667). So `t >= 5.2667` is false on
  frame 158 and fires on frame 159, one frame late.
- `99.8667` is a hair after frame 2996. On the first film a lookup in seconds mounted the
  previous section on frames 158, 2015, 2795 and 2996, and the cut to black landed a frame
  late. A builder found it, not the lead.
- `16.0833` is half a frame (482.5 x 1/30). A mark there has no frame at all.

So the loader snaps every time to its frame when it reads the file, and the lookups
compare whole frames. In a section:

- Use kit values: `cue("slam-1").from`, `mark("drop")`, `section(id).from`, and the
  `from` and `to` props. They are exact, so `t >= cue("slam-1").from` is true on the cue's
  first frame.
- Never type a time in seconds. Write `frame >= 158`, `frame >= F(5.2667)`, or a kit
  value. A section with many internal events keeps them as frame numbers in one file
  (`times.ts`), derived from kit values where it can.
- The same rule holds in Python and ffmpeg. `grade.py` gates the grade with the frame
  number (`lt(n, ...)`); a gate in seconds (`lt(t, 99.8667)`) still graded the first black
  frame on the first film.

Cue windows mean one thing: `from` is the first frame the words must be **readable**
(whole), `to` is when they may go. An entrance that writes on must start before `from`,
6 to 10 frames early; on the first film write-ons that began on the cue's frame showed
"Disea" and "Poverty endec" on that frame. When what is drawn differs from the readable
window, the lead records it in the cue's `shown: { from, to }`, and `check-timeline.py`
fails (exit 3) on any `shown` window outside the section's render range. `shownOf(cue)` returns the
drawn window. Builders do not edit the timeline; they put the drawn window in "Requests
to lead".

Cue ids are role-based (`stamp-1`, `slam-2`, `data-3`), never content: `stamp-1962`
once said 1966.

## 5. Sections, the registry and test cards

`SectionId` is a string; the sections come from `timeline.json` and match
`^[0-9]{2}-[a-z0-9-]+$`. `src/sections/registry.ts` maps ids to components. An id with no
component renders as a labelled test card in its palette, so a section added to the
timeline plays at once and the film always renders end to end. Before the builders launch,
each section gets a stub that is the same card, registered
(`export const Section = makePlaceholder("<id>");`, with `makePlaceholder` imported from the
kit; 05-build.md, section 3). `doctor.py` fails an unregistered section.

A section is one component:

```tsx
// src/sections/<id>/index.tsx
import { AbsoluteFill } from "remotion";
import { useFilmTime, cue, F, PALETTE, SAFE, font } from "../../kit";
import type { SectionComponent } from "../../kit";

const SERIF = font("Cormorant Garamond");               // module top level

export const Section: SectionComponent = () => {         // props: { from, to, prev?, next? }
  const { frame } = useFilmTime();                       // absolute film frame
  const pal = PALETTE("<id>");
  const line = cue("narration-1");
  const on = frame >= F(line.from) - 8 && frame < F(line.to);   // entrance 8 frames early
  return (
    <AbsoluteFill style={{ background: pal.bg }}>
      {/* shots first, then words */}
      {on ? (
        <div style={{ position: "absolute", left: SAFE.text.left, width: SAFE.text.width, top: SAFE.centerY,
          textAlign: "center", whiteSpace: "pre-line", fontFamily: SERIF, fontSize: 72, color: pal.ink }}>
          {line.text}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
```

Destructure only the props you use: the template's `tsconfig.json` makes unused names an
error.

The root is an opaque `<AbsoluteFill>` that covers the canvas. The film adds the music,
a light grain, the letterbox and the dev overlay on top (`FilmFrame`, bottom to top:
AudioTrack, FilmStack, Grain, Letterbox, DevOverlay). A section never adds its own
letterbox or audio. Words stay inside `SAFE.text`; anything that moves the eye stays inside
`SAFE.action`; nothing that matters sits under the bars (`LETTERBOX_PX` top and bottom).

## 6. Transitions: the owner model

During a transition window `[at - pre, at + post)` (whole frames) the film mounts **only
the owner** and hands it the other section's live render as a React node: `next` when the
owner is the outgoing section `a`, `prev` when it is the incoming section `b`. The owner
places that node wherever it wants: under its own layers, in a mask or clip-path, inside a
CSS or SVG filter, scaled, sliced, frozen with `FilmClockOverride`.

```tsx
export const Section: SectionComponent = ({ prev }) => {
  const { frame } = useFilmTime();
  const tin = transitionIn("<id>")!;
  const k = prog(frame, F(tin.at - tin.pre), F(tin.at + tin.post), ease.inOut);
  return (
    <AbsoluteFill>
      <MyFirstShot />
      {prev ? (
        <AbsoluteFill style={{ clipPath: `inset(0 0 ${k * 100}% 0)` }}>{prev}</AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
```

Why this model: no section depends on another's rendered pixels, any device a mask,
filter or transform can make is possible, and exactly one side answers for every pixel in
a window. Consequences:

- If the owner never draws the node, the neighbour is not on screen.
- The owner cannot read the neighbour's pixels into WebGL or a canvas. A device that needs
  the neighbour as data (a displacement of its luminance, a particle per pixel) is built
  from a shared plate both sides use, named in the handshake.
- Both sections draw valid full frames across the whole window, including the part outside
  their own span.
- A hard cut has `pre = post = 0`: no window, nothing shared, and the cut frame belongs
  entirely to the incoming section. Edge transitions (`t-start`, `t-end`, with no `a` or
  no `b`) never open a window.

**Handshakes.** For each boundary, `docs/transitions.md` states in exact pixels and frames
what each side owes the other, and repeats it on both sections' style-bible pages. Example
of the form: "From 48.9 s to the cut, S3 is `#0a0a0a` with one 2 px line `#f4f1e8` at rows
539 and 540, full width; S4's opening starts as that line." Both builders build to the
line, neither sees the other's code, and a script can assert it on lossless frames. Every
handshake of this kind held in the first film's final cut.

## 7. Render ranges

`renderRange(id)` is the section's span plus the transition windows on both sides, in
seconds, whoever owns them. A section draws a full, opaque frame for every frame in it:
start the first shot early and keep the last shot running late. Never return `null` or a
transparent frame in that range.

Why: the owner of a window renders the neighbour as `prev` or `next` for frames outside
the neighbour's own span. A neighbour that returns nothing there leaves a hole, or a black
frame, in the middle of a device.

## 8. The compositions and the solo harness

| Composition | What it is | Props |
|---|---|---|
| `Film` | the whole film, every registered section real | `showDevOverlay`, `grainStrength`, `muteAudio`, `debugSolo`, `bare`, `through` (applies with `debugSolo`) |
| `Solo` | one section real, every other section a test card, rendered over its render range | the Film props; `debugSolo` (required: the real section) and `through` |
| `Animatic` | `storyboard.json` panels, the real cues at their real times, a strip with section, panel and timecode, marks as ticks, transition names in their windows, the music | |

- `bare` drops grain, letterbox and overlay: picture only, for plates cut from the film
  (section 16). `debugSolo` makes `Film` show one section real.
- `data/props.final.json` holds the final props (overlay off). Studio and check renders
  default to the overlay on. Bars at least 34 px tall (scaled by `UNIT`) carry it and no
  picture is touched. With `letterbox` 0 (which `new-film.mjs` sets for any frame narrower
  than 3:2, 9:16 among them) it covers the top and bottom 34 px of picture with a 55 percent
  black strip, so judge edges on `--clean` stills.
- In `Solo` a test card that owns a transition draws nothing of the real section inside
  its window, so the frames a neighbour owns cannot be seen. `through: true`
  (`shots.mjs --through`) makes neighbouring owners place the live section full-frame
  instead. On the first film three builders each wrote their own harness to get this; it
  is now one flag.
- `Solo` is `Film`'s compositing with the registry swapped (`debugSolo` names the real
  section), so every bundle imports every registered section. Type errors do not stop a
  bundle (they show in `npm run typecheck`), but a syntax error or a broken import in one
  section stops everyone's check renders until it is fixed. Never leave a section folder
  half-saved and unimportable.

## 9. Determinism

Remotion renders frames out of order, some more than once, in several browser tabs that
share no state [3]. A frame must be a **pure function of its frame number** (and the
props and the timeline).

Banned in a section: `Math.random`, `Date`, `performance.now` as a clock, `setTimeout`,
`setInterval`, `requestAnimationFrame`, react-three-fiber's `useFrame`, CSS `transition`,
`animation` and `@keyframes`, and any `useState` or ref that accumulates from frame to
frame. CSS animations and timers cannot know the current frame [3].
`--concurrency=1` hides some of this and guarantees nothing [3].

Every section passes four component checks before its frames count as done (from the
Remotion flicker guide [3]):

| Check | How to test it |
|---|---|
| Same output on repeat calls | render the same frames twice with `--png` and compare them |
| No dependence on render order | render frames out of order (`--f 900,700,800`) and in a `--seq`, and compare the same frames |
| Nothing animates while paused | search the folder for clocks and CSS animation (command below); in Studio, a paused frame must not change |
| Randomness only through `rnd()` | search for `Math.random`; seeds are stable strings |

```
git grep -nE --untracked "Math\.random|Date\.now|new Date|performance\.now|setTimeout|setInterval|requestAnimationFrame|useFrame|@keyframes|animation:|transition:" -- src/sections/<id>
```

It must print nothing (or only lines you can explain, such as a comment).

Comparing renders: Chromium's text rasteriser and image resampling are not bit-stable. On
the first film 200 or more pixels on text differed by up to 3/255 between two renders of a
pure frame. Assert exact equality only on frames without text or scaled images; elsewhere
allow at most 3/255 on at most 0.05 percent of pixels, and say so.

Python generators follow the same rule: seed every random from a string key (the section,
the shot, the index), never from the clock or from call order.

## 10. Assets: images, video, plates

Everything a render loads lives under `assets/` (the public dir) and is referenced with
`staticFile("footage/<id>/a.webp")`. `staticFile` encodes file names itself since v4; do
not pre-encode them [4].

**Images.** Use Remotion's `<Img>`, never a plain `<img>`. `<Img>` holds the frame until the
image has loaded (it wraps `delayRender`), so a slow image cannot leave a blank frame; it
retries twice by default [4].

**Image sequences (plates).** Play them by film frame, one plate per film frame:

```tsx
const { frame } = useFilmTime();
const i = clamp(frame - FIRST, 0, COUNT - 1);
<Img src={staticFile(`footage/<id>/seq/${String(i).padStart(4, "0")}.webp`)} />
```

WebP with alpha for plates that lie over something; JPEG at quality 95 to 97 with 4:4:4
chroma for opaque plates that must match a still exactly. A clamp to the plates you have
turns a missing plate into a freeze; `motion-check.py` finds freezes (06-review.md).

**Video.** Three choices:

| Component | Use it when | Watch out |
|---|---|---|
| `Video` from `@remotion/media` | new code that plays a clip; recommended by Remotion: frame-accurate, fastest [5] | not in the template's `package.json`; the lead adds it at intake if a film needs it (builders never install) |
| `OffthreadVideo` (core) | a clip, extracted by FFmpeg outside the browser | no `loop` (the last frame holds), so trim explicitly; on the first film it returned a BT.709 clip about one level darker than the same frame as PNG, a visible step at a hand-off to a still [5] |
| a JPEG or WebP sequence with `<Img>` | a clip that must hand off seamlessly to a still, or that you have already processed per frame | disk size |

Avoid `Html5Video`: it is not frame-accurate [5]. Put a clip in a `<Sequence from={F(t0)}
layout="none">` to set when it starts; the film clock outside stays absolute.

**Anything loaded by hand** (a texture, a JSON fetched at render time, a canvas drawn from
an image) holds the frame with `delayRender`:

```tsx
const { delayRender, continueRender, cancelRender } = useDelayRender();
const [handle] = useState(() => delayRender("02-ink: stroke atlas", { timeoutInMilliseconds: 120000, retries: 2 }));
useEffect(() => {
  loadAtlas().then(() => continueRender(handle)).catch((err) => cancelRender(err));
}, [handle]);
```

- Create the handle once (in `useState`); a handle made in the component body is a new one
  on every re-render [6].
- Label every handle with the section and what it waits for: the label is printed when it
  times out [6].
- Set an explicit timeout. The default is about 30 s, and a loaded machine needs longer
  (section 20).
- Release the handle in the error branch too, or call `cancelRender(err)` for an error the
  render cannot recover from. A section that detects stale plates calls `cancelRender`
  with the command that rebuilds them, so the render stops with an instruction instead of
  shipping old frames.

## 11. Fonts

Fonts are vendored, never fetched at render time: `node scripts/fetch-fonts.mjs
"Family:400,700" ...` downloads them from Google Fonts into `assets/fonts/` (only after the
user's yes to downloads; builders never run it: they ask the lead) and records them in
`src/kit/fonts.manifest.json`. A section calls `const SERIF = font("Family")` at module
top level and uses the returned CSS family. A family that is not vendored falls back to
a system font with a console warning, so the film still renders, but on a font that
differs between machines; `python scripts/doctor.py` reports every such `font("X")`.

Why: a render that fetches fonts depends on the network, and a font that has not loaded
when the frame is taken renders in a fallback. `font()` holds the frame with a labelled
`delayRender`, a 180 s timeout and three retries: on the first film two builders and the
lead each lost a render to "a delayRender() font was not cleared after 28000ms" while
other renders were running.

A licensed brand typeface (a client's own font) is not on Google Fonts, so `fetch-fonts.mjs`
cannot vendor it. Copy the file into `assets/fonts/`, add its row to
`src/kit/fonts.manifest.json` by hand (`{ "family", "style", "weight", "file": "fonts/<name>",
"format" }`, `format` one of `woff2`, `woff`, `opentype`, `truetype`; later `fetch-fonts.mjs`
runs keep a row they did not write), check that the licence allows embedding the font in a
video, and record it: `python scripts/log-asset.py "assets/fonts/<name>: <foundry>, <licence
URL or agreement>, licensed, embedded in the rendered video"`. `doctor.py` then finds the
family like a vendored one. A licensed file is not for a public repository: add its path
to `.gitignore` and say in the report how to put it back (07-final-and-delivery.md,
section 11).

Rules that came from real faults:

- A glyph the font lacks (IBM Plex Mono has no empty-set sign) falls back to a system font,
  which makes the render depend on the machine. Draw it as SVG.
- Old-style figures can misread ("10" read as "1o" in Cormorant). Set
  `fontVariantNumeric: "lining-nums"` on numbers.
- Measure text (`fitText` from `@remotion/layout-utils`) only after the font has loaded
  [7].
- Python cannot draw with woff2 (Pillow reads TTF and OTF only). Convert a copy to TTF
  under `work/` with fontTools if it is installed; never ship the converted copy.

## 12. Three.js

Use `<ThreeCanvas width={CANVAS.width} height={CANVAS.height}>` from `@remotion/three`
(width and height are required) [8]. Rules:

- **Drive everything from the film frame passed in as a prop.** react-three-fiber renders
  in its own React root, so the kit's film clock does not reach inside the canvas. Read
  `useFilmTime()` outside and pass `frame` down. On the first film a 3D shot froze or ran
  on the wrong frame when the next section replayed it through `FilmClockOverride`,
  until the frame came in as a prop.
- Never use `useFrame`; `ThreeCanvas` sets `frameloop` to `never` [8]. After an
  asynchronous texture update, advance the scene as the Remotion docs describe [8].
- A `<Sequence>` inside the canvas needs `layout="none"` [8].
- Put text in the DOM above the canvas: it is sharper and exact.
- One canvas mounted at a time keeps memory down: key the scene by shot and mount only
  the current shot.
- WebGL needs a GL backend that works on the machine (section 19).

## 13. SVG filters and other slow CSS

- Give every filter `filterUnits="userSpaceOnUse"` and a region larger than the frame
  (for example `x="-200" y="-200" width="2320" height="1480"` at 1080p). The default
  region is the element's box plus 10 percent, so blurs and displacements clip at a hard
  rectangle.
- A full-frame `feTurbulence` regenerated every frame is slow. Use a pre-made noise plate
  under `assets/tex/` moved by transforms, seeded with `hold(frame, 2)`.
- GPU-dependent CSS and canvas work (filter blur, box-shadow, text-shadow, large
  gradients, WebGL) is slow, and slower on a machine without a GPU [9]. If a look costs
  over budget, pre-render it (section 14).

## 14. Heavy looks: pre-render them as plates

Per-pixel looks (film and tape damage, interlace, chroma bleed, charcoal and paint
strokes, tracked meshes, fluid ink) cannot run in a browser within budget. Do the work once
in Python (numpy, scipy, OpenCV, Pillow, librosa; matplotlib is optional for plots),
Blender (`blender -b`) or ffmpeg, write plates into `assets/footage/<id>/`, and play them back with `<Img>`. On the first film
every heavy look was done this way and played back at 50 to 130 ms a frame; the full
3600-frame render took under three minutes.

Rules for a generator in `scripts/<id>/`:

- Read words and cut points from `data/timeline.json` (`encoding="utf-8"`; Windows
  defaults to cp1252 and fails on curly quotes). Never hard-code a frame the timeline
  holds: duplicated constants drift.
- Be deterministic: seeds from string keys.
- Sources and intermediates go to `work/<id>/` (not committed); only final plates go to
  `assets/footage/<id>/`. Keep a section's plates under about 250 MB.
- Write a manifest of what was built and fail loudly on a gap: a frame in the render
  range with no plate, or a file that is missing.
- Give it a preview mode (a few frames, a contact sheet), so a look can be judged before
  a full build.
- Record every outside source with `python scripts/log-asset.py "<file>: source, URL,
  licence, how processed"`.
- Declare the generator as a chain (section 17) when its output depends on the timeline.
- A look that must register with code-drawn layers (a painted landscape and a wireframe of
  the same hills) comes from one scene description that both renderers read, with one
  shared camera.

## 15. Sections with baked words

Some looks draw their words into the plates (lettering chalked through paper tooth, a
title scratched into emulsion). Then a cue change does nothing on screen until the plates
are rebuilt. Rules:

- The generator reads the cue's `text` from the timeline at build time and draws it
  character for character.
- The section declares a chain whose inputs include `data/timeline.json#cues:<id>`, so a
  changed cue makes the chain stale, `chain.py check` fails and `doctor.py` stops the
  render.
- Line breaks and case are typesetting; words and punctuation are not. Any other change to
  a cue's wording is the lead's, in the timeline, and facts need a re-check.

## 16. Sections that reuse the film's frames

A recap, a rewind, a mosaic of the whole film: a section made from frames of the finished
film. On the first film the overload section was cut from 38 plates rendered out of the
integrated film. Rules:

- List the plates in a manifest (`data/plates.json`: a `consumer` section id, and each
  plate's film time `t` or frame `f` and the `file` under `assets/` it goes to) and render
  them with `node scripts/plates-from-film.mjs <plates.json>`. It renders `bare` stills of
  `Film` (no grain, letterbox or overlay), because the section scales and tiles them and
  baked-in bars would show as black bands. A `.png` file is lossless, `.jpg` is quality 95.
- No plate may fall inside the consuming section's render range (the tool refuses it): a
  section cannot contain frames it has not made yet.
- The section is built last, after the sections it samples are integrated. Until then it
  builds against placeholder plates, and **a placeholder is not a design reference**: on
  the first film black letters designed on a placeholder vanished on the real plate.
- Its chain lists the sampled sections as inputs (`data/timeline.json#section:<id>` and
  their folders) and runs the plate render, the section's own plate build and a flash check
  of its span. After any fix to a sampled section, the chain is stale and is re-run
  (06-review.md).
- Plates that carry figures or words must not be torn or blended into each other: on the
  first film two plates with different figures interleaved into a number no source gave.
  Name such plates and keep them apart.

## 17. Chains, the lock and doctor

`data/chains.json` declares every dependent-asset chain:

```jsonc
{ "chains": [
    { "name": "00-open-plates",
      "inputs": ["data/timeline.json#cues:00-open", "scripts/00-open/**", "work/00-open/src/**"],
      "outputs": ["assets/footage/00-open/seq/*.webp"],
      "build": ["python scripts/00-open/build.py all"],
      "check": ["python scripts/flash-check.py out/check/00-open --from 0 --to 8.5"] } ] }
```

`inputs` are globs, or `data/timeline.json#cues:<section>` (that section's cues, hashed)
or `data/timeline.json#section:<id>`. Commands:

```
python scripts/chain.py list               every chain and whether it is fresh
python scripts/chain.py check [name]       exit 3 when any chain is stale
python scripts/chain.py run [name|--all]   build, then check, then write data/chains.lock.json;
                                           no name: every stale chain, until none is;
                                           --all: every chain
python scripts/doctor.py [--quick]         the pre-render health check
```

`doctor.py` checks, one PASS, WARN or FAIL line each: the timeline is valid (it runs
`check-timeline.py`); every chain is fresh against its lock; every `font("X")` used in
`src/` is vendored; every `staticFile("...")` literal and every board image exists under
`assets/` with the exact case (Windows forgives a wrong case; Linux does not); every
registered section id is in the timeline and the other way round; `beats.json` exists when
the film has audio (and a WARN when it holds beats but `timeline.audio` is null, because
the film would render silent); the installed Remotion packages match the pins in
`package.json`; the final props turn the dev overlay off; ffmpeg and ffprobe are on PATH;
on Windows, the project path leaves room for Remotion's headless Chrome (the path plus about
110 characters must stay under 260, or every render fails with an ENOENT spawn error); and
numpy, scipy, cv2, PIL and librosa import (matplotlib only warns: it draws plots).
`doctor.py` never installs anything. Exit 3 on any FAIL. A fresh scaffold fails the registry
check until Phase 4 gives every section a stub, and the Remotion check until `npm install`
has run; that is expected.

Why: on the first film a changed cue in a baked section, or any change to the sections the
recap sampled, would have shipped old frames silently, and three hand-run commands were the
only guard. Run `doctor.py` before every full render of the Film (Phase 4 on). Write
`staticFile` paths as literals where you can, so `doctor.py` can see them; a path built from a
frame number is covered by the generator's own manifest instead.

## 18. Colour: limited-range BT.709

Render with `--color-space=bt709` (set in `remotion.config.ts` with
`Config.setColorSpace("bt709")`, and passed by `render:final`). Measured on 4.0.410 with a
six-frame test clip:

| Render | Pixel format | Range | Matrix | Black (Y) | White (Y) |
|---|---|---|---|---|---|
| default colour space | `yuvj420p` | full (`pc`) | `bt470bg`, transfer and primaries unset | 0 | 255 |
| `--color-space=bt709` | `yuv420p` | limited (`tv`) | `bt709` | 16 | 235 |

Why it matters: ffmpeg's `drawbox` paints black as limited-range Y 16. Drawn into a
full-range file, the letterbox bars decode to RGB 16 beside picture black at RGB 0: grey
bars. That is what happened on the first film; in the same test the bars drawn into the
bt709 file decode to RGB 0, the same as the picture. So the render is bt709 limited range,
`grade.py` converts to limited-range BT.709 before it grades and forces the tags at the
end, and `black-check.py` measures black and the bars on the graded file. Remotion's own
pages disagree about the default colour space, and 5.0 changes it, so set it explicitly
[10].

JPEG frames followed by two H.264 passes lose light below about 4/255 and band slow
gradients near black. PNG frames (`--image-format=png`) keep it and render more slowly
[9]. Take that cost only for a film that lives in near-black gradients.

## 19. GL backends

The template sets `angle` (`Config.setChromiumOpenGlRenderer("angle")`), right for a
desktop with a GPU; it also fixes "Failed to acquire WebGL2 context" [11]. On a machine
without a GPU (CI, a cloud VM) pass `--gl=swangle`, and expect WebGL shots to be slow.
`npx remotion gpu --gl=angle` prints Chrome's GPU status for a quick look; it is not meant
to be parsed [11]. Remotion warns that `angle` has known memory leaks [11]: on long
renders with heavy WebGL, lower the concurrency rather than switching backend.

## 20. Memory, concurrency and a shared machine

- Run `npx remotion browser ensure` once before the first render; let Remotion fetch its
  own headless Chrome and do not pin a system Chrome. A stalled render usually means a
  browser mismatch [12].
- Remotion's default concurrency is half the CPU threads [13]. Choose it with `npx remotion
  benchmark`, not by guess [9].
- If the OS kills the render (SIGKILL), lower `--concurrency`, cap
  `offthreadVideoCacheSizeInBytes`, or disallow parallel encoding (lower peak memory, slower)
  [14].
- Parallel builders share one machine. On the first film that caused font timeouts and one
  still that hung for eleven minutes on a frame that renders in 1.4 s. Hence: the long
  `delayRender` limit (section 11), a per-still `--timeout` in `shots.mjs`, a unique bundle
  per process, few Python processes per builder, and no full-film renders while builders
  bench. Close Studio before the final render.

## 21. The Windows command-line limit

Windows caps a command line at 8192 characters. Remotion's generated FFmpeg command grows
with audio layers and can pass it; Remotion cannot fix this itself [15]. Keep audio to the
film's one track (`AudioTrack`); mark every video clip `muted`; if it still fails, render in
parts with `--frames` and join them with ffmpeg's concat. Pass props as a file
(`--props=./data/props.final.json`): inline JSON props are not supported on Windows [16].

The same limit hits tools that build long ffmpeg expressions: split long frame lists into
several `select` expressions (the expression parser fails on a few hundred terms), and in
Python strings escape filter commas as `"\\,"`.

**The path limit.** Windows also caps a file path at 260 characters. Remotion's headless
Chrome sits at `<project>\node_modules\.remotion\chrome-headless-shell\win64\...\chrome-headless-shell.exe`,
about 110 characters below the project folder. In a deep folder (one scaffold measured 268
characters) every render, still and animatic fails with `spawn ... ENOENT`, and the message
never mentions the length. Keep the project at a short path such as `C:\films\<slug>`;
`doctor.py` fails a path that is too long.

## 22. The speed budget

Aim for under 1.5 s a frame at full resolution, measured with `node scripts/shots.mjs <id>
--bench a:b`. The first film's sections ran at 30 to 155 ms a frame, most of them because
anything heavy was a plate; the film rendered in 2 m 13 s to 2 m 31 s and graded in under a
minute. Over budget means pre-render (section 14), not "it is only the final render": the
final render is repeated after every fix, and review renders run while builders work. The
first frames on each render thread are slow; bench a span of at least two seconds [9].

## 23. Sources

Numbers and methods marked [n] come from the Remotion technical digest
(`dev/references/remotion-technical.md`, pages read 2026-10-22). Everything else comes from
*We Built a Mind* (its build guide, decisions log and section logs) or was measured for this
file.

1. Remotion 5.0 migration guide, https://www.remotion.dev/docs/5-0-migration
2. random(), https://www.remotion.dev/docs/random
3. Flickering; CSS animations, https://www.remotion.dev/docs/flickering ,
   https://www.remotion.dev/docs/troubleshooting/css-animations
4. staticFile() and Img, https://www.remotion.dev/docs/staticfile ,
   https://www.remotion.dev/docs/img
5. Video tags comparison; OffthreadVideo, https://www.remotion.dev/docs/video-tags ,
   https://www.remotion.dev/docs/offthreadvideo
6. delayRender() and continueRender(); Debugging timeouts,
   https://www.remotion.dev/docs/delay-render , https://www.remotion.dev/docs/timeout
7. fitText(), https://www.remotion.dev/docs/layout-utils/fit-text
8. @remotion/three and ThreeCanvas, https://www.remotion.dev/docs/three ,
   https://www.remotion.dev/docs/three-canvas
9. Performance guide, https://www.remotion.dev/docs/performance
10. Encoding guide; colorSpace option, https://www.remotion.dev/docs/encoding/ ,
    https://www.remotion.dev/docs/options/color-space
11. GL backends; WebGL2 context error; gpu command, https://www.remotion.dev/docs/gl-options ,
    https://www.remotion.dev/docs/troubleshooting/webgl2-context ,
    https://www.remotion.dev/docs/cli/gpu
12. Stuck renders, https://www.remotion.dev/docs/troubleshooting/stuck-render
13. renderMedia(), https://www.remotion.dev/docs/renderer/render-media
14. SIGKILL troubleshooting, https://www.remotion.dev/docs/troubleshooting/sigkill
15. ENAMETOOLONG on Windows, https://www.remotion.dev/docs/enametoolong
16. remotion.config.ts and the CLI render command, https://www.remotion.dev/docs/config ,
    https://www.remotion.dev/docs/cli/render
