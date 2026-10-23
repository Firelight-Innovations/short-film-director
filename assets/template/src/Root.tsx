import { Composition } from "remotion";
import { Animatic } from "./animatic/Animatic";
import { animaticSchema, defaultAnimaticProps, defaultFilmProps, filmSchema } from "./config";
import { Film } from "./Film";
import { Solo, defaultSoloProps } from "./solo";
import { DURATION_FRAMES, timeline } from "./timeline/timeline";

/**
 * Three compositions, all the film's size, frame rate and length, read from
 * data/timeline.json, so the timeline stays the one source of timing:
 *
 *   Film      the film (npm run render:final renders it with data/props.final.json)
 *   Solo      one section for real, the rest as test cards (scripts/shots.mjs <id>)
 *   Animatic  data/storyboard.json panels with every cue at its real time (npm run animatic)
 */
export const RemotionRoot: React.FC = () => {
  const common = { durationInFrames: DURATION_FRAMES, fps: timeline.fps, width: timeline.w, height: timeline.h };
  return (
    <>
      <Composition id="Film" component={Film} schema={filmSchema} defaultProps={defaultFilmProps} {...common} />
      <Composition id="Solo" component={Solo} schema={filmSchema} defaultProps={defaultSoloProps} {...common} />
      <Composition id="Animatic" component={Animatic} schema={animaticSchema} defaultProps={defaultAnimaticProps} {...common} />
    </>
  );
};
