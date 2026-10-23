import type React from "react";

/**
 * What every section component receives.
 *
 * `from` / `to` are the section's own span in absolute film seconds. The film
 * also asks a section to render inside the transition windows on either side
 * (see `renderRange(id)`), and the section must draw a valid, full, opaque
 * frame there: start the first shot early and keep the last shot running late.
 *
 * `prev` / `next` are set only for the section that OWNS a transition, and only
 * while its window is open. They hold the neighbour's live render as a React
 * node. The owner places it: under its own layers, in a mask or clip-path, in a
 * CSS or SVG filter, scaled, sliced. If the owner does not render the node, the
 * neighbour is simply not on screen.
 */
export interface SectionProps {
  from: number;
  to: number;
  /** Live render of the section before this one (owner of the transition in). */
  prev?: React.ReactNode;
  /** Live render of the section after this one (owner of the transition out). */
  next?: React.ReactNode;
}

export type SectionComponent = React.FC<SectionProps>;
