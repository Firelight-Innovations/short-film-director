/**
 * Scaffold a film project from the skill.
 *
 *   node <skill>/scripts/new-film.mjs <dir> [--title T] [--w 1920 --h 1080 --fps 30] [--dur 60]
 *
 * <dir> must not exist or must be empty: a scaffold never writes over work.
 *
 * It copies, from the skill folder:
 *   assets/template/        -> <dir>/            the Remotion starter (src, data, config)
 *   templates/*.md          -> <dir>/docs/       the fill-in documents
 *   templates/CLAUDE.md     -> <dir>/CLAUDE.md   the project brief for every session
 *   scripts/*               -> <dir>/scripts/    every tool except this one and workflows/
 * then:
 *   - replaces __SLUG__ and __TITLE__ in package.json, data/timeline.json, CLAUDE.md
 *     and docs/*.md (the slug is the title in lower case, words joined by "-");
 *   - applies --w --h --fps --dur to data/timeline.json. A new length or frame rate
 *     stretches the example sections, cues, marks and checks to fit and snaps every time
 *     to the new frame grid, so the scaffold passes check-timeline (exit 0) and renders. A
 *     shorter film gives each demo cue back its reading time (0.4 s a word + 0.5 s) where its
 *     section has room; below about 18 s some demo cues stay short, check-timeline.py warns
 *     about them, and the scaffold summary says so. A frame that is not wider than 3:2 gets
 *     no letterbox;
 *   - makes the empty folders of the project layout (docs/concepts, refs/img, ...);
 *   - writes "python3 " for "python " in package.json when only python3 is on PATH;
 *   - runs git init;
 *   - prints the next steps.
 * Without a flag the template's value stays (1920x1080, 30 fps, its example length).
 * Without --title the title is the folder name.
 *
 * Exit: 0 done; 1 the folder is not empty or the skill is incomplete; 2 bad arguments.
 */
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SELF = fileURLToPath(import.meta.url);
const SKILL = path.resolve(path.dirname(SELF), "..");
const TEMPLATE = path.join(SKILL, "assets", "template");
const DOC_TEMPLATES = path.join(SKILL, "templates");
const TOOLS = path.join(SKILL, "scripts");
const NEVER_COPY = new Set(["node_modules", ".git", "out", "__pycache__", ".bundle", ".cache"]);

function usage(code) {
  const text = readFileSync(SELF, "utf8").split("*/")[0].replace(/^\/\*\*?/, "").replace(/^ \* ?/gm, "");
  (code === 0 ? console.log : console.error)(text);
  process.exit(code);
}

function fail(code, msg) {
  console.error(msg);
  process.exit(code);
}

// ---- arguments --------------------------------------------------------------
const argv = process.argv.slice(2);
const opts = {};
const pos = [];
const FLAGS = new Set(["title", "w", "h", "fps", "dur"]);
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--help" || a === "-h") usage(0);
  if (a.startsWith("--")) {
    const [k, inline] = a.slice(2).split(/=(.*)/s);
    if (!FLAGS.has(k)) fail(2, `unknown option --${k}. Run with --help.`);
    const v = inline ?? argv[++i];
    if (v === undefined || (inline === undefined && v.startsWith("--"))) fail(2, `--${k} needs a value`);
    opts[k] = v;
  } else pos.push(a);
}
if (pos.length !== 1) usage(2);

const num = (k, test, what) => {
  if (opts[k] === undefined) return undefined;
  const v = Number(opts[k]);
  if (!Number.isFinite(v) || !test(v)) fail(2, `--${k} ${opts[k]}: must be ${what}`);
  return v;
};
const W = num("w", (v) => Number.isInteger(v) && v >= 16 && v % 2 === 0, "an even whole number of pixels (H.264 needs even sizes)");
const H = num("h", (v) => Number.isInteger(v) && v >= 16 && v % 2 === 0, "an even whole number of pixels (H.264 needs even sizes)");
const FPS = num("fps", (v) => v > 0 && v <= 120, "a frame rate above 0 and at most 120");
const DUR = num("dur", (v) => v > 0 && v <= 3600, "a length in seconds above 0");

const dir = path.resolve(pos[0]);
const folderName = path.basename(dir);
const title = (opts.title ?? folderName.replace(/[-_]+/g, " ").replace(/^\w/, (c) => c.toUpperCase())).trim() || "Untitled film";
const slug =
  title
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60)
    .replace(/-+$/, "") || "untitled-film";

