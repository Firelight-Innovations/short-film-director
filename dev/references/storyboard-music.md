# Storyboards, Animatics and Cutting to Music

This digest covers how film and motion-design teams storyboard, previsualise and time a piece to music; how beat and downbeat trackers work, what they get wrong and how to check them; a catalogue of named transitions with notes on code-rendered equivalents; and how timecoded review notes are kept. The short-film-director skill should use the last section as its default rules and checklists, cite the numbered sources when it makes a claim to the user, and treat the W3C and Remotion pages as hard references. Sources marked "read" were fetched in full. The rest were checked only through search excerpts, so their confidence is lower. Vendor and tool-company blogs appear only as practitioner heuristics and are labelled as such.

## Sources

1. **[1] Pixar in a Box: The Art of Storytelling (Lesson 6, Storyboarding)**, Khan Academy with Pixar Animation Studios; course launched 2015; article read: NoFilmSchool, 2017. https://nofilmschool.com/2017/02/pixar-training-next-generation-storytellers-pixar-box
   - A free six-lesson track in which Pixar story artists explain their process in each lesson; the last lesson is storyboarding. The article does not describe the storyboarding lesson's content, so the course itself is the primary source for thumbnails and iteration.
   - Read via article. Confidence: medium

2. **[2] 22 Rules of Storytelling**, Emma Coats (former Pixar story artist), tweets later collated; reposted by Laughing Squid. Tweet date (about 2011) is from memory, not verified here. https://laughingsquid.com/22-rules-of-storytelling-by-pixar-storyboard-artist/
   - Rule 11 says committing ideas to paper makes them fixable; rule 12 says to set aside the first obvious idea; rule 4 is a fill-in skeleton ("Once upon a time..."). Only rules 1 to 15 were visible, and wording differs between reposts.
   - Search excerpt. Confidence: medium

3. **[3] Guide to Completing a Motion Design Project**, School of Motion (motion-design training publisher), n.d. https://schoolofmotion.com/blog/guide-completing-motion-design-project
   - Eight pre-production steps: idea, outline, moodboard, storyboard, style frames, animatic, production boards, feedback. The animatic places boards on a timeline, syncs them to music or voice-over and adds simple motion to key elements, which exposes pacing problems before production. Lock timing in pre-production. If a transition is not clean in final animation, redo the rough animation rather than patch it.
   - Read via fetch. Confidence: high

4. **[4] Previsualization**, Wikipedia, n.d. https://en.wikipedia.org/wiki/Previsualization
   - Storyboarding came first, then Disney's Leica reels (1930s) and advertising animatics (1970s); computer previs appeared around 1988 to 1989. Traditional methods include storyboards, animatics and miniatures; VFX previs makes rough CG versions of effects before shooting. Use this as the terminology anchor: storyboards are static, while animatics and previs add motion and timing.
   - Read via fetch. Confidence: medium

5. **[5] Creating Beatboards for Pre-Production**, Gnomon Workshop blog (the linked course was recorded by a games-studio storyboard artist, per the excerpt), n.d. https://ilm.thegnomonworkshop.com/blog/creating-beatboards-for-pre-production
   - A beatboard is a condensed set of images for the story's key moments, used as a pitch before the production storyboard. The process starts with thumbnails and ends with rendered images. If the pitch is approved, the beatboard becomes the basis of the production storyboard.
   - Search excerpt; course marketing. Confidence: low

6. **[6] Boardomatics 101: Everything You Need to Know**, Storyboard Hero (sells an AI boardomatic tool), n.d. https://storyboardhero.ai/boardomatics-101-everything-you-need-to-know
   - A boardomatic is storyboard frames assembled into a timed video with a soundtrack. This guide allows limited camera animation. Other vendors define it more strictly, as stills with timing and audio and no motion. Uses: test creative options, catch story problems early, align the team on the director's vision.
   - Search excerpt; text cut off. Confidence: low

7. **[7] Boardomatics**, Animatic Media (studio service page), n.d. https://animaticmedia.com/boardomatics
   - A studio pattern worth copying: custom style frames delivered first for client sign-off before boarding starts. The page also states unlimited storyboard-phase revisions and two timing rounds during animation. The commercial terms are the vendor's, not a standard.
   - Search excerpt; vendor. Confidence: low

