# 🌌 Starfield Intelligent Gallery — Project README

**File:** README.md  
**Location:** repository root  
**Author:** Mark J. Latsha  
**Co-Author:** Microsoft Copilot  
**Created:** 2026-05-27  
**Description:** Full project overview, architecture, data flow, and canonical relic/artifact gating rules.

---

## Project purpose

Starfield Intelligent Gallery (SIG) captures, curates, and transcribes in‑game experiences from *Starfield* into a personal gallery that supports reflection and self‑discovery. The Gallery is offline‑first, modular, and designed to produce shareable artifacts and curated relics that represent meaningful moments.

---

## High level features

- **Image ingestion**: automatic discovery of Starfield screenshots and sidecar metadata.
- **Metadata extraction**: EXIF/XMP parsing, session provenance, and marker association.
- **Artifact generation**: transform sessions and markers into Seeds → Relics → Archive.
- **Relic gating**: config‑driven rules for promotion, verification, privacy, and retention.
- **UI**: desktop (PyQt) and optional web frontends for browsing, tagging, and exporting.
- **Persistence**: local DB for offline use; optional cloud sync adapters.
- **Extensibility**: plugin points for transcription models, export formats, and integrations.

---

## Architecture

# ðŸŒŒ Starfield Intelligent Gallery â€” Project README

**File:** README.md  
**Location:** repository root  
**Author:** Mark J. Latsha  
**Co-Author:** Microsoft Copilot  
**Created:** 2026-05-27  
**Description:** Full project overview, architecture, data flow, and canonical relic/artifact gating rules.

---

## Project purpose

Starfield Intelligent Gallery (SIG) captures, curates, and transcribes inâ€‘game experiences from *Starfield* into a personal gallery that supports reflection and selfâ€‘discovery. The Gallery is offlineâ€‘first, modular, and designed to produce shareable artifacts and curated relics that represent meaningful moments.

---

## High level features

- **Image ingestion**: automatic discovery of Starfield screenshots and sidecar metadata.
- **Metadata extraction**: EXIF/XMP parsing, session provenance, and marker association.
- **Artifact generation**: transform sessions and markers into Seeds â†’ Relics â†’ Archive.
- **Relic gating**: configâ€‘driven rules for promotion, verification, privacy, and retention.
- **UI**: desktop (PyQt) and optional web frontends for browsing, tagging, and exporting.
- **Persistence**: local DB for offline use; optional cloud sync adapters.
- **Extensibility**: plugin points for transcription models, export formats, and integrations.

---

## Architecture


## In-game capture sources

**Starfield screenshot capture**  
SIG is designed to consume Starfield's native screenshot and picture-capture features as a primary source of still images. Use the game's built-in capture (F12 or configured key) or the in-game photo mode to produce high-resolution screenshots. Store captures in a consistent folder structure and reference them from Python/assets/script.json for timed playback.

**Steam video capture**  
For motion and video sequences, SIG supports using Steam's video-capture (or other OS-level capture tools). Record gameplay clips using Steam (or OBS) and place trimmed clips in the ssets/videos/ folder. Use script.json entries to reference clip paths and timing metadata.

**Recommended workflow**  
1. Use Starfield photo mode for curated stills; export to ssets/images/.  
2. Use Steam/OBS for video capture; export trimmed clips to ssets/videos/.  
3. Keep a manifest (e.g., Python/assets/media_manifest.json) mapping in-game timestamps, capture metadata, and file paths for reproducible playback in the SIG player.
