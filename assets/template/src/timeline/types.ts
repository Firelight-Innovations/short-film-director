/**
 * Typed shape of data/timeline.json, schema version 3: the film as data.
 * Every time is in seconds; the loader (timeline.ts) snaps each one to its
 * frame. The rules are enforced by `python scripts/check-timeline.py`.
 */

/** Section ids come from timeline.json ("00-open"), so they are plain strings. */
export type SectionId = string;

/** A section's colours. Only bg, ink and accent are required in the file. */
export interface SectionPalette {
  /** Dominant field colour. */
  bg: string;
  /** Main ink or type colour. */
  ink: string;
  /** The one accent the section is allowed. */
  accent: string;
  /** Second accent, used sparingly. */
  accent2: string;
  /** Deepest tone. */
  shadow: string;
}

export interface SectionSpan {
  id: SectionId;
  /** The section owns [from, to). Frame-aligned after loading. */
  from: number;
  to: number;
  label: string;
  /** One line: the look. */
  style: string;
  palette?: Partial<SectionPalette>;
}

/**
 * What a cue is for. Sections decide how each role looks; the role says what
 * the words are. The set is open: these have meaning in the kit and animatic.
 *   stamp     a label inside the picture (a date on a tape, a leader card)
 *   slam      a one-beat word hit
 *   narration the film's own voice, on screen
 *   sub       a smaller second line under another cue
 *   quote     someone else's words; carries `attribution` and `source`
 *   data      a number that must be exactly right; carries `source`
 *   thesis    the line the film exists for
 *   question  a question to the viewer
 *   credit    an end credit
 *   logo      a studio or brand mark
 *   caption   a lower-third or subtitle line
 *   vo        a spoken line (voice-over), shown in the animatic as a subtitle
 */
export type KnownCueRole =
  | "stamp"
  | "slam"
  | "narration"
  | "sub"
  | "quote"
  | "data"
  | "thesis"
  | "question"
  | "credit"
  | "logo"
  | "caption"
  | "vo";
export type CueRole = KnownCueRole | (string & {});

export interface Cue {
  /** Role-based ("narration-2"), never content ("stamp-1962" once said 1966). */
  id: string;
  section: SectionId;
  role: CueRole;
  /** `from` is when the words must be READABLE (whole); `to` is when they may go. */
  from: number;
  to: number;
  /** \n = line break. The words on screen are exactly this string. */
  text: string;
  /** Who said it, or the label under a number. Shown on screen. */
  attribution?: string;
  /** Where the fact comes from. Required for `data` and `quote`. */
  source?: string;
  /** Extra strings a section may draw. */
  names?: string[];
  /** Direction for whoever builds the shot. Never shown. */
  note?: string;
  /** When what is DRAWN differs from the readable window (an early write-on, a late fade). */
  shown?: { from: number; to: number };
}

/**
 * One per section boundary. During [at - pre, at + post) only `owner` is
 * mounted and it receives the other section's live render as `next` (owner is
 * the outgoing section `a`) or `prev` (owner is the incoming section `b`).
 * A hard cut has pre = post = 0. `t-start` / `t-end` have no `a` or no `b`.
 */
export interface Transition {
  id: string;
  at: number;
  a: SectionId | null;
  b: SectionId | null;
  owner: SectionId;
  pre: number;
  post: number;
  /** The named device ("Iris"). */
  name: string;
  /** What happens, frame by frame. */
  device: string;
  /** A mark name or a short note on the musical event it sits on. */
  beat: string;
}

export interface AudioMeta {
  /** Path under assets/ ("audio/track.mp3"). */
  src: string;
  gain?: number;
  duration?: number;
  note?: string;
}

export interface Checks {
  /** [from, to) seconds that must be pure black. */
  black: Array<[number, number]>;
  lastFrameBlack: boolean;
}

export interface Grade {
  contrast: number;
  saturation: number;
  gamma: number;
  /** 0 = none; angle = vignette * PI/3. */
  vignette: number;
  /** ffmpeg noise alls. */
  grain: number;
  /** Seconds; the grade is off from here. null = the whole film. */
  until: number | null;
}

export interface Timeline {
  version: number;
  title: string;
  slug: string;
  w: number;
  h: number;
  fps: number;
  dur: number;
  /** Bar height as a fraction of h, top and bottom. 0 = none. */
  letterbox: number;
  /** Fractions of the picture inside the bars. */
  safe: { title: number; action: number };
  audio: AudioMeta | null;
  sections: SectionSpan[];
  marks: Record<string, number>;
  transitions: Transition[];
  cues: Cue[];
  checks: Checks;
  grade: Grade | null;
}
