# Sourcing, licensing and photosensitivity safety for a short film

This digest covers where a directed short film can legally get pictures, footage, fonts and music; what the stock, archive and music licences allow and forbid for a brand or essay film on LinkedIn, YouTube, Meta and TikTok; how fair use, likeness and trademarks limit what the film may show; the disclosure rules for AI-made or synthetic footage; and the photosensitive-epilepsy limits for flashing and patterned images, with exact numbers. The skill should use it in two places. In the references phase, the sourcing rules decide which assets are allowed and what each one must log in the footage log and the credits card. In the storyboard and review phases, the flash, pattern, caption and disclosure rules are the pass/fail checks. Research was done on 2026-10-22. Where a live page could not be read (HTTP 403 or 429, or a connection error), the entry says so and rests on search summaries; those are marked medium or low confidence. Read the primary text again before any public release.

## Sources

**[1] Understanding WCAG 2.2, Success Criterion 2.3.1 "Three Flashes or Below Threshold"**, W3C Web Accessibility Initiative, 2023, https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
- Take: the accessibility bar for flashing. Content must not flash more than three times in any one-second period unless it passes the general flash threshold (a luminance change of 10% or more where the darker frame is below relative luminance 0.80) and the red flash threshold (saturated red, where R/(R+G+B) is at least 0.8 and the chromaticity difference is above 0.2). The flashing area limit is 0.006 steradians within any 10-degree field, about 25%.
- Confidence: high.

**[2] Recommendation ITU-R BT.1702-3, "Guidance for the reduction of photosensitive epileptic seizures caused by television"**, International Telecommunication Union, 11/2023, https://www.itu.int/rec/R-REC-BT.1702-3-202311-I/en (PDF text read directly)
- Take: the broadcast engineering standard that most QC tools implement. A potentially harmful flash is an opposing luminance pair. When the darker frame is below 160 cd/m², a difference of 20 cd/m² or more counts. Transitions to or from saturated red count at any luminance. A sequence fails when flashing covers more than 25% of the screen and there are more than three flashes in any one second. Flashes whose leading edges are 360 ms apart (50 Hz) or 334 ms apart (60 Hz) pass irrespective of brightness or area. Flashing sequences over five seconds may carry risk even if they pass the per-second rule. Fast cuts that make screen areas flash fall under the same limits. Stripe patterns (more than five light/dark pairs) are also tested, with separate limits for stationary and moving patterns.
- Confidence: high.

**[3] Fisher RS et al., "Visually sensitive seizures: An updated review by the Epilepsy Foundation"**, Epilepsia 63(4):739–768, 2022, doi:10.1111/epi.17175 (open access; PDF read directly)
- Take: the medical review behind the thresholds. Flashes brighter than 20 cd/m² at roughly 3–60 Hz (most risk around 15–20 Hz), covering at least 10–25% of the visual field, are a risk. Red flashes and oscillating stripes are also risks. Photosensitive seizures affect up to about 1 in 4,000 people, and the true rate may be higher because of selection bias. The review says the equipment used to assay these characteristics is probably underused, and it names viewing distance and contrast as mitigations.
- Confidence: high.

**[4] "Flashing images in advertising"**, Advertising Standards Authority (UK), undated, https://www.asa.org.uk/news/flashing-images-in-advertising.html
- Take: the UK regulator's practice. Advertisers should check CAP Code rule 4.7 (non-broadcast) and BCAP Code rule 4.6 (broadcast), and Annex 1 of Ofcom's Guidance Note on flashing images. Broadcast ads should have passed a Harding Flash and Pattern Analyser test or an equivalent. Non-broadcast ads should be tested when there are grounds for concern. The page records that Ofcom found three technical parameters breached in a 2012 Citroën TV ad.
- Confidence: medium-high.

**[5] Understanding WCAG 2.2, Success Criterion 1.2.2 "Captions (Prerecorded)"**, W3C Web Accessibility Initiative, 2023, https://www.w3.org/WAI/WCAG22/Understanding/captions-prerecorded.html
- Take: Level A. Prerecorded audio in synchronized media needs captions, except where the media is a clearly labelled text alternative. Captions go beyond speech: they name speakers, describe meaningful sound effects, and identify non-vocal music by title and composer, with a short note on its character where that helps.
- Confidence: high.