8. **[8] Temp track**, Wikipedia, n.d. https://en.wikipedia.org/wiki/Temp_track
   - A temp track is placeholder music used during editing to show tempo, mood and atmosphere, and is usually replaced before release. It can help find the musical style and save time, but composers may feel boxed in by it.
   - Read via fetch. Confidence: high

9. **[9] 6 'Rules' for Good Cutting According to Oscar-Winning Editor Walter Murch**, NoFilmSchool, 2016, summarising Walter Murch, *In the Blink of an Eye* (book first published 1992, year from memory). https://nofilmschool.com/2016/11/6-rules-good-cutting-according-oscar-winning-editor-walter-murch
   - The six criteria in priority order: emotion, story, rhythm, eye-trace, two-dimensional plane of screen, three-dimensional space of action. Emotion is weighted at about 51 per cent and outweighs the other five combined. When a cut cannot satisfy all six, give up the lowest first, and spatial continuity goes before emotion. The page gives only the emotion figure. The other weights (story 23, rhythm 10, eye-trace 7, two-dimensional 5, three-dimensional 4) come from secondary excerpts, not the book, which was not read.
   - Read via fetch (emotion weight); other weights from excerpts. Confidence: medium

10. **[10] Edit to the beat in Final Cut Pro (Beat Detection)**, Apple, n.d. https://support.apple.com/guide/final-cut-pro/ver65b55a2b7/mac
    - Beat Detection draws a grid with three levels (song parts, bars, beats) that changes with zoom. The page recommends 4/4 music for the most accurate grid. Edits can be aligned to grid lines, and a song can be shortened by removing sections between song-part markers and closing the gap. This is a good model of how a commercial editor expects structure to be shown.
    - Read via fetch. Confidence: high

11. **[11] How to Edit Music for Video in 2026: Glossary & Workflow**, Foxi Music (stock-music vendor blog), 2026. https://www.foximusic.com/blog/?p=597
    - The cleanest transitions tend to sit on the first beat of a bar. Four bars usually form a phrase, and phrase changes are good places to check cuts. A logo or hit placed exactly on a drum hit reads as deliberate; between beats it reads as accidental. For montages, cut every two or four beats rather than every beat.
    - Search excerpt; vendor heuristics. Confidence: low

12. **[12] Beat Tracking by Dynamic Programming**, Daniel P. W. Ellis, *Journal of New Music Research* 36(1), 2007, DOI 10.1080/09298210701653344. The PDF could not be read through WebFetch; the method and the DOI come from search excerpts and the author's project page.
    - Estimate a global tempo, derive a cost for uneven beat spacing from it, then choose the best-scoring beat sequence by dynamic programming. The reported ability is to follow tempo changes of about plus or minus 10 per cent around the target. The librosa beat tracker is based on this method.
    - Search excerpts. Confidence: medium

13. **[13] librosa.beat.beat_track**, librosa project, docs v0.10.2. https://librosa.org/doc/0.10.2/generated/librosa.beat.beat_track.html
    - Three stages: onset strength, tempo from onset correlation, then peak picking that fits the tempo. It returns one global tempo and beat positions. Parameters: start_bpm (initial guess, 120 per the older docs excerpt), tightness, trim, bpm (fixed tempo, skips estimation), prior (overrides start_bpm), units, sparse. It returns 0 BPM and an empty list when no onset strength is found.
    - Read via fetch. Confidence: high

14. **[14] librosa.segment: Structure and segmentation**, librosa project, dev docs. https://librosa.org/doc/dev/api/segment.html (the gallery example is at https://librosa.org/doc/main/auto_examples/plot_segmentation.html)
    - The module covers self- and cross-similarity matrices and clustering-based segmentation. The gallery example builds a beat-synchronous recurrence matrix, a path matrix from MFCC similarity, an eigenvector structure, and k-means labels. An agglomerative option is listed, but its parameters were not verified.
    - Search excerpt. Confidence: medium

