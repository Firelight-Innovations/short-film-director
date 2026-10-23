/**
 * The kit: everything a section may import from outside its own folder.
 * Lead-owned. If something is missing, ask under "Requests to lead" in your
 * section log and build a local version in your own folder meanwhile.
 */
export type { SectionComponent, SectionProps } from "./section";
export {
  FilmClockOverride,
  clamp,
  ease,
  envelope,
  hold,
  lerp,
  prog,
  remap,
  rnd,
  rndRange,
  useFilmTime,
} from "./time";
export type { FilmTime } from "./time";
export { BEATS, BEAT_PERIOD, DOWNBEATS, ONSETS, beatEnv, beatIndex, beatsIn, level, music, sinceBeat } from "./music";
export type { Band } from "./music";
export { SYSTEM_FONTS, font, weightsOf } from "./fonts";
export type { FontKind } from "./fonts";
export {
  DURATION_FRAMES,
  F,
  FPS,
  T,
  cue,
  cuesAt,
  cuesOf,
  formatTimecode,
  mark,
  mustBeBlack,
  renderRange,
  section,
  sectionAt,
  shownOf,
  timeline,
  transitionAt,
  transitionIn,
  transitionOut,
} from "../timeline/timeline";
export type { Cue, CueRole, SectionId, SectionPalette, SectionSpan, Timeline, Transition } from "../timeline/types";
export { CANVAS, LETTERBOX_PX, PALETTE, SAFE, UNIT } from "../style/tokens";
export type { Box } from "../style/tokens";
/**
 * A labelled test card in the section's palette. A section stub is
 * `export const Section = makePlaceholder("<id>");` until the real one lands.
 */
export { makePlaceholder } from "./placeholder";
