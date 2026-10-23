/**
 * Check renders. Bundles once, then renders as many stills as you ask for in one browser.
 *
 *   node scripts/shots.mjs <section-id | film | animatic> [options]
 *
 * Run from the project root. Targets:
 *   <section-id>  composition Solo: that section for real, every other section a test card
 *                 in its palette. Frame numbers are the film's.
 *   film          composition Film: the whole film as registered.
 *   animatic      composition Animatic: the storyboard panels with the real cues.
 *
 * What to render (combine freely; all times are film seconds, all frames film frames):
 *   --t 15.4,16.08          stills at these times
 *   --f 460,461             stills at these frames
 *   --range 24:28.9:0.5     from a to b every step seconds
 *   --seq 15.0:16.2         EVERY frame from a to b (to judge motion)
 *   --all 2                 every N seconds over the target's render range (film and
 *                           animatic: the whole film)
 *   --boundaries            film: frames cut-2..cut+1 of every transition. A section: the
 *                           same around its two edges, plus the first, middle and last
 *                           frame of each transition window it takes part in.
 *
 * Output:
 *   --out dir               default out/check/<target>
 *   --sheet [name]          also a contact sheet <out>/<name>.jpg. --all and --boundaries
 *                           make one by default, named from what was asked (all-2s,
 *                           boundaries, plus -s1 -png -through -bare -clean -<tag> as they
 *                           apply), so two kinds of run never overwrite each other's sheet
 *   --no-sheet              no sheet, even for --all or --boundaries
 *   --cols 6  --tile 480    sheet columns and tile width
 *   --scale 0.5             render scale (0.5 = half size; 1 to judge detail)
 *   --png                   lossless PNG stills (to read exact pixels)
 *   --quality 88            JPEG quality
 *   --clean                 no dev overlay (default: overlay on, drawn in the letterbox bars)
 *   --bare                  picture only: no overlay, no grain, no letterbox
 *   --through               section target only: a test-card neighbour that owns a
 *                           transition with this section draws this section live,
 *                           full-frame, so you can see your frames inside its window
 *   --tag v2                suffix on file names, so a re-render does not overwrite
 *                           (--tag, --bundle and a --sheet name: letters, digits and . _ + -
 *                           only, one name, no slash)
 *
 * Harness:
 *   --bundle name           keep and reuse out/.bundle/<name>: rebuilt only when src/, data/,
 *                           package.json, tsconfig.json or remotion.config.ts changed. Do not
 *                           share a name with a run that may overlap yours. Default: a private
 *                           bundle for this run, deleted at the end. The tool deletes and
 *                           rebuilds this folder, and refuses any path outside out/.bundle.
 *                           When node_modules is a link (a shared one), the webpack cache is
 *                           off so that folder is never written to; a named bundle makes up
 *                           for the slower first bundle.
 *   --timeout 120           seconds per still; a still that takes longer fails and the
 *                           browser is restarted
 *   --gl angle              angle with a GPU; swangle without one
 *   --logs                  print the browser console
 *
 * Speed check:
 *   --bench 71:73 [--concurrency 4]   render that span at full size; prints ms per frame
 *
 * Stills are named f<frame>_t<seconds>.jpg (frame zero-padded to at least 4 digits). The
 * script prints ms per still so you can see what a shot costs.
 * Exit: 0 every still rendered; 1 a still failed or the arguments are wrong.
 */
import { spawnSync } from "node:child_process";
import { randomBytes } from "node:crypto";
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmdirSync, rmSync, statSync, symlinkSync, unlinkSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const SELF = fileURLToPath(import.meta.url);
const root = existsSync(path.join(process.cwd(), "data", "timeline.json")) ? process.cwd() : path.resolve(path.dirname(SELF), "..");
const rel = (p) => path.relative(root, p).replaceAll("\\", "/");

function usage(code) {
  const text = readFileSync(SELF, "utf8").split("*/")[0].replace(/^\/\*\*?/, "").replace(/^ \* ?/gm, "");
  (code === 0 ? console.log : console.error)(text);
  process.exit(code);
}
function die(msg) {
  console.error(msg);
  process.exit(1);
}

