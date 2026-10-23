/**
 * Render frames of the film as plates for a section that reuses the film's own
 * pictures (a recap, a mosaic, a rewind, a montage of everything so far).
 *
 *   node scripts/plates-from-film.mjs <plates.json>
 *
 * Run from the project root. The manifest names each plate by film time (t, seconds)
 * or film frame (f), and the file it goes to:
 *
 *   { "consumer": "06-recap",
 *     "scale": 1,
 *     "plates": [ { "t": 0.9, "file": "footage/06-recap/plates/p00.jpg" },
 *                 { "f": 412, "file": "footage/06-recap/plates/p01.png", "scale": 0.5 } ] }
 *
 * Every plate is a bare still of composition Film (picture only: no letterbox, no grain,
 * no dev overlay), at the plate's scale (default: the manifest's, else 1). A file path is
 * under assets/, as staticFile() reads it; a path that starts with "assets/" is read from
 * the project root instead. A file that would land outside assets/ ("../") is refused. The extension picks the format: .png is lossless, .jpg or
 * .jpeg is JPEG at quality 95.
 *
 * "consumer" (optional) is the section that shows the plates. No plate may fall inside
 * its render range: the section would be rendering itself, from frames it has not made.
 *
 * The stills are rendered with scripts/shots.mjs (one bundle for every group of scale and
 * format) into work/plates-from-film/<manifest name>/, then copied over the listed files,
 * so the consuming section needs no change. Declare it as a chain in data/chains.json, so
 * a change to an earlier section marks the plates stale:
 *   "build": ["node scripts/plates-from-film.mjs data/plates.json", ...the section's own plate builder]
 *
 * Exit: 0 every plate written; 1 a render failed or the manifest is wrong.
 */
import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, rmSync, lstatSync, unlinkSync, rmdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SELF = fileURLToPath(import.meta.url);
const root = existsSync(path.join(process.cwd(), "data", "timeline.json")) ? process.cwd() : path.resolve(path.dirname(SELF), "..");
const rel = (p) => path.relative(root, p).replaceAll("\\", "/");
const die = (msg) => {
  console.error(msg);
  process.exit(1);
};

const argv = process.argv.slice(2);
if (argv.includes("--help") || argv.includes("-h")) {
  console.log(readFileSync(SELF, "utf8").split("*/")[0].replace(/^\/\*\*?/, "").replace(/^ \* ?/gm, ""));
  process.exit(0);
}
if (argv.length !== 1) die("usage: node scripts/plates-from-film.mjs <plates.json>   (--help for the manifest format)");

const manifestPath = path.resolve(root, argv[0]);
if (!existsSync(manifestPath)) die(`no such manifest: ${argv[0]}`);
let manifest;
try {
  manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
} catch (e) {
  die(`${argv[0]} is not valid JSON: ${e.message}`);
}
const tl = JSON.parse(readFileSync(path.join(root, "data", "timeline.json"), "utf8"));
const FPS = tl.fps;
const TOTAL = Math.round(tl.dur * FPS);
const F = (s) => Math.round(s * FPS);

if (!Array.isArray(manifest.plates) || manifest.plates.length === 0) die(`${argv[0]} has no "plates" list`);

// The consumer's render range, in frames [from, to).
let range = null;
if (manifest.consumer) {
  const s = tl.sections.find((x) => x.id === manifest.consumer);
  if (!s) die(`consumer "${manifest.consumer}" is not a section in data/timeline.json`);
  const tin = (tl.transitions ?? []).find((x) => x.b === s.id && x.a);
  const tout = (tl.transitions ?? []).find((x) => x.a === s.id && x.b);
  range = [tin ? F(tin.at - (tin.pre ?? 0)) : F(s.from), tout ? F(tout.at + (tout.post ?? 0)) : F(s.to)];
}

