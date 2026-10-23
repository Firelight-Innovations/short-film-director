import { Audio, staticFile } from "remotion";
import { timeline } from "../timeline/timeline";

/**
 * The track. It starts at frame 0 and is never shifted or trimmed: the film is
 * cut to this file (data/beats.json is measured from it). `timeline.audio` is
 * null for a silent film; then nothing is mounted. `gain` scales the volume.
 */
export const AudioTrack: React.FC<{ muted?: boolean }> = ({ muted }) => {
  const audio = timeline.audio;
  if (!audio || !audio.src) return null;
  // publicDir is ./assets (remotion.config.ts), so src is a path under assets/.
  return <Audio src={staticFile(audio.src)} volume={audio.gain ?? 1} muted={muted} />;
};
