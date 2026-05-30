## In‑game capture sources

**Starfield screenshot capture**  
SIG is designed to consume Starfield's native screenshot and picture-capture features as a primary source of still images. Use the game's built-in capture (F12 or configured key) or the in-game photo mode to produce high-resolution screenshots. Store captures in a consistent folder structure and reference them from Python/assets/script.json for timed playback.

**Steam video capture**  
For motion and video sequences, SIG supports using Steam's video-capture (or other OS-level capture tools). Record gameplay clips using Steam (or OBS) and place trimmed clips in the ssets/videos/ folder. Use script.json entries to reference clip paths and timing metadata.

**Recommended workflow**  
1. Use Starfield photo mode for curated stills; export to ssets/images/.  
2. Use Steam/OBS for video capture; export trimmed clips to ssets/videos/.  
3. Keep a manifest (e.g., Python/assets/media_manifest.json) mapping in-game timestamps, capture metadata, and file paths for reproducible playback in the SIG player.