// ---- arguments --------------------------------------------------------------
const VALUED = new Set(["t", "f", "range", "seq", "all", "out", "cols", "tile", "scale", "quality", "tag", "bundle", "timeout", "gl", "bench", "concurrency"]);
const BOOL = new Set(["boundaries", "no-sheet", "png", "clean", "bare", "through", "logs", "help"]);
function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) {
      out._.push(a);
      continue;
    }
    const [key, inline] = a.slice(2).split(/=(.*)/s);
    if (key === "sheet") {
      const next = inline ?? argv[i + 1];
      if (inline !== undefined) out.sheet = inline;
      else if (next !== undefined && !next.startsWith("--") && !/^[0-9]{2}-|^(film|animatic)$/.test(next) && out._.length > 0) {
        out.sheet = next;
        i++;
      } else out.sheet = true;
    } else if (BOOL.has(key)) out[key] = true;
    else if (VALUED.has(key)) {
      const v = inline ?? argv[++i];
      if (v === undefined) die(`--${key} needs a value`);
      out[key] = v;
    } else die(`unknown option --${key}. Run with --help.`);
  }
  return out;
}
const args = parseArgs(process.argv.slice(2));
if (args.help) usage(0);
// --bundle, --tag and a --sheet name become folder and file names (and --bundle is deleted and
// rebuilt). One path segment only: a "..", a slash or a drive letter would reach outside out/.
const SAFE_NAME = /^[A-Za-z0-9](?:[A-Za-z0-9._+-]{0,78}[A-Za-z0-9_+-])?$/;
for (const [flag, v] of [["bundle", args.bundle], ["tag", args.tag], ["sheet", typeof args.sheet === "string" ? args.sheet : undefined]]) {
  if (v !== undefined && !SAFE_NAME.test(String(v))) die(`--${flag} ${JSON.stringify(v)}: use letters, digits and . _ + - only (one name, at most 80 characters, no slash)`);
}
const target = args._[0];
if (!target || args._.length > 1) usage(1);

const timeline = JSON.parse(readFileSync(path.join(root, "data", "timeline.json"), "utf8"));
const FPS = timeline.fps;
const TOTAL = Math.round(timeline.dur * FPS);
const F = (s) => Math.round(Number(s) * FPS);
const isFilm = target === "film";
const isAnimatic = target === "animatic";
const sec = timeline.sections.find((s) => s.id === target);
if (!isFilm && !isAnimatic && !sec) die(`unknown target "${target}". Use film, animatic or one of: ${timeline.sections.map((s) => s.id).join(", ")}`);
if (args.through && !sec) die("--through needs a section target (it changes how Solo's test cards draw that section)");
if (isAnimatic && (args.bare || args.through)) die("--bare and --through do not apply to the animatic");

const outDir = path.resolve(root, args.out || path.join("out", "check", target));
const scale = args.scale ? Number(args.scale) : 0.5;
if (!(scale > 0 && scale <= 4)) die(`--scale ${args.scale}: use a number above 0, at most 4`);
const quality = args.quality ? Number(args.quality) : 88;
const timeoutMs = (args.timeout ? Number(args.timeout) : 120) * 1000;
if (!(timeoutMs > 0)) die(`--timeout ${args.timeout}: use seconds above 0`);
// Remotion's own delayRender limit must be at least 7 s; the per-still race below uses yours.
const remotionTimeout = Math.max(7000, timeoutMs);
const tag = args.tag ? `_${args.tag}` : "";
const ext = args.png ? "png" : "jpg";
const gl = args.gl || "angle";

// ---- which frames --------------------------------------------------------------
const frames = new Set();
const clampF = (f) => Math.min(TOTAL - 1, Math.max(0, f));
const addT = (t) => frames.add(clampF(F(t)));
const list = (v) => String(v).split(",").map((x) => x.trim()).filter(Boolean);
const pair = (v, name) => {
  const p = String(v).split(":").map(Number);
  if (p.length < 2 || p.some((x) => !Number.isFinite(x))) die(`--${name} ${v}: use a:b in seconds`);
  return p;
};

function renderRangeOf(s) {
  const snapT = (t) => F(t) / FPS;
  const fr = (tr) => ({ pre: tr ? (F(tr.at) - F(tr.at - (tr.pre ?? 0))) / FPS : 0, post: tr ? (F(tr.at + (tr.post ?? 0)) - F(tr.at)) / FPS : 0 });
  const tin = timeline.transitions.find((x) => x.b === s.id && x.a);
  const tout = timeline.transitions.find((x) => x.a === s.id && x.b);
  return { from: snapT(s.from) - fr(tin).pre, to: snapT(s.to) + fr(tout).post, tin, tout };
}

