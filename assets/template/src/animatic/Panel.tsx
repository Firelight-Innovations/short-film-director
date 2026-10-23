/**
 * Storyboard panels (data/storyboard.json) and how the animatic draws one.
 *
 * A panel holds the screen from its `at` until the next panel's `at`. With an
 * `image` (a path under assets/, "board/p01.jpg") the panel is that picture,
 * cropped to fill. Without one it is a drawn card: the section's palette, the
 * action line, the camera, the sound, the section label and the palette
 * swatches. The words on screen are not drawn here: the animatic draws every
 * cue from timeline.json at its real time on top.
 */
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import board from "../../data/storyboard.json";
import { SYSTEM_FONTS } from "../kit/fonts";
import { CANVAS, PALETTE, SAFE, UNIT } from "../style/tokens";
import { F, sectionAt, timeline } from "../timeline/timeline";

export interface Panel {
  id: string;
  section: string;
  /** Seconds; snapped to a frame at load. */
  at: number;
  image?: string | null;
  action: string;
  camera?: string;
  words?: string[];
  sound?: string;
  refs?: string[];
  note?: string;
}

/** The panels, in time order, `at` snapped to frames. */
export const PANELS: Panel[] = ((board as unknown as { panels?: Panel[] }).panels ?? [])
  .map((p) => ({ ...p, at: F(p.at) / timeline.fps }))
  .sort((a, b) => a.at - b.at);

/** The panel on screen at a frame. With no panels, a stand-in card for the section. */
export function panelAt(frame: number): Panel {
  let hit: Panel | null = null;
  for (const p of PANELS) {
    if (F(p.at) <= frame) hit = p;
    else break;
  }
  if (hit) return hit;
  const s = sectionAt(frame / timeline.fps) ?? timeline.sections[0];
  return { id: "--", section: s?.id ?? "", at: 0, action: s ? s.style : "no storyboard panels", note: "no panel yet" };
}

const mono = SYSTEM_FONTS.mono;

export const PanelView: React.FC<{ panel: Panel }> = ({ panel }) => {
  const u = UNIT;
  const p = PALETTE(panel.section);
  const label = timeline.sections.find((s) => s.id === panel.section)?.label ?? "unknown section";
  const meta = (k: string, v?: string) =>
    v ? (
      <div style={{ fontFamily: mono, fontSize: 26 * u, lineHeight: 1.5, color: p.ink, opacity: 0.85 }}>
        <span style={{ color: p.accent, letterSpacing: 2 * u }}>{k}</span>
        {"  "}
        {v}
      </div>
    ) : null;

  // Small squares in the header line, in palette order: bg, ink, accent, accent2, shadow.
  const swatches = (["bg", "ink", "accent", "accent2", "shadow"] as const).map((k) => (
    <div key={k} style={{ width: 30 * u, height: 30 * u, background: p[k], border: `${Math.max(1, 2 * u)}px solid ${p.ink}66` }} />
  ));
  // Leaves room above for the animatic's transition banner, which runs just under the top bar.
  const top = SAFE.title.top + 36 * u;

  return (
    <AbsoluteFill style={{ background: p.bg, overflow: "hidden" }}>
      {panel.image ? (
        <Img src={staticFile(panel.image)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      ) : (
        <>
          <AbsoluteFill style={{ background: `linear-gradient(180deg, ${p.bg} 0%, ${p.bg} 45%, ${p.shadow} 120%)` }} />
          <div
            style={{
              position: "absolute",
              right: CANVAS.width - SAFE.title.right,
              top,
              fontFamily: SYSTEM_FONTS.sans,
              fontWeight: 900,
              fontSize: 260 * u,
              lineHeight: 1,
              color: p.ink,
              opacity: 0.07,
            }}
          >
            {panel.id}
          </div>
        </>
      )}
      {panel.image ? <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.65) 0%, transparent 38%)" }} /> : null}
      <div style={{ position: "absolute", left: SAFE.title.left, top, width: SAFE.title.width * 0.62 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 * u, fontFamily: mono, fontSize: 26 * u, letterSpacing: 2 * u, color: p.accent }}>
          <span style={{ marginRight: 14 * u }}>
            {panel.id.toUpperCase()}  {panel.section}  {label}
          </span>
          {swatches}
        </div>
        <div style={{ fontFamily: SYSTEM_FONTS.sans, fontSize: 42 * u, lineHeight: 1.25, color: p.ink, margin: `${10 * u}px 0 ${12 * u}px` }}>
          {panel.action}
        </div>
        {meta("CAMERA", panel.camera)}
        {meta("SOUND", panel.sound)}
        {meta("REFS", panel.refs && panel.refs.length ? panel.refs.join(" ") : undefined)}
        {meta("NOTE", panel.note)}
      </div>
    </AbsoluteFill>
  );
};