15. **[15] RhythmExtractor2013 (reference)**, Essentia (Music Technology Group, Universitat Pompeu Fabra), docs. https://essentia.upf.edu/reference/std_RhythmExtractor2013.html (tutorial also read: https://essentia.upf.edu/tutorial_rhythm_beatdetection.html)
    - Recommended beat and tempo estimator. The default method is multifeature: slower, more accurate, and it gives a confidence value. Degara is faster and always returns confidence 0. Default tempo search is 40 to 208 BPM (allowed ranges 40 to 180 minimum and 60 to 250 maximum). The reference says the input must be 44,100 Hz. The estimate uses statistics over the whole track, so it is for offline analysis, not real time.
    - Read via fetch. Confidence: high

16. **[16] Joint Beat and Downbeat Tracking with Recurrent Neural Networks**, Böck, Krebs and Widmer, ISMIR 2016. https://archives.ismir.net/ismir2016/paper/000186.pdf (PDF not readable through WebFetch; described through the madmom documentation and search excerpts)
    - An RNN learns beats and downbeats jointly from the spectrogram, without hand-crafted features. Downbeat decoding uses a dynamic Bayesian network (DBN). The method is the basis of madmom's downbeat processors.
    - Search excerpts. Confidence: medium

17. **[17] madmom documentation (v0.16), downbeats module**, madmom project (Böck et al.). https://madmom.readthedocs.io/en/v0.16/modules/features/downbeats.html
    - RNNDownBeatProcessor outputs beat and downbeat activations at 100 frames per second. DBNDownBeatTrackingProcessor decodes them with a default tempo range of 55 to 215 BPM. The lower bound matters for slow film music. The docs excerpt is v0.16; check current docs for newer options.
    - Search excerpt. Confidence: medium

18. **[18] Beat This! Accurate Beat Tracking Without DBN Postprocessing**, Foscarin, Schlüter and Widmer, ISMIR 2024 (arXiv:2407.21658). https://arxiv.org/abs/2407.21658
    - A beat and downbeat tracker that removes DBN postprocessing, because that step constrains meter and tempo. It uses a loss that tolerates small annotation timing shifts and an architecture that alternates convolutions with transformers. The authors report higher F1 than prior work without DBN. They also say it can still fail on difficult or underrepresented genres and does worse on continuity metrics.
    - Read via fetch (abstract). Confidence: high

19. **[19] beat_this (repository)**, CPJKU (Johannes Kepler University Linz), GitHub. https://github.com/CPJKU/beat_this
    - Code and published weights are MIT-licensed, but some training files carry narrower terms, so check before redistribution. Install with pip install beat-this, plus PyTorch 2.0 or later. The CLI and Python API return beat and downbeat times; save_beat_tsv writes a file that imports into Sonic Visualiser. The repo warns that running on training-set files can overstate accuracy. DBN postprocessing is optional and needs madmom.
    - Read via fetch. Confidence: high

20. **[20] mir_eval: beat module**, mir_eval project (Raffel and colleagues), docs. https://mir-eval.readthedocs.io/latest/api/beat.html
    - F-measure counts an estimated beat as correct within a window that defaults to 0.07 s. Other scores: Cemgil, Goto, P-score, and the continuity-based CMLc, CMLt, AMLc, AMLt. The continuity() thresholds (phase and period) default to 0.175, which is the plus-or-minus 17.5 per cent figure some third-party READMEs attach to CMLt. AMLt accepts double-tempo, half-tempo and off-beat readings, so the gap between CMLt and AMLt shows octave and metrical-level errors.
    - Read via fetch. Confidence: high

21. **[21] Evaluating the Online Capabilities of Onset Detection Methods**, Böck, Krebs and Schedl, ISMIR 2012, pp. 49 to 54. https://archives.ismir.net/ismir2012/paper/000049.pdf
    - Many detectors normalise over the whole signal, which rules out live use. A well-tuned online detector can approach offline accuracy on 27,774 annotated onsets. The paper proposes a spectral-flux-based detector with a new peak-picking method that beats traditional methods online and offline. Relevant to choosing hit times for percussive cuts.
    - Search excerpt. Confidence: medium

22. **[22] Sonic Visualiser reference manual (1.3)**, Sonic Visualiser project. https://www.sonicvisualiser.org/doc/reference/1.3/en (current release v5.2, 7 March 2025, per https://en.wikipedia.org/wiki/Sonic_Visualiser)
    - Panes stack layers on a shared time axis. Time-instant layers hold points such as beats, placed by clicking or by key presses during playback. Automatic beat finding comes from third-party Vamp plugins. Use it as the human-verification surface for any tracker's output.
    - Search excerpt; manual is for an older version. Confidence: medium

