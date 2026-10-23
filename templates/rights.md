# Rights register

Everything in the film that someone holds rights in, and what lets us use it
(`<skill>/references/safety-and-rights.md`). Started at intake; every agent that brings
media in adds to it; checked at the final gate and copied into the report's Rights table.
Replace each `<prompt>`; delete each example row once its table has a real one.

**Status** is one of:

- `open`: not decided yet; it does not go out until it is;
- `licensed`: a licence covers this use (CC0, CC BY with its credit, a paid plan that covers
  the platforms);
- `cleared`: permission or a release is in hand, or the public-domain status was checked;
- `own work`: made in code by this project, or by the user, who holds the rights;
- `not used`: dropped from the film (declined or replaced); keep the row so nobody adds it
  back.

## Music

| Item | Owner | Licence | Use | Status |
|---|---|---|---|---|
| <track title, artist, file> | <who holds the composition and the recording> | <the licence the user holds, or "none"> | <platforms and uses it covers> | <status> |
| *"<title>", <artist>, assets/audio/track.mp3* | *<label and publisher>* | *none: used for reference* | *not cleared for posting anywhere* | *open* |
| *assets/audio/track-cut.wav: an excerpt of the track above, faded at both ends (`references/music.md`, section 2)* | *as above* | *the licence must allow an edit; asked <date>* | *this film only* | *open* |

## People

Anyone who appears, is drawn, is heard or is quoted. Verifying a quote checks the words
(`docs/research/facts.md`); it does not clear the right to use them. A quote stays `open`
until the user has decided knowingly, and the row records that decision and its date.

| Item | How they appear | Owner | Licence or basis | Use | Status |
|---|---|---|---|---|---|
| <name or description> | <photographed, drawn, traced, voice, quoted> | <the person, or their estate> | <release, verified public quote, none> | <where, cue ids> | <status> |
| *a public figure* | *quoted (quote-1)* | *the speaker* | *verified quote; short quotation for comment (user's decision, <date>)* | *on screen, 4 s, attributed* | *open* |

## Generated media

| Item | Made with | Owner | Licence | Use and disclosure | Status |
|---|---|---|---|---|---|
| <file or plate> | <model or tool> | <who holds the output under the tool's terms> | <the tool's terms> | <where; does it resemble real people, places or events; how it is disclosed> | <status> |
| *assets/footage/01/face.mp4* | *<generator>* | *the user, per the tool's terms* | *<terms, with link>* | *01, a realistic face of no real person; "generated" on screen, YouTube "AI use", end card line* | *licensed* |

## Footage

| Item | Owner | Licence | Use and credit | Status |
|---|---|---|---|---|
| <file, and the page that states its licence> | <maker or archive> | <licence> | <where; the exact credit, or "none required"> | <status> |
| *assets/footage/02/office.mp4, https://archive.org/details/<id>* | *<studio>, via the Prelinger Archives* | *CC0* | *02, as charcoal plates only; credit given anyway* | *licensed* |

## Images

| Item | Owner | Licence | Use and credit | Status |
|---|---|---|---|---|
| <file, and the page that states its licence> | <maker or museum> | <licence> | <where; the exact credit, or "none required"> | <status> |
| *refs/img/02-ink-03.jpg, https://commons.wikimedia.org/wiki/File:<name>* | *<author>* | *CC-BY-4.0* | *reference board only; "<author>, CC BY 4.0, cropped"* | *licensed* |

## Fonts

| Item | Owner | Licence | Use | Status |
|---|---|---|---|---|
| <family> | <foundry or designer> | <licence> | <titles, logo, which sections> | <status> |
| *Cormorant Garamond, via scripts/fetch-fonts.mjs* | *<designer>* | *OFL-1.1* | *on-screen titles* | *licensed* |

## Software licences

| Item | Owner | Licence | Use | Status |
|---|---|---|---|---|
| Remotion 4.0.410 | Remotion | Remotion License: free for individuals, non-profits, and a for-profit company whose total headcount plus any client or studio that runs or co-develops the project is 3 or fewer; a Company License at 4 or more combined | renders the film | <headcount counted (whole companies), date asked> |
| H.264 and AAC in the delivered mp4 | patent pools | patent licensing is the user's responsibility (Remotion FAQ) | the delivered file | <told the user on date> |
| <other tool> | <owner> | <licence> | <use> | <status> |

## Assets

One line per file brought into `assets/` or `refs/img/`, appended by
`python scripts/log-asset.py "<file>: source, URL, licence, how processed"`. Keep this
section last.

