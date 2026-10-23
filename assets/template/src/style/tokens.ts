/**
 * Film-wide constants, all read from data/timeline.json (lead-owned).
 *
 * The look of a section lives in its own folder. What stays here must be the
 * same everywhere: the canvas, the letterbox, the safe areas, and one palette
 * per section so neighbours can quote each other's colours at a boundary
 * without importing each other's code.
 */
import { timeline } from "../timeline/timeline";
import type { SectionId, SectionPalette } from "../timeline/types";

export const CANVAS = { width: timeline.w, height: timeline.h, fps: timeline.fps } as const;

/** Size unit: 1 at 1080p, so `54 * UNIT` px stays the same share of a 9:16 or 4K frame. */
export const UNIT = Math.min(CANVAS.width, CANVAS.height) / 1080;

/** Letterbox bar height in px, top and bottom (timeline.letterbox x h; 0 = no bars). */
export const LETTERBOX_PX = Math.round(CANVAS.height * timeline.letterbox);

export interface Box {
  left: number;
  top: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
}

const PICTURE: Box = {
  left: 0,
  top: LETTERBOX_PX,
  right: CANVAS.width,
  bottom: CANVAS.height - LETTERBOX_PX,
  width: CANVAS.width,
  height: CANVAS.height - 2 * LETTERBOX_PX,
};

/** A centred box holding fraction k of the picture's width and height. */
function inset(k: number): Box {
  const width = Math.round(PICTURE.width * k);
  const height = Math.round(PICTURE.height * k);
  const left = Math.round((CANVAS.width - width) / 2);
  const top = Math.round(PICTURE.top + (PICTURE.height - height) / 2);
  return { left, top, right: left + width, bottom: top + height, width, height };
}

/**
 * Where things may go. `picture` is what the bars leave; anything that moves
 * the eye stays in `action`; every word stays in `title` (alias `text`).
 */
export const SAFE = {
  top: PICTURE.top,
  bottom: PICTURE.bottom,
  height: PICTURE.height,
  centerX: CANVAS.width / 2,
  centerY: CANVAS.height / 2,
  picture: PICTURE,
  action: inset(timeline.safe.action),
  title: inset(timeline.safe.title),
  text: inset(timeline.safe.title),
} as const;

/** Used for any colour a section's palette leaves out. */
export const DEFAULT_PALETTE: SectionPalette = {
  bg: "#101114",
  ink: "#f2efe8",
  accent: "#ff5a1f",
  accent2: "#7fb7c9",
  shadow: "#000000",
};

/** A section's palette from timeline.json, completed: accent2 falls back to accent, shadow to black. */
export function PALETTE(id: SectionId): SectionPalette {
  const p = timeline.sections.find((s) => s.id === id)?.palette ?? {};
  const accent = p.accent ?? DEFAULT_PALETTE.accent;
  return {
    bg: p.bg ?? DEFAULT_PALETTE.bg,
    ink: p.ink ?? DEFAULT_PALETTE.ink,
    accent,
    accent2: p.accent2 ?? accent,
    shadow: p.shadow ?? DEFAULT_PALETTE.shadow,
  };
}

/** Dev overlay type: drawn in the letterbox bars, never in the final. */
export const DEV = {
  font: "Consolas, 'Courier New', monospace",
  color: "rgba(255, 255, 255, 0.78)",
  warn: "#ffd24a",
  size: Math.round(20 * UNIT),
} as const;
