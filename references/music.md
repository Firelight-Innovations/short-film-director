# Music: analysing the track and cutting to it

The film's structure follows the track's. You cannot hear the track; the numbers can. So
analyse it once, read the numbers and the plot, put every boundary and cue on a measured
event, and check the result against the music twice: with `snap.py` before the build and
with `sync-check.py` after it. Numbers in brackets point to the sources at the end.

## Contents

1. [Analyse once](#1-analyse-once)
2. [Cutting a longer track to the film's length](#2-cutting-a-longer-track-to-the-films-length)
3. [What beats.json holds](#3-what-beatsjson-holds)
4. [Read the plot](#4-read-the-plot)
5. [Map the structure](#5-map-the-structure)
6. [Cutting on beats, bars, phrases and drops](#6-cutting-on-beats-bars-phrases-and-drops)
7. [Murch's rule of six](#7-murchs-rule-of-six)
8. [snap.py and the two-frame rule](#8-snappy-and-the-two-frame-rule)
9. [When the tracker is wrong](#9-when-the-tracker-is-wrong)
10. [Checking by ear: someone else's ears](#10-checking-by-ear-someone-elses-ears)
11. [sync-check.py: the picture against the music](#11-sync-checkpy-the-picture-against-the-music)
12. [Films without music](#12-films-without-music)
13. [Voice-over](#13-voice-over)
14. [Sources](#14-sources)

---

## 1. Analyse once

```bash
python scripts/analyze_music.py assets/audio/<track> [--fps 30] [--bpm N] [--beats-per-bar 4] [--zoom 30]
```

It writes `data/beats.json` and the plot `out/research/music.png` (`--zoom 30` also writes
one panel per 30 s, `music-000-030.png` and so on, for a closer look). With no audio
argument it reads `assets/<audio.src>` from the timeline; `--fps` defaults to the
timeline's. It prints a summary: tempo, beats, bars, any tempo warning, pumped regions,
hits, structure points, rises and drops, the loudest moment and where the music goes
silent. Read that summary first; it is the music brief for the concept panel.

Rules:

- **Never hand-edit `beats.json`.** Re-run the script (with `--bpm` or
  `--beats-per-bar` if the first run was wrong). Sections and the kit read it directly.
- **Analyse the final track.** The film is cut to the file in `assets/audio/`; a different
  master (a re-edit, a fade added) moves every event. If the track changes, re-run and
  then `python scripts/snap.py` to see what moved.
- **Do it yourself, first.** On the first film the lead ran the analysis itself and
  re-timed the whole film to it; the hand-placed cuts of the earlier cut had missed the
  real events by 0.5 to 1.5 s. Everything downstream depends on these numbers being
  right.
- **Cut a longer track first.** If the film is shorter than the song, cut the song to
  whole bars, then analyse the cut (section 2).

## 2. Cutting a longer track to the film's length

Skip this section if the film uses the whole track. If the film is shorter (a 30 s ad to
a 3 minute song), cut the track first. `AudioTrack` plays the file from frame 0, untrimmed,
with no offset and no fade; so the cut is a new file, and `data/beats.json` must describe
that file, not the song. Everything downstream is timed to it.

1. **Analyse the whole track away from the film's data.** `--out` keeps `data/beats.json`
   free for the cut:

   ```bash
   python scripts/analyze_music.py assets/audio/full.wav --out work/full-beats.json --no-plot
   ```

   Read the summary and look at the plot once (`--plot` and `--zoom` as in section 1)
   before you trust the downbeats: a wrong bar phase (section 9) puts every candidate cut
   mid-bar.

2. **List the candidate spans.** A good cut starts on a downbeat, lasts a whole number of
   bars, ends near the film's length, and holds what the film needs from the music: its
   change of section, its loudest moment, a rise to cut to. Run this from the project
   root; set `TARGET` (the film's length in seconds) and `SLUG`:

   ```python
   import json
   from pathlib import Path

   FULL = "work/full-beats.json"        # the whole track, from analyze_music.py --out work/full-beats.json
   SRC = "assets/audio/full.wav"        # the file that was analysed
   TARGET = 30.0                        # the film's length in seconds
   SLUG = "my-film"

   b = json.loads(Path(FULL).read_text(encoding="utf-8"))
   downs = b["downbeats"]
   bar = b["beat_period"] * b["beats_per_bar"]
   seams = [s["t"] for s in b["structure"]] + [r["t"] for r in b["rises"]]   # where the music changes
   end_of_music = min(b["silence_from"], b["duration"])

   def near(t, points, tol=0.25):
       return any(abs(t - p) <= tol for p in points)

   rows = []
   for a in downs:
       cands = [d for d in downs if abs(d - (a + TARGET)) <= bar]
       if not cands:
           continue
       z = min(cands, key=lambda d: abs(d - (a + TARGET)))
       if z > end_of_music:
           continue
       score, why = 0.0, []
       if near(a, seams):
           score += 3; why.append("starts on a change in the music")
       if near(z, seams):
           score += 2; why.append("ends on a change")
       if a <= b["loudest"] <= z:
           score += 2; why.append("holds the loudest moment")
       n_rise = sum(1 for r in b["rises"] if a <= r["t"] <= z)
       if n_rise:
           score += min(n_rise, 2); why.append(f"{n_rise} rise(s)")
       score -= abs((z - a) - TARGET) / bar
       rows.append((score, a, z, why))

   rows.sort(key=lambda r: -r[0])
   print(f"track {b['duration']:.1f} s, bar {bar:.3f} s, film {TARGET:.1f} s; best spans of whole bars:")
   for score, a, z, why in rows[:5]:
       n = round((z - a) / bar); dur = z - a
       print(f"  {a:7.3f} -> {z:7.3f}  ({dur:.3f} s, {n} bars)  score {score:+.1f}: {', '.join(why) or 'nothing special'}")
       print(f'    ffmpeg -y -ss {a:.3f} -t {dur:.3f} -i {SRC} -af "afade=t=in:d=0.02,afade=t=out:st={dur - bar:.3f}:d={bar:.3f}" assets/audio/{SLUG}-cut.wav')
   ```

   On a synthetic 150 s track at 120 BPM and `TARGET = 30` it printed
   `48.274 -> 78.274 (30.000 s, 15 bars) score +5.0: starts on a change in the music, holds
   the loudest moment`, with the matching `ffmpeg` line. The score ranks the spans; it does
   not judge them. The film's length is rarely a whole number of bars, so the cut is the
   nearest whole bars: set `dur` and the other times to the cut's measured length (step 4),
   not to `TARGET`. If no span holds a change in the music, run it again with `TARGET` one bar longer
   or shorter.

3. **Listen to the two or three best, or have the user do it.** You cannot hear. Cut each
   candidate with its `ffmpeg` line (use a different `SLUG` per file) and ask for a listen
   (section 10). A start that is on a downbeat on paper can still land on a vocal word or a
   tail of the last phrase.

4. **Cut the chosen span.** The `ffmpeg` line does it. The cut starts on the downbeat, so it
   needs only a 0.02 s fade-in to stop a click; the fade-out takes the last bar, so the film
   ends on a decay, not on a clipped note. Cut from a WAV: convert an mp3 or m4a first
   (`ffmpeg -i full.mp3 assets/audio/full.wav`) so the analysis and the cut read the same
   decoded samples. Then record what you did:

   ```bash
   python scripts/log-decision.py "lead: cut the track to 48.274-78.274 s (15 bars): starts on the second section, holds the loudest moment"
   python scripts/log-asset.py "assets/audio/my-film-cut.wav: user's track, an edit of assets/audio/full.wav (48.274 to 78.274 s, faded 0.02 s in and one bar out), licensed as full.wav"
   ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 assets/audio/my-film-cut.wav
   ```

   - Keep the full track in `assets/audio/`; it is what the licence is about. In
     `docs/rights.md`, write that the licence allows an edit (some do not).
   - Set `audio.src` to the cut, and `audio.duration` and `dur` to the length `ffprobe`
     printed.

5. **Analyse the cut.** `python scripts/analyze_music.py assets/audio/my-film-cut.wav`
   writes `data/beats.json` for the cut, and every later step reads that file. The tracker
   chooses the bar phase again from 30 s of audio, so check that it agrees with the cut:
   the cut starts on a downbeat, so every downbeat should sit on a whole number of bars
   from 0, to within a quarter of a beat:

   ```python
   import json
   from pathlib import Path

   b = json.loads(Path("data/beats.json").read_text(encoding="utf-8"))
   bar = b["beat_period"] * b["beats_per_bar"]
   off = [((d + bar / 2) % bar) - bar / 2 for d in b["downbeats"]]      # signed distance from the nearest whole bar
   worst = max(abs(o) for o in off)
   print(f"worst downbeat is {worst:.3f} s from a whole bar since 0 (limit {b['beat_period'] / 4:.3f} s)")
   print("OK" if worst <= b["beat_period"] / 4 else "bar phase is off the cut: see section 9")
   ```

   On the synthetic cut this printed 0.037 s against a limit of 0.125 s: OK. The tracker
   put 120.19 BPM on a 120.00 BPM track, so a small offset that grows over the film is
   normal. A bar phase that is a beat or two off is not; fix it as section 9 says before
   the concept panel reads the file.

## 3. What beats.json holds

Times are in seconds. `frames.*` has one value per video frame, so a section can index it
by frame number.

| Field | What it is | Use it for |
|---|---|---|
| `audio`, `duration`, `fps` | the file analysed, its length, the video frame rate of the curves | the timeline's `audio.duration` |
| `bpm`, `beat_period` | the beat tracker's tempo and beat length | the cutting rhythm |
| `tempo_candidates` | tempogram peaks, `{bpm, weight}`, strongest first | a second opinion on the tempo |
| `tempo_warning` | text, or null: the tracker may have halved or doubled the tempo | section 9 |
| `beats`, `beat_strength` | the tracked beats and how strong each one is (0 to 1) | cut points in montage |
| `beats_per_bar`, `bar_phase`, `bar_phase_scores` | the bar length assumed, which beat of the bar was taken as the downbeat, and the score of each candidate | section 9 |
| `downbeats` | the first beat of every bar | section boundaries, shot changes |
| `pumped_regions` | stretches where one fixed period explains the onsets better than the tracker: `from`, `to`, `period`, `first`, `contrast`, `coverage`, `tracker_drift`, `pulses` | pulse-locked motion; the tracker's error there |
| `grid` | the beats with each pumped region's fitted pulses swapped in | the best single beat list |
| `onsets` | transients, `{t, s}` with strength 0 to 1 | hits that are not on the grid |
| `hits` | the strongest onsets with a loudness jump behind them, `{t, strength, jump_db}` | slams, logo hits, flash frames |
| `structure` | novelty peaks over timbre, harmony and loudness, refined to the strongest onset within 0.6 s: `{t, raw_t, prominence, loudness_change_db}` | candidate section boundaries |
| `loudest` | the loudest moment | the climax |
| `rises`, `drops` | sudden loudness changes, `{t, db}` | entrances, a drop-out, the end of the music |
| `fade_below_-40db_from`, `silence_from` | where the music fades out and where it is silent | the end of the film's music; a held black |
| `frames.energy`, `low`, `mid`, `high`, `onset`, `perc` | per-frame curves, 0 to 1 | motion that breathes with the track |

In a section, read them through the kit, not the file: `BEATS`, `DOWNBEATS`, `ONSETS`,
`BEAT_PERIOD`, `beatIndex(t)`, `sinceBeat(t)`, `beatEnv(t, decay)`, `beatsIn(a, b)` and
`level(frame, band)` with `band` one of `energy`, `low`, `mid`, `high`, `onset`
(`references/04-architecture.md`).

A short music brief for the concept panel, printed from the file (run from the project
root):

```python
import json
from pathlib import Path

b = json.loads(Path("data/beats.json").read_text(encoding="utf-8"))
bar = b["beat_period"] * b["beats_per_bar"] if b["beat_period"] else 0
print(f"{b['duration']:.1f} s, {b['bpm']:.1f} BPM, beat {b['beat_period']} s, bar {bar:.2f} s, {len(b['downbeats'])} bars")
if b["tempo_warning"]:
    print("TEMPO WARNING:", b["tempo_warning"])
for r in b["pumped_regions"]:
    print(f"pumped {r['from']:.1f}-{r['to']:.1f} s: period {r['period']} s, {len(r['pulses'])} pulses, tracker off by up to {r['tracker_drift']} s")
print("loudest", b["loudest"], "| fades below -40 dB at", b["fade_below_-40db_from"], "| silent from", b["silence_from"])
print("rises:", [(r["t"], r["db"]) for r in b["rises"]], "drops:", [(r["t"], r["db"]) for r in b["drops"]])
print("strongest hits:", [h["t"] for h in sorted(b["hits"], key=lambda h: -h["strength"])[:8]])

# Structure points that are also near a downbeat are the best section boundaries.
downs = b["downbeats"]
print("structure point -> nearest downbeat (s apart), loudness change")
for s in sorted(b["structure"], key=lambda s: -s["prominence"]):
    d = min(downs, key=lambda x: abs(x - s["t"])) if downs else None
    gap = abs(d - s["t"]) if d is not None else float("nan")
    flag = "  <- boundary candidate" if gap <= 0.1 else ""
    print(f"  {s['t']:7.2f} -> {d if d is not None else '-':>7} ({gap:.2f}), {s['loudness_change_db']:+.1f} dB{flag}")
```

## 4. Read the plot

Open `out/research/music.png` with the Read tool. It has four rows on one time axis:

1. **Mel spectrogram.** Where the instruments enter and leave. A wall of high energy is a
   chorus or a climax; a band of nothing at the top is a quiet passage; vertical stripes
   are a regular pulse.
2. **Loudness in dB** (black), **bass under 160 Hz** (red) and **air over 2 kHz** (blue).
   Where the bass enters is usually where the film should change gear. A slow climb is a
   build; a sudden fall is a drop-out or the end.
3. **Onsets** (purple), with the tracked beats (grey), the downbeats (black), the fitted
   pulses of pumped regions (green) and the hits (red dots). Check that black lines sit
   on visible onsets; if they sit between them, the bar phase is wrong (section 9).
4. **Structure novelty** (green) and **loudness change** (orange). Peaks are candidate
   boundaries; the red dotted lines mark them on every row.

The title line carries the tempo and any tempo warning. The magenta line is the loudest
moment; the blue line is where silence begins.

## 5. Map the structure

Song structure is the film's first draft of a section map. Write it as a list of parts
with times, then turn it into sections (`references/01-intake-and-ideation.md`, section 16):

- **Intro, build, drop, break, outro.** Name each part by what it does, not by what a
  pop song would call it. A long pad intro is an establishing section; the moment the
  bass enters is the drop, whatever the genre.
- **Three levels.** A commercial editor shows song parts, bars and beats as three grids
  that change with zoom [10]. Use the same three: sections on part boundaries, shots on
  bars, motion on beats.
- **Four bars make a phrase** in most music; phrase boundaries are where to check cuts
  [11]. At 120 BPM in 4/4 a bar is 2 s and a phrase 8 s; at 63 BPM, as on the first film, a
  bar is 3.8 s and a phrase 15 s, so a 2-minute film has only about eight phrases.
- **Structure points are suggestions.** Recurrence and novelty analysis finds candidates
  [14]; check each one against the plot and the bars, and keep only those that land on a
  downbeat or a hit.
- **Marks.** Copy the landmarks you will cut to into `timeline.json` `marks` with names
  (`drop`, `loudest`, `bass-in`, `silence`), with the measured times. Sections and cues
  refer to marks by name, so a re-analysis changes one number.

## 6. Cutting on beats, bars, phrases and drops

- **Section changes on a bar's downbeat.** The cleanest transitions tend to sit on the
  first beat of a bar [11].
- **Phrase boundaries are the default section cut points**; bars are the default shot
  changes. In a montage, cut every two or four beats, not every beat [11].
- **Hits on hits.** A title, a logo or a flash that lands exactly on a drum hit reads as
  deliberate; between beats it reads as an accident [11]. Use `hits` and `onsets`, not the
  beat grid, for these: a hit is often a little off the grid, and onset detection with
  peak picking finds it [21].
- **Pickups.** When notes lead into a phrase (an anacrusis), put the picture change on the
  downbeat after the lead-in, not on the pickup [31].
- **The drop is the biggest change.** Save the film's biggest cut for the biggest event:
  the drop, the loudest moment, the cut to silence. The drop rules in the sources are
  vendor heuristics, so treat them as defaults, not laws.
- **Smash cuts at pivots only.** An abrupt cut where none is expected works at a hit, a
  drop or a reveal, as contrast; as the default cut it stops meaning anything [25].
- **A cue is readable on its event.** A cue's `from` is the frame its words are whole, so
  a word that "lands on the beat" has its entrance a few frames before the beat. The
  first film started write-ons on the cue's first frame and showed half-words on the
  beat.
- **Motion can breathe without cutting.** A section that pulses with `beatEnv` or
  `level(frame, "low")` feels locked to the music without a single cut on a beat.

## 7. Murch's rule of six

Walter Murch ranks what a cut must satisfy: emotion, story, rhythm, eye trace, the
two-dimensional plane of the screen, and three-dimensional space [9]. Emotion is weighted
at 51 percent, more than the other five together; the other weights (23, 10, 7, 5, 4) come
from secondary write-ups and were not verified, so use the order, not the numbers. When a
cut cannot satisfy all six, give up the lowest first [9].

For a film cut to music: rhythm is third. Cut on the beat when emotion and story still
hold; when the beat would cut a line before it is read, or land a reveal before the
viewer is ready, move the cut to the next measured event that serves the emotion, and log
why. Eye trace and screen geography go first: a cut that jumps the eye across the frame
is acceptable if it lands on the beat and on the feeling.

## 8. snap.py and the two-frame rule

```bash
python scripts/snap.py [--tol 2] [--min-onset 0.25] [--all]
```

For every section boundary (with the transition on it), every mark and every cue start in
`data/timeline.json`, it finds the nearest event of each kind in `data/beats.json`: beat,
downbeat, onset (at least `--min-onset` strong), hit, structure point, fitted pulse, and
loudness landmark (loudest, rise, drop, silence). Distances are signed frames, event minus
item: `+1` means the music moves one frame after the picture. An item is `ok` when some
event is within `--tol` frames (default 2), `OFF` when none is, and `silent` when it sits
after the music has ended. Only section boundaries decide the exit code: 3 if any is
`OFF`. It lists only the `OFF` cues unless you pass `--all`. Run it after every timing
change, before the animatic gate.

An `OFF` cue start is often fine: a cue's `from` is when the words are readable, and a
line that lands mid-phrase can be right for the reading. Look at each one and decide.

**Why two frames.** At 30 fps two frames are 67 ms. Beat-tracking evaluation counts an
estimated beat as correct within 70 ms of the true one (the F-measure window in
`mir_eval`) [20], so two frames is about the precision the trackers themselves are judged
at; asking for more is asking the numbers for something they cannot give. At 24 fps two
frames are 83 ms, and at 60 fps use `--tol 4`.

When a boundary is off, do one of two things:

1. Move it to a better measured event (the downbeat two frames away, the hit it was meant
   for), and log it:
   `python scripts/log-decision.py "lead: 03-press starts on downbeat 28.94 (was 28.90): snap.py"`.
2. Keep it and log the reason (a handshake needs that frame; a reading time needs the
   space). A boundary off the music without a logged reason is a mistake.

Frames, not seconds, are the truth. The kit snaps every time in the timeline to its frame
when it loads (`round(t x fps)`); a literal second typed in a component is not snapped and
can land a frame late (5.2667 s is a hair after frame 158). Compare frames, or use the
kit's times.

## 9. When the tracker is wrong

Beat trackers make a small number of characteristic mistakes. `analyze_music.py` checks
for most of them and writes `tempo_warning`; when it does, or when the plot looks wrong,
work through this list.

**Half or double tempo (octave errors).** The tracker locks onto every other beat, or onto
the eighth notes. The script warns when a tempogram peak near twice or half the tempo is
nearly as strong, when the off-beats carry about as much onset energy as the beats, when
every other beat is much weaker, or when the tempo is outside 70 to 160 BPM, where these
errors are commonest. Trackers carry priors that cause it: librosa's tracker (Ellis's
dynamic-programming method, which follows tempo changes of about 10 percent either side
of its estimate [12]) starts from an initial guess (120 BPM in the older docs) and
returns one global tempo [13]; madmom's
downbeat decoder searches 55 to 215 BPM by default, which matters for slow film music
[17]; Essentia's RhythmExtractor2013 searches 40 to 208 BPM and wants 44.1 kHz input [15].
Fix: decide which tempo the music is felt in (where would a listener clap?), then re-run
with `--bpm <that tempo>`; it skips estimation. If no one can say, cut on bars and hits,
which survive an octave error.

**Bar phase.** The downbeats are every fourth beat starting from `bar_phase`. When the
four `bar_phase_scores` are close, the phase is a guess. Check the plot: the black
(downbeat) lines should sit on the strongest low-end onsets. If the music is in three,
re-run with `--beats-per-bar 3`.

**Drift where there are no drums.** On a pad or a pumped synth the tracker can wander: on
the first film it was off by up to 0.1 s, enough to miss by two frames at the end of a
stretch. The script finds stretches where one fixed period explains the onsets
(`pumped_regions`), fits the pulses and snaps each one to a real onset peak;
`tracker_drift` says how far the tracker was off there. Inside a pumped region, cut to
`grid` (or the region's `pulses`), not to `beats`.

**No beat.** A 0 BPM result, or fewer than four beats, means there is no steady pulse
(an ambient piece, a speech, silence) [13]. Cut to `hits`, `onsets` and `structure`.

**A second opinion.** Run a second tracker and compare, and send disagreements to a
listen [18][19]. Beat This!, a 2024 tracker without the usual Bayesian post-processing,
is MIT-licensed and exports beat files that open in Sonic Visualiser [18][19]; it needs
PyTorch. Installing it is the user's call: ask first. Without a second tracker, these
checks run on what is there, and score the tracker against hand-marked beats when someone
can tap them:

```python
import json
from pathlib import Path

import numpy as np

b = json.loads(Path("data/beats.json").read_text(encoding="utf-8"))
grid = np.array(b["grid"] or b["beats"])
on = np.array([o["t"] for o in b["onsets"] if o["s"] >= 0.3])       # the clearer onsets
WIN = 0.07                                                          # mir_eval's F-measure window

def share_on(beats, events, win=WIN):
    if len(beats) == 0 or len(events) == 0:
        return 0.0
    d = np.abs(events[:, None] - beats[None, :]).min(axis=1)
    return float(np.mean(d <= win))

half = grid[::2]
double = np.sort(np.concatenate([grid, (grid[:-1] + grid[1:]) / 2]))
print(f"clear onsets on the grid: {share_on(grid, on):.0%}   on half: {share_on(half, on):.0%}   on double: {share_on(double, on):.0%}")
print("bar phase scores:", b["bar_phase_scores"], "chosen:", b["bar_phase"])
s = sorted(b["bar_phase_scores"], reverse=True)
if len(s) > 1 and s[0] - s[1] < 0.1 * s[0]:
    print("bar phase is a guess: the top two scores are within 10 percent; look at the plot or listen")

def f_measure(ref, est, win=WIN):
    """Beat F-measure: a hit is an estimated beat within win of an unused reference beat."""
    ref, est = list(ref), list(est)
    used, hits = set(), 0
    for e in est:
        best = min((i for i in range(len(ref)) if i not in used and abs(ref[i] - e) <= win),
                   key=lambda i: abs(ref[i] - e), default=None)
        if best is not None:
            used.add(best)
            hits += 1
    p, r = hits / max(len(est), 1), hits / max(len(ref), 1)
    return 2 * p * r / (p + r) if p + r else 0.0

taps = Path("work/taps.txt")                                        # one time per line, from a tap-along
if taps.exists():
    ref = [float(x.split()[0]) for x in taps.read_text(encoding="utf-8").split("\n") if x.strip()]
    lo, hi = min(ref) - WIN, max(ref) + WIN
    est = [t for t in grid if lo <= t <= hi]
    print(f"F-measure against {len(ref)} taps: grid {f_measure(ref, est):.2f}, "
          f"half {f_measure(ref, est[::2]):.2f}, double {f_measure(ref, double[(double >= lo) & (double <= hi)]):.2f}")
```

If clear onsets sit on the doubled grid much more than on the grid itself, either the tempo
is half what it should be or the music has strong off-beats (hi-hats, a shuffle): a
synthetic test track with a kick on every beat and a hat between them scored 50 percent on
the grid and 98 percent on the doubled grid at the right tempo. If the half grid scores as
well as the grid, the tempo may be double. Decide by where a listener would clap.
Against taps, an F-measure near 1.0 for the grid is a pass; a higher score for half or
double is an octave error. (The full `mir_eval` suite adds continuity scores: a low CMLt
with a high AMLt is the signature of an octave or metrical-level error [20].) To make
taps, hand-mark 20 to 30 seconds of the track [20], for example by tapping along in Sonic
Visualiser [22] and exporting the time instants.

## 10. Checking by ear: someone else's ears

No agent hears the film. Two things let a person check the analysis quickly:

1. **Sonic Visualiser** [22]: load the track, import the beats as a time-instant layer, and
   listen with clicks. Write the files it imports:

   ```python
   import json
   from pathlib import Path

   b = json.loads(Path("data/beats.json").read_text(encoding="utf-8"))
   Path("work").mkdir(exist_ok=True)
   for name, times in (("beats", b["grid"] or b["beats"]), ("downbeats", b["downbeats"]),
                       ("hits", [h["t"] for h in b["hits"]])):
       Path(f"work/{name}.txt").write_text("".join(f"{t:.3f}\t{name}\n" for t in times), encoding="utf-8")
       print(f"work/{name}.txt: {len(times)} points")
   ```

2. **A click check**: the track with a soft click on every beat, a brighter one on every
   downbeat and a high tick on every section boundary, so the user can hear in one listen
   whether the grid and the cuts sit on the music:

   ```python
   import json
   import subprocess
   from pathlib import Path

   import numpy as np
   from scipy.io import wavfile

   b = json.loads(Path("data/beats.json").read_text(encoding="utf-8"))
   tl = json.loads(Path("data/timeline.json").read_text(encoding="utf-8"))
   SR = 44100
   track = np.zeros(int((b["duration"] + 1) * SR), np.float32)

   def clicks(times, freq, amp, ms=25):
       k = int(SR * ms / 1000)
       tone = (np.sin(2 * np.pi * freq * np.arange(k) / SR) * np.exp(-np.linspace(0, 6, k)) * amp).astype(np.float32)
       for t in times:
           i = int(round(t * SR))
           if 0 <= i and i + k < len(track):
               track[i:i + k] += tone

   clicks(b["grid"] or b["beats"], 1000, 0.20)
   clicks(b["downbeats"], 1600, 0.35)
   clicks([s["from"] for s in tl["sections"]], 2600, 0.50, ms=60)
   Path("work").mkdir(exist_ok=True)
   wavfile.write("work/clicks.wav", SR, track)
   song = Path("assets") / tl["audio"]["src"]
   subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(song), "-i", "work/clicks.wav",
                   "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:normalize=0",
                   "-c:a", "libmp3lame", "-q:a", "4", "work/click-check.mp3"], check=True)
   print("work/click-check.mp3: the track with beat, downbeat and section clicks")
   ```

   Send `work/click-check.mp3` to the user with one question: "Do the clicks sit on the
   music, and do the high ticks fall where the picture should change?" Their answer goes
   in the decisions log.

The final gate is the same idea at full scale: a person watches the graded film with the
sound on, and the verdict goes in the report (`references/07-final-and-delivery.md`).

## 11. sync-check.py: the picture against the music

```bash
python scripts/sync-check.py out/pass1.mp4 --sections
```

It finds the peaks of picture change (how much the frame changes from one frame to the
next) and matches each to the nearest beat, downbeat, onset, hit or fitted pulse in
`beats.json`, as signed frames (event minus picture). For the film, or per section with
`--sections`, it prints the number of peaks, the share within `--tol` frames of an event
("on the beat"), the median distance, the correlation between picture change and the
music's onset curve, and the off-beat moves, biggest first; it writes
`out/sync/<name>.csv`. It reports and does not judge: the exit code is 0. Run it on
`pass1` during review and on the graded file at the end. A picture move within about 45 ms
of its sound reads as together (the tool's header cites ITU-R BT.1359), which is about one
and a half frames at 30 fps; that is why `--tol` defaults to 2.

How to read it:

- A section built to move with the music (a pumped type section, a montage) should have
  most of its big moves within two frames of an event. An off-beat list there is a list
  of bugs: a move started from a typed second, a cue that drifted, a plate sequence
  indexed by the wrong clock.
- A slow section (a held painting, a silent outro) will score low, and that is fine. Say
  so in the review instead of forcing moves onto beats.
- An off-beat move that is the right move (a reveal held for the viewer) stays; log it.

On the first film a section-specific version of this check (`pump_check.py`) was the only
measured sync test; this generalises it to every section.

## 12. Films without music

A film with no track (silence, ambience you will not cut to, or a voice-over only) still
needs a rhythm; it comes from the words and the picture instead:

- Set `"audio": null` in the timeline. `analyze_music.py` has nothing to measure; leave the
  empty `beats.json` the template ships, and `snap.py` has nothing to snap to.
  `check-timeline.py` only checks boundaries against beats when there are beats.
- Time each section from its reading budget first: the words' minimum times
  (`references/01-intake-and-ideation.md`, section 14) plus the transitions' windows plus a
  held beat before and after. Then round shot lengths to a chosen pulse (for example every
  shot a whole number of 0.8 s units) so the cutting has a felt rhythm.
- Name `marks` after picture events (`reveal`, `title`, `black`), so the timeline still
  speaks in landmarks.
- Silence is loud. A held black of a second or more before the last line is a strong
  device; the first film ended with 17.5 s of silence on purpose. Captions must say there
  is no sound when silence is meaningful (`references/safety-and-rights.md`).

## 13. Voice-over

The timeline has one audio track, so a voice-over and music are mixed into one file
before the film plays it:

1. **Script the VO** as `vo` cues: the spoken words, each with its window. The animatic
   shows `vo` cues as subtitles, so the board can be timed before the voice exists.
2. **Record or generate the voice.** A generated voice is generated media (disclosure
   rules, `references/safety-and-rights.md`); a voice that imitates a real person is a
   likeness question; ask the user first in both cases.
3. **Measure the recording.** Run the analysis on the VO file alone; its onsets are the word
   starts and its `silence_from`, rises and drops are the gaps. Set each `vo` cue's `from`
   to the measured start of its line, not to an estimate of speaking speed:

   ```bash
   python scripts/analyze_music.py assets/audio/vo.wav --out work/vo-beats.json --no-plot
   ```

4. **Duck and mix.** Lower the music under the voice with a sidechain compressor, place the
   voice at its start time, and write one file:

   ```bash
   ffmpeg -i assets/audio/music.wav -i assets/audio/vo.wav -filter_complex "[1:a]adelay=12000:all=1,asplit=2[vo][key];[key]apad[keyp];[0:a][keyp]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[bed];[bed][vo]amix=inputs=2:duration=first:normalize=0[mix]" -map "[mix]" -c:a pcm_s16le assets/audio/mix.wav
   ```

   `adelay=12000` starts the voice at 12.000 s; `apad` keeps the sidechain running after
   the voice ends, or the music would stop with it. Point `audio.src` at the mix, and run
   `analyze_music.py` on the **music stem** (`--out data/beats.json`) so the beats come
   from the music, not from the voice.
5. **Lead with sound when it helps.** A J cut starts the next scene's sound before its
   picture; an L cut carries sound over the cut [24]. With one continuous music track they
   apply only to the voice: a line that starts a beat before the picture changes pulls the
   viewer across the cut.
6. **Caption it.** Prerecorded speech needs captions (`references/safety-and-rights.md`),
   and every `vo` cue's text is the caption.

---

## 14. Sources

The numbers keep the numbering of the storyboard and music digest
(`dev/references/storyboard-music.md`). Confidence marks are the digest's.

9. No Film School, "6 Rules for Good Cutting According to Walter Murch" (2016; medium). https://nofilmschool.com/2016/11/6-rules-good-cutting-according-oscar-winning-editor-walter-murch
10. Apple, "Edit to the beat in Final Cut Pro (Beat Detection)". https://support.apple.com/guide/final-cut-pro/ver65b55a2b7/mac
11. Foxi Music, "How to Edit Music for Video in 2026" (vendor heuristics; low). https://www.foximusic.com/blog/?p=597
12. Daniel P. W. Ellis, "Beat Tracking by Dynamic Programming", Journal of New Music Research 36(1), 2007, doi:10.1080/09298210701653344 (the method librosa implements; medium).
13. librosa, `librosa.beat.beat_track`. https://librosa.org/doc/0.10.2/generated/librosa.beat.beat_track.html
14. librosa, `librosa.segment`. https://librosa.org/doc/dev/api/segment.html
15. Essentia, RhythmExtractor2013. https://essentia.upf.edu/reference/std_RhythmExtractor2013.html
17. madmom, downbeats module (v0.16; medium). https://madmom.readthedocs.io/en/v0.16/modules/features/downbeats.html
18. Foscarin, Schlüter and Widmer, "Beat This! Accurate Beat Tracking Without DBN Postprocessing", ISMIR 2024. https://arxiv.org/abs/2407.21658
19. CPJKU, beat_this repository. https://github.com/CPJKU/beat_this
20. mir_eval, beat module. https://mir-eval.readthedocs.io/latest/api/beat.html
21. Böck, Krebs and Schedl, "Evaluating the Online Capabilities of Onset Detection Methods", ISMIR 2012 (medium). https://archives.ismir.net/ismir2012/paper/000049.pdf
22. Sonic Visualiser reference manual (medium). https://www.sonicvisualiser.org/doc/reference/1.3/en
24. Wikipedia, "J cut". https://en.wikipedia.org/wiki/J_cut
25. Wikipedia, "Smash cut". https://en.wikipedia.org/wiki/Smash_cut
31. Songtive, "Anacrusis" (glossary; low). https://www.songtive.com/en/glossary/anacrusis

The first film's numbers (cuts 0.5 to 1.5 s off before the analysis, a tracker drift of
0.1 s on a drumless pad, half-words on the beat, 17.5 s of closing silence) come from
`dev/references/wbam-lessons.md`.