if (args.t) list(args.t).forEach(addT);
if (args.f) list(args.f).forEach((f) => frames.add(clampF(Math.round(Number(f)))));
if (args.range) {
  const [a, b, step = 0.5] = pair(args.range, "range");
  if (!(step > 0)) die("--range step must be above 0");
  for (let t = a; t <= b + 1e-6; t += step) addT(t);
}
if (args.seq) {
  const [a, b] = pair(args.seq, "seq");
  for (let f = F(a); f <= F(b); f++) frames.add(clampF(f));
}
if (args.boundaries) {
  const around = (f) => [-2, -1, 0, 1].forEach((d) => frames.add(clampF(f + d)));
  if (!sec) {
    for (const tr of timeline.transitions) around(F(tr.at));
  } else {
    const r = renderRangeOf(sec);
    around(F(sec.from));
    around(F(sec.to));
    for (const tr of [r.tin, r.tout].filter(Boolean)) {
      const a = F(tr.at - (tr.pre ?? 0));
      const b = F(tr.at + (tr.post ?? 0)) - 1;
      if (b > a) [a, Math.round((a + b) / 2), b].forEach((f) => frames.add(clampF(f)));
    }
  }
}
if (args.all) {
  const step = Number(args.all);
  if (!(step > 0)) die("--all needs a step in seconds above 0");
  const r = sec ? renderRangeOf(sec) : { from: 0, to: timeline.dur };
  for (let t = r.from; t < r.to - 1e-9; t += step) addT(t);
}
const frameList = [...frames].filter((f) => f >= 0 && f < TOTAL).sort((a, b) => a - b);
if (frameList.length === 0 && !args.bench) die("Nothing to render. Give --t, --f, --range, --seq, --boundaries, --all or --bench.");

const pad = Math.max(4, String(TOTAL - 1).length);
const name = (f) => `f${String(f).padStart(pad, "0")}_t${(f / FPS).toFixed(2).padStart(6, "0")}${tag}.${ext}`;

function defaultSheetName() {
  const kinds = [];
  if (args.all) kinds.push(`all-${args.all}s`);
  if (args.boundaries) kinds.push("boundaries");
  if (args.seq) kinds.push(`seq-${String(args.seq).replace(":", "-")}`);
  if (args.range) kinds.push(`range-${String(args.range).replaceAll(":", "-")}`);
  let n = kinds.join("+") || "sheet";
  if (scale !== 0.5) n += `-s${scale}`;
  if (args.png) n += "-png";
  if (args.through) n += "-through";
  if (args.bare) n += "-bare";
  else if (args.clean) n += "-clean";
  if (args.tag) n += `-${args.tag}`;
  return n;
}
let sheetName = null;
if (!args["no-sheet"]) {
  if (typeof args.sheet === "string") sheetName = args.sheet;
  else if (args.sheet || args.all || args.boundaries) sheetName = defaultSheetName();
}

// ---- Remotion, from the project's own node_modules --------------------------------
const req = createRequire(path.join(root, "package.json"));
async function load(pkg) {
  try {
    return await import(pathToFileURL(req.resolve(pkg)).href);
  } catch (e) {
    die(`cannot load ${pkg} from ${root} (${e.code || e.message}). Run npm install in the project.`);
  }
}
const { bundle } = await load("@remotion/bundler");
const { openBrowser, renderFrames, renderStill, selectComposition } = await load("@remotion/renderer");

// ---- bundle ------------------------------------------------------------------
// bundle() copies the public dir, and ./assets grows to gigabytes. Bundle with an empty
// public dir, then junction ./assets into the bundle. A recursive delete must never walk
// through that junction into ./assets: dropJunction unlinks it first.
function dropJunction(p) {
  let st;
  try {
    st = lstatSync(p);
  } catch {
    return;
  }
  if (st.isSymbolicLink()) {
    try {
      unlinkSync(p);
    } catch {
      rmdirSync(p);
    }
  } else rmSync(p, { recursive: true, force: true });
}
const bundleRoot = path.join(root, "out", ".bundle");
mkdirSync(bundleRoot, { recursive: true });
function removeBundle(dir) {
  // Only ever delete inside out/.bundle, whatever the caller built the path from.
  if (!path.resolve(dir).startsWith(bundleRoot + path.sep)) die(`refusing to delete ${path.resolve(dir)}: it is not inside ${rel(bundleRoot)}`);
  dropJunction(path.join(dir, "public"));
  if (existsSync(path.join(dir, "public"))) return; // never delete through a link we could not drop
  rmSync(dir, { recursive: true, force: true });
}
// Private bundles of runs that died without cleaning up: their process is gone.
for (const d of readdirSync(bundleRoot)) {
  const m = /\.p(\d+)\.[0-9a-f]+$/.exec(d);
  if (!m) continue;
  let alive = true;
  try {
    process.kill(Number(m[1]), 0);
  } catch (e) {
    alive = e.code === "EPERM";
  }
  if (!alive) removeBundle(path.join(bundleRoot, d));
}

