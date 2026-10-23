/**
 * The solo harness: composition "Solo". The whole film's timeline, frame for
 * frame (frame numbers are the film's), with ONE section for real (debugSolo)
 * and every other section as a labelled test card in its own palette. Timing,
 * audio, grain, letterbox and transition windows are exactly the film's: it is
 * the same FilmFrame.
 *
 * `through: true` lets the solo section be seen inside a window it does not
 * own: the test-card owner draws the live solo section full-frame.
 *
 *   node scripts/shots.mjs 01-turn --t 7.2,9.0 --through
 *   npx remotion still Solo out/s.jpg --frame=210 --props=solo.json
 *     (solo.json: { "debugSolo": "01-turn", "through": true })
 */
import React from "react";
import type { FilmProps } from "./config";
import { defaultFilmProps } from "./config";
import { FilmFrame } from "./kit/frame";
import type { Registry } from "./kit/frame";
import { makePlaceholder } from "./kit/placeholder";
import { SECTIONS } from "./sections/registry";
import { timeline } from "./timeline/timeline";
import type { SectionId } from "./timeline/types";

const registries = new Map<string, Registry>();

/** Throws unless id is a section of the timeline, so a typo fails loudly. */
export function checkSectionId(id: string, who: string): SectionId {
  if (!timeline.sections.some((s) => s.id === id)) {
    const ids = timeline.sections.map((s) => s.id).join(", ");
    throw new Error(`${who}: debugSolo "${id}" is not a section in data/timeline.json (${ids})`);
  }
  return id;
}

/** The solo section for real (or its test card if it has no component yet), every other one a test card. */
export function soloRegistry(id: SectionId, through: boolean): Registry {
  const key = `${id}|${through}`;
  const hit = registries.get(key);
  if (hit) return hit;
  const reg: Registry = {};
  for (const s of timeline.sections) {
    reg[s.id] = s.id === id ? (SECTIONS[s.id] ?? makePlaceholder(s.id)) : makePlaceholder(s.id, through ? id : null);
  }
  registries.set(key, reg);
  return reg;
}

export const Solo: React.FC<FilmProps> = ({ showDevOverlay, grainStrength, muteAudio, debugSolo, bare, through }) => {
  const id = checkSectionId(debugSolo, "Solo");
  return (
    <FilmFrame
      registry={soloRegistry(id, Boolean(through))}
      showDevOverlay={showDevOverlay}
      grainStrength={grainStrength}
      muteAudio={muteAudio}
      bare={bare}
    />
  );
};

/** Solo opens on the first section in the Studio; shots.mjs passes debugSolo. */
export const defaultSoloProps: FilmProps = { ...defaultFilmProps, debugSolo: timeline.sections[0]?.id ?? "" };
