/**
 * Fonts, vendored into assets/fonts/ by `node scripts/fetch-fonts.mjs
 * "Family:400,700"` and listed in src/kit/fonts.manifest.json, so a render
 * never touches the network.
 *
 *   const DISPLAY = font("Anton");          // at module top level, once
 *   <div style={{ fontFamily: DISPLAY }} />
 *
 * `font()` registers every file of the family the first time it is called and
 * holds the render until they are loaded. It returns a CSS font-family value
 * with a system fallback. A family that is not in the manifest falls back to a
 * system stack with a console warning (`python scripts/doctor.py` reports it):
 * the film still renders, but on a system font that differs between machines.
 */
import { loadFont } from "@remotion/fonts";
import { continueRender, delayRender, staticFile } from "remotion";
import manifest from "./fonts.manifest.json";

/** System stacks: the fallback for every family, and safe for check cards. */
export const SYSTEM_FONTS = {
  sans: "Arial, Helvetica, sans-serif",
  serif: "Georgia, 'Times New Roman', serif",
  mono: "Consolas, 'Courier New', monospace",
  hand: "'Segoe Print', 'Comic Sans MS', cursive",
} as const;
export type FontKind = keyof typeof SYSTEM_FONTS;

type FontFormat = "woff2" | "woff" | "opentype" | "truetype";

interface FontFile {
  family: string;
  style: string;
  weight: string;
  /** Path under assets/ ("fonts/Anton-normal-400.woff2"). */
  file: string;
  format?: FontFormat;
  kind?: FontKind;
}

type Entry = Partial<FontFile> & { url?: string; path?: string };

/**
 * The manifest, whichever of these shapes fetch-fonts wrote:
 *   { "Family": [ { style, weight, file } ] }                (preferred)
 *   { "Family": { kind?, files: [ { style, weight, file } ] } }
 *   { "fonts": [ { family, style, weight, file } ] }  or that array alone
 */
function readManifest(m: unknown): FontFile[] {
  const norm = (e: Entry, family: string, kind?: FontKind): FontFile | null => {
    const file = e.file ?? e.path ?? e.url;
    if (!file) return null;
    return {
      family: e.family ?? family,
      style: e.style ?? "normal",
      weight: String(e.weight ?? "400"),
      file,
      format: e.format,
      kind: e.kind ?? kind,
    };
  };
  const out: FontFile[] = [];
  const list = Array.isArray(m) ? m : Array.isArray((m as { fonts?: unknown })?.fonts) ? (m as { fonts: unknown[] }).fonts : null;
  if (list) {
    for (const e of list as Entry[]) {
      const f = norm(e, e.family ?? "");
      if (f && f.family) out.push(f);
    }
    return out;
  }
  for (const [family, v] of Object.entries((m ?? {}) as Record<string, unknown>)) {
    const block = v as { files?: Entry[]; kind?: FontKind } | Entry[];
    const files = Array.isArray(block) ? block : (block?.files ?? []);
    const kind = Array.isArray(block) ? undefined : block?.kind;
    for (const e of files) {
      const f = norm(e, family, kind);
      if (f) out.push(f);
    }
  }
  return out;
}

const FILES: FontFile[] = readManifest(manifest);

/** A guess at the kind of a family, from its name, for the fallback stack. */
function kindOf(family: string): FontKind {
  const k = FILES.find((f) => f.family === family && f.kind)?.kind;
  if (k) return k;
  if (/mono|code|courier|typewriter|vt323|elite/i.test(family)) return "mono";
  if (/marker|brush|hand|script|caveat|sketch/i.test(family)) return "hand";
  if (/sans|grotesk|gothic/i.test(family)) return "sans";
  if (/serif|garamond|caslon|baskerville|playfair|cormorant|bodoni|didot|fell|times|georgia/i.test(family)) return "serif";
  return "sans";
}

const loaded = new Set<string>();

/** Register a family (idempotent) and return its CSS font-family value. */
export function font(family: string): string {
  const stack = `'${family}', ${SYSTEM_FONTS[kindOf(family)]}`;
  if (loaded.has(family)) return stack;
  loaded.add(family);
  const files = FILES.filter((f) => f.family === family);
  if (files.length === 0) {
    console.warn(`fonts: "${family}" is not in src/kit/fonts.manifest.json; using a system font. Run: node scripts/fetch-fonts.mjs "${family}:400,700"`);
    return stack;
  }
  // A loaded machine (other renders running) can take longer than the default
  // to hand a tab its fonts; a long limit and retries keep one slow tab from
  // ending a long render.
  const handle = delayRender(`font ${family}`, { timeoutInMilliseconds: 180000, retries: 3 });
  Promise.all(
    files.map((f) =>
      loadFont({ family: f.family, url: staticFile(f.file), weight: f.weight, style: f.style, ...(f.format ? { format: f.format } : {}) }),
    ),
  )
    .then(() => continueRender(handle))
    .catch((err) => {
      console.error(`fonts: "${family}" failed to load`, err);
      continueRender(handle);
    });
  return stack;
}

/** Weights vendored for a family ("400", "700"), upright styles only. */
export function weightsOf(family: string): string[] {
  return FILES.filter((f) => f.family === family && f.style === "normal").map((f) => f.weight);
}
