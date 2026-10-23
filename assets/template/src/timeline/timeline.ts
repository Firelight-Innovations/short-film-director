/**
 * Loads data/timeline.json and gives the lookups every section, the animatic
 * and the film frame read through. Components never index the raw file.
 *
 * Every time is snapped to its frame at load. The file stores seconds to a few
 * decimals, and 99.8667 is a hair after frame 2996 (2996 / 30 = 99.8666...):
 * compared in seconds that frame lands on the wrong side of its boundary, and a
 * section shows one frame late. After snapping, `t = frame / FPS` compares
 * exactly, and the lookups below compare whole frames anyway.
 */
import raw from "../../data/timeline.json";
import type { Cue, SectionId, SectionSpan, Timeline, Transition } from "./types";

type RawTransition = Omit<Transition, "a" | "b"> & { a?: SectionId | null; b?: SectionId | null };
type RawTimeline = Partial<Omit<Timeline, "transitions">> &
  Pick<Timeline, "w" | "h" | "fps" | "dur" | "sections"> & { transitions?: RawTransition[] };

const r = raw as unknown as RawTimeline;

export const FPS: number = r.fps;

const snap = (sec: number): number => Math.round(sec * FPS) / FPS;

/** The whole frame a time falls in. */
const frameOf = (t: number): number => Math.floor(t * FPS + 1e-6);

export const timeline: Timeline = {
  version: r.version ?? 3,
  title: r.title ?? "",
  slug: r.slug ?? "film",
  w: r.w,
  h: r.h,
  fps: r.fps,
  dur: r.dur,
  letterbox: r.letterbox ?? 0,
  safe: r.safe ?? { title: 0.9, action: 0.95 },
  audio: r.audio ?? null,
  sections: r.sections.map((s) => ({ ...s, from: snap(s.from), to: snap(s.to) })),
  marks: Object.fromEntries(Object.entries(r.marks ?? {}).map(([k, v]) => [k, snap(v)])),
  cues: (r.cues ?? []).map((c) => ({
    ...c,
    from: snap(c.from),
    to: snap(c.to),
    ...(c.shown ? { shown: { from: snap(c.shown.from), to: snap(c.shown.to) } } : {}),
  })),
  // Window edges are rounded from the raw values, then pre and post are
  // restated as whole frames around the snapped `at`.
  transitions: (r.transitions ?? []).map((tr) => {
    const f = Math.round(tr.at * FPS);
    const a = Math.round((tr.at - (tr.pre ?? 0)) * FPS);
    const b = Math.round((tr.at + (tr.post ?? 0)) * FPS);
    return { ...tr, a: tr.a ?? null, b: tr.b ?? null, at: f / FPS, pre: (f - a) / FPS, post: (b - f) / FPS };
  }),
  checks: {
    black: (r.checks?.black ?? []).map(([a, b]) => [snap(a), snap(b)] as [number, number]),
    lastFrameBlack: r.checks?.lastFrameBlack ?? false,
  },
  grade: r.grade ? { ...r.grade, until: r.grade.until == null ? null : snap(r.grade.until) } : null,
};

/** Length of the film in frames: round(dur * fps). */
export const DURATION_FRAMES = Math.round(timeline.dur * FPS);

/** Seconds -> whole frame. */
export function F(sec: number): number {
  return Math.round(sec * FPS);
}

/** Frame -> seconds. */
export function T(frame: number): number {
  return frame / FPS;
}

/** The span of one section. Throws on a bad id so typos fail loudly. */
export function section(id: SectionId): SectionSpan {
  const s = timeline.sections.find((x) => x.id === id);
  if (!s) throw new Error(`timeline: no section "${id}" in data/timeline.json`);
  return s;
}

/** The section whose own span [from, to) holds time t, or null (never null inside the film). */
export function sectionAt(t: number): SectionSpan | null {
  const f = frameOf(t);
  for (const s of timeline.sections) {
    if (f >= F(s.from) && f < F(s.to)) return s;
  }
  return null;
}

/** One cue by id. Throws on a bad id. */
export function cue(id: string): Cue {
  const c = timeline.cues.find((x) => x.id === id);
  if (!c) throw new Error(`timeline: no cue "${id}" in data/timeline.json`);
  return c;
}

/** All cues of a section, in time order. */
export function cuesOf(id: SectionId): Cue[] {
  return timeline.cues.filter((c) => c.section === id).sort((a, b) => a.from - b.from);
}

/** All cues readable at time t ([from, to), whole frames). */
export function cuesAt(t: number): Cue[] {
  const f = frameOf(t);
  return timeline.cues.filter((c) => f >= F(c.from) && f < F(c.to));
}

/** The window a cue is drawn in: `shown` when given, else its readable window. */
export function shownOf(c: Cue): { from: number; to: number } {
  return c.shown ?? { from: c.from, to: c.to };
}

/** A named musical landmark, in seconds. Throws on a bad name. */
export function mark(name: string): number {
  const v = timeline.marks[name];
  if (v === undefined) throw new Error(`timeline: no mark "${name}" in data/timeline.json`);
  return v;
}

/** The transition into a section (at its `from`), or null if the file has none. Throws on a bad id. */
export function transitionIn(id: SectionId): Transition | null {
  section(id);
  return timeline.transitions.find((x) => x.b === id) ?? null;
}

/** The transition out of a section (at its `to`), or null if the file has none. Throws on a bad id. */
export function transitionOut(id: SectionId): Transition | null {
  section(id);
  return timeline.transitions.find((x) => x.a === id) ?? null;
}

/**
 * The transition whose window [at - pre, at + post) holds time t, if any.
 * Hard cuts (pre = post = 0) and edge transitions (no a or no b) never open one.
 */
export function transitionAt(t: number): Transition | null {
  const f = frameOf(t);
  for (const tr of timeline.transitions) {
    if (!tr.a || !tr.b) continue;
    if (tr.pre + tr.post <= 0) continue;
    if (f >= F(tr.at - tr.pre) && f < F(tr.at + tr.post)) return tr;
  }
  return null;
}

/**
 * The widest range a section can be asked to render, in seconds: its own span
 * plus the transition windows on either side, whoever owns them. A section
 * draws a full, opaque frame for every frame of it.
 */
export function renderRange(id: SectionId): { from: number; to: number } {
  const s = section(id);
  const tin = timeline.transitions.find((x) => x.b === id && x.a);
  const tout = timeline.transitions.find((x) => x.a === id && x.b);
  return { from: s.from - (tin?.pre ?? 0), to: s.to + (tout?.post ?? 0) };
}

/** True on frames that `checks` says must be pure black (checks.black, and the last frame). */
export function mustBeBlack(frame: number): boolean {
  if (timeline.checks.lastFrameBlack && frame === DURATION_FRAMES - 1) return true;
  return timeline.checks.black.some(([a, b]) => frame >= F(a) && frame < F(b));
}

/** m:ss.cc timecode ("0:07.50"). */
export function formatTimecode(t: number): string {
  const mm = Math.floor(t / 60);
  const ss = t - 60 * mm;
  return `${mm}:${ss.toFixed(2).padStart(5, "0")}`;
}
