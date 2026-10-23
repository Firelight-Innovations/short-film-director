/**
 * The film's compositing frame, shared by Film (src/Film.tsx) and Solo
 * (src/solo.tsx). Layers, bottom to top:
 *
 *   1. AudioTrack   the track from frame 0, untouched (timeline.audio may be null)
 *   2. FilmStack    one section, or a transition owner holding its neighbour
 *   3. Grain        light, seeded film-wide grain (the real grain is the grade)
 *   4. Letterbox    timeline.letterbox bars (none when 0)
 *   5. DevOverlay   section, timecode, frame, transition window (never in the final)
 *
 * `bare` drops 3 to 5: picture only, for plates cut from the film.
 *
 * Frames that timeline.checks says must be black (checks.black, lastFrameBlack)
 * mount no section at all, so the film cuts to black whatever the sections draw.
 */
import React from "react";
import { AbsoluteFill } from "remotion";
import { AudioTrack } from "../components/AudioTrack";
import { DevOverlay } from "../components/DevOverlay";
import { Grain } from "../components/Grain";
import { Letterbox } from "../components/Letterbox";
import { mustBeBlack, section, sectionAt, transitionAt } from "../timeline/timeline";
import type { SectionId } from "../timeline/types";
import { makePlaceholder } from "./placeholder";
import type { SectionComponent, SectionProps } from "./section";
import { FilmClockProvider, useFilmTime } from "./time";

/** Section id -> component. An id the timeline has but the registry lacks plays as a test card. */
export type Registry = Record<SectionId, SectionComponent>;

/**
 * Mounts the section that owns the current frame. Inside a transition window
 * [at - pre, at + post) it mounts only the owner and passes it the other
 * section's live render as `next` (owner is `a`) or `prev` (owner is `b`).
 * On a must-be-black frame it mounts nothing, and FilmFrame's #000 shows.
 */
export const FilmStack: React.FC<{ registry: Registry }> = ({ registry }) => {
  const { t, frame } = useFilmTime();
  if (mustBeBlack(frame)) return null;

  const render = (id: SectionId, extra?: Partial<SectionProps>) => {
    const s = section(id);
    const Comp = registry[id] ?? makePlaceholder(id);
    return <Comp key={id} from={s.from} to={s.to} {...extra} />;
  };

  const tr = transitionAt(t);
  if (tr && tr.a && tr.b) {
    const other = tr.owner === tr.a ? tr.b : tr.a;
    const neighbour = <AbsoluteFill>{render(other)}</AbsoluteFill>;
    return tr.owner === tr.a ? render(tr.a, { next: neighbour }) : render(tr.b, { prev: neighbour });
  }

  const s = sectionAt(t);
  return s ? render(s.id) : null;
};

export interface FilmFrameProps {
  registry: Registry;
  showDevOverlay: boolean;
  grainStrength: number;
  muteAudio: boolean;
  /** Picture only: no grain, no letterbox, no overlay. */
  bare?: boolean;
}

export const FilmFrame: React.FC<FilmFrameProps> = ({ registry, showDevOverlay, grainStrength, muteAudio, bare }) => {
  return (
    <FilmClockProvider>
      <AbsoluteFill style={{ background: "#000" }}>
        <AudioTrack muted={muteAudio} />
        <AbsoluteFill style={{ overflow: "hidden" }}>
          <FilmStack registry={registry} />
        </AbsoluteFill>
        {bare ? null : <Grain strength={grainStrength} />}
        {bare ? null : <Letterbox />}
        {showDevOverlay && !bare ? <DevOverlay /> : null}
      </AbsoluteFill>
    </FilmClockProvider>
  );
};
