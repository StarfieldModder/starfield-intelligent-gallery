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

