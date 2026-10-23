# Brief

Filled at intake from the user's answers (`<skill>/references/01-intake-and-ideation.md`).
Mark every value you chose yourself with "(default)". Replace each `<prompt>`; delete each
example line once the field is filled.

## The film

- **Title:** <working title>
  *Example: We Built a Mind*
- **The idea:** <two or three sentences, in the user's words where possible>
  *Example: An essay about where AI is taking us: the promise, the peril, and who is responsible.*
- **Source material:** <files the user gave, with paths>
  *Example: docs/source/essay.md, assets/audio/track.mp3*
- **Length:** <seconds>
  *Example: 120 s*
- **Size and rate:** <w x h at fps>; letterbox <fraction>; safe areas <title> / <action>;
  platform UI zone <x and y ranges in px for a vertical feed, or "none">
  *Example: 1920x1080 at 30 fps; letterbox 0.06 (default); safe 0.9 / 0.95 (default); UI zone none*
  *Example, vertical: 1080x1920 at 30 fps; letterbox 0; safe 0.9 / 0.95 (default); UI zone x 65
  to 1015, y 269 to 1248 (default: Meta's Reels figure for ads; check on the posting day)*
- **Platforms:** <where it will be posted, first one first>
  *Example: LinkedIn, then YouTube*
- **Audience:** <who will watch, and what they already know>
  *Example: professionals who use AI at work and skim posts about it*
- **The feeling at the end:** <one line>
  *Example: unsettled but not hopeless; responsible*
- **Language of the words on screen:** <language>
  *Example: English (US spelling)*

## Sound

- **Track:** <path under assets/audio/>, <title>, <artist>
  *Example: assets/audio/track.mp3, "<title>", <artist>*
- **Rights:** <who holds them; what the user's licence covers; or "not cleared">
  *Example: not cleared; the user has no sync licence (told them at intake)*
- **Voice-over:** <none, recorded, or generated; who speaks>
  *Example: none (default: music only, no SFX)*
- **Measured:** <tempo, bar length, loudest moment, where silence begins> (after `analyze_music.py`)
  *Example: 63.0 BPM, bar 3.8 s, loudest 97.65 s, silent from 102.05 s*

## How we work

- **Autonomy:** <checkpoints or one shot>
  *Example: checkpoints at the concept and the animatic (default)*
- **Budget:** <share of the usage window>; **model rules:** <any the user set>
  *Example: up to most of one five-hour window; Sonnet for reviewers*
- **Posting date:** <date, or "none">
  *Example: 2026-11-03*
- **Deliverables:** <graded mp4, phone preview, captions, vertical cut, thumbnail, report>
  *Example: graded mp4, preview under 28 MiB, .srt captions, report*

## Rights stance

- **Generated media:** <allowed or not>; disclosure needed on <platforms>
  *Example: not allowed; code-drawn and public-domain only (default)*
- **Real people:** <who may appear, be drawn or be quoted, and on what basis>
  *Example: quotes from two public figures, verified; no likenesses*
- **Footage and images:** <code-drawn only, PD and CC0, stock, the user's own>
  *Example: PD and CC0 from Commons and the Prelinger Archives*
- **Brand marks:** <whose, which files, where they may appear>
  *Example: the user's own logo, assets/brand/mark.svg, end card only*
- **Claims and who stands behind them:** <claims about a product, service or client (what it
  does, how well, for how much); who confirms each, in writing; or "none">
  *Example: price, launch date and "40% faster setup"; Example Co.'s marketing lead confirms
  each by email before the script; no superlatives (default)*
- **Facts:** <will the film show figures, dates or quotes; how many>
  *Example: about six figures and two quotes: two checks each before the storyboard gate*

## Remotion

- **Version pin:** <from package.json>
  *Example: remotion and @remotion/* 4.0.410, react 19.0.0, typescript 5.6.3, zod 3.22.3, three 0.170.0*
- **Licence:** <people in the collaborating group, freelancers and an operating client included>; <free or company licence needed>; asked on <date>
  *Example: 1 person; free licence applies; asked 2026-10-22*
- **Remotion agent skills:** <offered; installed or declined>
  *Example: offered; declined*

## Keep and kill

- **Keep:** <what the user loves and wants in the film>
  *Example: one line held on black at the end*
- **Kill:** <what they never want>
  *Example: robots with red eyes; stock footage of handshakes*

## Defaults chosen

- <the default, and why>
  *Example: 30 fps (default): the platform's native rate; the track is not tied to 24*

## Cost estimate

- <the size row from the estimate table, and when you told the user>
  *Example: long film (2 min, 8 sections): about 4 to 6 h and most of a usage window; told 2026-10-22*
