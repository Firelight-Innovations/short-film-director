# Remotion 4 as a film engine: technical digest

This digest covers Remotion 4 (React and TypeScript, with its bundled FFmpeg) as the render engine for a code-rendered short film: determinism, sequencing and timing, fonts and assets, video and audio, 3D, render options for quality and speed, Windows and GPU pitfalls, cloud rendering, the licence, and code-first alternatives. The short-film-director skill should use the "What this means" section as its default rules: the licence check at intake, the determinism contract and component checks in the build phase, and the encoding and checks in the final phase. Cite entries by number when giving a reason. Pages were read on 2026-10-22. Remotion 5.0 was announced but was not released on that date, so pin a 4.x version. Where two official pages disagree, the entry says so and Open questions lists it. The 35 entries bundle some closely related pages; every URL read is listed.

## Sources

**[1] Remotion License (LICENSE.md)**, Remotion (remotion-dev), n.d. (text as shipped in 4.0.529), https://github.com/remotion-dev/remotion/blob/main/LICENSE.md ; mirror https://cdn.jsdelivr.net/npm/remotion@4.0.529/LICENSE.md
Free use covers individuals, non-profits, evaluators not yet using it commercially, and for-profit organisations "with up to 3 employees". Anyone else must obtain a Company License. Free users may use Remotion commercially, but may not sell or relicense Remotion or a derivative. The file says the licence changes slightly in 5.0. It does not say who owns rendered output.
Confidence: high

**[2] Remotion License FAQ and licence pricing FAQ**, Remotion, n.d., https://www.remotion.dev/docs/license/faq ; https://www.remotion.dev/docs/license-pricing-compliance/faq
Eligibility depends on total company headcount, not seats used. The free tier is up to 3 people. A client that operates or co-develops the project has its headcount added; an agency delivering only a finished file counts only its own staff. Freelancers and other studios working on the project are added to the total. Stated prices: Remotion for Creators $25/month per person who writes Remotion code; Remotion for Automators $0.01 per render with a $100/month minimum; Enterprise minimum spend $500 (the FAQ compares it with $100). No Company License price was found. Creators users keep the right to use videos they made after cancelling. The FAQ says codec patents (H.264/AVC, HEVC, AAC) are the user's responsibility, and gives hi@remotion.dev for clarification.
Confidence: high for eligibility; medium for prices (read through a fetch summary)

**[3] Building with Remotion and AI; Generate Remotion code using LLMs**, Remotion, n.d., https://www.remotion.dev/docs/ai/ ; https://www.remotion.dev/docs/ai/generate
Any doc URL can be read as markdown by adding .md, or by requesting it with an Accept: text/markdown header, which lets coding agents fetch the docs directly. The generation guide advises preferring interpolate() with Easing over spring() unless physics-based motion is requested, keeping components self-contained, and using inline interpolate() in style props. It names no deprecated-API list, and no llms.txt or AGENTS.md was confirmed.
Confidence: high

**[4] remotion-dev/skills and the Remotion Skills page**, Remotion, n.d., https://github.com/remotion-dev/skills ; https://www.remotion.dev/skills
Official Agent Skills, installed with `npx skills add remotion-dev/skills`, for Claude Code, Codex, Kimi Code and Cursor. There are 12 skills: the umbrella /remotion-best-practices, plus /remotion-create, /remotion-markup, /remotion-render, /remotion-studio, /remotion-docs, /remotion-upgrade, /remotion-multimedia, and others for maps, captions, SaaS and interactivity. The SKILL.md bodies were not read. A third-party registry scan (search snippet only) rated a remotion-docs skill as high risk, so review any copy before installing.
Confidence: high for the listing; low for the third-party scan

**[5] random()**, Remotion, n.d., https://www.remotion.dev/docs/random
`random(seed)` returns a deterministic value from 0 to 1 for a given seed. `random(null)` gives a different value each call. Calling `random()` with no argument is an error. Math.random returns different values in each render tab and thread, and the ESLint setup warns on it.
Confidence: high

