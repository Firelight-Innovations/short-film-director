import { AbsoluteFill } from "remotion";
import { LETTERBOX_PX } from "../style/tokens";

/**
 * Two #000 bars of timeline.letterbox x h, top and bottom, above every section.
 * None when letterbox is 0. Sections never draw their own bars.
 */
export const Letterbox: React.FC = () => {
  if (LETTERBOX_PX <= 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: LETTERBOX_PX, background: "#000" }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: LETTERBOX_PX, background: "#000" }} />
    </AbsoluteFill>
  );
};
