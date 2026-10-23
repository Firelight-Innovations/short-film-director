/**
 * Vendor Google Fonts into assets/fonts/ so a render never needs the network.
 *
 * THIS SCRIPT DOWNLOADS from Google Fonts (the file URLs in @remotion/google-fonts, on
 * Google's servers). Run it only after the user has said yes to downloads (SKILL.md, rule
 * 11); it never asks. A builder does not run it: the builder asks the lead in its log.
 *
 *   node scripts/fetch-fonts.mjs "Family:400,700" ["Other Family:400,400i@serif" ...] [--subset latin]
 *   node scripts/fetch-fonts.mjs            (no families: fetch any file the manifest lists but the disk lacks)
 *
 * Run from the project root. Each argument is a family name as Google Fonts spells it
 * ("IBM Plex Mono"), then the weights after a colon (default 400). A weight ending in
 * "i" is the italic ("400i"). An optional "@sans", "@serif", "@mono" or "@hand" sets the
 * system fallback kind; without it src/kit/fonts.ts guesses from the name.
 *
 * File URLs come from @remotion/google-fonts metadata (installed with the template).
 * Each weight's woff2 for one subset (default latin) lands in
 * assets/fonts/<ImportName>-<style>-<weight>.woff2; a file already there is kept.
 * src/kit/fonts.manifest.json lists the files, one row each, a shape src/kit/fonts.ts
 * reads and a script can loop over (references/02-references.md checks glyphs that way):
 *
 *   [ { "family": "Anton", "style": "normal", "weight": "400", "file": "fonts/Anton-normal-400.woff2", "format": "woff2" } ]
 *
 * "file" is under assets/ (a download is only ever written under assets/fonts/). The
 * manifest is merged, not replaced: other families and weights stay, and a manifest in
 * another shape fonts.ts accepts is read and rewritten as rows. Remove a family by deleting its rows. A family new to the manifest gets a
 * line per file in the rights register through scripts/log-asset.py, when that tool is
 * present.
 *
 * Only one subset is vendored per file, because fonts.ts registers each file without a
 * unicode-range. Latin covers English and most Western European accents; pick
 * latin-ext for Central European text.
 *
 * Exit: 0 when every requested file is on disk; 1 for an unknown family or weight or a
 * failed download; 2 for bad arguments.
 */
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = existsSync(path.join(process.cwd(), "package.json")) ? process.cwd() : path.resolve(here, "..");
const KINDS = new Set(["sans", "serif", "mono", "hand"]);
const MANIFEST = path.join(root, "src", "kit", "fonts.manifest.json");
const FONT_DIR = path.join(root, "assets", "fonts");

function usage(code) {
  console.log(readFileSync(fileURLToPath(import.meta.url), "utf8").split("*/")[0].replace(/^\/\*\*?/, "").replace(/^ \* ?/gm, ""));
  process.exit(code);
}

// ---- arguments --------------------------------------------------------------
const argv = process.argv.slice(2);
let subset = "latin";
const specs = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--help" || a === "-h") usage(0);
  else if (a === "--subset") {
    subset = argv[++i];
    if (!subset) usage(2);
  } else if (a.startsWith("--")) {
    console.error(`unknown option ${a}`);
    process.exit(2);
  } else specs.push(a);
}

function parseSpec(s) {
  let rest = s.trim();
  let kind;
  const at = rest.lastIndexOf("@");
  if (at > 0) {
    kind = rest.slice(at + 1).trim().toLowerCase();
    rest = rest.slice(0, at);
    if (!KINDS.has(kind)) {
      console.error(`"${s}": kind must be one of ${[...KINDS].join(", ")}`);
      process.exit(2);
    }
  }
  const [name, weightList] = rest.split(":");
  const family = name.trim();
  if (!family) {
    console.error(`"${s}": no family name`);
    process.exit(2);
  }
  const want = [];
  for (const w of (weightList ?? "400").split(",").map((x) => x.trim()).filter(Boolean)) {
    const m = /^(\d{3})(i|italic)?$/i.exec(w);
    if (!m) {
      console.error(`"${s}": weight "${w}" should look like 400 or 400i`);
      process.exit(2);
    }
    want.push({ weight: m[1], style: m[2] ? "italic" : "normal" });
  }
  return { family, want, kind };
}

