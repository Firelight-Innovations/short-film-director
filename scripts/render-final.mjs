/**
 * The final render: composition Film with data/props.final.json, to out/<slug>.mp4.
 *
 *   node scripts/render-final.mjs [--scale s] [--out path] [--frames a-b] [-- <more remotion flags>]
 *   npm run render:final
 *
 * Run from the project root. It runs the project's own Remotion CLI:
 *
 *   remotion render src/index.ts Film out/<slug>.mp4 --codec=h264 --crf=16
 *     --color-space=bt709 --jpeg-quality=95 --props=data/props.final.json
 *
 * and prints that command before it starts. Why each flag:
 *   --crf=16             the master is graded and re-encoded once more (scripts/grade.py),
 *                        so it starts above the delivery quality
 *   --color-space=bt709  Remotion 4's default writes full-range bt470bg, which players and
 *                        the grade read as lifted black (letterbox bars at RGB 16, not 0)
 *   --jpeg-quality=95    frames are JPEG; the default 80 bands dark gradients
 *   --props=<file>       a file, never inline JSON: Windows has no inline --props, and the
 *                        command line there stops at 8192 characters
 * data/props.final.json turns the dev overlay off. The slug comes from data/timeline.json.
 *
 *   --scale 0.25         a quick, small render of the same thing (still to out/<slug>.mp4
 *                        unless --out says otherwise)
 *   --out path           where to write
 *   --frames 0-299       a part of the film, in frames (inclusive)
 *   -- ...               anything after "--" goes to remotion render as it is
 *                        (for example --concurrency=4 or --gl=swangle)
 *
 * Exit: Remotion's exit code (0 when the file was written); 1 when the project is
 * missing a piece; 2 for bad arguments.
 */
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SELF = fileURLToPath(import.meta.url);
const root = existsSync(path.join(process.cwd(), "data", "timeline.json")) ? process.cwd() : path.resolve(path.dirname(SELF), "..");
const relp = (p) => path.relative(root, p).replaceAll("\\", "/");

function usage(code) {
  const text = readFileSync(SELF, "utf8").split("*/")[0].replace(/^\/\*\*?/, "").replace(/^ \* ?/gm, "");
  (code === 0 ? console.log : console.error)(text);
  process.exit(code);
}
const bad = (msg) => {
  console.error(msg);
  process.exit(2);
};

// ---- arguments ----------------------------------------------------------------
const argv = process.argv.slice(2);
const dash = argv.indexOf("--");
const own = dash >= 0 ? argv.slice(0, dash) : argv;
const extra = dash >= 0 ? argv.slice(dash + 1) : [];
const opts = {};
for (let i = 0; i < own.length; i++) {
  const a = own[i];
  if (a === "--help" || a === "-h") usage(0);
  const m = /^--(scale|out|frames)(?:=(.*))?$/s.exec(a);
  if (!m) bad(`unknown argument ${a}. Run with --help.`);
  const v = m[2] ?? own[++i];
  if (v === undefined) bad(`--${m[1]} needs a value`);
  opts[m[1]] = v;
}
if (opts.scale !== undefined && !(Number(opts.scale) > 0 && Number(opts.scale) <= 16)) bad(`--scale ${opts.scale}: use a number above 0, at most 16`);
if (opts.frames !== undefined && !/^\d+(-\d+)?$/.test(opts.frames)) bad(`--frames ${opts.frames}: use a-b in frames, for example 0-299`);

// ---- the project ------------------------------------------------------------------
const fail = (msg) => {
  console.error(msg);
  process.exit(1);
};
const tl = JSON.parse(readFileSync(path.join(root, "data", "timeline.json"), "utf8"));
let slug = typeof tl.slug === "string" && tl.slug && !tl.slug.includes("__") ? tl.slug : "";
if (!slug) {
  try {
    slug = JSON.parse(readFileSync(path.join(root, "package.json"), "utf8")).name || "";
  } catch {
    slug = "";
  }
}
slug = slug.replace(/[^a-zA-Z0-9._-]+/g, "-") || "film";
const props = path.join(root, "data", "props.final.json");
if (!existsSync(props)) fail("data/props.final.json is missing; it must exist and set showDevOverlay to false");
try {
  if (JSON.parse(readFileSync(props, "utf8")).showDevOverlay !== false) console.warn("warning: data/props.final.json does not turn the dev overlay off");
} catch {
  fail("data/props.final.json is not valid JSON");
}
if (opts.frames) {
  const [a, b = a] = opts.frames.split("-").map(Number);
  const total = Math.round(tl.dur * tl.fps);
  if (a > b || b >= total) bad(`--frames ${opts.frames}: the film has frames 0-${total - 1}`);
}

const req = createRequire(path.join(root, "package.json"));
let cli;
try {
  const pkgPath = req.resolve("@remotion/cli/package.json");
  const pkg = JSON.parse(readFileSync(pkgPath, "utf8"));
  const bin = typeof pkg.bin === "string" ? pkg.bin : pkg.bin?.remotion;
  cli = path.join(path.dirname(pkgPath), bin);
} catch {
  fail("cannot find @remotion/cli in this project's node_modules. Run npm install.");
}

const entry = ["src/index.ts", "src/index.tsx"].find((f) => existsSync(path.join(root, f)));
const out = path.resolve(root, opts.out || path.join("out", `${slug}.mp4`));
mkdirSync(path.dirname(out), { recursive: true });

const flags = [
  "--codec=h264",
  "--crf=16",
  "--color-space=bt709",
  "--jpeg-quality=95",
  `--props=${relp(props)}`,
  ...(opts.scale ? [`--scale=${opts.scale}`] : []),
  ...(opts.frames ? [`--frames=${opts.frames}`] : []),
  ...extra,
];
const renderArgs = ["render", ...(entry ? [entry] : []), "Film", relp(out), ...flags];
const quote = (s) => (/[\s"]/.test(s) ? `"${s.replaceAll('"', '\\"')}"` : s);
console.log(`render-final: remotion ${renderArgs.map(quote).join(" ")}`);
const cliShown = relp(cli).startsWith("..") ? cli : relp(cli);
console.log(`  (run as: ${quote(process.execPath)} ${quote(cliShown)} ${renderArgs.map(quote).join(" ")})`);

const t0 = Date.now();
const res = spawnSync(process.execPath, [cli, ...renderArgs], { cwd: root, stdio: "inherit" });
const secs = ((Date.now() - t0) / 1000).toFixed(0);
if (res.error) fail(`could not start the Remotion CLI: ${res.error.message}`);
if (res.status !== 0) {
  console.error(`render-final: remotion exited with ${res.status} after ${secs} s`);
  process.exit(res.status ?? 1);
}
const mb = existsSync(out) ? (statSync(out).size / 1048576).toFixed(1) : "?";
console.log(`render-final: ${relp(out)} (${mb} MiB) in ${secs} s`);
console.log(`next: python scripts/grade.py ${relp(out)} ${relp(out).replace(/\.mp4$/, "")}-graded.mp4`);