**[6] "Commons:Reusing content outside Wikimedia"**, Wikimedia Commons, undated (live page read 2026-10-22), https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia
- Take: each file's licence is on its own description page. When several licences are offered, you may choose any one. Credit the author, name the licence, link to it, and flag changes. Attribution is recommended but not required for public-domain files. Personality, privacy and trademark rights still apply. Files on other Wikimedia projects can follow different rules, and the Foundation does not guarantee the licence data.
- Confidence: high.

**[7] "Images and Media", NASA Brand Center**, National Aeronautics and Space Administration, undated, https://www.nasa.gov/nasa-brand-center/images-and-media/
- Take: most NASA images and video fall outside US copyright and can be used for educational and informational purposes with NASA credited. The insignia, logotype, seal and identifiers are protected and are not public domain. Use must not suggest NASA endorses a product, and commercial use of an identifiable employee or astronaut needs that person's permission. NASA says AI outputs cannot be attributed to NASA, and the insignia cannot be used with AI-generated imagery.
- Confidence: high.

**[8] "Prints & Photographs: Rights and Restrictions" (risk-assessment guide)**, Library of Congress, undated, https://guides.loc.gov/p-and-p-rights-and-restrictions/risk-assessment
- Take: "No known restrictions on publication" means the Library knows of no limits. It does not mean the item is public domain. The Library generally holds no copyright and charges no permission fee, so the user must clear the item: copyright term, publicity, privacy and trademarks. A record with no rights note means the rights were not evaluated. The Library asks for a credit line.
- Confidence: high.

**[9] "Rights", Internet Archive Help Center**, Internet Archive, undated, https://help.archive.org/help/rights/
- Take: the Archive does not vouch for copyright status. Rights information comes from uploaders. A Creative Commons logo on an item page links to that licence. Users take on the risk of infringement under the Terms of Use. Repeat-infringer and counter-notice processes apply.
- Confidence: high.

**[10] "Prelinger Archive", Internet Archive Help Center**, Internet Archive, undated, https://help.archive.org/help/prelinger-archive/
- Take: films carrying a Creative Commons licence can be reused on that licence. Descriptions and shot lists are jointly copyrighted by Prelinger Archives and Getty Images, and may not be used commercially without permission. Commercial footage licensing is routed to Getty. Credit is requested but not required, and the page gives a suggested credit line.
- Confidence: high.

**[11] "Open Access FAQ", Smithsonian Institution**, Smithsonian, undated, https://dashboard.si.edu/openaccess/faq (fetch blocked; read from search summaries)
- Take: Open Access images and data are released under CC0, which waives copyright and allows commercial use without attribution or fee. CC0 does not clear third-party, personality or privacy rights, and not every item is CC0, so check each record.
- Confidence: medium.

**[12] "Data policy", Rijksmuseum**, Rijksmuseum, undated, https://data.rijksmuseum.nl/policy
- Take: items marked Public Domain or CC0 can be reused, commercially included, without permission. Some items carry CC BY 4.0 and need credit to the Rijksmuseum. Photographs of in-copyright objects are not freely available, and the copyright notice names the rights holder. The museum asks for credit even where it is not required. Usage restrictions are marked item by item.
- Confidence: medium-high.

**[13] "The Met Makes Its Collection of Images Available Under CC0"**, The Metropolitan Museum of Art, press release, 2017, https://www.metmuseum.org/press/news/2017/open-access (current policy page blocked; read from search results of the 2017 announcement)
- Take: images of public-domain artworks released under CC0, free for any use without permission or fee, with select data under CC0. At launch the policy covered more than 375,000 images. Check the current Open Access page for the present count and terms.
- Confidence: medium-low.

**[14] "Open access images", Art Institute of Chicago**, undated, https://www.artic.edu/open-access/open-access-images (read from search summaries; fetch returned 429)
- Take: over 50,000 images of public-domain or waived works, labelled "CC0 Public Domain Designation", usable for any purpose. There is no legal duty to credit, but the museum asks for the credit form artist, title, date, then "The Art Institute of Chicago". Modern works still in copyright are excluded. Other images come through the Art Resource licensing partner.
- Confidence: medium.