const named = typeof args.bundle === "string";
const bundleDir = path.join(bundleRoot, named ? args.bundle : `${target}.p${process.pid}.${randomBytes(3).toString("hex")}`);
const stampFile = `${bundleDir}.stamp.json`;
let emptyPublic = null;
let browser = null;
let cleaned = false;
function cleanup() {
  if (cleaned) return;
  cleaned = true;
  if (!named) removeBundle(bundleDir);
  if (emptyPublic) rmSync(emptyPublic, { recursive: true, force: true });
}
process.on("SIGINT", () => {
  cleanup();
  process.exit(130);
});

/** Path, size and time of every file the bundle is built from. */
function sourceSignature() {
  const parts = [];
  const walk = (d) => {
    if (!existsSync(d)) return;
    for (const e of readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.isFile()) {
        const st = statSync(p);
        parts.push(`${rel(p)}:${st.size}:${Math.round(st.mtimeMs)}`);
      }
    }
  };
  walk(path.join(root, "src"));
  walk(path.join(root, "data"));
  for (const f of ["package.json", "tsconfig.json", "remotion.config.ts"]) {
    const p = path.join(root, f);
    if (existsSync(p)) {
      const st = statSync(p);
      parts.push(`${f}:${st.size}:${Math.round(st.mtimeMs)}`);
    }
  }
  return parts.sort().join("\n");
}

const entry = (() => {
  for (const f of ["entry.ts", "entry.tsx"]) {
    const p = sec ? path.join(root, "src", "sections", target, f) : null;
    if (p && existsSync(p)) return p; // a section's own entry, when it keeps one
  }
  for (const f of ["src/index.ts", "src/index.tsx"]) if (existsSync(path.join(root, f))) return path.join(root, f);
  die("no src/index.ts in the project");
})();
const compId = isAnimatic ? "Animatic" : isFilm ? "Film" : "Solo";

const t0 = performance.now();
const signature = sourceSignature() + `\nentry:${rel(entry)}`;
let reused = false;
if (named && existsSync(path.join(bundleDir, "index.html")) && existsSync(stampFile)) {
  try {
    reused = JSON.parse(readFileSync(stampFile, "utf8")).signature === signature;
  } catch {
    reused = false;
  }
}
let serveUrl = bundleDir;
const modulesLinked = (() => {
  try {
    return lstatSync(path.join(root, "node_modules")).isSymbolicLink();
  } catch {
    return false;
  }
})();
try {
  if (!reused) {
    if (modulesLinked) console.log("node_modules is a link: the webpack cache is off so the shared folder is not written to (reuse a bundle with --bundle <name>)");
    removeBundle(bundleDir);
    emptyPublic = mkdtempSync(path.join(os.tmpdir(), "sfd-empty-public-"));
    serveUrl = await bundle({
      entryPoint: entry,
      outDir: bundleDir,
      publicDir: emptyPublic,
      // Remotion sets the webpack cache itself, after webpackOverride runs, and webpack puts it
      // in node_modules/.cache. A node_modules that is a link (05-build.md section 7 shares one
      // across worktrees) belongs to another tree, so it is never written to: no cache then.
      enableCaching: !modulesLinked,
    });
    const pub = path.join(bundleDir, "public");
    dropJunction(pub);
    mkdirSync(path.join(root, "assets"), { recursive: true });
    symlinkSync(path.join(root, "assets"), pub, "junction");
    if (named) writeFileSync(stampFile, JSON.stringify({ signature }) + "\n");
  }
} catch (err) {
  cleanup();
  die(`bundling failed: ${String(err?.message || err).split("\n").slice(0, 12).join("\n")}`);
}
console.log(`${reused ? "reused bundle" : "bundled"} ${rel(entry)} for ${compId}${sec ? ` (${target}${args.through ? ", through" : ""})` : ""} in ${((performance.now() - t0) / 1000).toFixed(1)} s`);

// ---- render -------------------------------------------------------------------
const inputProps = isAnimatic
  ? { muteAudio: true }
  : {
      showDevOverlay: !args.clean && !args.bare,
      grainStrength: args.bare ? 0 : 1,
      muteAudio: true,
      debugSolo: sec ? target : "",
      bare: Boolean(args.bare),
      through: Boolean(args.through),
    };
