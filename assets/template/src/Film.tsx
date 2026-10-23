import type { FilmProps } from "./config";
import { FilmFrame } from "./kit/frame";
import { SECTIONS } from "./sections/registry";
import { checkSectionId, soloRegistry } from "./solo";

/**
 * The film. All compositing lives in FilmFrame (src/kit/frame.tsx):
 *
 *   AudioTrack -> FilmStack (one section, or a transition owner holding its
 *   neighbour) -> Grain -> Letterbox -> DevOverlay
 *
 * Timing and words come from data/timeline.json. Each section is one component
 * in src/sections/<id>/; a section with no component plays as a test card.
 * `debugSolo` renders one section for real and the rest as test cards (the
 * same as the Solo composition). The grade runs once, over the rendered mp4
 * (scripts/grade.py), never per section.
 */
export const Film: React.FC<FilmProps> = ({ showDevOverlay, grainStrength, muteAudio, debugSolo, bare, through }) => {
  const registry = debugSolo ? soloRegistry(checkSectionId(debugSolo, "Film"), Boolean(through)) : SECTIONS;
  return (
    <FilmFrame
      registry={registry}
      showDevOverlay={showDevOverlay}
      grainStrength={grainStrength}
      muteAudio={muteAudio}
      bare={bare}
    />
  );
};