// ---- checks before writing anything ------------------------------------------
if (!existsSync(path.join(TEMPLATE, "package.json"))) fail(1, `the skill has no template at ${TEMPLATE} (assets/template/package.json is missing)`);
if (existsSync(dir)) {
  if (!statSync(dir).isDirectory()) fail(1, `${dir} exists and is a file`);
  const inside = readdirSync(dir);
  if (inside.length) fail(1, `${dir} is not empty (${inside.slice(0, 5).join(", ")}${inside.length > 5 ? ", ..." : ""}). new-film never writes over a folder; pick a new one.`);
}
mkdirSync(dir, { recursive: true });

// ---- copy ---------------------------------------------------------------------
const copyFilter = (src) => !NEVER_COPY.has(path.basename(src)) && !src.endsWith(".pyc");
cpSync(TEMPLATE, dir, { recursive: true, filter: copyFilter });

const docs = path.join(dir, "docs");
mkdirSync(docs, { recursive: true });
let docCount = 0;
if (existsSync(DOC_TEMPLATES)) {
  for (const f of readdirSync(DOC_TEMPLATES)) {
    if (!f.endsWith(".md")) continue;
    cpSync(path.join(DOC_TEMPLATES, f), f === "CLAUDE.md" ? path.join(dir, "CLAUDE.md") : path.join(docs, f));
    docCount++;
  }
} else console.warn(`warning: ${DOC_TEMPLATES} is missing; docs/ starts empty`);

const scriptsOut = path.join(dir, "scripts");
mkdirSync(scriptsOut, { recursive: true });
let toolCount = 0;
for (const f of readdirSync(TOOLS)) {
  if (f === path.basename(SELF) || f === "workflows" || NEVER_COPY.has(f) || f.endsWith(".pyc")) continue;
  cpSync(path.join(TOOLS, f), path.join(scriptsOut, f), { recursive: true, filter: copyFilter });
  toolCount++;
}

// The rest of the project layout. Empty folders git should keep get a .gitkeep.
const keep = ["docs/concepts", "docs/research", "docs/sections", "docs/review", "refs/img", "assets/audio", "assets/fonts", "assets/board", "assets/footage", "assets/tex", "data"];
for (const d of keep) {
  const p = path.join(dir, d);
  mkdirSync(p, { recursive: true });
  if (readdirSync(p).length === 0) writeFileSync(path.join(p, ".gitkeep"), "");
}
for (const d of ["work", "out"]) mkdirSync(path.join(dir, d), { recursive: true });
const refsManifest = path.join(dir, "refs", "manifest.json");
if (!existsSync(refsManifest)) writeFileSync(refsManifest, '{ "refs": [] }\n');

// ---- names ----------------------------------------------------------------------
const jsonText = (s) => JSON.stringify(s).slice(1, -1);
function fill(file, inJson) {
  if (!existsSync(file)) return false;
  const text = readFileSync(file, "utf8");
  const out = text.replaceAll("__SLUG__", slug).replaceAll("__TITLE__", inJson ? jsonText(title) : title);
  if (out !== text) writeFileSync(file, out);
  return true;
}
fill(path.join(dir, "package.json"), true);
fill(path.join(dir, "data", "timeline.json"), true);
fill(path.join(dir, "CLAUDE.md"), false);
for (const f of readdirSync(docs)) if (f.endsWith(".md")) fill(path.join(docs, f), false);

// ---- timeline size, rate and length -----------------------------------------------
const notes = [];
const tlPath = path.join(dir, "data", "timeline.json");
if (existsSync(tlPath)) {
  const tl = JSON.parse(readFileSync(tlPath, "utf8"));
  tl.title = title;
  tl.slug = slug;
  if (W !== undefined || H !== undefined || FPS !== undefined || DUR !== undefined) {
    if (W !== undefined) tl.w = W;
    if (H !== undefined) tl.h = H;
    if ((W !== undefined || H !== undefined) && tl.w / tl.h < 1.5 && tl.letterbox) {
      tl.letterbox = 0;
      notes.push(`letterbox set to 0 for a ${tl.w}x${tl.h} frame (set data/timeline.json "letterbox" to bring bars back)`);
    }
    const oldDur = tl.dur;
    const fps = FPS ?? tl.fps;
    const k = DUR !== undefined ? DUR / oldDur : 1;
    tl.fps = fps;
    tl.dur = DUR ?? oldDur;
    retime(tl, k, fps);
    // The example panels move with the cues they name, so the animatic still matches.
    const sbPath = path.join(dir, "data", "storyboard.json");
    if (existsSync(sbPath)) {
      const sb = JSON.parse(readFileSync(sbPath, "utf8"));
      for (const p of sb.panels ?? []) if (typeof p.at === "number") p.at = Math.round(Math.round(p.at * k * fps) / fps * 10000) / 10000;
      writeFileSync(sbPath, JSON.stringify(sb, null, 2) + "\n");
    }
    if (k !== 1) notes.push(`the example timeline and storyboard were stretched from ${oldDur} s to ${tl.dur} s; replace them at the storyboard`);
    if (k < 1) {
      const short = restoreReading(tl, fps);
      if (short.length) notes.push(`demo cue(s) ${short.join(", ")} are under their reading time at ${tl.dur} s, so check-timeline.py warns about them: expected below about 18 s, and gone when you write your own cues`);
    }
  }
  writeFileSync(tlPath, fmt(tl) + "\n");
}

