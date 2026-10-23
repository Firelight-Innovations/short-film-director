/**
 * Frame dumps for the boundary reviews, rendered from the integrated film.
 *
 *   node scripts/review-frames.mjs [t-00-01 t-01-02 ...] [--margin 12]   (default: every transition)
 *
 * Run from the project root. For each transition in data/timeline.json it renders the
 * film, clean (no dev overlay), and writes out/review/<transition id>/:
 *
 *   frames/          every frame from <margin> frames before the window to <margin> after
 *                    it, at half size (a hard cut, which has no window: 30 before, 14 after)
 *   sheet-NN.jpg     those frames, 24 to a sheet (6 x 4, 480 px tiles), labelled f<frame>_t<sec>
 *   phone-NN.jpg     the same frames as 360 px tiles: the size an upright phone shows a
 *                    16:9 film. Read every word on these; type that fails here fails the post
 *   full_f....jpg    the frames cut-1, cut and cut+1 at full size
 *   motion.csv/.png  the motion trace of frames/ from scripts/motion-check.py (frame-to-frame
 *                    change: freezes, jumps, one-frame pops), when that tool is present
 *   frames.json      what is where, for the reviewer
 *
 * A transition with no "a" (the film's start) dumps the first 24 frames and full frames 0
 * and 6; one with no "b" (the end) dumps the last 24 and the full frames 16 before the end
 * and the last.
 *
 * The stills come from scripts/shots.mjs, two runs (half and full size) on one shared
 * bundle that is removed at the end.
 * Exit: 0 every dump written (a motion-check finding does not fail it; frames.json and the
 * console say so); 1 a render or a sheet failed, or an id is unknown.
 */
import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, lstatSync, mkdirSync, readFileSync, rmdirSync, rmSync, unlinkSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SELF = fileURLToPath(import.meta.url);
const root = existsSync(path.join(process.cwd(), "data", "timeline.json")) ? process.cwd() : path.resolve(path.dirname(SELF), "..");
const rel = (p) => path.relative(root, p).replaceAll("\\", "/");
const die = (msg) => {
  console.error(msg);
  process.exit(1);
};

// ---- arguments ----------------------------------------------------------------
const argv = process.argv.slice(2);
let margin = 12;
const want = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--help" || a === "-h") {
    console.log(readFileSync(SELF, "utf8").split("*/")[0].replace(/^\/\*\*?/, "").replace(/^ \* ?/gm, ""));
    process.exit(0);
  } else if (a === "--margin") {
    margin = Number(argv[++i]);
    if (!Number.isInteger(margin) || margin < 0) die("--margin needs a whole number of frames");
  } else if (a.startsWith("--")) die(`unknown option ${a}`);
  else want.push(a);
}

const tl = JSON.parse(readFileSync(path.join(root, "data", "timeline.json"), "utf8"));
const FPS = tl.fps;
const TOTAL = Math.round(tl.dur * FPS);
const F = (s) => Math.round(s * FPS);
const clamp = (f) => Math.min(TOTAL - 1, Math.max(0, f));
const pad = Math.max(4, String(TOTAL - 1).length);
const name = (f) => `f${String(f).padStart(pad, "0")}_t${(f / FPS).toFixed(2).padStart(6, "0")}.jpg`;
const range = (a, b) => Array.from({ length: Math.max(0, b - a + 1) }, (_, i) => a + i);

