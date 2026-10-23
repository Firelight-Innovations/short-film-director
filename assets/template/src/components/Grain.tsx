import { AbsoluteFill, Img, random } from "remotion";
import { useFilmTime } from "../kit/time";
import { CANVAS } from "../style/tokens";
import { mustBeBlack } from "../timeline/timeline";

/**
 * Light film-wide grain. One noise tile, made once per browser tab from
 * Remotion's seeded random (so every tab makes the same pixels), laid out as a
 * grid and moved and flipped by a seeded random each frame. Overlay blending
 * leaves mid-grey and pure black untouched, and frames that must be black get
 * no grain at all. Each section brings its own texture; the film's real grain
 * is the grade (scripts/grade.py).
 */
const TILE = 640;
let tileUrl: string | null = null;

function grainTile(): string {
  if (tileUrl) return tileUrl;
  const canvas = document.createElement("canvas");
  canvas.width = TILE;
  canvas.height = TILE;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Grain: no 2D canvas context");
  const img = ctx.createImageData(TILE, TILE);
  for (let i = 0; i < TILE * TILE; i++) {
    // Mean of two uniforms: a soft, roughly bell-shaped grain around mid-grey.
    const v = (random(i + 1) + random(-(i + 1))) / 2;
    const g = Math.max(0, Math.min(255, Math.round(128 + (v - 0.5) * 230)));
    img.data[4 * i] = g;
    img.data[4 * i + 1] = g;
    img.data[4 * i + 2] = g;
    img.data[4 * i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  tileUrl = canvas.toDataURL("image/png");
  return tileUrl;
}

export const Grain: React.FC<{ strength: number }> = ({ strength }) => {
  const { frame } = useFilmTime();
  const opacity = Math.min(0.3, 0.11 * strength);
  if (opacity <= 0.001 || mustBeBlack(frame)) return null;

  const src = grainTile();
  const cols = Math.ceil(CANVAS.width / TILE) + 1;
  const rows = Math.ceil(CANVAS.height / TILE) + 1;
  const dx = Math.floor(random(`grain-x-${frame}`) * TILE);
  const dy = Math.floor(random(`grain-y-${frame}`) * TILE);
  const fx = random(`grain-fx-${frame}`) > 0.5 ? -1 : 1;
  const fy = random(`grain-fy-${frame}`) > 0.5 ? -1 : 1;

  const tiles = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      tiles.push(
        <Img
          key={`${r}-${c}`}
          src={src}
          style={{ position: "absolute", left: c * TILE - dx, top: r * TILE - dy, width: TILE, height: TILE, maxWidth: "none" }}
        />,
      );
    }
  }

  return (
    <AbsoluteFill
      style={{ pointerEvents: "none", overflow: "hidden", mixBlendMode: "overlay", opacity, transform: `scale(${fx}, ${fy})` }}
    >
      {tiles}
    </AbsoluteFill>
  );
};
