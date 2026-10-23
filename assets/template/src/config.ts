/**
 * Composition input props and their defaults (zod, so the Studio can edit them).
 *
 * The final export forces the dev overlay off with data/props.final.json:
 *   { "showDevOverlay": false, "grainStrength": 1, "muteAudio": false, "debugSolo": "" }
 */
import { z } from "zod";

export const filmSchema = z.object({
  /** Section, timecode, frame and transition window in the letterbox bars. Off for the final. */
  showDevOverlay: z.boolean(),
  /** Multiplier for the light in-render grain (0 turns it off). */
  grainStrength: z.number().min(0).max(2),
  /** Mute the track (check renders, iterating on picture). */
  muteAudio: z.boolean(),
  /**
   * A section id ("01-turn"): that section for real, every other section as a
   * labelled test card. "" renders the whole film. Solo always needs one.
   */
  debugSolo: z.string(),
  /** Picture only: no grain, no letterbox, no overlay (plates cut from the film). */
  bare: z.boolean().optional(),
  /**
   * With debugSolo: a test-card neighbour that owns a transition into or out of
   * the solo section draws the live solo section full-frame instead of itself,
   * so the section can be checked through a window it does not own.
   */
  through: z.boolean().optional(),
});

export type FilmProps = z.infer<typeof filmSchema>;

export const defaultFilmProps: FilmProps = {
  showDevOverlay: true,
  grainStrength: 1,
  muteAudio: false,
  debugSolo: "",
  bare: false,
  through: false,
};

export const animaticSchema = z.object({
  /** Mute the track. */
  muteAudio: z.boolean(),
});

export type AnimaticProps = z.infer<typeof animaticSchema>;

export const defaultAnimaticProps: AnimaticProps = { muteAudio: false };