23. **[23] Match cut**, Wikipedia, n.d. https://en.wikipedia.org/wiki/Match_cut
    - A cut where action, subject or composition lines up across the cut so the two shots feel joined. A graphic match aligns shape, colour or movement and often marks a more conspicuous change. The article is visual-only (no sound matches) and is flagged as needing citations. Examples include the bone-to-satellite cut in *2001: A Space Odyssey*.
    - Read via fetch. Confidence: medium

24. **[24] J cut**, Wikipedia, n.d. https://en.wikipedia.org/wiki/J_cut
    - The sound of the following scene starts before its picture; a form of split edit, also called an audio lead or audio advance. The name comes from the shape the joined audio and video made on analog film. The article does not define the L cut, which search excerpts describe as the reverse: sound carries over from the previous shot.
    - Read via fetch (L-cut from excerpts). Confidence: high

25. **[25] Smash cut**, Wikipedia, n.d. https://en.wikipedia.org/wiki/Smash_cut
    - An abrupt switch to another scene at a point where a cut is not expected, used for shock, humour, or to contrast pace or mood. The article gives no historical origin.
    - Read via fetch. Confidence: high

26. **[26] Whip pan**, Wikipedia, n.d. https://en.wikipedia.org/wiki/Whip_pan
    - A camera pan fast enough to become streaks, used as a transition that masks the cut, and to suggest time passing or frantic action. The article notes its use in 1970s martial-arts films and by directors such as Sam Raimi and Edgar Wright.
    - Read via fetch. Confidence: high

27. **[27] Wipe (transition)**, Wikipedia, n.d. https://en.wikipedia.org/wiki/Wipe_(transition)
    - A moving edge or shape brings in the new shot. Named variants: iris (growing or shrinking circle), star, heart, matrix (patterned), clock (radius sweeping from the centre), invisible (hidden during a camera move), and barn door (edges meeting at the centre). The article is flagged as needing citations. Morph, flash and film burn are not covered here.
    - Read via fetch. Confidence: medium

28. **[28] Transitions (@remotion/transitions)**, Remotion, docs. https://remotion.dev/docs/transitions (presentation names from the presentations page excerpt: https://www.remotion.dev/docs/transitions/presentations)
    - TransitionSeries behaves like Series, with transition slots between sequences. Each transition is a presentation (the visual effect) plus timing. Presentations named in excerpts: fade, slide (four directions), wipe (eight directions), flip, clockWipe, iris; cube is marked paid. Timing presets: linearTiming and springTiming. The package is available from v4.0.53. Whip pan and morph are not among the named presentations; the docs describe custom presentations.
    - Overview read via fetch; presentation list from excerpt. Confidence: medium

29. **[29] Using randomness and random()**, Remotion, docs. https://www.remotion.dev/docs/random
    - random(seed) returns a deterministic value between 0 and 1 for a numeric or string seed. The docs advise against Math.random, because parallel render workers would get different values. random(null) gives a non-reproducible value and is for true randomness only. Give each element its own string seed, for example one built from an index.
    - Read via fetch. Confidence: high

30. **[30] Understanding Success Criterion 2.3.1: Three Flashes or Below Threshold**, W3C Web Accessibility Initiative, WCAG 2.2 understanding document (WCAG 2.2 is a 2023 W3C Recommendation). https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
    - Content passes with no more than three general flashes and/or three red flashes in any one-second period. A general flash is an opposing luminance change of 10 per cent or more of maximum, applying when the darker state is below 0.80 relative luminance. The area alternative allows concurrent flashing covering no more than 0.006 steradians (25 per cent of a 10-degree field). The criterion applies to all page content.
    - Read via fetch. Confidence: high

31. **[31] Anacrusis**, Songtive (music glossary), n.d. https://www.songtive.com/en/glossary/anacrusis
    - One or more notes before the first full bar of a phrase, also called a pickup or upbeat. They lead into the first downbeat and should not be accented themselves. A phrase-level device.
    - Search excerpt; glossary. Confidence: low

