/**
 * The animatic: composition "Animatic" (npm run animatic -> out/animatic.mp4).
 *
 * It plays data/storyboard.json on the real track, with every cue of
 * data/timeline.json drawn at its real time and styled by its role, so the
 * words, their timing and the music can be signed off before anyone builds.
 * Layers: the panel (black on frames that checks say must be black), the
 * letterbox, the cues, the open transition's name and device, and a strip with
 * the timecode, section, panel id, the next mark, and a bar of sections, cue
 * spans, transition windows and marks as ticks. Frame-pure, like the film.
 */
import React from "react";
import { AbsoluteFill } from "remotion";
import { AudioTrack } from "../components/AudioTrack";
import { Letterbox } from "../components/Letterbox";
import type { AnimaticProps } from "../config";
import { SYSTEM_FONTS } from "../kit/fonts";
import { FilmClockProvider, useFilmTime } from "../kit/time";
import { CANVAS, DEV, LETTERBOX_PX, PALETTE, SAFE, UNIT } from "../style/tokens";
import { F, formatTimecode, mustBeBlack, sectionAt, shownOf, timeline } from "../timeline/timeline";
import type { Cue, Transition } from "../timeline/types";
import { PanelView, panelAt } from "./Panel";

const u = UNIT;
// A portrait frame is too narrow for the strip's text on one line: it wraps to two.
const STRIP = Math.round((CANVAS.width < CANVAS.height ? 128 : 96) * u);
const MARKS = Object.entries(timeline.marks).sort((a, b) => a[1] - b[1]);

type Slot = "top" | "center" | "lower";
const SLOT: Record<string, Slot> = {
  stamp: "top",
  slam: "center",
  thesis: "center",
  quote: "center",
  data: "center",
  question: "center",
  logo: "center",
};

/** How each role looks in the animatic: a stand-in for the section's own type. */
function roleStyle(role: string, ink: string, accent: string): React.CSSProperties {
  const base: React.CSSProperties = { color: ink, fontFamily: SYSTEM_FONTS.sans, textShadow: "0 2px 10px rgba(0,0,0,0.55)" };
  switch (role) {
    case "slam": return { ...base, fontSize: 150 * u, fontWeight: 900, textTransform: "uppercase", letterSpacing: -2 * u, lineHeight: 1 };
    case "thesis": return { ...base, fontFamily: SYSTEM_FONTS.serif, fontSize: 84 * u, lineHeight: 1.15 };
    case "quote": return { ...base, fontFamily: SYSTEM_FONTS.serif, fontStyle: "italic", fontSize: 60 * u, lineHeight: 1.2 };
    case "data": return { ...base, color: accent, fontSize: 120 * u, fontWeight: 800, lineHeight: 1 };
    case "question": return { ...base, fontFamily: SYSTEM_FONTS.serif, fontStyle: "italic", fontSize: 72 * u };
    case "logo": return { ...base, color: accent, fontSize: 90 * u, fontWeight: 800, letterSpacing: 8 * u };
    case "stamp": return { ...base, color: accent, fontFamily: SYSTEM_FONTS.mono, fontSize: 34 * u, letterSpacing: 5 * u, border: `${2 * u}px solid ${accent}`, padding: `${6 * u}px ${14 * u}px` };
    case "sub": return { ...base, fontSize: 38 * u };
    case "credit": return { ...base, fontSize: 40 * u, letterSpacing: 6 * u, textTransform: "uppercase" };
    case "caption":
    case "vo": return { ...base, fontSize: 40 * u, fontStyle: role === "vo" ? "italic" : "normal", background: "rgba(0,0,0,0.6)", padding: `${6 * u}px ${16 * u}px` };
    default: return { ...base, fontSize: 56 * u, fontWeight: 600, lineHeight: 1.2 };
  }
}

const CueView: React.FC<{ c: Cue; dim: boolean }> = ({ c, dim }) => {
  const p = PALETTE(c.section);
  const small: React.CSSProperties = { fontFamily: SYSTEM_FONTS.mono, color: p.ink, opacity: 0.85 };
  return (
    <div style={{ opacity: dim ? 0.45 : 1, display: "flex", flexDirection: "column", alignItems: "inherit", gap: 8 * u }}>
      <div style={{ ...small, fontSize: 18 * u, color: p.accent }}>[{c.id}]</div>
      <div style={{ ...roleStyle(c.role, p.ink, p.accent), whiteSpace: "pre-line" }}>{c.role === "vo" ? `VO  ${c.text}` : c.text}</div>
      {c.attribution ? <div style={{ ...small, fontFamily: SYSTEM_FONTS.sans, fontSize: 36 * u }}>{c.role === "quote" ? `- ${c.attribution}` : c.attribution}</div> : null}
      {c.source ? <div style={{ ...small, fontSize: 24 * u }}>Source: {c.source}</div> : null}
    </div>
  );
};

/** Name and device of the transition whose window holds this frame (hard cuts and edges: half a second). */
function transitionOn(frame: number): Transition | null {
  for (const tr of timeline.transitions) {
    const open = tr.pre + tr.post > 0;
    const end = tr.at >= timeline.dur - 1e-6;
    const a = open ? F(tr.at - tr.pre) : end ? F(tr.at - 0.5) : F(tr.at);
    const b = open ? F(tr.at + tr.post) : end ? F(tr.at) : F(tr.at + 0.5);
    if (frame >= a && frame < b) return tr;
  }
  return null;
}

