/**
 * Test cards: what a section with no component yet looks like, and what the
 * solo harness shows for the neighbours of the section under test.
 *
 * A card is moving and detailed, in the section's own palette and labelled
 * with its label, so a transition that masks, slices or inverts its neighbour
 * has something to act on. It is not what the section will look like. It also
 * draws the title-safe and action-safe boxes and the cues that are up.
 *
 * On frames that timeline.checks says must be black, a card is pure #000 (and
 * FilmStack mounts nothing there anyway), so a film of test cards passes the
 * black check.
 *
 * A card that owns a transition cuts hard at `at`: before it, the outgoing
 * section; from it, the incoming one. So the cut lands where the timeline puts
 * it until the owner's real component lands with its device.
 *
 * Through mode (Solo with `through: true`): a card that owns a transition into
 * or out of the solo section draws that section's live render full-frame for
 * the whole window instead, so the solo section can be checked through a window
 * it does not own. Magenta behind it means "nobody drew this pixel".
 */
import { AbsoluteFill } from "remotion";
import { CANVAS, PALETTE, SAFE, UNIT } from "../style/tokens";
import { cuesAt, formatTimecode, mustBeBlack, renderRange, section, transitionAt } from "../timeline/timeline";
import type { SectionId } from "../timeline/types";
import { SYSTEM_FONTS } from "./fonts";
import type { SectionComponent } from "./section";
import { useFilmTime } from "./time";

const cache = new Map<string, SectionComponent>();

export function makePlaceholder(id: SectionId, throughFor: SectionId | null = null): SectionComponent {
  const key = `${id}|${throughFor ?? ""}`;
  const hit = cache.get(key);
  if (hit) return hit;

  const Card: SectionComponent = ({ from, to, prev, next }) => {
    const { t, frame } = useFilmTime();
    const tr = transitionAt(t);

    const live = prev ?? next;
    if (throughFor && live && tr && (tr.a === throughFor || tr.b === throughFor)) {
      return <AbsoluteFill style={{ background: "#ff00ff" }}>{live}</AbsoluteFill>;
    }
    if (!throughFor && tr) {
      if (prev && t < tr.at) return <AbsoluteFill>{prev}</AbsoluteFill>;
      if (next && t >= tr.at) return <AbsoluteFill>{next}</AbsoluteFill>;
    }
    if (mustBeBlack(frame)) return <AbsoluteFill style={{ background: "#000" }} />;

    const p = PALETTE(id);
    const s = section(id);
    const rr = renderRange(id);
    const local = t - from;
    const sweep = ((local * 120) % 360) - 180;
    const u = UNIT;
    const box = (b: { left: number; top: number; width: number; height: number }, color: string) => (
      <div
        style={{
          position: "absolute",
          left: b.left,
          top: b.top,
          width: b.width,
          height: b.height,
          border: `${Math.max(1, Math.round(2 * u))}px dashed ${color}`,
          boxSizing: "border-box",
        }}
      />
    );
    const owner = tr && tr.owner === id ? tr : null;
    const cues = cuesAt(t);

    return (
      <AbsoluteFill style={{ background: p.bg, overflow: "hidden" }}>
        <AbsoluteFill
          style={{
            backgroundImage: `repeating-linear-gradient(115deg, ${p.shadow}88 0 ${40 * u}px, transparent ${40 * u}px ${120 * u}px)`,
            transform: `translateX(${sweep * u}px) scale(1.4)`,
          }}
        />
        <AbsoluteFill
          style={{
            backgroundImage: `radial-gradient(circle at ${50 + 30 * Math.sin(local * 0.9)}% ${50 + 20 * Math.cos(local * 0.7)}%, ${p.accent}cc 0 9%, transparent 26%), radial-gradient(circle at ${78 - 6 * Math.sin(local * 0.5)}% 32%, ${p.accent2}aa 0 6%, transparent 18%)`,
          }}
        />
        {box(SAFE.action, `${p.ink}44`)}
        {box(SAFE.title, `${p.ink}88`)}
        <div style={{ position: "absolute", left: SAFE.centerX - 30 * u, top: SAFE.centerY, width: 60 * u, height: Math.max(1, 2 * u), background: p.ink }} />
        <div style={{ position: "absolute", left: SAFE.centerX, top: SAFE.centerY - 30 * u, width: Math.max(1, 2 * u), height: 60 * u, background: p.ink }} />
        <div
          style={{
            position: "absolute",
            left: SAFE.title.left + 24 * u,
            right: CANVAS.width - SAFE.title.right + 24 * u,
            top: SAFE.title.top + 20 * u,
            fontFamily: SYSTEM_FONTS.sans,
            fontWeight: 900,
            fontSize: 150 * u,
            lineHeight: 1,
            letterSpacing: -2 * u,
            color: p.ink,
          }}
        >
          {s.label}
        </div>
        <div
          style={{
            position: "absolute",
            left: SAFE.title.left + 28 * u,
            right: CANVAS.width - SAFE.title.right + 28 * u,
            bottom: CANVAS.height - SAFE.title.bottom + 20 * u,
            fontFamily: SYSTEM_FONTS.mono,
            fontSize: 30 * u,
            lineHeight: 1.35,
            color: p.ink,
            whiteSpace: "pre-wrap",
          }}
        >
          {`TEST CARD ${id}  own ${from.toFixed(2)}-${to.toFixed(2)} s  render ${rr.from.toFixed(2)}-${rr.to.toFixed(2)} s\n`}
          {`${s.style}\n`}
          {owner ? `owner of ${owner.id} "${owner.name}" (a test card cuts hard at ${owner.at.toFixed(2)} s)\n` : ""}
          {cues.map((c) => `[${c.id}] ${c.text.replace(/\n/g, " / ")}\n`).join("")}
          {`${formatTimecode(t)}  f${frame}`}
        </div>
      </AbsoluteFill>
    );
  };
  Card.displayName = `TestCard(${id}${throughFor ? `, through ${throughFor}` : ""})`;
  cache.set(key, Card);
  return Card;
}
