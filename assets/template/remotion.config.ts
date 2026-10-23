// Remotion CLI settings (they apply to `remotion studio`, `still` and `render`,
// not to scripts that call @remotion/renderer directly; those pass the same
// values themselves). The grade and the unifying grain are NOT here: they run
// once over the finished render (scripts/grade.py).
import { Config } from "@remotion/cli/config";

Config.setEntryPoint("./src/index.ts");

// JPEG frames are fast. Use --image-format=png on a still when a pixel must be proven.
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setOverwriteOutput(true);

// "angle" on a desktop with a GPU. On a machine without one (CI, cloud) pass
// --gl=swangle on the command line instead.
Config.setChromiumOpenGlRenderer("angle");

// Limited-range BT.709, tagged. Remotion 4's default writes full-range bt470bg,
// which players and the grade read as lifted black (letterbox bars at RGB 16).
Config.setColorSpace("bt709");

// Media and fonts live in ./assets and are referenced with staticFile().
Config.setPublicDir("assets");

Config.setCodec("h264");

// Fonts, plates and WebGL warm-up on a busy machine can take longer than the
// 30 s default; one slow tab must not end a long render.
Config.setDelayRenderTimeoutInMilliseconds(180000);