**[15] "License", Pexels**, Pexels, undated, https://www.pexels.com/license/
- Take: free for commercial and non-commercial use, including ads; credit not required; edits allowed. Prohibited: showing identifiable people in an unflattering or offensive way, implying that people or brands endorse your product, using the material in a trademark or business name, and selling unmodified copies or redistributing on other stock platforms. The page does not address logos inside footage.
- Confidence: high.

**[16] "Content License Summary", Pixabay**, Pixabay, undated, https://pixabay.com/service/license-summary/
- Take: free, no attribution required, and content may be modified. Prohibited: standalone resale without creative effort, commercial use with recognisable trademarks or logos (including on merchandise), use as part of a trademark or business name, immoral or illegal use (especially of recognisable people), and misleading use. Third-party copyright, trademark, design and privacy rights may still apply. The summary is not binding; the full licence is.
- Confidence: high.

**[17] "Unsplash License"**, Unsplash, undated, https://unsplash.com/license
- Take: free for commercial use, no permission or attribution required (credit appreciated). Selling images without significant modification is not allowed, and compiling Unsplash images to build a similar or competing service is not allowed. The page does not address identifiable people, trademarks, political use or AI training.
- Confidence: high.

**[18] "SIL Open Font License FAQ"**, SIL International, undated, https://openfontlicense.org/ofl-faq/
- Take: OFL fonts can be used in logos, posters and on-screen video titling without permission, and the creator keeps copyright in the finished work. The conditions apply when the font file itself is redistributed, bundled or modified. Embedding in documents is allowed, and a font cannot be sold on its own. Credit is appreciated but optional.
- Confidence: high.

**[19] "Use music and sound effects from the Audio Library", YouTube Help**, Google, undated, https://support.google.com/youtube/answer/3376882
- Take: standard-licence Audio Library tracks need no credit. Creative Commons Attribution tracks need credit in the video description, and the Studio licence icon gives the credit text. Tracks marked copyright-safe are shielded from Content ID claims. The page covers use inside YouTube only and refers off-platform questions to a lawyer, so do not assume it clears a LinkedIn or paid-ad use.
- Confidence: high.

**[20] "How Content ID works", YouTube Help**, Google, undated, https://support.google.com/youtube/answer/2797370
- Take: uploads are scanned automatically against rights holders' reference files. A match lets the rights holder block the video, monetise it with ads, or track it, and these options can vary by country. The page also points to dispute routes. Content ID is open only to eligible rights holders. The page excerpt read did not give dispute timelines.
- Confidence: medium-high.

**[21] "FAQ For Videos & Films", Free Music Archive**, Free Music Archive, undated, https://freemusicarchive.org/FAQ_For_Videos/
- Take: BY tracks need credit in the video and in the accompanying text. NC tracks cannot be used in commercial work, including fundraising videos, without written permission from the artist. ND tracks need permission because syncing to picture counts as a derivative. SA tracks require the film to carry the same licence. FMA-Limited tracks cannot be used in video. Some artists use Content ID, and FMA cannot resolve claims.
- Confidence: high.

**[22] "NonCommercial interpretation", Creative Commons wiki**, Creative Commons, undated, https://wiki.creativecommons.org/wiki/NonCommercial_interpretation
- Take: NC is an intent test: is the use primarily intended for commercial advantage or monetary compensation? It is judged by the use, not by who the user is, so a company's promotional film is a commercial use. An NC licence does not limit fair use or publicity rights. Creative Commons does not give legal advice.
- Confidence: high.

**[23] "Attribution 4.0 International (CC BY 4.0) deed"**, Creative Commons, undated, https://creativecommons.org/licenses/by/4.0/
- Take: appropriate credit means naming the creator and any party named for attribution, giving the copyright notice when supplied, naming the licence with a link, including a disclaimer notice, linking to the material, and saying whether it was changed. Credit cannot suggest the creator endorses your use. The licence does not grant publicity, privacy or moral rights.
- Confidence: high.

