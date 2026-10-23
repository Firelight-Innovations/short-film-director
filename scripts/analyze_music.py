"""Measure the track once, so every cut can sit on a real musical event.

    python scripts/analyze_music.py [<audio>] [--fps 30] [--out data/beats.json]
                                    [--bpm N] [--beats-per-bar 4] [--zoom 0] [--no-plot]

<audio> defaults to assets/<audio.src> from data/timeline.json, and --fps to the
timeline's fps (30 without a timeline). Writes data/beats.json (never hand-edit
it; re-run this instead) and a plot, out/research/music.png. Run from the film
project root. Deterministic: same file in, same numbers out.

What it measures (field names are the ones src/kit/music.ts and snap.py read):
  bpm, beat_period, beats, beat_strength     librosa's dynamic-programming beat tracker
  tempo_candidates, tempo_warning            tempogram peaks, and a warning when the
                                             tracker may have halved or doubled the tempo
  downbeats, bar_phase, bar_phase_scores     which beat of the bar carries the most
                                             bass and onset energy (assumes --beats-per-bar)
  pumped_regions, grid                       stretches where one fixed period explains
                                             the onsets better than the tracker does;
                                             there the pulses are fitted and snapped to
                                             the real onset peaks (grid = beats with
                                             those pulses swapped in)
  onsets {t, s}, hits {t, strength, jump_db} transients; hits are the strongest ones
                                             with a loudness jump behind them
  structure {t, raw_t, prominence, loudness_change_db}
                                             novelty over timbre, harmony and loudness,
                                             refined to the strongest onset within 0.6 s
  loudest, rises, drops, fade_below_-40db_from, silence_from
  frames {energy, low, mid, high, onset, perc}
                                             one value per video frame, 0..1, so a
                                             section can index them by frame number

Why: on We Built a Mind the hand-placed cuts missed the music by 0.5 to 1.5 s,
and on a drumless pumping pad the tracker drifted by up to 0.1 s, which a fitted
grid fixed. Beat tracking method: Ellis, "Beat Tracking by Dynamic Programming",
JNMR 36(1), 2007, doi:10.1080/09298210701653344, as implemented by librosa
(https://librosa.org/doc/0.10.2/generated/librosa.beat.beat_track.html). Trackers
make octave errors (half or double tempo) above all on slow music; see the
mir_eval beat metrics (https://mir-eval.readthedocs.io/latest/api/beat.html) and
the madmom DBN tempo range of 55 to 215 BPM
(https://madmom.readthedocs.io/en/v0.16/modules/features/downbeats.html).
When it warns, listen and, if you know the tempo, pass --bpm.

Exit codes: 0 written, 2 bad arguments or no audio, 1 ffmpeg failed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 22050
HOP = 256  # about 11.6 ms


def die(msg: str, code: int = 2) -> None:
    print(f"analyze_music: {msg}")
    sys.exit(code)


def load_audio(path: Path) -> np.ndarray:
    """Decode any format ffmpeg reads to mono float32 at SR, through a pipe."""
    try:
        p = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
            capture_output=True, check=True,
        )
    except FileNotFoundError:
        die("ffmpeg not found on PATH", 1)
    except subprocess.CalledProcessError as e:
        die(f"ffmpeg could not read {path}: {e.stderr.decode(errors='replace').strip()[:300]}", 1)
    return np.frombuffer(p.stdout, np.float32).astype(np.float64)


def to_db(x: np.ndarray, ref: float) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(x, 1e-10) / max(ref, 1e-10))


def norm01(x: np.ndarray) -> np.ndarray:
    if len(x) == 0:
        return x
    lo, hi = float(np.min(x)), float(np.max(x))
    return (x - lo) / (hi - lo) if hi > lo else np.zeros_like(x)


def per_frame(values: np.ndarray, times: np.ndarray, n_frames: int, fps: float, how: str) -> np.ndarray:
    """Resample a hop-rate curve onto the video-frame grid (max or mean per frame)."""
    idx = np.clip((times * fps).astype(int), 0, n_frames - 1)
    if how == "max":
        out = np.zeros(n_frames)
        np.maximum.at(out, idx, values)
        return out
    sums, counts = np.zeros(n_frames), np.zeros(n_frames)
    np.add.at(sums, idx, values)
    np.add.at(counts, idx, 1)
    out = sums / np.maximum(counts, 1)
    # frames with no hop sample (fps above the hop rate) take the previous value
    for i in range(1, n_frames):
        if counts[i] == 0:
            out[i] = out[i - 1]
    return out


def r3(x: float) -> float:
    return round(float(x), 3)


def main() -> int:
    ap = argparse.ArgumentParser(prog="analyze_music.py", description="Measure the track into data/beats.json and plot it.")
    ap.add_argument("audio", nargs="?", help="the track (default: assets/<audio.src> from data/timeline.json)")
    ap.add_argument("--fps", type=float, default=None, help="video frame rate for the per-frame curves (default: timeline fps, else 30)")
    ap.add_argument("--out", default="data/beats.json", help="where to write (default data/beats.json)")
    ap.add_argument("--bpm", type=float, default=None, help="fix the tempo instead of estimating it (use after a tempo warning)")
    ap.add_argument("--beats-per-bar", type=int, default=4, help="beats in a bar, for the downbeats (default 4)")
    ap.add_argument("--plot", default="out/research/music.png", help="the plot (default out/research/music.png)")
    ap.add_argument("--zoom", type=float, default=0, help="also write music-<a>-<b>.png panels of this many seconds (default 0: none)")
    ap.add_argument("--no-plot", action="store_true", help="skip the plots")
    a = ap.parse_args()

    tl_path = Path("data/timeline.json")
    tl = json.loads(tl_path.read_text(encoding="utf-8")) if tl_path.exists() else {}
    if a.audio:
        audio = Path(a.audio)
    elif tl.get("audio") and tl["audio"].get("src"):
        audio = Path("assets") / tl["audio"]["src"]
    else:
        die("no audio given and data/timeline.json has no audio.src")
    if not audio.exists():
        die(f"{audio} not found")
    fps = float(a.fps or tl.get("fps") or 30)
    bpb = max(1, a.beats_per_bar)

    import librosa  # slow import: after argument checks
    import scipy.ndimage
    import scipy.signal

    y = load_audio(audio)
    if len(y) < SR // 2:
        die("the audio is shorter than half a second")
    sr = SR
    duration = len(y) / sr
    n_frames = int(np.ceil(duration * fps))
    hop_s = HOP / sr

    # --- spectra -----------------------------------------------------------
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=HOP)
    rms = librosa.feature.rms(S=S, frame_length=2048, hop_length=HOP)[0]
    rms_db = to_db(rms, float(np.max(rms)))

    def band(lo: float, hi: float) -> np.ndarray:
        m = (freqs >= lo) & (freqs < hi)
        return np.sqrt(np.mean(S[m] ** 2, axis=0))

    low, mid, high = band(20, 160), band(160, 2000), band(2000, 11000)

    # --- onsets and beats ----------------------------------------------------
    y_h, y_p = librosa.effects.hpss(y)
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP, aggregate=np.median)
    oenv_p = librosa.onset.onset_strength(y=y_p, sr=sr, hop_length=HOP)
    oenv_low = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[freqs < 160], ref=np.max), sr=sr, hop_length=HOP)
    env_max = scipy.ndimage.maximum_filter1d(oenv, size=7)  # strongest onset within +-3 hops (+-35 ms)
    env_low_max = scipy.ndimage.maximum_filter1d(oenv_low, size=7)

    def at(env: np.ndarray, t: np.ndarray | float) -> np.ndarray:
        idx = np.clip(np.round(np.asarray(t) / hop_s).astype(int), 0, len(env) - 1)
        return env[idx]

    kw = {"bpm": a.bpm} if a.bpm else {}
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=HOP, tightness=100, **kw)
    tempo = float(np.atleast_1d(tempo)[0])
    beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=HOP)
    period = float(np.median(np.diff(beats))) if len(beats) > 1 else 0.0

    # Tempogram second opinion: distinct peaks of the mean autocorrelation tempogram.
    tg = librosa.feature.tempogram(onset_envelope=oenv, sr=sr, hop_length=HOP)
    tg_bpm = librosa.tempo_frequencies(tg.shape[0], sr=sr, hop_length=HOP)
    tg_mean = np.mean(tg, axis=1)
    ok = np.isfinite(tg_bpm) & (tg_bpm >= 40) & (tg_bpm <= 240)
    cb, cw = tg_bpm[ok], tg_mean[ok]
    order = np.argsort(cb)
    cb, cw = cb[order], cw[order]
    pk, _ = scipy.signal.find_peaks(cw)
    pk = sorted(pk, key=lambda i: -cw[i])[:6]
    top_w = float(cw[pk[0]]) if pk else 1.0
    tempo_candidates = [{"bpm": round(float(cb[i]), 2), "weight": round(float(cw[i]) / top_w, 3)} for i in pk]

    # Octave check, from measured hints that the tracker counted half or double:
    # a tempogram peak at 2x nearly as strong, or off-beats (midpoints) as strong as
    # the beats (the real pulse may be twice as fast); every other beat much weaker
    # than its neighbours, or a stronger peak at 0.5x (it may be half as fast).
    warnings = []
    beat_strength = at(env_max, beats) if len(beats) else np.zeros(0)
    if tempo <= 0 or len(beats) < 4:
        warnings.append("no steady beat found (0 BPM or under 4 beats): cut to onsets, hits and structure instead")
    else:
        def weight_near(bpm: float) -> float:
            near = [c["weight"] for c in tempo_candidates if abs(c["bpm"] / bpm - 1) < 0.05]
            return max(near) if near else 0.0
        w_here = max(weight_near(tempo), 1e-6)
        mids = (beats[:-1] + beats[1:]) / 2
        mid_ratio = float(np.mean(at(env_max, mids)) / (np.mean(beat_strength) + 1e-9))
        even, odd = beat_strength[0::2], beat_strength[1::2]
        alt_ratio = float(min(np.mean(even), np.mean(odd)) / (max(np.mean(even), np.mean(odd)) + 1e-9))
        if weight_near(2 * tempo) >= 0.6 * w_here or mid_ratio >= 0.75:
            warnings.append(
                f"tempo may be double: {2 * tempo:.1f} BPM also fits (tempogram weight {weight_near(2 * tempo):.2f} vs {w_here:.2f}; "
                f"off-beats carry {mid_ratio:.0%} of the beat strength)")
        # An autocorrelation tempogram always peaks at half tempo (twice the lag) for a
        # steady pulse, so only a half-tempo peak stronger than the tracked one counts.
        if weight_near(tempo / 2) > 1.05 * w_here or alt_ratio <= 0.5:
            warnings.append(
                f"tempo may be half: {tempo / 2:.1f} BPM also fits (tempogram weight {weight_near(tempo / 2):.2f} vs {w_here:.2f}; "
                f"the weaker half of the beats carries {alt_ratio:.0%} of the stronger half)")
        if not warnings and (tempo < 70 or tempo > 160):
            warnings.append(f"{tempo:.1f} BPM is outside 70-160, where trackers most often halve or double; listen to one bar")
    tempo_warning = "; ".join(warnings) if warnings else None

    # Bar phase: which beat of the bar carries the most bass and onset energy.
    if len(beats) >= bpb:
        beat_low = at(env_low_max, beats)
        phase_scores = [
            float(np.mean(beat_low[p::bpb]) / (np.mean(beat_low) + 1e-9) + np.mean(beat_strength[p::bpb]) / (np.mean(beat_strength) + 1e-9))
            for p in range(bpb)
        ]
        phase = int(np.argmax(phase_scores))
    else:
        phase_scores, phase = [], 0
    downbeats = beats[phase::bpb] if len(beats) else beats

    # --- pumped regions: one fixed period explains the onsets ----------------
    # Slide a window of 8 beats; where one period and phase put nearly every grid
    # point on a real onset (coverage), join the windows, refit the whole stretch,
    # snap each pulse to the strongest onset within 60 ms, split at three misses in
    # a row and trim misses at the ends. On a drumless pad this grid is steadier
    # than the tracker (We Built a Mind: the tracker drifted up to 0.1 s).
    thresh_on = 0.25 * float(np.percentile(oenv, 99))
    half_w = int(0.06 / hop_s)

    def fit(t0: float, t1: float, p0: float, span: float = 0.04) -> dict | None:
        best = None
        for per in np.arange(p0 * (1 - span), p0 * (1 + span), 0.0005):
            n = int((t1 - t0) / per)
            if n < 4:
                continue
            offs = np.arange(0.0, per, 0.004)
            ts = t0 + offs[:, None] + per * np.arange(n)[None, :]
            score = at(env_max, ts).mean(axis=1)
            j = int(np.argmax(score))
            if best is None or score[j] > best[0]:
                best = (float(score[j]), float(per), float(t0 + offs[j]), n)
        if best is None:
            return None
        _, per, first, n = best
        grid_t = first + per * np.arange(n)
        return {"period": per, "first": first, "coverage": float(np.mean(at(env_max, grid_t) >= thresh_on))}

    def pulse_runs(f: dict, t1: float) -> list[list[tuple[float, float, bool]]]:
        """Grid -> (grid time, snapped time, on an onset) runs, split at 3 misses in a row."""
        rows = []
        for tt in np.arange(f["first"], t1, f["period"]):
            k0 = int(round(tt / hop_s))
            lo, hi = max(0, k0 - half_w), min(len(oenv), k0 + half_w + 1)
            k = lo + int(np.argmax(oenv[lo:hi]))
            on = bool(oenv[k] >= thresh_on)
            rows.append((float(tt), float(k * hop_s) if on else float(tt), on))
        runs, cur, misses = [], [], 0
        for r in rows:
            cur.append(r)
            misses = 0 if r[2] else misses + 1
            if misses >= 3:
                runs.append(cur[:-3])
                cur, misses = [], 0
        runs.append(cur)
        out = []
        for run in runs:
            while run and not run[0][2]:
                run = run[1:]
            while run and not run[-1][2]:
                run = run[:-1]
            if run:
                out.append(run)
        return out

    pumped = []
    if period > 0 and duration > 12 * period:
        win, step = 8 * period, 2 * period
        spans = []
        t = 0.0
        while t + win <= duration:
            f = fit(t, t + win, period)
            if f and f["coverage"] >= 0.85:
                if spans and t <= spans[-1][1]:
                    spans[-1][1] = t + win
                else:
                    spans.append([t, t + win])
            t += step
        for s0, s1 in spans:
            f = fit(s0, s1, period)
            if not f:
                continue
            for run in pulse_runs(f, s1):
                cov = sum(r[2] for r in run) / len(run)
                if len(run) < 12 or cov < 0.85:
                    continue
                pulses = [r3(r[1]) for r in run]
                r0, r1 = pulses[0] - f["period"] / 2, pulses[-1] + f["period"] / 2
                inside = beats[(beats >= pulses[0]) & (beats <= pulses[-1])]
                drift = max((min(abs(b - p) for p in pulses) for b in inside), default=0.0)
                pumped.append({"from": r3(r0), "to": r3(r1), "period": round(f["period"], 4), "first": pulses[0],
                               "coverage": round(cov, 2), "tracker_drift": r3(drift), "pulses": pulses})
    grid = sorted([float(b) for b in beats if not any(r["from"] <= b <= r["to"] for r in pumped)]
                  + [p for r in pumped for p in r["pulses"]])

    onset_frames = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=HOP, backtrack=False,
                                              delta=0.12, wait=int(0.08 / hop_s))
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=HOP)
    onset_str = oenv[onset_frames]
    onset_norm = onset_str / (np.max(onset_str) + 1e-9) if len(onset_str) else onset_str

    # Hits: onsets weighted by how far the loudness jumps across them.
    def jump_db(t: float, w: float = 0.25) -> float:
        b4 = (times >= t - w) & (times < t - 0.02)
        af = (times >= t) & (times < t + w)
        if not b4.any() or not af.any():
            return 0.0
        return float(np.max(rms_db[af]) - np.mean(rms_db[b4]))

    onset_jump = np.array([jump_db(t) for t in onset_times])
    hit_score = onset_norm * np.clip(onset_jump, 0, 30) / 30 + onset_norm * 0.5
    n_hits = int(np.clip(round(duration / 2.5), 12, 120))
    hits = []
    for i in np.argsort(hit_score)[::-1]:
        t = float(onset_times[i])
        if all(abs(t - h["t"]) > 0.35 for h in hits):
            hits.append({"t": r3(t), "strength": r3(onset_norm[i]), "jump_db": round(float(onset_jump[i]), 1)})
        if len(hits) >= n_hits:
            break
    hits.sort(key=lambda h: h["t"])

    # --- structure -----------------------------------------------------------
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=HOP)
    chroma = librosa.feature.chroma_cqt(y=y_h, sr=sr, hop_length=HOP)
    n = min(mfcc.shape[1], chroma.shape[1], len(rms))
    feat = np.vstack([librosa.util.normalize(mfcc[:, :n], axis=1), librosa.util.normalize(chroma[:, :n], axis=1)])
    w = max(4, int(min(4.0, duration / 6) / hop_s))  # 4 s before vs 4 s after (shorter for short tracks)
    csum = np.cumsum(np.pad(feat, ((0, 0), (1, 0))), axis=1)
    nov = np.zeros(n)
    for i in range(w, n - w):
        nov[i] = np.linalg.norm((csum[:, i + w] - csum[:, i]) / w - (csum[:, i] - csum[:, i - w]) / w)
    w2 = max(2, int(min(2.0, duration / 8) / hop_s))
    c2 = np.cumsum(np.pad(rms ** 2, (1, 0)))
    loud_nov = np.zeros_like(rms)
    for i in range(w2, len(rms) - w2):
        loud_nov[i] = 10 * np.log10(((c2[i + w2] - c2[i]) / w2 + 1e-12) / ((c2[i] - c2[i - w2]) / w2 + 1e-12))
    combo = norm01(scipy.ndimage.gaussian_filter1d(nov, max(1, int(0.3 / hop_s)))) + 0.5 * norm01(np.abs(loud_nov[:n]))
    peaks, props = scipy.signal.find_peaks(combo, distance=max(1, int(min(3.0, duration / 8) / hop_s)), prominence=0.12)
    structure = []
    for p, prom in zip(peaks, props["prominences"]):
        t = float(times[p])
        near = [(float(onset_norm[i]), float(onset_times[i])) for i in range(len(onset_times)) if abs(onset_times[i] - t) <= 0.6]
        refined = max(near)[1] if near else t
        structure.append({"t": r3(refined), "raw_t": r3(t), "prominence": r3(prom), "loudness_change_db": round(float(loud_nov[p]), 1)})

    # --- loudness landmarks ----------------------------------------------------
    audible = np.where(rms_db > -50)[0]
    silence_from = float(times[audible[-1]]) if len(audible) else duration
    q40 = np.where(rms_db > -40)[0]
    fade_from = float(times[q40[-1]]) if len(q40) else duration
    loudest = float(times[int(np.argmax(scipy.ndimage.uniform_filter1d(rms, max(1, int(0.1 / hop_s)))))])
    dist = max(1, int(min(2.0, duration / 8) / hop_s))
    di, _ = scipy.signal.find_peaks(-loud_nov, distance=dist, height=4.0)
    ri, _ = scipy.signal.find_peaks(loud_nov, distance=dist, height=4.0)
    drops = [{"t": r3(times[i]), "db": round(float(loud_nov[i]), 1)} for i in di]
    rises = [{"t": r3(times[i]), "db": round(float(loud_nov[i]), 1)} for i in ri]

    # --- per-video-frame curves --------------------------------------------------
    def band_curve(x: np.ndarray) -> np.ndarray:
        return norm01(per_frame(to_db(x, float(np.max(x))).clip(-60, 0), times, n_frames, fps, "mean"))

    curves = {
        "energy": norm01(np.clip(per_frame(rms_db, times, n_frames, fps, "mean"), -60, 0)),
        "low": band_curve(low), "mid": band_curve(mid), "high": band_curve(high),
        "onset": norm01(per_frame(oenv, times[:len(oenv)], n_frames, fps, "max")),
        "perc": norm01(per_frame(oenv_p, times[:len(oenv_p)], n_frames, fps, "max")),
    }

    data = {
        "_note": "Generated by scripts/analyze_music.py; do not hand-edit, re-run it. Times in seconds; frames.* has one value per video frame at fps.",
        "audio": audio.as_posix(),
        "duration": r3(duration),
        "fps": fps if fps != int(fps) else int(fps),
        "bpm": r3(tempo),
        "beat_period": round(period, 4) if period else None,
        "tempo_candidates": tempo_candidates,
        "tempo_warning": tempo_warning,
        "beats_per_bar": bpb,
        "bar_phase": phase,
        "bar_phase_scores": [r3(s) for s in phase_scores],
        "beats": [r3(b) for b in beats],
        "beat_strength": [r3(s / (np.max(beat_strength) + 1e-9)) for s in beat_strength],
        "downbeats": [r3(b) for b in downbeats],
        "pumped_regions": pumped,
        "grid": [r3(g) for g in grid],
        "onsets": [{"t": r3(t), "s": r3(s)} for t, s in zip(onset_times, onset_norm)],
        "hits": hits,
        "structure": structure,
        "loudest": r3(loudest),
        "rises": rises,
        "drops": drops,
        "fade_below_-40db_from": r3(fade_from),
        "silence_from": r3(silence_from),
        "frames": {k: [r3(v) for v in arr] for k, arr in curves.items()},
    }
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")

    # --- plots -------------------------------------------------------------------
    plots = []
    if not a.no_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        mel = librosa.power_to_db(librosa.feature.melspectrogram(S=S ** 2, sr=sr, n_mels=96), ref=np.max)
        pulses_all = [p for r in pumped for p in r["pulses"]]

        def plot(t0: float, t1: float, path: Path) -> None:
            span = t1 - t0
            width = float(np.clip(span / 4.0, 14, 40))
            fig, ax = plt.subplots(4, 1, figsize=(width, 11), sharex=True)
            m = (times >= t0) & (times <= t1)
            ax[0].imshow(mel[:, m], aspect="auto", origin="lower", extent=[t0, t1, 0, 96], cmap="magma")
            ax[0].set_ylabel("mel band")
            ax[0].set_title(f"{audio.name}: {tempo:.1f} BPM, beat {period:.3f} s, {len(beats)} beats, {len(downbeats)} bars of {bpb}"
                            + (f"   WARNING: {tempo_warning}" if tempo_warning else ""), loc="left", fontsize=10)
            ax[1].plot(times[m], rms_db[m], color="k", lw=0.8, label="loudness dB")
            ax[1].plot(times[m], to_db(low, float(np.max(low)))[m], color="tab:red", lw=0.6, alpha=0.7, label="bass < 160 Hz")
            ax[1].plot(times[m], to_db(high, float(np.max(high)))[m], color="tab:blue", lw=0.6, alpha=0.7, label="air > 2 kHz")
            ax[1].set_ylim(-60, 3)
            ax[1].legend(loc="lower right", fontsize=8)
            mo = m[:len(oenv)]
            ax[2].plot(times[:len(oenv)][mo], oenv[mo], color="tab:purple", lw=0.8)
            for b in beats:
                if t0 <= b <= t1:
                    ax[2].axvline(b, color="0.6", lw=0.5)
            for b in downbeats:
                if t0 <= b <= t1:
                    ax[2].axvline(b, color="k", lw=1.0)
            for p in pulses_all:
                if t0 <= p <= t1:
                    ax[2].axvline(p, color="tab:green", lw=0.6, ls="--")
            for r in pumped:
                if r["to"] >= t0 and r["from"] <= t1:
                    ax[2].axvspan(max(t0, r["from"]), min(t1, r["to"]), color="tab:green", alpha=0.07)
            hy = float(np.max(oenv[mo])) if mo.any() else 1.0
            ax[2].scatter([h["t"] for h in hits if t0 <= h["t"] <= t1], [hy * 1.02] * sum(t0 <= h["t"] <= t1 for h in hits),
                          color="tab:red", s=14, zorder=3)
            ax[2].set_ylabel("onsets\n(grey beats, black bars,\ngreen fitted pulses, red hits)", fontsize=8)
            ax[3].plot(times[:n][m[:n]], combo[m[:n]], color="tab:green", lw=0.9, label="structure novelty")
            ax[3].plot(times[m], loud_nov[m] / 20.0, color="tab:orange", lw=0.7, label="loudness change / 20 dB")
            ax[3].legend(loc="upper right", fontsize=8)
            for a_ in ax:
                for s in structure:
                    if t0 <= s["t"] <= t1:
                        a_.axvline(s["t"], color="red", lw=1.1, ls=":")
                for t_, c_ in ((loudest, "magenta"), (silence_from, "tab:blue")):
                    if t0 <= t_ <= t1:
                        a_.axvline(t_, color=c_, lw=1.4)
            step = 1 if span <= 30 else (5 if span <= 150 else 10)
            ax[3].set_xticks(np.arange(np.ceil(t0), t1 + 0.01, step))
            ax[3].set_xlim(t0, t1)
            ax[3].set_xlabel("seconds   (red dotted = structure, magenta = loudest, blue = silence from)")
            fig.tight_layout()
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, dpi=70)
            plt.close(fig)
            plots.append(path.as_posix())

        main_plot = Path(a.plot)
        plot(0, duration, main_plot)
        if a.zoom and a.zoom > 0:
            t0 = 0.0
            while t0 < duration:
                t1 = min(duration, t0 + a.zoom)
                plot(t0, t1, main_plot.with_name(f"{main_plot.stem}-{int(t0):03d}-{int(np.ceil(t1)):03d}.png"))
                t0 += a.zoom

    # --- the music brief ---------------------------------------------------------
    print(f"analyze_music: {audio.as_posix()} -> {out.as_posix()}")
    print(f"duration {duration:.3f} s, {n_frames} frames at {fps:g} fps")
    print(f"tempo {tempo:.2f} BPM (beat {period:.4f} s), {len(beats)} beats, {len(downbeats)} downbeats "
          f"(bar phase {phase} of {bpb}, scores {[round(s, 2) for s in phase_scores]})")
    print("tempogram peaks: " + ", ".join(f"{c['bpm']:.1f} ({c['weight']:.2f})" for c in tempo_candidates))
    for wmsg in warnings:
        print(f"WARNING: {wmsg}")
    for r in pumped:
        print(f"pumped {r['from']:.2f}-{r['to']:.2f} s: period {r['period']:.4f} s, {len(r['pulses'])} pulses, "
              f"tracker off by up to {r['tracker_drift']:.3f} s there")
    print(f"onsets {len(onset_times)}, hits {len(hits)}: " + ", ".join(f"{h['t']:.2f}" for h in hits[:12]) + (" ..." if len(hits) > 12 else ""))
    print("structure: " + ", ".join(f"{s['t']:.2f} ({s['loudness_change_db']:+.1f} dB)" for s in structure))
    print("rises: " + (", ".join(f"{r['t']:.2f} ({r['db']:+.1f} dB)" for r in rises) or "none"))
    print("drops: " + (", ".join(f"{r['t']:.2f} ({r['db']:+.1f} dB)" for r in drops) or "none"))
    print(f"loudest {loudest:.2f} s, below -40 dB from {fade_from:.2f} s, silent from {silence_from:.2f} s")
    for p in plots:
        print(f"plot: {p}")
    return 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="ascii", errors="backslashreplace")
    sys.exit(main())