const chromiumOptions = { gl };
const onBrowserLog = args.logs ? (l) => console.log(`BROWSER ${l.type}: ${String(l.text).slice(0, 700)}`) : undefined;
let composition;
async function start() {
  browser = await openBrowser("chrome", { chromiumOptions });
  composition = await selectComposition({ serveUrl, id: compId, inputProps, puppeteerInstance: browser, chromiumOptions, timeoutInMilliseconds: Math.max(remotionTimeout, 30000), logLevel: "error" });
}
function withTimeout(promise, ms) {
  let timer;
  return Promise.race([promise, new Promise((_, rej) => (timer = setTimeout(() => rej(new Error(`timed out after ${ms / 1000} s`)), ms)))]).finally(() => clearTimeout(timer));
}

const written = [];
let failed = 0;
try {
  await start();
  if (composition.durationInFrames !== TOTAL) console.warn(`warning: ${compId} is ${composition.durationInFrames} frames, the timeline says ${TOTAL}`);
  if (frameList.length) mkdirSync(outDir, { recursive: true });
  for (const f of frameList) {
    const file = path.join(outDir, name(f));
    const s0 = performance.now();
    try {
      await withTimeout(
        renderStill({
          composition,
          serveUrl,
          frame: f,
          output: file,
          inputProps,
          imageFormat: args.png ? "png" : "jpeg",
          ...(args.png ? {} : { jpegQuality: quality }),
          scale,
          puppeteerInstance: browser,
          chromiumOptions,
          timeoutInMilliseconds: remotionTimeout,
          logLevel: "error",
          onBrowserLog,
        }),
        timeoutMs,
      );
      written.push(file);
      console.log(`${rel(file)}  ${Math.round(performance.now() - s0)} ms`);
    } catch (err) {
      failed++;
      console.error(`FAILED frame ${f} (t=${(f / FPS).toFixed(2)}): ${String(err?.message || err).split("\n").slice(0, 6).join("\n")}`);
      if (/timed out/.test(String(err?.message))) {
        // The tab may be wedged: start a fresh browser for the next still.
        await browser.close({ silent: true }).catch(() => undefined);
        await start();
      }
    }
  }

  if (args.bench) {
    const [a, b] = pair(args.bench, "bench");
    const range = [clampF(F(a)), clampF(F(b) - 1)];
    const concurrency = args.concurrency ? Number(args.concurrency) : 4;
    const benchDir = mkdtempSync(path.join(os.tmpdir(), "sfd-bench-"));
    const b0 = performance.now();
    await renderFrames({
      composition,
      serveUrl,
      inputProps,
      frameRange: range,
      outputDir: benchDir,
      imageFormat: "jpeg",
      concurrency,
      puppeteerInstance: browser,
      chromiumOptions,
      muted: true,
      logLevel: "error",
      timeoutInMilliseconds: remotionTimeout,
      onStart: () => undefined,
      onFrameUpdate: () => undefined,
    });
    const n = range[1] - range[0] + 1;
    const ms = performance.now() - b0;
    console.log(`BENCH ${a}-${b} s: ${n} frames at ${timeline.w}x${timeline.h}, ${concurrency} tabs, ${(ms / 1000).toFixed(1)} s = ${(ms / n).toFixed(0)} ms/frame wall (${((n / ms) * 1000).toFixed(1)} fps)`);
    rmSync(benchDir, { recursive: true, force: true });
  }
} catch (err) {
  failed++;
  console.error(`render failed: ${String(err?.message || err).split("\n").slice(0, 10).join("\n")}`);
} finally {
  if (browser) await browser.close({ silent: true }).catch(() => undefined);
  cleanup();
}

// ---- sheet ----------------------------------------------------------------------
function python() {
  for (const p of ["python", "python3"]) {
    const r = spawnSync(p, ["--version"], { encoding: "utf8" });
    if (r.status === 0 && /Python 3/.test(`${r.stdout}${r.stderr}`)) return p;
  }
  return null;
}
if (sheetName && written.length > 0) {
  const sheet = path.join(outDir, `${sheetName}.jpg`);
  const py = python();
  const tool = path.join(root, "scripts", "sheet.py");
  if (!py) console.error("no Python 3 on PATH: sheet skipped");
  else if (!existsSync(tool)) console.error("scripts/sheet.py is missing: sheet skipped");
  else {
    const res = spawnSync(py, [tool, sheet, "--cols", String(args.cols || 6), "--w", String(args.tile || 480), ...written.map(rel)], { stdio: "inherit", cwd: root });
    if (res.status === 0) console.log(`sheet: ${rel(sheet)}`);
    else {
      console.error(`sheet.py exited with ${res.status}`);
      failed++;
    }
  }
}

if (frameList.length) console.log(`${written.length} stills, ${failed} failed -> ${rel(outDir)}`);
process.exit(failed > 0 ? 1 : 0);