// ---- manifest ---------------------------------------------------------------
/** Read any manifest shape fonts.ts accepts into { Family: [entries] }. */
function readManifest() {
  if (!existsSync(MANIFEST)) return {};
  let m;
  try {
    m = JSON.parse(readFileSync(MANIFEST, "utf8"));
  } catch (e) {
    console.error(`src/kit/fonts.manifest.json is not valid JSON: ${e.message}`);
    process.exit(1);
  }
  const out = {};
  const add = (family, e, kind) => {
    const file = e.file ?? e.path ?? e.url;
    if (!family || !file) return;
    const entry = { style: e.style ?? "normal", weight: String(e.weight ?? "400"), file };
    if (e.format) entry.format = e.format;
    if (e.kind ?? kind) entry.kind = e.kind ?? kind;
    (out[family] ??= []).push(entry);
  };
  const list = Array.isArray(m) ? m : Array.isArray(m?.fonts) ? m.fonts : null;
  if (list) for (const e of list) add(e.family, e);
  else
    for (const [family, block] of Object.entries(m ?? {})) {
      const files = Array.isArray(block) ? block : (block?.files ?? []);
      for (const e of files) add(e.family ?? family, e, Array.isArray(block) ? undefined : block?.kind);
    }
  return out;
}

function writeManifest(m) {
  const sorted = {};
  for (const family of Object.keys(m).sort((a, b) => a.localeCompare(b))) {
    sorted[family] = [...m[family]].sort((a, b) => (a.style === b.style ? Number(a.weight) - Number(b.weight) : a.style === "normal" ? -1 : 1));
  }
  const rows = Object.entries(sorted).flatMap(([family, entries]) => entries.map((e) => ({ family, ...e })));
  const line = (e) => `  { ${Object.entries(e).map(([k, v]) => `${JSON.stringify(k)}: ${JSON.stringify(v)}`).join(", ")} }`;
  const lines = rows.length ? ["[", rows.map(line).join(",\n"), "]"] : ["[]"];
  mkdirSync(path.dirname(MANIFEST), { recursive: true });
  writeFileSync(MANIFEST, lines.join("\n") + "\n");
}

// ---- Google Fonts metadata -------------------------------------------------
const require = createRequire(path.join(root, "package.json"));
let available;
try {
  available = require("@remotion/google-fonts").getAvailableFonts();
} catch {
  console.error("@remotion/google-fonts is not installed in this project. Run: npm install");
  process.exit(1);
}
const squash = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

function lookup(family) {
  const key = squash(family);
  const hit = available.find((f) => squash(f.fontFamily) === key || squash(f.importName) === key);
  if (hit) return hit;
  const near = available.filter((f) => squash(f.fontFamily).includes(key)).slice(0, 8).map((f) => f.fontFamily);
  console.error(`unknown Google Font "${family}".${near.length ? ` Did you mean: ${near.join(", ")}?` : ""}`);
  return null;
}

async function download(url, dest) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  writeFileSync(dest, Buffer.from(await res.arrayBuffer()));
}

const hasFile = (p) => existsSync(p) && statSync(p).size > 0;

// ---- main -------------------------------------------------------------------
mkdirSync(FONT_DIR, { recursive: true });
const manifest = readManifest();
let failed = 0;
let fetched = 0;
let kept = 0;
const newFamilies = [];