32. **[32] otio-cmx3600-adapter**, OpenTimelineIO project (Academy Software Foundation), GitHub. https://github.com/OpenTimelineIO/otio-cmx3600-adapter
    - Reads and writes CMX 3600 EDLs, with Avid (default), Nucoda and Premiere Pro output styles. EDLs carry no frame-rate metadata, so the adapter assumes 24 unless told otherwise. A cut list for this 30 fps timeline should state 30 explicitly.
    - Search excerpt. Confidence: medium

33. **[33] SMPTE timecode**, Wikipedia, n.d. https://en.wikipedia.org/wiki/SMPTE_timecode
    - Drop-frame labelling is for 29.97 fps (the article applies the drop-frame flag to 29.97 and 30 fps rates). It skips label numbers 00 and 01 at the start of each minute except every tenth minute, so labels are dropped, not frames. Non-drop 29.97 labels drift from wall-clock time. For an exact 30 fps timeline, use non-drop labels in HH:MM:SS:FF form.
    - Search excerpt (the article itself was not fully read). Confidence: medium

34. **[34] Add comments on shared projects (Premiere Pro)**, Adobe, help page last updated 14 December 2023. https://helpx.adobe.com/premiere-pro-next/export-and-share/collaborate-with-others/add-comments-on-shared-projects.html
    - Reviewers comment on specific frames, and selecting a comment in the review panel takes the timeline to that frame. Use this as the model for frame-anchored review notes: each note carries a frame, an ID and a status.
    - Search excerpt. Confidence: medium

35. **[35] The Making of Toy Story** (secondary PDF on a university course site; original article and author not verified). https://people.uncw.edu/ricanekk/teaching/spring09/csc100/lectures/pattersone/TheMakingOfToyStory.pdf
    - Storyboard drawings were scanned into an editing system and mixed with temporary dialogue and sound effects to make story reels. Editorial used the reel to check shot lengths and pacing, and the reel was revised repeatedly as material arrived. This is a secondary account, not Pixar's own text.
    - Search excerpt only. Confidence: low

## What This Means for the Skill

