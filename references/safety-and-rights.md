# Safety and rights

Rights and safety are part of the craft, not paperwork at the end. This file covers flash
safety, facts and quotes on screen, likeness, music, footage, image and font licences,
AI-generated media and its disclosure, captions, the Remotion licence, codec patents,
what never goes in a public repository, and what to tell the user before the film is
posted. It is not legal advice; where a question turns on law, say so to the user and
suggest they ask someone qualified. Numbers in brackets point to the sources at the end.

## Contents

1. [Flash and pattern safety](#1-flash-and-pattern-safety)
2. [flash-check.py](#2-flash-checkpy)
3. [Designing under the limit](#3-designing-under-the-limit)
4. [Facts on screen](#4-facts-on-screen)
5. [Quotes and attribution](#5-quotes-and-attribution)
6. [Real people: likeness and traced images](#6-real-people-likeness-and-traced-images)
7. [Music rights and platform claims](#7-music-rights-and-platform-claims)
8. [Footage, image and font licences](#8-footage-image-and-font-licences)
9. [AI-generated media and its disclosure](#9-ai-generated-media-and-its-disclosure)
10. [Captions and accessibility](#10-captions-and-accessibility)
11. [The Remotion licence and codec patents](#11-the-remotion-licence-and-codec-patents)
12. [Public repositories: what never goes in](#12-public-repositories-what-never-goes-in)
13. [Before posting: what to tell the user](#13-before-posting-what-to-tell-the-user)
14. [Sources](#14-sources)

---

## 1. Flash and pattern safety

Flashing images can trigger seizures in people with photosensitive epilepsy, up to about
1 in 4,000 people, and the true rate may be higher [3]. The risk cannot be removed
entirely [2]; the limits below are what broadcast and accessibility standards accept.
Every film made with this skill must pass them, measured on the graded file.

**The rule this skill enforces** (contract G7):

- **At most three general flashes and at most three red flashes in any one-second
  window** [1][2].
- **A general flash** is a pair of opposing changes in relative luminance of 10 percent or
  more of the maximum, where the darker state is below 0.80 [1][2]. For standard-range
  video, ITU expresses the same as a change of 20 cd/m² or more where the darker state is
  below 160 cd/m² [2]. How much of the picture must change for it to count differs by
  standard: ITU-R BT.1702 counts it over more than a quarter of the screen [2]; WCAG's
  area limit is much smaller (the area bullet below).
- **A red flash** is any pair of opposing transitions to or from a saturated red, where
  R / (R + G + B) is at least 0.8 and the chromaticity difference is above 0.2 [1]. ITU
  counts transitions to or from saturated red at any luminance [2]. This skill adds: no
  saturated red fields at all.
- **Long flashing sequences**: flashing that goes on for more than five seconds may be a
  risk even when every second passes [2]. Keep strobe passages short and log their length
  per section.
- **Fast cuts count.** Rapid cuts that make areas of the screen flash fall under the same
  limits [2]. Datamosh, glitch transitions, strobing titles and fast recuts all need the
  measured pass.

**Useful corollaries:**

- Flashes whose leading edges are at least 360 ms apart (50 Hz) or 334 ms apart (60 Hz)
  pass whatever their brightness or area [2]. At 30 fps that is 11 frames (367 ms): flashes
  11 or more frames apart cannot fail the per-second rule.
- The medical review puts most risk between about 15 and 20 flashes a second, over a band
  of about 3 to 60 Hz, for flashes brighter than 20 cd/m² covering 10 to 25 percent of the
  visual field or more [3]. A one-frame white flash every other frame is the worst case.
- **The area limit differs between the two standards.** ITU-R BT.1702 counts a flash only
  when it covers more than a quarter of the screen [2]. WCAG's limit is 0.006 steradians,
  which is 25 percent of any 10-degree visual field [1]; on WCAG's 1024x768 reference
  screen that field is about 341x256 pixels, so the limit is 21,824 pixels, about 3 percent
  of the screen [A1]. `flash-check.py`'s default (`--area 0.25`) is the broadcast reading,
  so **a PASS at the default is not a WCAG 2.3.1 claim**. A test film with a white box
  over 15 percent of the frame, on and off every three frames (ten changes a second),
  passes at the default and fails at `--area 0.03`. For web delivery (LinkedIn, YouTube,
  a site) also run `--area 0.03` and judge each region that fails (section 2).

**Patterns.** Regular stripes are a separate risk [2][3]. More than five light and dark
stripe pairs is a potentially harmful pattern when stationary over more than 40 percent of
the screen, or moving, flashing or reversing over more than 25 percent [2]. Treat
scanlines, halftone screens, op-art grids, moiré and interlace combs as patterns: keep
them small, low in contrast, or still, and look at them on the review sheets.

**UK broadcast and advertising.** UK ad codes (CAP rule 4.7 non-broadcast, BCAP rule 4.6
broadcast) and Ofcom's guidance apply; broadcast ads should pass a Harding Flash and
Pattern Analyser test or an equivalent, and a pass is not a guarantee: a 2012 TV ad was
found in breach [4]. `flash-check.py` is a screening tool, not a certified analyser. If
the film will be broadcast or run as a UK ad, tell the user it needs a certified test.

## 2. flash-check.py

```bash
python scripts/flash-check.py out/<slug>-graded.mp4
python scripts/flash-check.py out/pass1.mp4 --from 92.0 --to 100.6
python scripts/flash-check.py out/check/06-reckoning --fps 30
```

It reads a video or a folder of frames, counts general and red flashes per second with
the flash definitions of WCAG 2.3.1 and ITU-R BT.1702 and the **broadcast area rule by
default** (a quarter of the screen), prints the transitions, the flashes (two transitions
make one flash), the worst one-second window and the times of each transition (`+`
brighter, `-` darker), and exits 0 on PASS and 3 on FAIL. How it measures: each frame is shrunk to about 96x54 and turned into relative
luminance; each cell follows its own rise or fall, so **a fade over three frames counts
the same as a cut** (a fade is not a way around the limit); a frame registers a transition
when cells changing the same way cover a quarter of the screen (`--area`); two
transitions make a flash. It also warns on flashing that runs longer than five seconds
(`--long`) and on any saturated red field over a quarter of the screen, flashing or not.
It has no pattern test and no viewing distance: judge stripes and grids by eye on the
review sheets.

Two limits to know when you read a PASS:

- **Area.** The default is the broadcast reading. For a film that will be posted on the
  web, also run `python scripts/flash-check.py out/<slug>-graded.mp4 --area 0.03`, which
  approximates WCAG's much smaller area limit (section 1). A FAIL there means a small
  bright region changes more than three times in a second. Slow it, dim it or shrink it;
  keep it only if it is plainly not a flash of the picture (a thin line of light), and log
  why.
- **Red.** The tool uses the older red test: a state is saturated red when
  R / (R + G + B) is at least 0.8, and a red transition is a change in (R - G - B) x 320
  above 20, counted as a pair like any flash. WCAG 2.2's newer form measures a CIE 1976
  u'v' chromaticity difference above 0.2 [1]. This skill bans saturated red fields, so the
  choice of red test seldom decides anything; a film that flashes red needs a certified
  test (section 1).

When to run it:

- on `out/pass1.mp4` after integration (`references/05-build.md`);
- on any section or window you changed, with `--from` and `--to`;
- after rebuilding a chain that recuts the film's frames (`python scripts/chain.py run <name>`
  runs the chain's own check);
- **on the graded mp4, always, as the last measurement.** The grade's contrast lift can
  push a change that measured just under the threshold over it.

Record the result (flash count, worst second, red count) in the report. The first film's
own checker, which counted flashes differently from this tool, reported 29 luminance
transitions, 8 flashes and a worst second of 2 against a limit of 3, and no saturated red.
This tool, run later on the same graded file, prints 31 luminance transitions = 15.5
flashes, a worst second of 5 transitions = 2.5 flashes, no saturated red, PASS. Compare a
new film's numbers with the second set, not the first.

## 3. Designing under the limit

Treat the limit as a design input, not a test at the end. The first film's overload
section was designed from the measured numbers and its worst second measured 1 to 2:

- **Level the brightness of what you cut between.** Fast cutting between pictures of
  similar brightness is fine; it is the light-dark alternation that flashes. The first
  film levelled each recut plate's mean luminance into one band (0.10 to 0.42 in linear
  light) before cutting.
- **Tear a violent cut over several frames.** Deal it in horizontal bands over up to five
  frames so no single frame changes more than a small share of the screen (0.16 on the
  first film).
- **Divide instead of cutting faster.** A mosaic that splits from 4x4 to 32x32 cells reads
  as acceleration without full-frame alternation.
- **No white flash frames on the beat** unless they are 11 or more frames apart.
- **Negative snaps and inversions** are full-frame changes; one is fine, a run is not.
- **Red is the accent, never the field.** A saturated red title on black is a red flash
  every time it cuts in and out.
- **A photosensitivity notice** at the start (a card or a line in the post) is worth
  considering when a film strobes at all; the sources do not require it, but they agree the
  risk is never zero [2].

## 4. Facts on screen

Every figure on screen is exact, sourced, current and not misleading. The method (two
independent checks, the facts table, verdicts, re-verify dates) is in
`references/02-references.md`, sections 11 and 12. The rules that bind the picture:

- **Quote figures exactly as published**: unit, sample, date range, place [35].
- **Show the source.** A `data` cue from a public source draws its `source` on screen,
  small but legible (32 px or more at 1080). The exception is the client's own claim
  (below), whose `source` begins `Client:` and is not drawn.
- **Not materially misleading** [35]. A true figure in the wrong frame fails: "everything"
  where the series measures household net worth; "a record" where the series starts in
  1989 and the record is since 1989.
- **Charts must read as the fact, at phone size.** The first film's one broken item was a
  grid of 18 lit cells framed in a row of 20, beside "fewer than 1 in 5"; on a phone it
  read as a meter nine-tenths full. Make empty cells visible tiles, not hairlines.
- **Motion must not invent data.** A counter that counts up passes through figures nobody
  published; a bar comparing two figures implies a ratio their sources may not make. Lock
  the correct figure on its first frame; spin a short reel between two published figures
  if you must; never chart two different measures against each other.
- **Decorative readouts assert nothing**, or they measure what is really under them.
- **Figures move.** Set each row's re-verify-by date, and re-check on the posting day.
- **The client's own claims** (roast date, origin, founding year, opening date, price, a
  feature list) have no public primary source, because the client is the source. Ask for
  the list at intake (`docs/brief.md`, "Claims and who stands behind them"). A claim is
  checked against the client's written confirmation: who confirmed it, in what form, on
  what date. That record is the primary record for a first-party claim
  (`references/02-references.md`, section 12). Such a cue is a `data` cue with
  `source: "Client: <name>, <date of confirmation>"`; no source line is drawn, because the
  film is the client speaking. The words and numbers still equal the confirmed wording.
- **Advertising claims are regulated, and are the user's call.** A launch or product film
  is an advertisement, and an advertiser must have evidence for objective claims before
  running one: in the US the FTC requires that claims be truthful, not misleading and
  substantiated, and counts what an ad implies as well as what it says [A2]; in the UK the
  CAP Code (rule 3.7) requires documentary evidence for claims consumers will take as
  objective [A3]. Claims such as "organic", "fair trade", "made in", health or
  environmental benefits, comparisons and superlatives ("best") can fall under those
  rules, and some terms are certified or defined by law. Pure opinion ("the best hairspray
  in the world") is generally not pursued as a factual claim, but any objective part of it
  needs support [A2]. Do not decide these for the user: list every such claim in the
  report, say that the user must hold the evidence for it, and cut a claim the user cannot
  support. A disclaimer rarely cures a claim that misleads; narrow the claim instead [A2].

## 5. Quotes and attribution

- **Verbatim, from a primary record**: the speaker's own recording, transcript or
  publication. A quote is verified only against that (`fact-check.js`). Nothing inserted,
  nothing changed: the first film's script had added "all" and turned "eliminate" into
  "erase".
- **Attribution names who said it and where**: the person, the outlet or occasion, the
  date. The `attribution` field is drawn on screen; the `source` field says where it was
  verified.
- **A paraphrase is not in quotation marks.** Reported speech ("X said AI could ...") must
  still be accurate to the record.
- **Short.** A short quotation for comment or criticism sits within the purposes fair use
  names, but fair use is decided case by case on four factors (purpose and character,
  nature of the work, amount, effect on the market), there is no safe word count, and a
  commercial use weighs against it [26][27]. **Fair use is US law.** Elsewhere the tests
  differ: UK fair dealing for quotation asks for a fair, no more than required use with a
  sufficient acknowledgement [A4], and the EU quotation exception requires that the work
  was already lawfully public, that the source be named, and that the use stay within what
  its purpose needs, with Member States implementing it differently [A5]. Ask where the
  film will be published. A brand film quoting a public figure is a question for the
  user to decide knowingly, not a default; record the decision and its date in the rights
  register.
- **Context.** A quote used to say something its speaker did not mean fails the facts test
  even when every word is right.

## 6. Real people: likeness and traced images

- **Do not trace, redraw or rotoscope a photograph or footage of a real person for a
  commercial film.** In *Warhol v. Goldsmith* (2023) a photograph-derived artwork licensed
  for the same purpose as the photograph weighed against fair use; new expression alone
  was not decisive, and commerciality counted against it [27]. A charcoal drawing traced
  from a broadcast interview is likely to be treated as that kind of derivative. The first film shipped with one
  open; decide it at intake.
- **A licence for the picture does not clear the person.** Commons files can carry
  personality and privacy rights beyond their copyright licence [6]; stock licences bar
  unflattering use of identifiable people and implied endorsement [15][16][17]; NASA needs
  an identifiable astronaut's permission for commercial use [7].
- **Publicity and voice rights vary by place.** US states have their own statutes, and
  some protect a voice as well as a face (the research found these only through summaries,
  so treat any real person's face or voice as a clearance question).
- **Generated faces** that look real are synthetic media of people who may not exist;
  disclose them (section 9). A generated face made to look like a real person is both a
  likeness and a disclosure question.
- **The user's own likeness, or people who signed a release**, are fine; record the release
  in the rights register.
- **Brands in the picture.** Visible logos and products in footage are a clearance
  question; Pixabay bars commercial use with recognisable trademarks [16]. Keep faces and
  logos out of brand footage, or blur or replace them.

## 7. Music rights and platform claims

- **The track is the biggest rights question in most films.** Ask at intake who holds the
  rights and what the user's licence covers, and record it in the register. A recording
  in picture usually needs clearance of both the composition (sync) and the recording
  (master); the research found this only in summaries, so tell the user to confirm with
  the rights holder.
- **Content ID can match anything.** YouTube scans uploads against reference files from
  eligible rights holders; on a match the holder can block the video, monetise it, or
  track it, and the options can vary by country [20]. A track used outside what its licence
  covers can be claimed on any platform; keep each track's licence certificate with the
  register [20][19].
- **Library licences fit only the use they cover.** YouTube Audio Library tracks are cleared
  for YouTube; the page does not cover other platforms or paid ads [19]. Epidemic Sound's
  business plan has revenue limits and excludes out-of-home, livestream and radio [24];
  Artlist's personal licence does not cover client and brand work [25]. Match the plan to
  the film's real uses.
- **Creative Commons music.** BY needs credit in the video and its description; NC blocks
  commercial use (a company's film is commercial) without written permission; ND needs
  permission because syncing to picture is a derivative; SA forces the film under the same
  licence [21][22]. Some CC artists still use Content ID [21].
- **A track used "for reference"** (the user loves it but has no licence) can be built to,
  but the film should not be posted with it. Say so at intake and again at delivery, and
  offer to re-cut to a licensed track: the analysis and the timeline make that a re-time,
  not a rebuild.
- **Credit the music** on the end card and in captions (section 10).

## 8. Footage, image and font licences

The licence table is in `references/02-references.md`, section 4. The points that most
often go wrong:

- **Public domain is not a clearance.** "No known restrictions" (Library of Congress) or an
  uploader's claim (Internet Archive) is not a guarantee; check the copyright term, the
  people and the trademarks yourself [8][9].
- **Each Commons file has its own licence** on its description page; record the author,
  licence, link and the exact credit string, and say if you changed it [6].
- **Prelinger clips** are reusable on their stated Creative Commons licence; the
  descriptions are copyrighted, and other commercial licensing goes through Getty [10].
- **NASA**: never the insignia or logotype, no implied endorsement, and the insignia may not
  appear with AI-generated imagery [7].
- **CC BY credit** names the creator, any copyright notice, the licence with a link, a
  disclaimer notice, a link to the material, and whether it was changed; it may not imply
  endorsement [23].
- **Stock is not a reel.** The film must be an edited work, not a compilation of stock
  [16][17].
- **Fonts.** OFL fonts may be used in video titling and logos without permission or credit;
  the conditions apply when the font files themselves are redistributed [18]. Log each
  family in the register.

Every file that enters `assets/` or `refs/img/` gets a line from `log-asset.py`; the end
credits and the report are built from those lines.

## 9. AI-generated media and its disclosure

Ask at intake whether generated media may be used. If it is, every generated image, clip,
voice or track gets a line in the register, and the film's disclosure follows the strictest
platform it will be posted on:

| Where | What must be disclosed | How |
|---|---|---|
| EU (AI Act, Article 50, applies from 2 August 2026) | deployers who generate or alter image, audio or video that resembles real people, objects, places or events and could falsely appear authentic must disclose it; for evidently artistic, creative, satirical or fictional work, a disclosure that such content exists, in a way that does not hamper the work; providers must mark output in machine-readable form [29] | an AI-use line on the end card; keep any provenance data the generator embeds |
| YouTube | realistic altered or synthetic content: a real person appearing to say or do what they did not, altered footage of real events or places, a lifelike scene that never happened, AI music as the main focus; animation, fantasy, effects and AI help with scripts or titles are exempt [30] | set "AI use" at upload; YouTube may auto-label content carrying C2PA metadata [30] |
| Meta (Facebook, Instagram) | the "AI info" label comes from industry signals or self-disclosure; a more prominent label where content could materially mislead [31]. Whether self-disclosure is mandatory reads differently across Meta's 2024 pages | disclose realistic AI video and audio at upload |
| TikTok | realistic AI images, audio or video must be labelled; a built-in AI-generated label, or a sticker or caption [32] (2023 announcement; check the current rules) | the AI-generated label |
| LinkedIn | labels in-feed AI visuals from C2PA provenance data in the file (press report only; low confidence) [34] | keep Content Credentials intact on export |

Content Credentials (C2PA) are a signed manifest of an asset's origin, edits and AI
involvement; they show origin and integrity, not truth, and re-encoding can strip them [33].
The grade and preview passes re-encode the film, so a generator's credentials will not
survive into the mp4 unless they are added back after the last encode. Tell the user this;
the on-screen and in-post disclosure is what carries the duty.

The first film said "generated" on screen over every generated face. That is the default:
when a generated picture could pass for a record of something real, say so in the picture.

## 10. Captions and accessibility

- **Captions are WCAG Level A for prerecorded video with sound.** They carry speech, name
  speakers, describe meaningful sound, and identify non-vocal music by title and composer
  [5]. A music-only film still gets a caption that names the track.
- **On-screen words are already in the picture**; the caption file carries what the picture
  does not: the music, the voice, meaningful silence.
- **Design for sound off** anyway: every text shot works muted
  (`references/01-intake-and-ideation.md`).

A caption file from the timeline, with the music named and every `vo` cue as a line
(run from the project root; fill in the track's title and composer):

```python
import json
from pathlib import Path

MUSIC = "<track title> by <composer or artist>"
tl = json.loads(Path("data/timeline.json").read_text(encoding="utf-8"))

def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

events = []
if tl.get("audio"):
    end = min(tl["audio"].get("duration") or tl["dur"], 4.0)
    events.append((0.0, end, f"[Music: {MUSIC}]"))
for c in sorted(tl["cues"], key=lambda c: c["from"]):
    if c["role"] == "vo":
        events.append((c["from"], c["to"], c["text"]))
if tl.get("audio") and (tl["audio"].get("duration") or tl["dur"]) < tl["dur"] - 1:
    events.append((tl["audio"]["duration"], min(tl["audio"]["duration"] + 3, tl["dur"]), "[Silence]"))

out = Path("out") / f"{tl['slug']}.srt"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n" for i, (a, b, text) in enumerate(events, 1)),
               encoding="utf-8")
print(f"{out}: {len(events)} captions")
```

Upload the `.srt` with the film where the platform takes one, and put the track credit in
the post text as well.

## 11. The Remotion licence and codec patents

- **Licence.** Free for individuals, non-profits, evaluators, and organisations of up to
  three people; count everyone in the collaborating group who writes, operates or
  co-develops the project, including freelancers and a client that operates it; a client
  that only receives the mp4 does not count; four or more need a Company License [R1][R2].
  The check happens at intake (`references/01-intake-and-ideation.md`, section 4) and its
  answer goes in the brief and the register.
- **Output.** Neither the LICENSE nor the FAQ says who owns rendered output; before a
  commercial release, the user may want Remotion's answer in writing [R1][R2].
- **Codec patents.** Remotion's FAQ makes patent licensing for H.264/AVC, HEVC and AAC the
  user's responsibility [R2]. The film is H.264 with AAC audio; say so in the report's
  rights section.
- **Version.** The pin is in the brief; Remotion 5.0 changes the licence terms slightly
  (telemetry for some uses) [R1][R2].

## 12. Public repositories: what never goes in

Assume the film's repository may become public, and the skill's repository is public.
Never commit:

- **keys, tokens and credentials**: `.env` files, `keys.json` of any tool, API keys pasted
  into scripts, cookies;
- **`work/` and `out/`**: sources, intermediates and renders (the template's `.gitignore`
  already lists `node_modules/`, `out/`, `work/` and `.remotion/`);
- **media whose licence does not allow redistribution**: the music (almost always), stock
  files whose licence bars redistribution as files, link-only references, footage under
  any licence you have not read;
- **traced or derived images of real people** and generated likenesses;
- **personal data**: email addresses, phone numbers, names of private people, anything the
  user gave you in confidence;
- **font files without their licence**: OFL fonts may be redistributed with the licence
  text beside them [18]; otherwise leave them out and let `fetch-fonts.mjs` fetch them.

Before the first push, list what would be committed and look for trouble (run from the
project root):

```python
import re
import subprocess
from pathlib import Path

files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                       capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
files = [f for f in files if f.strip()]
MEDIA = re.compile(r"\.(mp3|wav|aac|m4a|flac|ogg|mp4|mov|mkv|webm|avi)$", re.I)
SECRET = re.compile(r"(api[_-]?key|secret|token|passw(or)?d)\s*[:=]\s*['\"][^'\"]{8,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
problems = 0
for f in files:
    p = Path(f)
    if f.startswith(("work/", "out/")) or p.name in ("keys.json", ".env"):
        print("NEVER COMMIT", f); problems += 1
    elif MEDIA.search(f):
        print("MEDIA: check its licence allows redistribution:", f); problems += 1
    elif p.suffix in (".ts", ".tsx", ".js", ".mjs", ".py", ".json", ".md", ".txt") and p.exists() and p.stat().st_size < 2_000_000:
        text = p.read_text(encoding="utf-8", errors="replace")
        if SECRET.search(text):
            print("POSSIBLE SECRET in", f); problems += 1
        for m in set(EMAIL.findall(text)):
            if not m.endswith(("example.com", "remotion.dev")):
                print("EMAIL ADDRESS in", f, ":", m); problems += 1
print(f"{len(files)} files would be committed; {problems} to look at")
```

Each line it prints is a question, not a verdict: a track the user owns outright may be
committed to a private repo; an email in a credit may be wanted. Resolve each one before
pushing anywhere public.

## 13. Before posting: what to tell the user

The report (`templates/report.md`) carries this list with each item's state. Say each one
plainly, even when the answer is "nothing to do":

1. **Music**: whose it is, what the licence covers, and whether a claim or block is likely
   on each platform.
2. **People**: every real person who appears, is drawn or is quoted, and on what basis.
3. **Facts**: every figure and quote, its verdict, and which rows must be re-verified on the
   posting day. For a launch or product film, also every client claim and advertising claim,
   who stands behind it, and that the user must hold the evidence.
4. **Generated media**: what is generated, what the film and the post must disclose on
   each platform, and that provenance data does not survive the re-encode.
5. **Flash safety**: the measured result on the graded file (the default broadcast area,
   and `--area 0.03` for web delivery), and whether a certified test or a notice is
   advisable (broadcast, UK ads, strobe passages).
6. **Footage, images and fonts**: the credits the licences require, ready for the end card
   and the post.
7. **Captions**: the caption file, and the track credit for the post text.
8. **Remotion licence and codec patents**: the headcount answer, and that H.264 and AAC
   patent licensing is the user's responsibility.
9. **The human sound gate**: no agent has heard the film; someone must watch the graded file
   with the sound on before it is posted, and the verdict goes in the report.

---

## 14. Sources

Plain numbers keep the numbering of the rights, safety and sourcing digest
(`dev/references/rights-safety-sourcing.md`); `R` numbers are from the Remotion digest.
Confidence marks are the digests'. Research was done on 2026-10-22; re-read the primary
pages before a public release.

1. W3C WAI, "Understanding WCAG 2.2, Success Criterion 2.3.1 Three Flashes or Below Threshold". https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
2. ITU-R BT.1702-3, "Guidance for the reduction of photosensitive epileptic seizures caused by television" (11/2023). https://www.itu.int/rec/R-REC-BT.1702-3-202311-I/en
3. Fisher RS et al., "Visually sensitive seizures: An updated review by the Epilepsy Foundation", Epilepsia 63(4):739-768, 2022, doi:10.1111/epi.17175.
4. Advertising Standards Authority, "Flashing images in advertising" (medium-high). https://www.asa.org.uk/news/flashing-images-in-advertising.html
5. W3C WAI, "Understanding WCAG 2.2, Success Criterion 1.2.2 Captions (Prerecorded)". https://www.w3.org/WAI/WCAG22/Understanding/captions-prerecorded.html
6. Wikimedia Commons, "Reusing content outside Wikimedia". https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia
7. NASA Brand Center, "Images and Media". https://www.nasa.gov/nasa-brand-center/images-and-media/
8. Library of Congress, "Prints & Photographs: Rights and Restrictions". https://guides.loc.gov/p-and-p-rights-and-restrictions/risk-assessment
9. Internet Archive Help Center, "Rights". https://help.archive.org/help/rights/
10. Internet Archive Help Center, "Prelinger Archive". https://help.archive.org/help/prelinger-archive/
15. Pexels, licence. https://www.pexels.com/license/
16. Pixabay, content licence summary. https://pixabay.com/service/license-summary/
17. Unsplash, licence. https://unsplash.com/license
18. SIL, Open Font License FAQ. https://openfontlicense.org/ofl-faq/
19. YouTube Help, "Use music and sound effects from the Audio Library". https://support.google.com/youtube/answer/3376882
20. YouTube Help, "How Content ID works" (medium-high). https://support.google.com/youtube/answer/2797370
21. Free Music Archive, "FAQ For Videos & Films". https://freemusicarchive.org/FAQ_For_Videos/
22. Creative Commons wiki, "NonCommercial interpretation". https://wiki.creativecommons.org/wiki/NonCommercial_interpretation
23. Creative Commons, CC BY 4.0 deed. https://creativecommons.org/licenses/by/4.0/
24. Epidemic Sound, business plan (medium-high). https://www.epidemicsound.com/our-plans/business-plan/
25. Artlist Help Center, licence articles (medium-low). https://help.artlist.io/hc/en-us/articles/29490991524253
26. U.S. Copyright Office, "Fair Use". https://www.copyright.gov/fair-use/
27. U.S. Copyright Office, summary of *Andy Warhol Foundation v. Goldsmith*, 143 S. Ct. 1258 (2023). https://www.copyright.gov/fair-use/summaries/Andy-Warhol-Found-for-the-Visual-Arts-Inc-v-Goldsmith-143-S-Ct-1258-2023.pdf
29. Regulation (EU) 2024/1689 (AI Act), Article 50, third-party text (medium-high). https://artificialintelligenceact.eu/article/50/
30. YouTube Help, "Disclosing use of altered or synthetic content". https://support.google.com/youtube/answer/14328491
31. Meta, "Our approach to labeling AI-generated content and manipulated media" (April 2024; medium). https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/
32. TikTok Newsroom, "New labels for disclosing AI-generated content" (2023; medium-low). https://newsroom.tiktok.com/new-labels-for-disclosing-ai-generated-content?lang=en
33. C2PA, Content Credentials explainer (specification 2.2). https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html
34. MediaPost, "LinkedIn Begins Labeling AI-Generated Content" (press report; low). https://www.mediapost.com/publications/article/396225/linkedin-begins-labeling-ai-generated-content.html
35. Office for Statistics Regulation, Code of Practice for Statistics, Edition 3.0 (medium). https://osr.statisticsauthority.gov.uk/publications/the-code-of-practice-for-statistics/pages/2/
Added after review (not in the digest; read on 2026-10-23):

- [A1] W3C WAI, "Technique G176: Keeping the flashing area small enough" (the 10-degree field, 341x256 pixels, 21,824 pixels at 1024x768). https://www.w3.org/WAI/WCAG22/Techniques/general/G176.html
- [A2] FTC, "Advertising and Marketing Basics" and "Advertising FAQ's: A Guide for Small Business" (truthful, not misleading, substantiated; implied claims; puffery). https://www.ftc.gov/business-guidance/advertising-marketing/advertising-marketing-basics and https://www.ftc.gov/business-guidance/resources/advertising-faqs-guide-small-business
- [A3] ASA and CAP, "CAP Code, section 03 Misleading advertising" (rule 3.7, substantiation). https://www.asa.org.uk/type/non_broadcast/code_section/03.html
- [A4] GOV.UK, "Exceptions to copyright" (fair dealing for criticism, review and quotation; sufficient acknowledgement). https://www.gov.uk/guidance/exceptions-to-copyright
- [A5] Directive 2001/29/EC (InfoSoc), Article 5(3)(d), quotation for criticism or review (read through secondary summaries; confirm in the official text). https://eur-lex.europa.eu/eli/dir/2001/29/oj

- [R1] Remotion, LICENSE.md. https://github.com/remotion-dev/remotion/blob/main/LICENSE.md
- [R2] Remotion, License FAQ. https://www.remotion.dev/docs/license/faq and https://www.remotion.dev/docs/license-pricing-compliance/faq

The first film's figures (the measured flash counts, the levelled plates, the misread grid,
the reworded quote, the open likeness question) come from `dev/references/wbam-lessons.md`.