const Strip: React.FC<{ frame: number; t: number; panelId: string }> = ({ frame, t, panelId }) => {
  const s = sectionAt(t);
  const nm = MARKS.find(([, v]) => F(v) > frame);
  const x0 = 40 * u;
  const W = CANVAS.width - 2 * x0;
  const X = (sec: number) => x0 + (W * sec) / timeline.dur;
  const bar = 20 * u;
  const by = STRIP - 34 * u;
  const rect = (key: string, a: number, b: number, y: number, h: number, style: React.CSSProperties) => (
    <div key={key} style={{ position: "absolute", left: X(a), width: Math.max(1, X(b) - X(a)), top: y, height: h, ...style }} />
  );
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: STRIP, background: "rgba(0,0,0,0.85)" }}>
      <div style={{ position: "absolute", left: x0, right: x0, top: 10 * u, display: "flex", flexWrap: "wrap", justifyContent: "space-between", columnGap: 24 * u, fontFamily: DEV.font, fontSize: 24 * u, color: DEV.color, whiteSpace: "nowrap" }}>
        <span>
          {formatTimecode(t)}  f{frame}   {s ? `${s.id} ${s.label}` : "no section"}   panel {panelId}
        </span>
        <span style={{ color: DEV.warn }}>
          {nm ? `next mark: ${nm[0]} ${formatTimecode(nm[1])} (in ${(nm[1] - t).toFixed(2)} s)` : "no marks ahead"}
          {timeline.audio ? "" : "   NO TRACK"}
        </span>
      </div>
      {timeline.sections.map((sec) => rect(`s-${sec.id}`, sec.from, sec.to, by, bar, { background: PALETTE(sec.id).accent, opacity: 0.55, borderRight: `${2 * u}px solid #000` }))}
      {timeline.cues.map((c) => rect(`c-${c.id}`, c.from, c.to, by + bar + 3 * u, 5 * u, { background: "#ffffff", opacity: 0.6 }))}
      {timeline.checks.black.map(([a, b], i) => rect(`k-${i}`, a, b, by, bar, { background: "#000", outline: `${u}px solid #777` }))}
      {timeline.transitions.map((tr) => rect(`t-${tr.id}`, tr.at - tr.pre, tr.at + tr.post, by - 4 * u, bar + 8 * u, { background: "rgba(255,255,255,0.35)", borderLeft: `${2 * u}px solid #fff` }))}
      {MARKS.map(([k, v]) => rect(`m-${k}`, v, v, by - 8 * u, bar + 16 * u, { width: Math.max(1, 2 * u), background: "#ffffff" }))}
      {rect("head", t, t, by - 12 * u, bar + 24 * u, { width: Math.max(2, 3 * u), background: DEV.warn })}
    </div>
  );
};

const AnimaticFrame: React.FC = () => {
  const { frame, t } = useFilmTime();
  const panel = panelAt(frame);
  const tr = transitionOn(frame);
  const slots: Record<Slot, Array<{ c: Cue; dim: boolean }>> = { top: [], center: [], lower: [] };
  for (const c of timeline.cues) {
    const sh = shownOf(c);
    const readable = frame >= F(c.from) && frame < F(c.to);
    if (readable || (frame >= F(sh.from) && frame < F(sh.to))) slots[SLOT[c.role] ?? "lower"].push({ c, dim: !readable });
  }
  const tb = SAFE.title;
  const col = (items: Array<{ c: Cue; dim: boolean }>) => items.map(({ c, dim }) => <CueView key={c.id} c={c} dim={dim} />);
  return (
    <AbsoluteFill>
      {mustBeBlack(frame) ? <AbsoluteFill style={{ background: "#000" }} /> : <PanelView panel={panel} />}
      <Letterbox />
      <div style={{ position: "absolute", right: CANVAS.width - tb.right, top: tb.top, display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 16 * u }}>{col(slots.top)}</div>
      <div style={{ position: "absolute", left: tb.left, width: tb.width, top: SAFE.centerY - 120 * u, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", gap: 20 * u }}>{col(slots.center)}</div>
      <div style={{ position: "absolute", left: tb.left, width: tb.width, bottom: CANVAS.height - tb.bottom + STRIP, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", gap: 16 * u }}>{col(slots.lower)}</div>
      {tr ? (
        // The name sits in the top bar; the device runs on one line just under it.
        <div style={{ position: "absolute", left: tb.left, width: tb.width, top: 0, textAlign: "center", fontFamily: DEV.font, color: DEV.warn }}>
          <div style={{ height: Math.max(LETTERBOX_PX, 44 * u), display: "flex", alignItems: "center", justifyContent: "center", fontSize: 30 * u }}>
            {tr.pre + tr.post > 0 ? "TRANSITION" : "CUT"} {tr.id}  "{tr.name}"  owner {tr.owner}
          </div>
          <div
            style={{ fontSize: 22 * u, lineHeight: 1.3, padding: `${4 * u}px ${12 * u}px`, background: "rgba(0,0,0,0.6)", overflow: "hidden",
              display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}
          >
            {tr.device}
          </div>
        </div>
      ) : null}
      <Strip frame={frame} t={t} panelId={panel.id} />
    </AbsoluteFill>
  );
};

export const Animatic: React.FC<AnimaticProps> = ({ muteAudio }) => (
  <FilmClockProvider>
    <AbsoluteFill style={{ background: "#000" }}>
      <AudioTrack muted={muteAudio} />
      <AnimaticFrame />
    </AbsoluteFill>
  </FilmClockProvider>
);
