import { AbsoluteFill } from "remotion";
import { useFilmTime } from "../kit/time";
import { DEV, LETTERBOX_PX, UNIT } from "../style/tokens";
import { F, cuesAt, formatTimecode, sectionAt, transitionAt } from "../timeline/timeline";

/**
 * Check-still aid. Top: the section and any open transition window (id, name,
 * owner, frames). Bottom: the cues that are up, the timecode and the frame.
 * Drawn inside the letterbox bars so it never covers picture; with no bars it
 * sits on thin dark strips at the edges. On in the Studio and check stills, off
 * for the final (data/props.final.json).
 */
export const DevOverlay: React.FC = () => {
  const { frame, t } = useFilmTime();
  const s = sectionAt(t);
  const tr = transitionAt(t);
  const cues = cuesAt(t)
    .map((c) => c.id)
    .join(" + ");

  const h = Math.max(LETTERBOX_PX, Math.round(34 * UNIT));
  const row: React.CSSProperties = {
    position: "absolute",
    left: 0,
    right: 0,
    height: h,
    padding: `0 ${Math.round(40 * UNIT)}px`,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    fontFamily: DEV.font,
    fontSize: DEV.size,
    color: DEV.color,
    letterSpacing: 1,
    whiteSpace: "nowrap",
    overflow: "hidden",
    background: LETTERBOX_PX >= h ? "transparent" : "rgba(0, 0, 0, 0.55)",
    boxSizing: "border-box",
  };
  const win = tr
    ? `TRANSITION ${tr.id} "${tr.name}" owner ${tr.owner}  f${F(tr.at - tr.pre)}-${F(tr.at + tr.post) - 1} cut f${F(tr.at)}`
    : "";

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ ...row, top: 0 }}>
        <span>{s ? `${s.id}  ${s.label}` : "no section"}</span>
        <span style={{ color: DEV.warn }}>{win}</span>
      </div>
      <div style={{ ...row, bottom: 0 }}>
        <span>{cues ? `cue: ${cues}` : ""}</span>
        <span>
          {formatTimecode(t)}  f{frame}
        </span>
      </div>
    </AbsoluteFill>
  );
};
