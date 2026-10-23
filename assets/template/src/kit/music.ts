/**
 * The track, as numbers: data/beats.json, measured by
 * `python scripts/analyze_music.py <audio>`. Nothing here is guessed, and
 * nothing here is hand-edited. A film with no track has a beats.json of empty
 * arrays; then every helper returns its "no music" value (level 0, beatEnv 0,
 * sinceBeat Infinity) and sections still render.
 *
 * What you can cut to:
 *   BEATS, DOWNBEATS, ONSETS   event times in seconds, ascending
 *   marks in timeline.json     the one-off events (a drop, a hit, silence)
 *   level(frame, band)         loudness curves, one sample per frame, 0..1
 */
import beats from "../../data/beats.json";
import { FPS } from "../timeline/timeline";

export type Band = "energy" | "low" | "mid" | "high" | "onset";

interface Beats {
  audio?: string | null;
  fps?: number;
  duration?: number;
  bpm?: number;
  beat_period?: number;
  beats?: number[];
  downbeats?: number[];
  /** Either times, or { t, s } with s the onset strength. */
  onsets?: Array<number | { t: number; s?: number }>;
  frames?: Partial<Record<Band, number[]>>;
  [key: string]: unknown;
}

/** The whole file, for anything not wrapped below (hits, structure, loudest, silence_from). */
export const music = beats as unknown as Beats;

const sorted = (xs: number[]): number[] => [...xs].sort((a, b) => a - b);

/** Tracked beats, seconds. */
export const BEATS: number[] = sorted(music.beats ?? []);
/** Bar starts, seconds. */
export const DOWNBEATS: number[] = sorted(music.downbeats ?? []);
/** Onsets (transients), seconds. */
export const ONSETS: number[] = sorted((music.onsets ?? []).map((o) => (typeof o === "number" ? o : o.t)));

/** Median beat spacing in seconds (0 without beats). */
export const BEAT_PERIOD: number = (() => {
  if (BEATS.length < 2) return music.beat_period ?? 0;
  const d = BEATS.slice(1).map((b, i) => b - BEATS[i]).sort((a, b) => a - b);
  return d[Math.floor(d.length / 2)];
})();

/**
 * Loudness of a band at a film frame, 0..1 (normalised over the track).
 * "energy" overall, "low" the bass, "mid", "high" the air, "onset" transient
 * strength. Fractional frames interpolate; before the start and past the end it is 0.
 */
export function level(frame: number, band: Band = "energy"): number {
  const arr = music.frames?.[band];
  if (!arr || arr.length === 0) return 0;
  const x = frame * ((music.fps ?? FPS) / FPS);
  if (x < 0 || x > arr.length - 1) return 0;
  const i = Math.floor(x);
  const k = x - i;
  return i + 1 < arr.length ? arr[i] * (1 - k) + arr[i + 1] * k : arr[i];
}

/** Index of the last beat at or before t (-1 if none). */
export function beatIndex(t: number): number {
  let lo = 0;
  let hi = BEATS.length - 1;
  let idx = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (BEATS[mid] <= t + 1e-6) {
      idx = mid;
      lo = mid + 1;
    } else hi = mid - 1;
  }
  return idx;
}

/**
 * Seconds since the last beat. Infinity before the first beat, and more than
 * two beat periods after the last one (the music has stopped beating).
 */
export function sinceBeat(t: number): number {
  const i = beatIndex(t);
  if (i < 0) return Infinity;
  const d = t - BEATS[i];
  const gap = Math.max(2 * BEAT_PERIOD, 1.5);
  return d > gap ? Infinity : d;
}

/**
 * A decaying kick: 1 on each beat, near 0 after `decay` seconds. Drive scale,
 * brightness or displacement with it so a shot breathes with the music.
 */
export function beatEnv(t: number, decay = 0.35): number {
  const d = sinceBeat(t);
  if (!Number.isFinite(d)) return 0;
  return Math.exp((-3 * d) / decay);
}

/** Beats with a <= t < b. */
export function beatsIn(a: number, b: number): number[] {
  return BEATS.filter((x) => x >= a && x < b);
}