// ---- jobs -----------------------------------------------------------------------
const jobs = [];
for (const tr of tl.transitions ?? []) {
  const base = { id: tr.id, name: tr.name ?? "", a: tr.a ?? null, b: tr.b ?? null, owner: tr.owner ?? null };
  if (!tr.a && !tr.b) continue;
  if (!tr.a || !tr.b) {
    const start = !tr.a;
    jobs.push({
      ...base,
      cut: start ? 0 : TOTAL - 1,
      window: null,
      seq: start ? range(0, Math.min(23, TOTAL - 1)) : range(Math.max(0, TOTAL - 24), TOTAL - 1),
      full: (start ? [0, 6] : [TOTAL - 16, TOTAL - 1]).map(clamp),
    });
    continue;
  }
  const cut = F(tr.at);
  const a = F(tr.at - (tr.pre ?? 0));
  const b = F(tr.at + (tr.post ?? 0)) - 1;
  const hasWindow = b >= a;
  jobs.push({
    ...base,
    cut,
    window: hasWindow ? [a, b] : null,
    seq: range(clamp(hasWindow ? a - margin : cut - 30), clamp(hasWindow ? b + margin : cut + 14)),
    full: [...new Set([cut - 1, cut, cut + 1].map(clamp))],
  });
}
// out/review/<id> is deleted and rebuilt, so an id is one safe path segment (the same form
// check-timeline.py and the review workflow require).
const TID = /^t-[a-z0-9][a-z0-9-]*$/;
const badIds = jobs.filter((j) => typeof j.id !== "string" || !TID.test(j.id)).map((j) => JSON.stringify(j.id));
if (badIds.length) die(`transition id ${badIds.join(", ")} in data/timeline.json: use t- then lower-case letters, digits and hyphens (t-00-01)`);
const todo = want.length ? jobs.filter((j) => want.includes(j.id)) : jobs;
const unknown = want.filter((w) => !jobs.some((j) => j.id === w));
if (unknown.length) die(`no such transition: ${unknown.join(", ")}. Known: ${jobs.map((j) => j.id).join(", ") || "(none)"}`);
if (todo.length === 0) die("the timeline has no transitions to review");

// ---- tools -------------------------------------------------------------------------
const python = ["python", "python3"].find((p) => {
  const r = spawnSync(p, ["--version"], { encoding: "utf8" });
  return r.status === 0 && /Python 3/.test(`${r.stdout}${r.stderr}`);
});
if (!python) die("no Python 3 on PATH (scripts/sheet.py needs it)");
const bundleName = `review.p${process.pid}`;