**[6] Flickering and CSS animations troubleshooting**, Remotion, n.d., https://www.remotion.dev/docs/flickering ; https://www.remotion.dev/docs/troubleshooting/css-animations
Frames render out of order, some more than once, across several browser tabs that share no state. A component must return the same output on every call, must not depend on render order, must not animate while paused, and may use randomness only through random(). CSS transitions, @keyframes and setTimeout break because they cannot know the current frame. Derive all motion from useCurrentFrame(). `--concurrency=1` hides some flicker but is slow and not a guarantee.
Confidence: high

**[7] Sequence, Series and TransitionSeries**, Remotion, n.d., https://www.remotion.dev/docs/sequence ; https://www.remotion.dev/docs/series ; https://www.remotion.dev/docs/transitions/transitionseries
Sequence: children see the composition frame minus `from`, adjusted by trimBefore and playbackRate. premountFor mounts early; the Studio default premount is 2 s from 4.0.535. Series: a negative offset overlaps the previous sequence, and only the last Series.Sequence may use Infinity. TransitionSeries: total length is the scene durations minus the transition durations (40 + 60 - 30 = 70 frames). A transition cannot be longer than an adjacent scene or touch another transition or an overlay. `layout="none"` is deprecated and throws in 5.0. The default presentation is slide(). springTiming with damping 200 is 23 frames at 30 fps.
Confidence: high

**[8] Timing: frames, trimBefore, playbackRate, loop**, Remotion, n.d., https://www.remotion.dev/docs/timing
Child frame = trimBefore + (frame - from) x playbackRate. With loop, the term wraps modulo durationInFrames. Looping needs durationInFrames, except for media with an intrinsic length (Video, Audio, Lottie, Gif, AnimatedImage). The page covers timing props only, not useVideoConfig or seconds conversion.
Confidence: high

**[9] spring() and interpolate()**, Remotion, n.d., https://www.remotion.dev/docs/spring ; https://www.remotion.dev/docs/interpolate
spring defaults: mass 1, damping 10, stiffness 100, overshootClamping false. Raising damping suppresses the bounce. durationInFrames stretches the curve; delay holds the start; reverse plays it backwards. interpolate: extrapolateLeft and extrapolateRight default to 'extend', with 'clamp', 'identity' and 'wrap' as alternatives. easing defaults to linear; a multi-segment range takes an array with one easing per segment.
Confidence: high

**[10] calculateMetadata**, Remotion, n.d., https://www.remotion.dev/docs/calculate-metadata
Returns optional durationInFrames, fps, width, height, props, defaultOutName, defaultCodec, defaultVideoImageFormat, defaultPixelFormat, defaultProResProfile and defaultSampleRate. It runs once at render start, in a separate tab, before rendering. Studio re-runs it on every prop change. Its arguments include isRendering and an abortSignal. The return value must be JSON-serialisable, and it may be async within the delayRender timeout.
Confidence: high

**[11] delayRender() and continueRender()**, Remotion, n.d., https://www.remotion.dev/docs/delay-render
A handle holds the frame open until continueRender() clears it; cancelRender() is for unrecoverable errors. Prefer the useDelayRender() hook. The default timeout is stated as 30 s on this page and on [12], but the sample error text reads 28000 ms. Per-call timeoutInMilliseconds arrived in 4.0.140, and retries defaults to 0. Labels appear in timeout errors. Creating a handle in the component body makes a new one on every re-render, so keep it in useState.
Confidence: high (the 28 s / 30 s mismatch is noted)

**[12] Debugging timeouts**, Remotion, n.d., https://www.remotion.dev/docs/timeout
Causes: a missing continueRender(), blocked network (including cloud VPC rules), high concurrency with Html5Video (Chrome may skip some elements), and large OffthreadVideo files that must download first. The timeout can be raised with the CLI timeout flag, Config.setDelayRenderTimeoutInMilliseconds, the per-call option, or media component props. A delayRender timeout longer than the Lambda function timeout fails with no error.
Confidence: high