**[24] "Business plan", Epidemic Sound**, Epidemic Sound, undated, https://www.epidemicsound.com/our-plans/business-plan/
- Take: eligibility is set by revenue: brands under $10M annual revenue, and agencies, publishers and production companies with their own revenue under $5M and clients under $50M. Permitted: social posts, paid ads, corporate videos, client work, and online ads with sound synced to video (ad campaigns limited to non-major organisations). Not permitted: out-of-home, livestream and radio. OTT and extended broadcast rights sit on higher tiers. A published project keeps its licence. The full terms are linked from the page and were not read.
- Confidence: medium-high.

**[25] "Artlist Help Center, licence articles"**, Artlist, undated, https://help.artlist.io/hc/en-us/articles/29490991524253 (page fetch returned 403; read from search summaries)
- Take: the Social licence is for personal creators and covers one channel on each named platform; the Pro licence adds client and brand work and more media. Projects published during an active subscription keep their licence after cancellation. Playlist-style passive-listening use is not permitted. Third-party comparisons disagree on plan details, so read the current terms.
- Confidence: medium-low.

**[26] "Fair Use", U.S. Copyright Office**, U.S. Copyright Office, undated, https://www.copyright.gov/fair-use/
- Take: fair use turns on four factors under 17 U.S.C. §107: purpose and character of the use, nature of the work, amount and substantiality used, and effect on the market. "Transformative" sits within the first factor. Criticism, comment, news reporting, teaching, scholarship and research are examples only. Each case is decided on its facts, and there is no safe word count or percentage.
- Confidence: high.

**[27] Summary of Andy Warhol Foundation for the Visual Arts v. Goldsmith, 143 S. Ct. 1258 (2023)**, U.S. Copyright Office, 2023, https://www.copyright.gov/fair-use/summaries/Andy-Warhol-Found-for-the-Visual-Arts-Inc-v-Goldsmith-143-S-Ct-1258-2023.pdf (PDF text read directly)
- Take: the Court held that licensing a photograph-derived artwork to a magazine for the same purpose as the source photograph weighed against fair use under the first factor. New expression is not, without more, decisive, and commerciality counts against the use. The practical reading: a traced or derived image used commercially for the same purpose as its source is high risk.
- Confidence: high.

**[28] "License FAQ", Remotion**, Remotion (company documentation), undated, https://www.remotion.dev/docs/license/faq
- Take: the free licence covers individuals, teams of up to three people, non-profits and evaluators. Headcount includes the agency and any client team that operates the project; if a client only receives the finished file, only the agency's headcount counts. Four or more people generally need a Company License. The FAQ notes that the license and terms change in Remotion 5.0 (telemetry for server-side use).
- Confidence: high.

**[29] Article 50, Regulation (EU) 2024/1689 (AI Act), transparency obligations**, European Union, 2024, https://artificialintelligenceact.eu/article/50/ (third-party text of the regulation; EUR-Lex not read)
- Take: deployers who generate or alter image, audio or video that resembles real people, objects, places or events and could falsely appear authentic must disclose that it is AI-generated or manipulated. For evidently artistic, creative, satirical or fictional works, the duty is reduced to disclosing that such content exists, in a way that does not hinder the viewing experience. Providers must mark synthetic output in machine-readable form. The page states the article applies from 2 August 2026.
- Confidence: medium-high.

**[30] "Disclosing use of altered or synthetic content", YouTube Help**, Google, undated, https://support.google.com/youtube/answer/14328491
- Take: disclose realistic content that is altered or synthetic: a real person appearing to say or do something they did not, changed footage of a real event or place, or a lifelike scene that never happened, and AI-generated music that is the main focus. Animation, fantasy, effects, minor edits and AI help with scripts or titles do not need disclosure. Disclosure is set at upload under "AI use". YouTube may auto-label content made with its own tools or carrying C2PA metadata.
- Confidence: high.

**[31] "Our approach to labeling AI-generated content and manipulated media" (updated April 2024)**, Meta, 2024, https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/
- Take: the AI info label is applied on industry-standard signals or on self-disclosure. A more prominent label may be applied where digitally created or altered content could materially mislead on an important matter. AI-retouched content gets a less prominent label from September 2024. The February 2024 announcement (read in search summaries) said users must disclose photorealistic video and realistic audio, but the April page does not present self-disclosure as mandatory. Treat disclosure as expected and check Meta's live help pages.
- Confidence: medium.

