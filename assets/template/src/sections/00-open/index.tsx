/**
 * 00-open: the worked example of the section contract. Copy its shape.
 *
 * 1. Words come from the timeline (cuesOf), never typed here.
 * 2. Time is ABSOLUTE film time (useFilmTime), compared with the kit's
 *    frame-snapped times (cue.from, mark(), the transition window), never
 *    with seconds typed into the code.
 * 3. It draws a full, opaque frame for all of renderRange("00-open"), which
 *    runs past its own `to` into the window of the transition it owns.
 * 4. It owns t-00-01 ("Iris"): inside the window it gets 01-turn's live
 *    render as `next` and places it in a circle that opens from the centre.
 * 5. Frame-pure: motion from t and frame only, randomness from rnd(seed).
 */
import { AbsoluteFill } from "remotion";
import { CANVAS, PALETTE, SAFE, SYSTEM_FONTS, UNIT } from "../../kit";
import { beatEnv, cuesOf, ease, envelope, hold, mark, prog, remap, rndRange, transitionOut, useFilmTime } from "../../kit";
import type { Cue, SectionComponent } from "../../kit";

const ID = "00-open";
const P = PALETTE(ID);
// Vendored fonts: node scripts/fetch-fonts.mjs "Family:400,700", then the kit's
// font loader with that family at module top level. A system stack until then.
const TYPE = SYSTEM_FONTS.sans;
// Entrances start this many frames early, so the words are whole on the cue's first frame.
const LEAD = 8;

/** One cue, styled by its role. */
const Words: React.FC<{ c: Cue; t: number; fps: number }> = ({ c, t, fps }) => {
  const lead = LEAD / fps;
  const a = envelope(t, c.from - lead, c.to, lead, 0.3);
  if (a <= 0) return null;
  if (c.role === "stamp") {
    const box = { border: `${2 * UNIT}px solid ${P.accent}`, padding: `${6 * UNIT}px ${14 * UNIT}px` };
    return (
      <div
        style={{ position: "absolute", left: SAFE.title.left, top: SAFE.title.top, opacity: a, ...box,
          fontFamily: SYSTEM_FONTS.mono, fontSize: 34 * UNIT, letterSpacing: 6 * UNIT, color: P.accent }}
      >
        {c.text}
      </div>
    );
  }
  const rise = (1 - prog(t, c.from - lead, c.from, ease.out)) * 24 * UNIT;
  return (
    <div
      style={{ position: "absolute", left: SAFE.title.left, width: SAFE.title.width, top: SAFE.centerY - 45 * UNIT,
        textAlign: "center", opacity: a, transform: `translateY(${rise}px)`, whiteSpace: "pre-line",
        fontFamily: TYPE, fontWeight: 700, fontSize: 72 * UNIT, lineHeight: 1.15, color: P.ink }}
    >
      {c.text}
    </div>
  );
};

export const Section: SectionComponent = ({ from, next }) => {
  const { t, frame, fps } = useFilmTime();

  // The ember drifts in, breathes with the beat (beatEnv is 0 with no track)
  // and swells on the measured hit. It boils on twos: seeded by hold(frame, 2).
  const hit = mark("hit-1");
  const swell = t >= hit ? Math.exp(-(t - hit) * 2) : 0;
  const glow = 0.6 + 0.25 * beatEnv(t) + 0.45 * swell;
  const ex = remap(t, from, from + 6.5, 22, 64, ease.inOut) + rndRange(`ember-x-${hold(frame, 2)}`, -0.25, 0.25);
  const ey = 60 + 3 * Math.sin(t * 0.8) + rndRange(`ember-y-${hold(frame, 2)}`, -0.25, 0.25);
  const push = 1 + 0.035 * prog(t, hit, hit + 4.5, ease.inOut);

  // Iris: the window of the transition out, [at - pre, at + post). `next` is
  // only set inside it. The circle covers the frame before the window ends, so
  // the first frame of 01-turn alone matches the last frame of the window.
  const tr = transitionOut(ID);
  const k = tr && next ? prog(t, tr.at - tr.pre, tr.at + tr.post, ease.inOut) : 0;
  const r = k * 1.12 * Math.hypot(CANVAS.width, CANVAS.height) / 2;

  return (
    <AbsoluteFill style={{ background: P.bg, overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${push})` }}>
        <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 125%, ${P.accent2}66, transparent 62%)` }} />
        <AbsoluteFill
          style={{ background: `radial-gradient(circle at ${ex}% ${ey}%, ${P.accent} 0, ${P.accent}77 ${3 * glow}%, transparent ${16 * glow}%)` }}
        />
        {cuesOf(ID).map((c) => (
          <Words key={c.id} c={c} t={t} fps={fps} />
        ))}
      </AbsoluteFill>
      {next ? (
        <>
          <AbsoluteFill style={{ clipPath: `circle(${r}px at 50% 50%)` }}>{next}</AbsoluteFill>
          <div
            style={{ position: "absolute", left: CANVAS.width / 2 - r, top: CANVAS.height / 2 - r, width: 2 * r, height: 2 * r,
              borderRadius: "50%", border: `${3 * UNIT}px solid ${P.accent}`, boxSizing: "border-box", opacity: 1 - k }}
          />
        </>
      ) : null}
    </AbsoluteFill>
  );
};