**[13] Fonts**, Remotion, n.d., https://www.remotion.dev/docs/fonts
@remotion/google-fonts: loadFont from the font's own path, with style, weights and subsets; it returns fontFamily. Load fonts in one shared module and wait for them before rendering. @remotion/fonts (4.0.164+): loadFont({family, url: staticFile(...), weight}). Google Fonts @import in CSS is waited on automatically since 2.2. A manual FontFace needs delayRender and continueRender, and the error branch must release the handle too. Text inside SVG uses a separate document; from 4.0.525 the font packages keep a registry to mitigate this. The page does not say whether loadFont blocks rendering.
Confidence: medium

**[14] staticFile() and Img**, Remotion, n.d., https://www.remotion.dev/docs/staticfile ; https://www.remotion.dev/docs/img
public/ sits beside package.json, even when the code is in a subfolder. staticFile encodes filenames from v4, so do not pre-encode them. Img wraps a delayRender call, so a slow image cannot leave a flicker frame, which a plain img can. maxRetries defaults to 2 with exponential backoff from 1000 ms; onImageError (4.0.526+) receives the error after retries. Use @remotion/gif for GIFs. A non-empty effects array renders a canvas, which drops native img props such as alt and onLoad.
Confidence: high

**[15] fitText() in @remotion/layout-utils**, Remotion, n.d., https://www.remotion.dev/docs/layout-utils/fit-text
Returns fontSize in pixels for a withinWidth, given the fontFamily, letterSpacing, fontWeight and related styles (4.0.88+). The font must be loaded first. Remotion's default box-sizing is border-box, so borders shrink the box; use outline or subtract the border. validateFontIsLoaded defaults to true in 5.0. measureText was not covered in what was read.
Confidence: medium

**[16] Video tags comparison and OffthreadVideo**, Remotion, n.d., https://www.remotion.dev/docs/video-tags ; https://www.remotion.dev/docs/offthreadvideo
Video from @remotion/media is the recommended component for new code. It uses Mediabunny and WebCodecs, is frame-accurate and fastest, supports partial downloads, requires CORS, may fall back to OffthreadVideo during render, and is the only video option for client-side rendering. Html5Video is not frame-accurate. OffthreadVideo extracts frames with FFmpeg outside the browser; it needs no CORS, has no loop prop (the last frame holds), pauses while buffering only if pauseWhenBuffering is set, and uses acceptableTimeShiftInSeconds (default 0.45) in preview. transparent=true extracts PNG, which is slower.
Confidence: high

**[17] ProRes**, Remotion, n.d., https://www.remotion.dev/docs/prores
Use codec prores (output .mov) for handoff to an editor. Profiles run from proxy and light through standard and hq (the default) to 4444 and 4444-xq. Only 4444 and 4444-xq carry alpha, which needs PNG frames and pixel format yuva444p10le. crf is ignored. Not for web delivery.
Confidence: high