/** Stretch every time by k and snap it to the frame grid of fps. */
function retime(tl, k, fps) {
  const snap = (t) => Math.round(Math.round(t * k * fps) / fps * 10000) / 10000;
  const span = (t) => (t > 0 ? Math.max(1, Math.round(t * k * fps)) / fps : 0);
  const total = Math.round(tl.dur * fps);
  for (const s of tl.sections ?? []) {
    s.from = snap(s.from);
    s.to = snap(s.to);
  }
  if (tl.sections?.length) tl.sections[tl.sections.length - 1].to = Math.round(total / fps * 10000) / 10000;
  for (const key of Object.keys(tl.marks ?? {})) tl.marks[key] = snap(tl.marks[key]);
  for (const t of tl.transitions ?? []) {
    t.at = snap(t.at);
    t.pre = Math.round(span(t.pre ?? 0) * 10000) / 10000;
    t.post = Math.round(span(t.post ?? 0) * 10000) / 10000;
  }
  for (const c of tl.cues ?? []) {
    c.from = snap(c.from);
    c.to = snap(c.to);
    if (c.shown) {
      c.shown.from = snap(c.shown.from);
      c.shown.to = snap(c.shown.to);
    }
  }
  if (tl.checks?.black) tl.checks.black = tl.checks.black.map(([a, b]) => [snap(a), Math.min(snap(b), tl.dur)]);
  if (tl.grade && typeof tl.grade.until === "number") tl.grade.until = snap(tl.grade.until);
  if (tl.audio && typeof tl.audio.duration === "number" && k !== 1) notes.push("timeline.audio.duration was left as it is: it is the track's length");
}

/**
 * A short --dur squeezes the demo cues under their reading time (0.4 s a word + 0.5 s, at least
 * 5/6 s: check-timeline.py). Give each cue its time back where its section has room: up to 0.1 s
 * before the next cue of the section, the section's outgoing transition window, or the black at
 * the end. Returns the ids that are still short.
 */
function restoreReading(tl, fps) {
  const words = (s) => String(s ?? "").split(/\s+/).filter(Boolean).length;
  const fr = (t) => Math.round(t * fps);
  const gap = Math.max(1, Math.round(0.1 * fps));
  const cues = tl.cues ?? [];
  const still = [];
  for (const c of cues) {
    const n = words(c.text) + (c.role === "data" || c.role === "quote" ? words(c.attribution) : 0);
    if (!n) continue;
    const from = fr(c.from);
    const want = Math.ceil(Math.max(5 / 6, 0.4 * n + 0.5) * fps - 1e-6);
    if (fr(c.to) - from >= want) continue;
    let limit = fr((tl.sections ?? []).find((s) => s.id === c.section)?.to ?? c.to);
    for (const t of tl.transitions ?? []) if (t.a === c.section && fr(t.at - (t.pre ?? 0)) >= fr(c.to)) limit = Math.min(limit, fr(t.at - (t.pre ?? 0)));
    for (const o of cues) if (o !== c && o.section === c.section && fr(o.from) >= fr(c.to)) limit = Math.min(limit, fr(o.from) - gap);
    for (const [b] of tl.checks?.black ?? []) if (fr(b) >= fr(c.to)) limit = Math.min(limit, fr(b));
    const to = Math.min(from + want, Math.max(limit, fr(c.to)));
    c.to = Math.round((to / fps) * 10000) / 10000;
    if (c.shown && fr(c.shown.to) < to) c.shown.to = c.to;
    if (to - from < want) still.push(c.id);
  }
  return still;
}

