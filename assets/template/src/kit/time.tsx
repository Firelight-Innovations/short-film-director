/**
 * Film time. Sections are mounted without a <Sequence>, so time is ABSOLUTE:
 * frame 0 is the first frame of the film, not of the section. `useFilmTime()`
 * stays absolute inside <Sequence>, <Freeze> and <Loop>, because it reads the
 * clock the composition root provides.
 *
 * react-three-fiber renders in its own React root, so this context does not
 * reach inside <ThreeCanvas>: call useFilmTime() outside and pass `frame` in.
 */
import React, { createContext, useContext } from "react";
import { Easing, interpolate, random, useCurrentFrame } from "remotion";
import { FPS } from "../timeline/timeline";

const FilmClock = createContext<number | null>(null);

/** Mounted once at the root of every composition (Film, Solo, Animatic). */
export const FilmClockProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  return <FilmClock.Provider value={frame}>{children}</FilmClock.Provider>;
};

/**
 * Pins the film clock for a subtree: wrap a neighbour's node in it to freeze
 * that neighbour on one absolute frame, or to replay it at another time.
 */
export const FilmClockOverride: React.FC<{ frame: number; children: React.ReactNode }> = ({ frame, children }) => {
  return <FilmClock.Provider value={frame}>{children}</FilmClock.Provider>;
};

export interface FilmTime {
  /** Absolute film frame (an integer during a render). */
  frame: number;
  /** Absolute film time in seconds: frame / fps. */
  t: number;
  fps: number;
}

export function useFilmTime(): FilmTime {
  const clock = useContext(FilmClock);
  const local = useCurrentFrame();
  const frame = clock ?? local;
  return { frame, t: frame / FPS, fps: FPS };
}

// ---------------------------------------------------------------------------
// Pure helpers. Each is a function of its arguments only: no state, no clock,
// no Math.random. Frames render in parallel tabs, in any order.
// ---------------------------------------------------------------------------
export const clamp = (v: number, lo = 0, hi = 1): number => Math.min(hi, Math.max(lo, v));
export const lerp = (a: number, b: number, k: number): number => a + (b - a) * k;

export const ease = {
  linear: (x: number) => x,
  in: Easing.in(Easing.cubic),
  out: Easing.out(Easing.cubic),
  inOut: Easing.inOut(Easing.cubic),
  outExpo: Easing.out(Easing.exp),
  inExpo: Easing.in(Easing.exp),
  outBack: Easing.out(Easing.back(1.6)),
  outQuint: Easing.out(Easing.poly(5)),
  inQuint: Easing.in(Easing.poly(5)),
} as const;

/** 0..1 progress of t through [a, b], clamped, optionally eased. */
export function prog(t: number, a: number, b: number, easing: (x: number) => number = ease.linear): number {
  if (b <= a) return t >= b ? 1 : 0;
  return easing(clamp((t - a) / (b - a)));
}

/** Map t from [a, b] to [c, d], clamped, optionally eased. */
export function remap(
  t: number,
  a: number,
  b: number,
  c: number,
  d: number,
  easing: (x: number) => number = ease.linear,
): number {
  if (b <= a) return t >= b ? d : c;
  return interpolate(t, [a, b], [c, d], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing });
}

/** Fade envelope for something on screen during [from, to]: 0 -> 1 -> 0. */
export function envelope(t: number, from: number, to: number, fadeIn = 0.4, fadeOut = 0.4): number {
  return Math.min(prog(t, from, from + fadeIn), 1 - prog(t, to - fadeOut, to));
}

/**
 * Stepped frame for animating "on twos" or "threes": hold(frame, 2) changes
 * every second frame. Seed boil and jitter with it so they hold, not buzz.
 */
export function hold(frame: number, n: number): number {
  return Math.floor(frame / n) * n;
}

/** Seeded random in [0, 1) (Remotion random()). Same seed, same number, every render. */
export function rnd(seed: string | number): number {
  return random(seed);
}

/** Seeded random in [lo, hi). */
export function rndRange(seed: string | number, lo: number, hi: number): number {
  return lo + random(seed) * (hi - lo);
}