**[18] Audio (the Html5Audio page)**, Remotion, n.d., https://www.remotion.dev/docs/audio
This page documents the older Html5Audio and points new work to Audio from @remotion/media. Core props, which the page describes for the component: volume (a number; iOS Safari forces 1), playbackRate, trimBefore and durationInFrames (both in source frames), loop, and muted, which can change over time. Use interpolate() to compute volume for fades. Preview seeks when drift exceeds 0.45 s. toneFrequency applies only in render.
Confidence: medium (props are described on the older component's page)

**[19] useAudioData and visualizeAudio**, Remotion, n.d., https://www.remotion.dev/docs/use-audio-data ; https://www.remotion.dev/docs/visualize-audio
useAudioData(src, {sampleRate, requestInit}) returns null until loaded and wraps delayRender. sampleRate defaults to 48000. Remote files need CORS. A file with no audio track throws (4.0.75+). visualizeAudio({audioData, frame, fps, numberOfSamples, smoothing, optimizeFor}) returns numbers from 0 to 1, with low indices holding bass. numberOfSamples must be a power of two. smoothing defaults to true. optimizeFor defaults to 'accuracy' and becomes 'speed' in 5.0. If the audio is trimmed or shifted, adjust the frame passed in.
Confidence: high

**[20] @remotion/three and ThreeCanvas**, Remotion, n.d., https://www.remotion.dev/docs/three ; https://www.remotion.dev/docs/three-canvas
ThreeCanvas requires width and height. Animate from useCurrentFrame(), not R3F's useFrame; ThreeCanvas sets frameloop to 'never', so call advance(performance.now()) after asynchronous texture updates. A Sequence inside needs layout="none". The package also provides useVideoTexture and useOffthreadVideoTexture. For renders, use GL angle, set in config and in chromiumOptions.gl for the SSR API.
Confidence: high

**[21] Motion blur**, Remotion, n.d., https://www.remotion.dev/docs/motion-blur
CameraMotionBlur (props shutterAngle and samples) works without HTML-in-canvas. It blends frames, so it can shift colour and opacity. Trail is stylised rather than camera-accurate. The page gives no defaults or cost figures; cost rises with samples (inference).
Confidence: low (only the props named were confirmed)

**[22] renderMedia()**, Remotion, n.d., https://www.remotion.dev/docs/renderer/render-media
Defaults: concurrency is half the CPU threads; timeoutInMilliseconds is 30000; imageFormat is jpeg; jpegQuality follows the browser, currently 80. frameRange takes a number, a [start, end] pair, or ordered non-overlapping ranges (4.0.502+). everyNthFrame works for GIF only. chromiumOptions.gl sets the GL backend. Pass the same inputProps to selectComposition and renderMedia.
Confidence: high

**[23] Encoding guide and the colorSpace option**, Remotion, n.d., https://www.remotion.dev/docs/encoding/ ; https://www.remotion.dev/docs/options/color-space
Codec default is h264; others are h265, vp8, vp9, av1 and prores. CRF defaults: h264 18, h265 23, vp8 9, vp9 28, av1 30. CRF cannot be used with hardware acceleration, where videoBitrate applies. colorSpace values: bt601, bt709 (4.0.28+), bt2020-ncl and bt2020-cl (4.0.88+). Real conversion only happens from 4.0.83. The page recommends png frames alongside it. Its statement on the default conflicts with [31] (see Open questions).
Confidence: high, except the default conflict

**[24] remotion.config.ts and the CLI render command**, Remotion, n.d., https://www.remotion.dev/docs/config ; https://www.remotion.dev/docs/cli/render
Config applies to CLI commands only, not to the SSR API. Defaults: JPEG quality 80; delayRender timeout 30000 ms; video image format jpeg. Methods include setCrf, setCodec, setConcurrency, setChromiumOpenGlRenderer, setPixelFormat and setVideoImageFormat. CLI: --crf cannot be combined with --video-bitrate; --props on Windows must be a file, since inline JSON is not supported there; --frames with a list turns on sequence output; --scale defaults to 1 (maximum 16).
Confidence: high

**[25] GL backends, the WebGL2 context error and the gpu command**, Remotion, n.d., https://www.remotion.dev/docs/gl-options ; https://www.remotion.dev/docs/troubleshooting/webgl2-context ; https://www.remotion.dev/docs/cli/gpu
gl values: null (the 4.0 default; Chrome chooses); angle (a desktop with a GPU, and the default in 5.0 with a SwiftShader fallback); angle-egl (a Linux cloud GPU); swangle (no GPU; default on Lambda and Cloud Run). egl, swiftshader and vulkan are listed without descriptions. The page warns that angle has known memory leaks, and in 4.0 angle fails on GitHub Actions runners, which have no GPU. The "Failed to acquire WebGL2 context" error is fixed by angle. `npx remotion gpu --gl=angle` prints Chrome's GPU feature status; the output is not meant to be parsed.
Confidence: high for the listed values; low for egl and vulkan

**[26] SIGKILL troubleshooting**, Remotion, n.d., https://www.remotion.dev/docs/troubleshooting/sigkill
The OS kills the compositor or FFmpeg, usually from memory use. The frame-extraction cache can grow to 50% of the memory available at render start, and halves under pressure. Fixes: offthreadVideoCacheSizeInBytes; lower concurrency; disallowParallelEncoding, which lowers peak memory at a speed cost; and updating Remotion, since the page says memory management keeps improving (it names 4.0.171).
Confidence: high

**[27] Stuck renders**, Remotion, n.d., https://www.remotion.dev/docs/troubleshooting/stuck-render
Some newer Chrome builds have dropped the headless mode Remotion uses and can stall renders. The fix is Chrome Headless Shell: run `npx remotion browser ensure` before the first render, do not install Chrome from a Linux package manager, and do not set the Chrome executable option; let Remotion fetch a compatible build. An oversized delayRender timeout can hide a hang, so lower it to surface errors.
Confidence: high

**[28] ENAMETOOLONG on Windows**, Remotion, n.d., https://www.remotion.dev/docs/enametoolong
Windows limits a command line to 8192 characters. Many audio layers can produce a longer generated FFmpeg command, and Remotion says it cannot fix this itself. Workarounds: set muted on silent videos; render on macOS, Linux or WSL; or render in parts with --frames and join the parts with an FFmpeg concat.
Confidence: high

**[29] Performance guide**, Remotion, n.d., https://www.remotion.dev/docs/performance
Run `npx remotion benchmark` to choose --concurrency. PNG frames render more slowly than JPEG. --scale lowers the output resolution. GPU-dependent CSS and canvas work (WebGL, 2D canvas, box-shadow, text-shadow, gradients, filter blur) is slow, and cloud instances have no GPU, so pre-render these as images. --log=verbose lists the slowest frames; the first frames on each thread are slow. The page has no memory guidance and no timing figures.
Confidence: high

**[30] Remotion Lambda and server-side rendering**, Remotion, n.d., https://www.remotion.dev/docs/lambda ; https://www.remotion.dev/docs/ssr-node
Lambda splits a render across parallel functions and stitches the parts. Limits stated: the AWS 15-minute function timeout (the page suggests Full HD under about 80 minutes), about 5 GB of output, 10 GB of disk per function, 1,000 concurrent functions per region by default, and no AV1. The page says companies using cloud rendering need a Remotion for Automators licence. SSR is three calls: bundle(), selectComposition() or getCompositions(), then renderMedia(). SSR APIs send telemetry only when licenseKey is set.
Confidence: medium (the licence sentence should be checked against [2])

**[31] Remotion 5.0 migration guide**, Remotion, n.d., https://www.remotion.dev/docs/5-0-migration
The page says Remotion 5.0 is not yet released. The planned breaking changes include: the default colour space becomes bt709 and the "default" option is removed; WebGL and WebGPU are enabled by default in renders; the default GL backend becomes angle with SwANGLE fallback; visualizeAudio defaults to speed; inputProps is required by selectComposition and getCompositions; TransitionSeries drops layout="none"; renderMediaOnLambda overwrites by default; the minimum Node version rises; company licence holders must enable telemetry or arrange render reporting; media components pause while loading or buffering by default.
Confidence: high for the content; status may have changed since the read

**[32] Motion Canvas**, Motion Canvas project, n.d., https://motioncanvas.io/docs/ ; https://motioncanvas.io/docs/rendering
A free and open-source TypeScript library that programs vector animation with generators, with a real-time editor. It is aimed at informative vector animation synced to voice-over, not at general video editing. Rendering exports an image sequence (PNG, JPEG or WebP) to an output folder, with fps, resolution, frame range, background and colour space (sRGB or DCI-P3) as options. FFmpeg is a separate step to make the video.
Confidence: medium

**[33] Revideo**, Revideo (Midrender), n.d., https://midrender.com/revideo
An open-source TypeScript framework for programmatic video, forked from Motion Canvas. It renders headless, with FFmpeg exporters, a Renderer API and a React Player for preview. The upgrade guides run from 0.5.x to 0.10.x, which suggests a pre-1.0 project. The public repository may trail the engine Midrender uses. The page does not name the licence.
Confidence: medium

**[34] FFmpeg filters manual**, FFmpeg project, n.d., https://www.ffmpeg.org/ffmpeg-filters.html
The index confirms the names noise, vignette, eq, curves, colorbalance, lut3d, zoompan, fade, drawtext and loudnorm. The one-line descriptions used in this digest come from general knowledge, not from the page read.
Confidence: high for names; medium for descriptions

**[35] Client-side rendering, and the Remotion 4.0 launch post**, Remotion, n.d., https://www.remotion.dev/docs/client-side-rendering ; Jonny Burger (Remotion), 3 July 2023, https://remotion.dev/blog/4-0
Client-side rendering (@remotion/web-renderer) has been stable since 4.0.491. It uses WebCodecs through Mediabunny, needs Chrome 94+, Firefox 130+ or Safari 26+, and supports a subset of HTML elements. The 4.0 launch post describes a Rust binary, a slim bundled FFmpeg 6.0 build in each project, a Studio "Render" button, and composition props defined as Zod schemas, which makes them type-safe and editable in Studio.
Confidence: medium

## What this means for the skill

1. Pin a 4.x release and record it in the brief. The 5.0 migration changes defaults that alter output (colour space, GL backend, visualizeAudio, Lambda overwrite) [31].
2. Run the licence check at intake. Count everyone who writes, operates or co-develops the project, including freelancers and a client that runs the project. Three or fewer is free; four or more needs a Company License [1][2].
3. Treat 3 as the ceiling for the whole collaborating group. The LICENSE says "up to 3 employees", while the FAQ says "up to 3 people" and adds collaborators [1][2].
4. A client who only receives the finished MP4 does not add headcount [2].
5. Budget paid options with the stated prices: Creators $25/month per writer; Automators $0.01 per render with a $100/month minimum; Enterprise minimum spend $500. Get a Company License quote before promising a figure [2].
6. Ask Remotion in writing (hi@remotion.dev) about rights in rendered output before any commercial release. Neither LICENSE nor the FAQ grants ownership of output [1][2].
7. Note in the final report that codec patent licensing (H.264/AVC, HEVC, AAC) is the user's responsibility [2].
8. Install the official agent skills with `npx skills add remotion-dev/skills`, using /remotion-best-practices as the router. Review SKILL.md files before install [4].
9. Agents can read Remotion docs as markdown by adding .md to a doc URL [3].
10. Write a determinism contract into the build guide. Output is a pure function of frame, props and video config. Randomness comes only from random(seed). No CSS transitions, keyframes, setTimeout or state that depends on render order [5][6].
11. Each section passes four component checks before its frames count as done: same output on repeat calls, no order dependence, no animation while paused, and randomness only through random() [6].
12. Use interpolate() with Easing for ordinary motion. Reserve spring() for physics-led moves, starting from its defaults (mass 1, damping 10, stiffness 100) [3][9].
13. Convert timeline seconds to frames once (frame = round(t x fps)). Use Sequence from and durationInFrames for scenes, trimBefore for cuts into the middle of a clip, and Series for ordered scenes [7][8].
14. Derive durationInFrames, fps, size and props in calculateMetadata from the timeline data. It runs at render start and on every Studio prop change, so use abortSignal when it fetches anything [10].
15. Wrap every async load in delayRender through useDelayRender. Label each handle, set an explicit timeout, and call cancelRender on unrecoverable errors. Never leave a handle open [11][12].
16. Load fonts once in a shared module, with explicit weights and subsets. Wait for them to load before any fitText or measurement [13][15].
17. Put media in public/ and reference it with staticFile(). Use Img rather than a plain img, so each load blocks its frame [14].
18. For video, use Video from @remotion/media in new code and avoid Html5Video. Do not rely on loop with OffthreadVideo; trim explicitly, because the last frame holds [16].
19. Use transparent video only for overlays, since PNG extraction slows renders [16].
20. For waveform-driven visuals, use useAudioData (null until ready; 48 kHz default) and visualizeAudio with a power-of-two numberOfSamples. Set optimizeFor to 'accuracy' on 4.x so output does not change under 5.0 [18][19][31].
21. In 3D scenes, drive animation from useCurrentFrame, pass width and height to ThreeCanvas, and set layout="none" on any Sequence inside it [20].
22. For a graded master: codec h264, CRF 18 (the default) unless tuned, png frames where colour accuracy matters, and colorSpace bt709 set explicitly until the default conflict is resolved [22][23][31].
23. Hardware acceleration disables CRF, so use a video bitrate instead [23][24].
24. For an editor handoff, use ProRes 4444 with png frames and yuva444p10le only when alpha is needed. crf is ignored for ProRes [17].
25. Choose the GL backend by hardware: angle on a GPU desktop (set in config or with --gl), swangle on a machine without a GPU. Check with `npx remotion gpu --gl=angle` [24][25].
26. When SIGKILL appears, cap offthreadVideoCacheSizeInBytes and lower --concurrency. disallowParallelEncoding lowers peak memory at a speed cost [26].
27. Run `npx remotion browser ensure` before the first render and do not pin a Chrome binary. A stalled render usually means a browser mismatch [27].
28. On Windows, keep the generated FFmpeg command under the 8192-character limit: mute silent clips, or render in parts with --frames and concat. Pass --props as a file, not inline JSON [24][28].
29. Choose --concurrency with `npx remotion benchmark`, not by guess. Pre-render shadows, gradients and blur as images for final renders [22][29].
30. Keep the grade and grain as one FFmpeg pass after Remotion's output. The bundled FFmpeg handles encoding, and the filter names are in the manual [34][35].
31. A short film does not need cloud rendering. Lambda's per-function limits and its licence note make it a later option, if local render time becomes the bottleneck [30].
32. Remotion's TransitionSeries length is the sum of scenes minus the transitions. Transitions cannot touch each other or an overlay [7].
33. Client-side rendering is not suitable for the final film. It needs modern browsers and a subset of HTML [35].
34. Motion Canvas and Revideo are code-first alternatives for vector explainer work. Both export image sequences or use FFmpeg as a separate step, so they add a pipeline stage [32][33].

## Open questions

- Remotion 5.0 status: the migration page says it is unreleased; the changelog and npm were not checked against the 2026-10-22 date [31].
- Colour space default: the colorSpace page says "default" is the default from 5.0, but the migration guide says the default becomes bt709 and "default" is removed. Set bt709 explicitly until resolved [23][31].
- delayRender default timeout: 30 s per the prose on [11] and [12], but the sample error text reads 28000 ms [11][12].
- Video tag advice: one search summary said OffthreadVideo is the documented default; the fetched pages recommend Video from @remotion/media. A comparison snippet also called @remotion/media experimental, which the fetched pages did not confirm [16].
- Company License price: not found. The companies terms link redirected to remotion.pro/terms, which was not read [2].
- Whether cloud rendering requires an Automators licence: stated on the Lambda page, not reconciled with the FAQ [30][2].
- Output ownership and codec licensing need a written answer from Remotion [2].
- Whether @remotion/fonts loadFont blocks the render automatically is not stated [13].
- Not verified: measureText, useVideoConfig, the Studio docs page (404), and useWindowedAudioData (search snippet only) [15][19].
- Motion-blur prop defaults and cost are unverified [21].
- The egl and vulkan GL backend descriptions are missing; reports of black frames under ANGLE on Windows came from old sources only, with no official guidance [25].
- Revideo's licence and maturity, and Motion Canvas's rendering internals, were not stated on the pages read [32][33].
- FFmpeg filter descriptions are from general knowledge, not from the page [34].
- Blender was researched, but its manual pages could not be fetched, so its FFmpeg output and bit-depth details are left out.
- The third-party skill security scan is unverified [4].
