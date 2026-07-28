# Copilot instructions for Starfield Intelligent Gallery (SIG)

Purpose
-------
Short, actionable guidance for Copilot-style AI sessions working on SIG. Read README.md and AGENTS.md first for full context.

Build, test, and lint (how-to)
-----------------------------
- Run app (dev):
  - python main.py
  - Headless render: python main.py --render --output out.mp4 --width 1920 --height 1080 --fps 24 --duration 8
- Install editable package (optional): python -m pip install -e .  (pyproject.toml defines `sig` entry)
- CLI entry (after install): sig

- Tests (CI helpers exist under tools/):
  - Run full suite: pytest  OR python tools/run_tests.py
  - Run single test function: pytest path/to/test_file.py::test_function_name
  - Run a single test file: pytest path/to/test_file.py
  - Use -q for concise output: pytest -q
  - Pytest uses repo root on PYTHONPATH (see pytest.ini: `pythonpath = .`).

- Linting:
  - CI calls: python tools/lint.py (wrapper around `ruff`)
  - Direct: ruff check .

- Coverage & CI helpers:
  - CI scripts use tools/run_coverage.py and other validators under tools/ (see tools/.github/workflows/ci.yml)

High-level architecture (big picture)
-------------------------------------
- Purpose: capture, curate, transcribe, and export in-game Starfield captures into an offline-first local gallery (Seeds → Relics → Archive).
- Entry points:
  - Development: main.py — provides cinematic intro, carrier deck UI, and headless render mode.
  - Packaged CLI: `sig` → GalleryApp.cli:main (pyproject.toml).
- Components:
  - GalleryApp/ (package) — primary application code and CLI integration.
  - intro/ — cinematic/intro rendering pipeline used by the launcher and headless mode.
  - ui/ — PyQt/PySide UI components (desktop player, carrier deck, etc.).
  - sig_launcher.py / launchers/ — bootstrapping and environment checks (used by CI).
  - sig/ (domain logic) — gating_engine, artifact promotion, data model for Seeds/Relics/Archive.
  - tools/ — project tooling (lint, test wrappers, validators, doc generation) used by CI.
  - Assets/, Python/assets/, sample_images/ — image/video asset storage and sample DBs (data/photos.db).
- Tests: configured via pytest.ini; CI runs many validation scripts (validate_structure.py, validate_headers.py, validate_relics.py).

Key repository conventions and patterns
--------------------------------------
- Packaging & entry: update pyproject.toml when adding runtime dependencies; entry script `sig` is defined there.
- Tool wrappers: prefer tools/* wrappers for CI parity (e.g., python tools/lint.py and python tools/run_tests.py) when running checks locally to match CI behavior.
- Linting: ruff is the canonical linter (tools/lint.py). Don't introduce a competing linter without updating CI and tools/* wrappers.
- Tests: tests assume repository root on PYTHONPATH. Use the pytest.ini `pythonpath = .` setting when running tests from other directories or CI.
- Headless rendering and debugging: main.py exposes --render, --debug, and --skip-intro flags—use these for CI-friendly runs and dev iteration.
- CI expectations: the tools/ scripts are exercised in CI; keep them stable or update tools/.github/workflows/ci.yml together with changes.
- Assets & DBs: sample DBs exist under sample_images/ and Python/sample_images/; treat these as test fixtures for dev and CI.

Where to look first
-------------------
1. README.md — project goals and workflows.
2. AGENTS.md — quick commands and agent-specific guidance (already present in repo).
3. pyproject.toml — packaging and entry points.
4. main.py — development entrypoint and available CLI flags.
5. tools/ — CI wrappers and validators (match what CI runs).

If editing: minimal, focused changes
-----------------------------------
- Run tests (pytest) before proposing broad changes.
- Update pyproject.toml when adding dependencies and explain rationale in PR.
- Keep tools/* wrappers in sync with CI if changing behaviors for lint/test/validation.

References included in repo
--------------------------
- README.md
- AGENTS.md (useful short agent guidance)
- pyproject.toml
- pytest.ini
- tools/*.py (lint/test/CI helpers)

---
Created/copied guidance pulls essential workflow items from README.md and AGENTS.md to help Copilot-style agents act safely and predictably. If you'd like, add repository-specific examples (a small test file to demonstrate single-test runs) or permit adding a light-weight pre-commit config referencing ruff.