function shots(frames, scale, out) {
  const res = spawnSync(
    process.execPath,
    [path.join(root, "scripts", "shots.mjs"), "film", "--clean", "--no-sheet", "--bundle", bundleName, "--f", frames.join(","), "--scale", String(scale), "--out", out],
    { stdio: ["ignore", "ignore", "inherit"], cwd: root },
  );
  if (res.status !== 0) {
    cleanupBundle();
    die(`shots.mjs exited with ${res.status} for ${rel(out)}`);
  }
}
function cleanupBundle() {
  const dir = path.join(root, "out", ".bundle", bundleName);
  const pub = path.join(dir, "public");
  try {
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
  if (!existsSync(pub)) rmSync(dir, { recursive: true, force: true });
  rmSync(`${dir}.stamp.json`, { force: true });
}
function sheet(out, files, tile) {
  const res = spawnSync(python, [path.join(root, "scripts", "sheet.py"), out, "--cols", "6", "--w", String(tile), ...files.map(rel)], { stdio: "inherit", cwd: root });
  if (res.status !== 0) die(`sheet.py exited with ${res.status} for ${rel(out)}`);
}

// ---- render: one bundle, one browser per scale, every job at once --------------------
const reviewRoot = path.join(root, "out", "review");
const tmpHalf = path.join(reviewRoot, ".half");
const tmpFull = path.join(reviewRoot, ".full");
for (const d of [tmpHalf, tmpFull]) {
  rmSync(d, { recursive: true, force: true });
  mkdirSync(d, { recursive: true });
}
const t0 = Date.now();
shots([...new Set(todo.flatMap((j) => j.seq))].sort((x, y) => x - y), 0.5, tmpHalf);
shots([...new Set(todo.flatMap((j) => j.full))].sort((x, y) => x - y), 1, tmpFull);
cleanupBundle();
console.log(`rendered in ${((Date.now() - t0) / 1000).toFixed(0)} s`);

// ---- per job: frames, sheets, phone sheets, full frames, motion ------------------------
const motionTool = path.join(root, "scripts", "motion-check.py");
let flagged = 0;

for (const j of todo) {
  const dir = path.join(reviewRoot, j.id);
  if (!path.resolve(dir).startsWith(reviewRoot + path.sep)) die(`refusing to delete ${path.resolve(dir)}: it is not inside ${rel(reviewRoot)}`);
  rmSync(dir, { recursive: true, force: true });
  const framesDir = path.join(dir, "frames");
  mkdirSync(framesDir, { recursive: true });
  const files = [];
  for (const f of j.seq) {
    const src = path.join(tmpHalf, name(f));
    if (!existsSync(src)) die(`missing render of frame ${f}`);
    const dst = path.join(framesDir, name(f));
    copyFileSync(src, dst);
    files.push(dst);
  }
  const sheets = [];
  const phone = [];
  for (let i = 0; i < files.length; i += 24) {
    const part = files.slice(i, i + 24);
    const k = String(sheets.length + 1).padStart(2, "0");
    const span = [j.seq[i], j.seq[Math.min(i + 23, j.seq.length - 1)]];
    const s = path.join(dir, `sheet-${k}.jpg`);
    sheet(s, part, 480);
    sheets.push({ file: rel(s), frames: span });
    const p = path.join(dir, `phone-${k}.jpg`);
    sheet(p, part, 360);
    phone.push({ file: rel(p), frames: span, tile: 360 });
  }
  const full = [];
  for (const f of j.full) {
    const src = path.join(tmpFull, name(f));
    if (!existsSync(src)) continue;
    const dst = path.join(dir, `full_${name(f)}`);
    copyFileSync(src, dst);
    full.push({ file: rel(dst), frame: f });
  }

  let motion = null;
  if (existsSync(motionTool)) {
    // motion-check names its files after the folder ("frames"): write them aside, then rename.
    const tmp = path.join(dir, ".motion");
    const res = spawnSync(python, [motionTool, rel(framesDir), "--out", rel(tmp)], { cwd: root, encoding: "utf8" });
    const lines = (res.stdout || "")
      .split(/\r?\n/)
      .map((l) => l.trim().replaceAll(`${rel(tmp)}/frames`, `${rel(dir)}/motion`))
      .filter(Boolean);
    motion = { exit: res.status, csv: null, png: null, summary: lines.slice(-6) };
    for (const [key, extName] of [["csv", ".csv"], ["png", ".png"]]) {
      const src = path.join(tmp, `frames${extName}`);
      if (existsSync(src)) {
        const dst = path.join(dir, `motion${extName}`);
        copyFileSync(src, dst);
        motion[key] = rel(dst);
      }
    }
    rmSync(tmp, { recursive: true, force: true });
    if (res.status === 3) flagged++;
    else if (res.status !== 0) console.error(`${j.id}: motion-check.py exited with ${res.status}: ${(res.stderr || "").trim().split("\n").slice(-3).join(" | ")}`);
  }

  writeFileSync(
    path.join(dir, "frames.json"),
    JSON.stringify(
      {
        id: j.id, name: j.name, a: j.a, b: j.b, owner: j.owner, fps: FPS, cut: j.cut, window: j.window,
        seq: [j.seq[0], j.seq[j.seq.length - 1]], frames: rel(framesDir), sheets, phone, full, motion,
      },
      null,
      2,
    ) + "\n",
  );
  const m = motion ? (motion.exit === 3 ? ", motion-check FLAGGED (see motion.png)" : motion.exit === 0 ? ", motion ok" : `, motion-check exit ${motion.exit}`) : ", no motion-check.py";
  console.log(`${j.id}: ${j.seq.length} frames on ${sheets.length} sheet(s) + ${phone.length} phone sheet(s), ${full.length} full-size${m} -> ${rel(dir)}`);
}
rmSync(tmpHalf, { recursive: true, force: true });
rmSync(tmpFull, { recursive: true, force: true });
if (flagged) console.log(`${flagged} window(s) with motion-check findings: look at their motion.png and frames`);