const plates = manifest.plates.map((p, i) => {
  const where = `plates[${i}]`;
  if (typeof p.file !== "string" || !p.file) die(`${where} has no "file"`);
  const frame = p.f !== undefined ? Math.round(Number(p.f)) : p.t !== undefined ? F(Number(p.t)) : NaN;
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL) die(`${where} (${p.file}): give "t" in seconds or "f" in frames inside the film (0 to ${TOTAL - 1})`);
  if (range && frame >= range[0] && frame < range[1]) {
    die(`${where} (${p.file}) is frame ${frame}, inside ${manifest.consumer}'s render range (frames ${range[0]}-${range[1] - 1}): the section would render itself`);
  }
  const ext = path.extname(p.file).toLowerCase();
  if (![".png", ".jpg", ".jpeg"].includes(ext)) die(`${where} (${p.file}): use .png, .jpg or .jpeg`);
  const scale = Number(p.scale ?? manifest.scale ?? 1);
  if (!(scale > 0 && scale <= 4)) die(`${where} (${p.file}): scale ${p.scale} is out of range`);
  if (path.isAbsolute(p.file) || /^[A-Za-z]:/.test(p.file)) die(`${where} (${p.file}): the file is a path under assets/, not an absolute path`);
  const dest = p.file.replaceAll("\\", "/").startsWith("assets/") ? path.join(root, p.file) : path.join(root, "assets", p.file);
  // A plate is only ever written inside assets/ (a "../" in the manifest must not leave it).
  if (!path.resolve(dest).startsWith(path.join(root, "assets") + path.sep)) die(`${where} (${p.file}): the file must stay inside assets/`);
  return { frame, png: ext === ".png", scale, dest, file: p.file };
});

// One shots.mjs run per (scale, format) group, sharing one bundle.
const name = path.basename(manifestPath, path.extname(manifestPath));
const work = path.join(root, "work", "plates-from-film", name);
rmSync(work, { recursive: true, force: true });
mkdirSync(work, { recursive: true });
const bundleName = `plates-${name.replace(/[^A-Za-z0-9_-]+/g, "-").slice(0, 40)}.p${process.pid}`; // shots.mjs accepts letters, digits . _ + - only, 80 characters at most
const groups = new Map();
for (const p of plates) {
  const key = `${p.scale}|${p.png ? "png" : "jpg"}`;
  if (!groups.has(key)) groups.set(key, []);
  groups.get(key).push(p);
}

const pad = Math.max(4, String(TOTAL - 1).length);
const stillName = (f, png) => `f${String(f).padStart(pad, "0")}_t${(f / FPS).toFixed(2).padStart(6, "0")}.${png ? "png" : "jpg"}`;

let failed = false;
let g = 0;
for (const [key, list] of groups) {
  const [scale, fmt] = key.split("|");
  const dir = path.join(work, `g${++g}`);
  const frames = [...new Set(list.map((p) => p.frame))].sort((a, b) => a - b);
  const args = [path.join(root, "scripts", "shots.mjs"), "film", "--bare", "--no-sheet", "--f", frames.join(","), "--scale", scale, "--out", dir, "--bundle", bundleName];
  if (fmt === "png") args.push("--png");
  else args.push("--quality", "95");
  console.log(`rendering ${frames.length} plate frame(s) at scale ${scale} as ${fmt}`);
  const res = spawnSync(process.execPath, args, { stdio: "inherit", cwd: root });
  if (res.status !== 0) {
    console.error(`shots.mjs exited with ${res.status}; the plates of this group were NOT replaced`);
    failed = true;
    continue;
  }
  for (const p of list) {
    const src = path.join(dir, stillName(p.frame, p.png));
    if (!existsSync(src)) {
      console.error(`missing render for ${p.file} (frame ${p.frame})`);
      failed = true;
      continue;
    }
    mkdirSync(path.dirname(p.dest), { recursive: true });
    copyFileSync(src, p.dest);
  }
}

// The shared bundle was named so the groups could reuse it; remove it now.
const bundleDir = path.join(root, "out", ".bundle", bundleName);
try {
  const pub = path.join(bundleDir, "public");
  if (lstatSync(pub).isSymbolicLink()) {
    try {
      unlinkSync(pub);
    } catch {
      rmdirSync(pub);
    }
  }
} catch {
  /* no junction */
}
if (!existsSync(path.join(bundleDir, "public"))) rmSync(bundleDir, { recursive: true, force: true });
rmSync(`${bundleDir}.stamp.json`, { force: true });

if (failed) die("plates-from-film: some plates were not written");
const dirs = [...new Set(plates.map((p) => rel(path.dirname(p.dest))))];
console.log(`${plates.length} plate(s) written to ${dirs.join(", ")}`);