- Run pre-production in this order: thumbnails, then a beatboard of stills on the real track, then an animatic with simple motion and scratch voice or effects, then production boards, then the final render. [3][4][5][35]
- Make thumbnails small and cheap, many per beat, and judge framing and sequence before any rendering. Beatboards come after thumbnails and are the pitch stage. Commit each idea to a board so it can be fixed, and set aside the first obvious idea for one more pass. [5][2]
- Get style sign-off before boarding. Deliver one key style frame first, or a small set of options if the look is open; the "three to four options" figure is a vendor rule of thumb, not a verified standard. [7] (synthesis on the count)
- A boardomatic is stills timed to the track with no motion. Use it as the first audition of the rhythm and cut sequence, before any animation is built. [6][7]
- Build the animatic by placing boards on a timeline, syncing them to the music and adding simple motion to key elements. Its job is to show what to speed up or slow down before production. [3]
- After the animatic is approved, treat shot durations as fixed. If a shot grows, log the borrowed time and rebalance the runtime rather than letting the total drift. [3][35]
- Here the licensed track is the final audio, not a temp, so the animatic should use the real track from the first board and never wait for a score. [8] (synthesis)
- Record or place scratch voice before final boards are timed, and review pacing on the animatic rather than the finals: check whether scenes drag, whether a line lands, and whether a shot needs more frames. [35][3]
- Rank cut trade-offs with Murch's order: emotion, story, rhythm, eye-trace, two-dimensional screen plane, three-dimensional space. In a music film, cut on the beat only when emotion and story still hold; when they conflict, give up from the bottom of the list. Treat the percentages as a ranking, not as measurements; only the emotion weight comes from the source page. [9]
- Find the bar grid before cutting. Assume 4/4 unless the downbeat check says otherwise, and zoom out to see song parts. Put section changes on bar downbeats, treat four-bar phrase boundaries as the default section cut points, and cut every two or four beats in montage sections. [10][19][11]
- Plan visual hits, such as a title, logo or flash, to land on a drum hit. A hit between beats reads as an accident. [11]
- For pickups, put the picture change on the downbeat after the lead-in notes, not on the pickup itself. This is synthesis from a glossary entry. [31]
- Run at least two independent trackers, for example librosa and Beat This!, and compare beats and downbeats. Send disagreements to a human listen before any cut is placed. (synthesis) [13][18][19]
- librosa beat_track returns one global tempo. If the measured tempo is known, pass it as bpm. Check that the output is not 0 BPM, which means no onset strength was found. [13]
- Know each tracker's built-in tempo range before trusting it. Essentia RhythmExtractor2013 searches 40 to 208 BPM by default and needs 44.1 kHz input, so resample first and use it offline. The madmom DBN defaults to 55 to 215 BPM, so check slow passages for a doubled tempo. [15][17]
- Beat This! drops the DBN. Its code is MIT-licensed and exports .beats files that open in Sonic Visualiser for listening checks. Read the training-data note before redistributing weights. [18][19][22]
- To evaluate any tracker, hand-mark 20 to 30 seconds of the track and run mir_eval. The F-measure window is 0.07 s. If CMLt is low but AMLt is high, the tracker is making octave or metrical-level errors. [20]
- Treat structure candidates from recurrence or self-similarity analysis as suggestions; verify them by ear and against the measured marks in the timeline. [14]
- Use onset detection with peak picking for hit times on percussive passages, not the beat grid. Check results by listening, since online and offline detectors differ. [21]
- Use a smash cut only at a pivot, such as a hit, a drop or a reveal, as a contrast tool, not as the default cut. [25]
- A match cut aligns a shape, position or movement across the boundary frame. Build it in code by sharing the anchor element between the outgoing and incoming compositions. [23]
- A whip pan is a fast directional move with blur on both sides, matched in direction and speed. Remotion has no named whip presentation, so build it as a custom presentation. Remotion's built-in wipe, iris, clockWipe and slide cover the wipe family; keep each wipe on a beat or measured mark. [26][28][27]
- J and L cuts make sound lead or trail the picture. A single continuous music track does not need them; use them only for voice-over leads. [24]
- Keep flash frames within the three-per-second limit and avoid saturated red fields. Run the flash check on the rendered mp4, not just on the source frames. [30]
- Use random(seed) with a string seed for each element and frame. Never use Math.random in a render. [29]
- Use non-drop 30 fps timecode (HH:MM:SS:FF) on every board, note and cut list; drop-frame labels belong to 29.97 material. State the frame rate explicitly in any EDL export, because the OpenTimelineIO adapter assumes 24 by default. [33][32]
- Record each board panel with: shot ID, in and out frames, action, the exact on-screen words copied from the cue, the transition into the next panel, the sound cue as a mark name or bar and beat, and any camera move. Store review notes the same way, as records with frame number, cue or shot ID, author, text and status, anchored to a frame as Premiere's review panel does [34]. No single source gives the panel field list; it is synthesis.

## Open Questions

- The Pixar in a Box storyboarding lesson was not readable. No primary Pixar account of thumbnails or story reels was read; source 35 is secondary.
- Murch's weights for criteria 2 to 6 come from secondary excerpts. The book and the Film Comment interview were not read.
- No studio-authored account of a Buck or Ordinary Folk board, style-frame or animatic process was found. The only Buck material seen was a session listing with no process detail.
- Film burn and morph transitions have no sourced definition in this digest. The Remotion presentation list came from an excerpt; check the presentation pages before coding these.
- Flash-frame sources were forum and tutorial posts and were dropped. The single-frame flash guidance above is unsourced practice.
- Pickups and anacrusis are covered only by a glossary entry. EDM build-ups and drops have no authoritative source; the drop rules above are unverified.
- The music-video editing sources are vendor blogs. No practitioner interview was retrieved.
- The Ellis 2007 and Böck 2016 PDFs could not be read through WebFetch; their details come from excerpts and secondary docs.
- A madmom failure-mode analysis of a slow-tempo DBN bias exists (title seen in search results), but its authors were not verified and it is not in the source list.
- ITU-R BT.1702-3 (in force, November 2023) was located but not read; its numeric thresholds are not used here. The WCAG figures are the ones used.
- Remotion's Audio component has changed between core (formerly Html5Audio) and @remotion/media across versions; the audio API was not verified and is not in this digest.
- The librosa segment agglomerative parameters and the librosa onset_strength defaults were not verified against current docs.
- Current Frame.io review and export documentation was not retrieved. The Adobe page is the only review-tool source.
- No standard field list for storyboard panel annotations was found. The field list above is synthesis.
- The year of the Emma Coats tweets (about 2011) is from memory and is not verified in this session.