if (specs.length === 0) {
  // Re-fetch anything the manifest lists that is missing on disk.
  const fams = Object.keys(manifest);
  if (fams.length === 0) {
    console.log('the manifest is empty. Add a family: node scripts/fetch-fonts.mjs "Family:400,700"');
    process.exit(0);
  }
  for (const family of fams) {
    for (const e of manifest[family]) {
      const dest = path.join(root, "assets", e.file);
      if (hasFile(dest)) {
        kept++;
        continue;
      }
      // The manifest is hand-editable: never write a download outside assets/fonts/.
      if (path.isAbsolute(e.file) || !path.resolve(dest).startsWith(FONT_DIR + path.sep)) {
        console.error(`SKIPPED assets/${e.file} (${family}): a font file must be under assets/fonts/ ("file": "fonts/<name>.woff2")`);
        failed++;
        continue;
      }
      const meta = lookup(family);
      const url = meta && require(`@remotion/google-fonts/${meta.importName}`).getInfo().fonts?.[e.style]?.[e.weight]?.[subset];
      if (!url) {
        console.error(`MISSING assets/${e.file}: no ${subset} file for ${family} ${e.style} ${e.weight}`);
        failed++;
        continue;
      }
      try {
        mkdirSync(path.dirname(dest), { recursive: true });
        await download(url, dest);
        fetched++;
        console.log(`fetched assets/${e.file}`);
      } catch (err) {
        console.error(`FAILED assets/${e.file}: ${err.message}`);
        failed++;
      }
    }
  }
} else {
  for (const s of specs) {
    const { family: asked, want, kind } = parseSpec(s);
    const meta = lookup(asked);
    if (!meta) {
      failed++;
      continue;
    }
    const info = require(`@remotion/google-fonts/${meta.importName}`).getInfo();
    const family = info.fontFamily;
    const wasNew = !manifest[family];
    const entries = manifest[family] ?? [];
    const files = [];
    for (const { weight, style } of want) {
      const url = info.fonts?.[style]?.[weight]?.[subset];
      if (!url) {
        const have = Object.entries(info.fonts ?? {})
          .map(([st, ws]) => `${st}: ${Object.keys(ws).join(",")}`)
          .join("; ");
        const subsets = Object.keys(info.fonts?.[style]?.[weight] ?? {}).join(", ");
        console.error(`MISSING ${family} ${style} ${weight} ${subset}. ${subsets ? `Subsets for that weight: ${subsets}. ` : ""}Available: ${have}`);
        failed++;
        continue;
      }
      const ext = path.extname(new URL(url).pathname) || ".woff2";
      const name = `${meta.importName}-${style}-${weight}${subset === "latin" ? "" : `-${subset}`}${ext}`;
      const dest = path.join(FONT_DIR, name);
      if (hasFile(dest)) kept++;
      else {
        try {
          await download(url, dest);
          fetched++;
          console.log(`fetched assets/fonts/${name}`);
        } catch (err) {
          console.error(`FAILED ${family} ${style} ${weight}: ${err.message}`);
          failed++;
          continue;
        }
      }
      const entry = { style, weight, file: `fonts/${name}`, format: ext === ".woff2" ? "woff2" : ext === ".woff" ? "woff" : ext === ".otf" ? "opentype" : "truetype" };
      if (kind) entry.kind = kind;
      const i = entries.findIndex((e) => e.style === style && e.weight === weight);
      if (i >= 0) entries[i] = { ...entries[i], ...entry };
      else entries.push(entry);
      files.push(`assets/fonts/${name}`);
    }
    if (entries.length) {
      if (kind) for (const e of entries) e.kind = kind;
      manifest[family] = entries;
      if (wasNew && files.length) newFamilies.push({ family, files });
    }
  }
  writeManifest(manifest);
}

// The rights register: one line per family that is new to this film.
const logTool = path.join(root, "scripts", "log-asset.py");
if (newFamilies.length && existsSync(logTool)) {
  const py = ["python", "python3"].find((p) => spawnSync(p, ["--version"], { stdio: "ignore" }).status === 0);
  for (const { family, files } of newFamilies) {
    const spec = `https://fonts.google.com/specimen/${family.replace(/ /g, "+")}`;
    for (const file of files) {
      const line = `${file}: Google Fonts family "${family}", ${spec}, licence OFL-1.1 for most Google Fonts (a few are Apache-2.0 or UFL: confirm on the specimen page), ${subset} subset woff2 vendored by fetch-fonts.mjs`;
      const r = py ? spawnSync(py, [logTool, line], { cwd: root, stdio: "inherit" }) : { status: 1 };
      if (r.status !== 0) console.log(`note: could not log ${file} in docs/rights.md; add it: python scripts/log-asset.py "${line}"`);
    }
  }
}

const families = Object.keys(manifest).length;
const total = Object.values(manifest).reduce((n, e) => n + e.length, 0);
console.log(`${fetched} fetched, ${kept} already on disk, ${failed} failed; manifest: ${families} family(ies), ${total} file(s) -> src/kit/fonts.manifest.json`);
if (fetched) console.log("note: font files are licensed for use in the film; keep assets/fonts/ out of a public repository unless the licence allows redistribution.");
process.exit(failed ? 1 : 0);