**[32] "New labels for disclosing AI-generated content", TikTok Newsroom**, TikTok, 19 September 2023, https://newsroom.tiktok.com/new-labels-for-disclosing-ai-generated-content?lang=en (read from search summaries; fetch failed)
- Take: creators can apply a built-in AI-generated label to content that is fully generated or substantially edited with AI. A sticker or caption is an alternative disclosure. The Community Guidelines' synthetic-media rule requires labelling of realistic AI images, audio or video. TikTok planned automatic detection labels. No 2025–26 text was read.
- Confidence: medium-low.

**[33] Content Credentials and C2PA Explainer (specification 2.2)**, Coalition for Content Provenance and Authenticity, 2024–2025, https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html
- Take: a Content Credential is a signed manifest of assertions about an asset: origin, edits, and AI involvement. A hard binding (cryptographic hash) shows whether the asset has changed. Soft bindings such as watermarks or fingerprints help find the manifest after metadata is stripped. Credentials show origin and integrity, not truth, and a missing credential proves nothing by itself.
- Confidence: high.

**[34] "LinkedIn Begins Labeling AI-Generated Content"**, MediaPost, date not confirmed (article 396225; read from search summary only), https://www.mediapost.com/publications/article/396225/linkedin-begins-labeling-ai-generated-content.html
- Take: LinkedIn labels in-feed AI-generated visuals using C2PA provenance data embedded in the file, and the data stays with the file after download. LinkedIn concedes it cannot yet label all AI content. Press descriptions of the badge differ, so check LinkedIn's help centre. Keep provenance intact on export.
- Confidence: low.

**[35] Code of Practice for Statistics (Edition 3.0), Office for Statistics Regulation (UK)**, OSR, 2025, https://osr.statisticsauthority.gov.uk/publications/the-code-of-practice-for-statistics/pages/2/ (read from search summaries; the redirect target did not carry the principles)
- Take: the code rests on three pillars, Trustworthiness, Quality and Value, and ten principles. Statistics must not be materially misleading, must be open about their quality, and must be clear and accessible. Use this as the test for every number shown on screen.
- Confidence: medium.

## What this means for the skill