/** JSON with small objects and arrays on one line, like the template. */
function fmt(v, indent = "", depth = 0) {
  const inline = (x) => {
    if (x === null || typeof x !== "object") return JSON.stringify(x);
    if (Array.isArray(x)) return `[${x.map(inline).join(", ")}]`;
    const parts = Object.entries(x).map(([k, y]) => `${JSON.stringify(k)}: ${inline(y)}`);
    return parts.length ? `{ ${parts.join(", ")} }` : "{}";
  };
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  const one = inline(v);
  if (depth > 0 && indent.length + one.length <= 110 && !(depth === 1 && !Array.isArray(v) && Object.keys(v).length > 4)) return one;
  const inner = indent + "  ";
  if (Array.isArray(v)) return v.length ? `[\n${v.map((x) => inner + fmt(x, inner, depth + 1)).join(",\n")}\n${indent}]` : "[]";
  const entries = Object.entries(v);
  if (!entries.length) return "{}";
  return `{\n${entries.map(([k, x]) => `${inner}${JSON.stringify(k)}: ${fmt(x, inner, depth + 1)}`).join(",\n")}\n${indent}}`;
}

// ---- python or python3 -------------------------------------------------------------
const works = (exe) => {
  const r = spawnSync(exe, ["--version"], { encoding: "utf8" });
  return r.status === 0 && /Python 3/.test(`${r.stdout}${r.stderr}`);
};
let python = "python";
if (!works("python") && works("python3")) {
  python = "python3";
  const pkgPath = path.join(dir, "package.json");
  const pkg = readFileSync(pkgPath, "utf8");
  writeFileSync(pkgPath, pkg.replace(/(["\s&;])python /g, "$1python3 "));
  notes.push('package.json scripts call "python3": only python3 is on PATH here');
} else if (!works("python")) notes.push("no Python 3 found on PATH: the tools in scripts/*.py need Python 3 with numpy, OpenCV, Pillow and librosa");

// ---- path length (Windows) --------------------------------------------------------------
// Remotion's headless Chrome sits about 110 characters below the project path. At 260 or more
// Windows cannot start it and every render fails with a bare ENOENT.
const CHROME_TAIL = 110;
if (process.platform === "win32" && dir.length + CHROME_TAIL > 259) {
  notes.push(`WARNING: this path is ${dir.length} characters; Remotion's headless Chrome needs the project path plus about ${CHROME_TAIL} under 260. Move the folder to a shorter path (for example C:\\films\\${slug}) before npm install`);
}

// ---- git -----------------------------------------------------------------------------
const git = spawnSync("git", ["init", "-q"], { cwd: dir, encoding: "utf8" });
if (git.status === 0) notes.push("git repository initialised (nothing committed yet)");
else notes.push(`git init failed (${(git.stderr || git.error?.message || "git not found").trim()}); run it yourself`);

// ---- report ---------------------------------------------------------------------------
const tl = existsSync(tlPath) ? JSON.parse(readFileSync(tlPath, "utf8")) : {};
const rel = path.relative(process.cwd(), dir) || ".";
console.log(`new film "${title}" (slug ${slug}) in ${dir}`);
console.log(`  ${tl.w}x${tl.h}, ${tl.fps} fps, ${tl.dur} s, ${(tl.sections ?? []).length} example sections`);
console.log(`  template copied; ${docCount} document template(s); ${toolCount} tool(s) in scripts/`);
for (const n of notes) console.log(`  ${n}`);
console.log(`
Next (ask the user before anything is installed or downloaded):
  cd "${rel}"
  npm install                       (downloads Remotion ${pinOf(dir)} and its packages)
  npx remotion browser ensure       (downloads the headless Chrome Remotion renders with)
  ${python} -c "import numpy, scipy, cv2, PIL, librosa"     (the tools need these; matplotlib is optional, for plots; pip install only after a yes)
  copy the track to assets/audio/ and set "audio" in data/timeline.json
  ${python} scripts/analyze_music.py assets/audio/<track>
  npm run check                     (typecheck + check-timeline)
  node scripts/shots.mjs film --all 2 --sheet     (stills of the test-card film; look at the sheet)
  ${python} scripts/doctor.py       (after npm install; it reports the section registry as failing until Phase 4 gives every section a stub: expected)
  npm run studio                    (to watch it)
On Windows keep the project path short (under about 150 characters, such as C:\\films\\<slug>): Remotion's Chrome needs the whole path plus about 110 characters under 260.`);

function pinOf(d) {
  try {
    return JSON.parse(readFileSync(path.join(d, "package.json"), "utf8")).dependencies?.remotion ?? "";
  } catch {
    return "";
  }
}
