/**
 * Section id -> component. Lead-owned, and the only file that imports every
 * section, so it is the only place one section's compile error can stop the
 * whole film from bundling.
 *
 * A section in data/timeline.json with no entry here plays as a labelled test
 * card in its palette (src/kit/placeholder.tsx), so a new section in the
 * timeline renders at once. Before the builders launch, give every section a
 * stub and register it (references/05-build.md section 3): builders do not edit
 * this file, and Solo renders a section for real only when it is here. A stub is
 * `import { makePlaceholder } from "../../kit";` and
 * `export const Section = makePlaceholder("<id>");` in src/sections/<id>/index.tsx. Remove
 * an entry when its section leaves the timeline (`python scripts/doctor.py`
 * checks both ways).
 */
import type { Registry } from "../kit/frame";
import { Section as Open } from "./00-open";

export const SECTIONS: Registry = {
  "00-open": Open,
};