- **Flash check, per frame.** Use ITU-R BT.1702-3 as the baseline: a flash is an opposing luminance pair; when the darker frame is below 160 cd/m², a 20 cd/m² difference counts; saturated-red transitions count at any luminance. [2]
- **Hard per-second cap.** Fail any sequence where flashing covers more than 25% of the screen and there are more than three flashes in one second. Flashes spaced at least 360 ms apart (50 Hz) or 334 ms apart (60 Hz) pass regardless of brightness or area. [2]
- **Duration cap on flashing.** ITU notes that flashing sequences longer than five seconds may be risky even when each second passes, so cap strobing sections and log total flash seconds per section. [2][3]
- **Fast cuts and glitch count.** Rapid cuts that make screen areas flash fall under the same limits, so datamosh, glitch transitions and strobing titles need the same measured pass. [2]
- **Pattern rule.** More than five light/dark stripe pairs, stationary over more than 40% of the screen, or moving, flashing or reversing over more than 25%, is potentially harmful under the pattern guidance. Treat scanlines, halftone, Op-art and moiré as patterns to measure. [2]
- **Public bar: WCAG 2.3.1.** Stay at or under three flashes per second unless the general threshold (10% relative-luminance change, darker frame below 0.80) and the red threshold (R/(R+G+B) at least 0.8, chromaticity change above 0.2) are both passed. [1]
- **Red is separately risky.** Keep saturated red fields out of the film, or measure every red transition; ITU, WCAG and the Epilepsy Foundation review all flag red. [1][2][3]
- **Test band 3–60 Hz.** The review puts most risk between about 15 and 20 Hz and covers flashes up to 60 Hz, so check that whole band, not only the three-per-second line. Flashes over 20 cd/m² covering 10–25% of the field are the review's reference risk. [3]
- **Measure the graded mp4.** Run a measured flash and pattern analysis on the final file (the project's flash-check script, or a Harding FPA equivalent for UK broadcast or ad use) and log the result. Eyeballing does not count. [4][2]
- **UK ad clearance.** Broadcast creative should pass Harding FPA or an equivalent, and CAP rule 4.7 and BCAP rule 4.6 apply. A pass is not a guarantee: the ASA page records a 2012 Citroën ad that Ofcom found in breach. [4]
- **Record residual risk.** ITU says it is impossible to eliminate the risk of flashing images causing seizures, so log the residual and consider an opening photosensitivity notice when strobing is used (a recommendation of this digest, not a requirement in these sources). [2]
- **Captions are a Level A requirement.** Prerecorded video with sound needs captions that name speakers, describe meaningful sound effects, and identify non-vocal music by title and composer. Put the track title and artist in the captions and the end credits. [5]
- **Log every Commons file.** Record the description-page URL, author, licence name and link, and the exact credit string in the footage log. Choose the licence that fits the film, and prefer one without ShareAlike or NonCommercial for a commercial film. [6]
- **Public domain is not a clearance.** Log who asserted "no known restrictions" or "no copyright reserved" (Library of Congress, Internet Archive, Commons). Check the copyright term, identifiable people and trademarks yourself. [8][9][6]
- **Government and museum images.** NASA imagery and CC0 museum scans (Smithsonian, Rijksmuseum, Art Institute of Chicago, Met) can be used without permission, but check each item's rights note. Never use NASA insignia or imply NASA endorsement in a brand film. [7][11][12][13][14]
- **Credit lines are cheap.** The Art Institute asks for "Artist, title, date, The Art Institute of Chicago", the Rijksmuseum and the Library of Congress ask for credit, and Pexels, Pixabay and Unsplash do not require it. Put them on the credits card. [14][12][8][15][16][17]
- **Prelinger footage.** Use CC-licensed Prelinger clips under their licence. For other clips, the descriptions are copyrighted and commercial footage goes through Getty, so do not assume a Prelinger clip is free for a company film. [10]
- **Stock is not clearance for people or logos.** Pexels, Pixabay and Unsplash allow commercial use, but none clears identifiable people, endorsements or recognisable trademarks by itself. Keep faces and logos out of brand footage unless you hold a release, or blur or replace them. [15][16][17]
- **Stock is not a reel.** Pixabay bars standalone resale, and Unsplash bars selling unmodified images or compiling them into a competing service. The film must be an edited work, not a stock-footage compilation. [16][17][15]
- **Fonts.** OFL fonts can be used in titles and logos without permission or credit. Keep font files out of any shipped or public repository, and log each font's licence in the footage log. [18]
- **Audio Library limits.** Standard Audio Library tracks need no credit, and CC BY tracks need a description credit. The page covers only YouTube use, so for a LinkedIn or paid-ad film, check the licence for that use before publishing. [19]
- **Content ID can match anything.** A rights holder can block, monetise or track a match, so a track used outside what its licence covers can be claimed on any platform. Keep each track's licence certificate and licence type with the footage log. [20][19]
- **CC music filter.** NC blocks commercial and fundraising films without written permission, ND blocks syncing without permission, SA forces the film under the same licence, and BY needs credit in the video and the description. [21][22][23]
- **NC is about purpose.** A company's brand or promotional film is a commercial use even without a direct sale, so NC tracks are out for this project regardless of the publisher's size. [22][21]
- **Attribution checklist.** For each BY-licensed item, record title, creator, source link, licence name with link, a disclaimer, and whether it was changed. Credit may not suggest the creator endorses the film. [23]
- **Subscription music fits only the use it covers.** Epidemic's business plan has revenue limits and excludes out-of-home, livestream and radio; OTT and extended broadcast need higher tiers. Artlist's Social licence is for personal creators, so client and brand work needs its Pro licence. Match the plan to the film's real uses before publishing. [24][25]
- **Decide Remotion's licence before the first commercial render.** Free use covers up to three people across the company and any client team that runs the project. Four or more people, or a client that runs the project, needs a Company License. [28]
- **Fair use is a weak shield for brand films.** Weigh the four factors, and treat commerciality as a strong negative. A commercial use that shares the original's purpose is weighed against fair use even when new expression is added. [26][27]
- **Traced likeness is a derivative.** Do not trace or redraw a photograph of a real person or a copyrighted image for a commercial film; the Warhol decision treats a commercially licensed derivative with the same purpose as the source as high risk. [27][6][7]
- **Quotations and news clips.** A short quotation for criticism or comment can sit within the first-factor purposes, but the film's commercial character weighs against it. Use original or licensed material for news footage and stills. [26][27]
- **EU disclosure, from 2 August 2026.** Realistic AI footage that resembles real people, places or events must be disclosed. For fictional or artistic work, a brief disclosure that AI was used, shown without hindering the film, is enough. Add an AI-use credit to the end card. [29]
- **YouTube disclosure.** Set "AI use" to Yes for realistic altered or synthetic footage at upload. Animation, effects and scripting help are exempt. [30]
- **Meta and TikTok.** Disclose realistic AI video on both, even where the platform's own signal does not catch it. Meta's AI info label relies on industry metadata or self-disclosure, and TikTok offers a built-in AI label or a caption disclosure. [31][32]
- **LinkedIn and provenance.** Embed Content Credentials (C2PA) on export, with an AI-involvement assertion, so platforms can read and label the file. Credentials show origin and integrity, not truth, and re-encoding or stripping metadata can remove them. [33][34]
- **Numbers on screen.** Every statistic needs its publisher, title, year, URL and access date, quoted exactly as published (unit, sample, date range). Go to the primary source, not a secondary article. [35]
- **Not materially misleading.** The UK OSR code's test is that statistics must not be materially misleading and must be open about quality. Apply it to every figure, and drop any figure that fails it. [35]

## Open questions

- **Ofcom's current photosensitivity rule and Annex 1 values.** Ofcom pages returned 403, so the current Broadcasting Code rule number and the technical parameters were not read. Search summaries disagree on the rule number across editions.
- **BT.1702-3 HDR values.** The HDR contrast rule (one-seventeenth Michelson contrast) was read but not tested against any HDR delivery. Confirm before an HDR master.
- **Harding FPA and Netflix PSE guidance.** The vendor and Netflix pages were blocked or redirected to nothing readable, so their test details are not in this digest.
- **Current museum and stock policy pages.** The Smithsonian, Met, Art Institute of Chicago, Europeana and Adobe Stock live pages were blocked. Their claims rest on search summaries and the 2017 Met announcement. Re-check before use. Europeana's rights-statement scheme and Adobe Stock's AI video rules were not included.
- **Music platform terms.** Musicbed, Soundstripe and Artlist's current terms were not read. Epidemic's full licence was not read. Treat vendor claims as unverified.
- **Sync versus master rights.** A licensed recording used in picture usually needs both a sync (composition) and a master-use (recording) clearance. Search summaries support this, but no primary source was read, so the point is unsourced here.
- **LinkedIn policy text.** LinkedIn's own AI-label and C2PA help pages were not retrieved. Press coverage is the only source.
- **Meta's disclosure duty.** The February 2024 announcement and the April 2024 page appear to differ on whether self-disclosure is mandatory. Check the live help pages.
- **TikTok current policy.** Only the 2023 announcement was read.
- **EU Article 50 penalties and guidance.** Penalty levels and the Commission's Article 50 guidance (a draft reportedly appeared in 2026) were not verified against primary text. The EUR-Lex text was not read.
- **US likeness and publicity law.** State publicity statutes (New York and California) and Tennessee's 2024 ELVIS Act were found only through summaries and are not in the source list. Verify the statutes before any film uses a real person's voice or face.
- **Trademark use in footage.** The Rogers-test trademark limits (Jack Daniel's, 2023) were found in a summary, not in this source list. Treat any visible brand as a clearance question until checked.
- **Muted-viewing and caption-effect statistics.** Figures found were vendor-sourced and conflicting, so none is included.
- **Google Fonts' own licensing page** was not readable (title only). This digest relies on the OFL FAQ.
- **Content ID dispute timelines** were not confirmed from YouTube's own pages.
