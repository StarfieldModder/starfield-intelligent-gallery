r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗                                                 ║
║        ██╔════╝ ██║ ██╔════╝   S I G _ D I A G N O S T I C S . P Y         ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "The Intelligent Gallery checks itself."     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  sig_diagnostics.py                                            ║
║  Location   :  C:\SIG\sig_diagnostics.py                                    ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.05 — Check Engine Light Edition                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                           ║
║                                                                              ║
║  The SIG "Check Engine Light" — an independent health-check that tests      ║
║  every subsystem before the cinematic launch sequence begins.               ║
║                                                                              ║
║  Run standalone at any time:                                                 ║
║    .venv\Scripts\python.exe sig_diagnostics.py                              ║
║                                                                              ║
║  Or import and call from sig_launcher.py:                                   ║
║    from sig_diagnostics import run_diagnostics                               ║
║    if not run_diagnostics(silent=False): sys.exit(1)                        ║
║                                                                              ║
║  TESTS (each returns PASS / WARN / FAIL)                                    ║
║    01  Python version (≥ 3.10)                                              ║
║    02  PySide6 core                                                          ║
║    03  PySide6.QtMultimedia                                                  ║
║    04  PySide6.QtSvg                                                         ║
║    05  PySide6.QtWidgets + QApplication constructs                           ║
║    06  Video file found in search paths                                      ║
║    07  Varuun SVG glyph files (6 of 6)                                       ║
║    08  ui.intro_panel_widget  → IntroPanelWidget                            ║
║    09  ui.space_flight_widget → SpaceFlightWidget                           ║
║    10  ui.carrier_deck        → CarrierDeck                                  ║
║    11  cosmic_choice_panel    → CosmicChoicePanel  (import only)            ║
║    12  gallery_mode           → GalleryMode                                  ║
║    13  relics_mode            → RelicsMode                                   ║
║    14  companions_mode        → CompanionMode                                ║
║    15  archive_mode           → ArchiveMode                                  ║
║    16  nebula_module          → render_nebula()                              ║
║    17  ui.active_random_nebula → ActiveRandomNebula                          ║
║    18  Steam / Starfield install detection (advisory)                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import importlib
import os
import platform
import sys
import textwrap
from pathlib import Path
from typing import Callable, List, NamedTuple, Optional, Tuple

# ── Ensure C:\SIG is on sys.path when run from any directory ─────────────────
_SIG_ROOT = Path(__file__).resolve().parent
if str(_SIG_ROOT) not in sys.path:
    sys.path.insert(0, str(_SIG_ROOT))


# ══════════════════════════════════════════════════════════════════════════════
#  C O L O U R   H E L P E R S   (Windows 10 ANSI support)
# ══════════════════════════════════════════════════════════════════════════════

_USE_COLOUR = sys.stdout.isatty()

if _USE_COLOUR and platform.system() == "Windows":
    os.system("color")   # enable ANSI on Windows 10

_R  = "\033[91m"   # red
_G  = "\033[92m"   # green
_Y  = "\033[93m"   # yellow
_C  = "\033[96m"   # cyan
_W  = "\033[97m"   # bright white
_DIM = "\033[2m"   # dim
_RST = "\033[0m"   # reset


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RST}" if _USE_COLOUR else text


def _pass(msg: str)  -> str: return _c(_G,  f"  ✓  PASS  {msg}")
def _warn(msg: str)  -> str: return _c(_Y,  f"  ⚠  WARN  {msg}")
def _fail(msg: str)  -> str: return _c(_R,  f"  ✗  FAIL  {msg}")
def _info(msg: str)  -> str: return _c(_DIM, f"           {msg}")
def _head(msg: str)  -> str: return _c(_C,  msg)


# ══════════════════════════════════════════════════════════════════════════════
#  R E S U L T   T Y P E
# ══════════════════════════════════════════════════════════════════════════════

class Result(NamedTuple):
    status  : str     # "PASS" | "WARN" | "FAIL"
    label   : str
    detail  : str = ""


# ══════════════════════════════════════════════════════════════════════════════
#  I N D I V I D U A L   T E S T S
# ══════════════════════════════════════════════════════════════════════════════

def _test_python_version() -> Result:
    ver   = sys.version_info
    label = f"Python {ver.major}.{ver.minor}.{ver.micro}"
    if ver >= (3, 10):
        return Result("PASS", label, f"Full compatibility confirmed.")
    if ver >= (3, 8):
        return Result("WARN", label,
                      "Python 3.10+ recommended. Some PySide6 features may differ.")
    return Result("FAIL", label,
                  "Python 3.10 or newer is required. Please upgrade your interpreter.")


def _test_pyside6_core() -> Result:
    try:
        import PySide6
        ver = getattr(PySide6, "__version__", "unknown")
        return Result("PASS", f"PySide6  v{ver}", "Core module present.")
    except ImportError as e:
        return Result("FAIL", "PySide6",
                      f"Not installed: {e}  →  Run: pip install PySide6")


def _test_qtmultimedia() -> Result:
    try:
        from PySide6.QtMultimedia import QMediaPlayer   # noqa: F401
        return Result("PASS", "PySide6.QtMultimedia", "QMediaPlayer available — video playback OK.")
    except ImportError as e:
        return Result("FAIL", "PySide6.QtMultimedia",
                      f"Missing: {e}  →  Run: pip install PySide6")


def _test_qtsvg() -> Result:
    try:
        from PySide6.QtSvg import QSvgRenderer   # noqa: F401
        return Result("PASS", "PySide6.QtSvg", "QSvgRenderer available — Varuun glyphs will render from SVG.")
    except ImportError:
        return Result("WARN", "PySide6.QtSvg",
                      "Not available — SIG will use procedural fallback hexagons for Varuun glyphs. "
                      "Run: pip install PySide6 to restore SVG support.")


def _test_qtwidgets(app_holder: list) -> Result:
    """Create a QApplication (or reuse existing) for downstream instantiation tests."""
    try:
        from PySide6.QtWidgets import QApplication
        existing = QApplication.instance()
        if existing is None:
            _app = QApplication.instance() or QApplication(sys.argv)
            app_holder.append(_app)
        else:
            app_holder.append(existing)
        return Result("PASS", "PySide6.QtWidgets + QApplication",
                      "Event-loop host created successfully.")
    except Exception as e:
        return Result("FAIL", "PySide6.QtWidgets", f"Could not create QApplication: {e}")


# ── Video ─────────────────────────────────────────────────────────────────────

_VIDEO_SEARCH_PATHS = [
    Path(r"C:\SIG\video"),
    _SIG_ROOT / "video",
    Path.home() / "Videos",
]
_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def _test_video_file() -> Result:
    candidates: list[Path] = []
    for search in _VIDEO_SEARCH_PATHS:
        if search.exists():
            candidates.extend(
                f for f in search.iterdir()
                if f.suffix.lower() in _VIDEO_EXTENSIONS
            )

    if not candidates:
        return Result(
            "FAIL", "Video file",
            "No video file found in C:\\SIG\\video\\ (or ~/Videos). "
            "Place The_Crossing mp4 there and update the path in intro_panel_widget.py.",
        )

    found = candidates[0]
    mb    = found.stat().st_size / (1024 * 1024)
    detail = f"Found: {found.name}  ({mb:.1f} MB)"
    if len(candidates) > 1:
        detail += f"  (+{len(candidates) - 1} others)"
    return Result("PASS", "Video file", detail)


# ── Varuun SVG glyphs ────────────────────────────────────────────────────────

_GLYPH_DIR   = Path(r"C:\SIG\intro\assets\glyphs")
_GLYPH_NAMES = [
    "glyph_hex.svg",
    "glyph_eye.svg",
    "glyph_sigma.svg",
    "glyph_diamond.svg",
    "glyph_arrow.svg",
    "glyph_cross.svg",
]


def _test_glyph_svgs() -> Result:
    missing = []
    present = []
    for name in _GLYPH_NAMES:
        path = _GLYPH_DIR / name
        if path.exists():
            present.append(name)
        else:
            missing.append(name)

    if not _GLYPH_DIR.exists():
        return Result(
            "FAIL", "Varuun SVG glyphs",
            f"Directory missing: {_GLYPH_DIR}  — "
            "Create it and place the 6 SVG glyph files there.",
        )
    if missing:
        return Result(
            "WARN", f"Varuun SVG glyphs  ({len(present)}/{len(_GLYPH_NAMES)} found)",
            f"Missing: {', '.join(missing)}  "
            "→  SIG will use procedural hexagon fallback for absent glyphs.",
        )
    return Result(
        "PASS", f"Varuun SVG glyphs  (6/6 found)",
        f"All in {_GLYPH_DIR}",
    )


# ── Module import helper ──────────────────────────────────────────────────────

def _try_import(module_path: str, class_name: Optional[str] = None) -> Result:
    """
    Import module_path (dot notation).  If class_name given, also verify the
    class attribute exists.  Does NOT instantiate — avoids needing a display.
    """
    label = f"{module_path}" + (f"  →  {class_name}" if class_name else "")
    try:
        mod = importlib.import_module(module_path)
        if class_name:
            if not hasattr(mod, class_name):
                return Result(
                    "FAIL", label,
                    f"Module loaded but '{class_name}' not found — check class name.",
                )
        return Result("PASS", label, "Import successful.")
    except SyntaxError as e:
        return Result(
            "FAIL", label,
            f"SyntaxError at line {e.lineno}: {e.msg}  →  Fix before launch.",
        )
    except ImportError as e:
        return Result(
            "FAIL", label,
            f"ImportError: {e}  →  Check file exists and dependencies are installed.",
        )
    except Exception as e:
        return Result(
            "FAIL", label,
            f"{type(e).__name__}: {e}",
        )


# ── Carrier Deck signal check ─────────────────────────────────────────────────

def _test_carrier_deck() -> Result:
    base = _try_import("ui.carrier_deck", "CarrierDeck")
    if base.status == "FAIL":
        return base
    try:
        from ui.carrier_deck import CarrierDeck
        sig = getattr(CarrierDeck, "panel_selected", None)
        if sig is None:
            return Result(
                "WARN", "ui.carrier_deck  →  CarrierDeck",
                "CarrierDeck loaded but panel_selected Signal not found. "
                "Verify you are importing from ui.carrier_deck (not root carrier_deck.py).",
            )
        return Result("PASS", "ui.carrier_deck  →  CarrierDeck",
                      "Signal panel_selected confirmed.")
    except Exception as e:
        return Result("WARN", "ui.carrier_deck  →  CarrierDeck",
                      f"Loaded but signal check raised: {e}")


# ── nebula_module functional test ─────────────────────────────────────────────

def _test_nebula_module() -> Result:
    try:
        mod = importlib.import_module("nebula_module")
        fn  = getattr(mod, "render_nebula", None)
        if fn is None:
            return Result(
                "WARN", "nebula_module  →  render_nebula",
                "Module loaded but render_nebula() not found.",
            )
        result = fn()
        return Result("PASS", "nebula_module  →  render_nebula()",
                      f"Called successfully, returned: {type(result).__name__}")
    except SyntaxError as e:
        return Result("FAIL", "nebula_module",
                      f"SyntaxError at line {e.lineno}: {e.msg}")
    except Exception as e:
        return Result("FAIL", "nebula_module",
                      f"{type(e).__name__}: {e}")


# ── Steam / Starfield detection (advisory only) ───────────────────────────────

_STEAM_PATHS = [
    Path(r"C:\STEAM\steam.exe"),                              # Mark's custom install path
    Path(r"C:\Program Files (x86)\Steam\steam.exe"),
    Path(r"C:\Program Files\Steam\steam.exe"),
    Path.home() / ".steam" / "steam" / "steam.exe",
]

_STARFIELD_RELATIVE = Path(
    r"steamapps\common\Starfield\Starfield.exe"
)


def _test_steam_starfield() -> Result:
    steam_found: Optional[Path] = None
    for sp in _STEAM_PATHS:
        if sp.exists():
            steam_found = sp.parent
            break

    if steam_found is None:
        return Result(
            "WARN", "Steam installation",
            "Steam not detected in default paths. "
            "If SIG integrates with Steam/Starfield, verify paths manually.",
        )

    sf_exe = steam_found / _STARFIELD_RELATIVE
    if sf_exe.exists():
        return Result(
            "PASS", "Steam + Starfield",
            f"Steam: {steam_found}   Starfield.exe confirmed.",
        )
    return Result(
        "WARN", "Steam found — Starfield.exe NOT found",
        f"Steam at: {steam_found}\n"
        f"           Expected Starfield.exe at: {steam_found / _STARFIELD_RELATIVE}\n"
        f"           Advisory only — SIG launches independently of Starfield.",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  M A I N   D I A G N O S T I C   R U N N E R
# ══════════════════════════════════════════════════════════════════════════════

def run_diagnostics(silent: bool = False) -> bool:
    """
    Run all SIG subsystem checks.
    Returns True if no FAIL results; False otherwise.
    When silent=True, only prints FAIL and WARN results.
    """
    _app_holder: list = []

    # ── Header ────────────────────────────────────────────────────────────────
    if not silent:
        banner = textwrap.dedent(r"""
        ╔══════════════════════════════════════════════════════════════════╗
        ║   SIG  CHECK ENGINE LIGHT  — Subsystem Diagnostics              ║
        ║   Starfield Intelligent Gallery  ·  2026.07.05                  ║
        ╚══════════════════════════════════════════════════════════════════╝
        """).strip()
        print()
        print(_head(banner))
        print()

    # ── Define test suite ─────────────────────────────────────────────────────
    tests: List[Tuple[str, Callable[[], Result]]] = [
        ("Runtime",          _test_python_version),
        ("PySide6 Core",     _test_pyside6_core),
        ("QtMultimedia",     _test_qtmultimedia),
        ("QtSvg",            _test_qtsvg),
        ("QtWidgets / App",  lambda: _test_qtwidgets(_app_holder)),
        ("Video File",       _test_video_file),
        ("Varuun Glyphs",    _test_glyph_svgs),
        ("IntroPanelWidget", lambda: _try_import("ui.intro_panel_widget", "IntroPanelWidget")),
        ("SpaceFlightWidget",lambda: _try_import("ui.space_flight_widget", "SpaceFlightWidget")),
        ("CarrierDeck",      _test_carrier_deck),
        ("CosmicChoicePanel",lambda: _try_import("cosmic_choice_panel",   "CosmicChoicePanel")),
        ("GalleryMode",      lambda: _try_import("gallery_mode",          "GalleryMode")),
        ("RelicsMode",       lambda: _try_import("relics_mode",           "RelicsMode")),
        ("CompanionMode",    lambda: _try_import("companions_mode",       "CompanionMode")),
        ("ArchiveMode",      lambda: _try_import("archive_mode",          "ArchiveMode")),
        ("NebulaModule",     _test_nebula_module),
        ("ActiveRandomNebula",lambda: _try_import("ui.active_random_nebula","ActiveRandomNebula")),
        ("Steam/Starfield",  _test_steam_starfield),
    ]

    # ── Run each test ─────────────────────────────────────────────────────────
    results: List[Result] = []
    n_pass = n_warn = n_fail = 0

    for group, fn in tests:
        try:
            res = fn()
        except Exception as e:
            res = Result("FAIL", group, f"Unexpected error in test harness: {e}")

        results.append(res)

        if res.status == "PASS":
            n_pass += 1
        elif res.status == "WARN":
            n_warn += 1
        else:
            n_fail += 1

        if silent and res.status == "PASS":
            continue

        if res.status == "PASS":
            print(_pass(res.label))
        elif res.status == "WARN":
            print(_warn(res.label))
        else:
            print(_fail(res.label))

        if res.detail and not silent:
            for line in res.detail.splitlines():
                print(_info(line))

    # ── Footer ────────────────────────────────────────────────────────────────
    print()
    total = len(results)
    summary = (
        f"  Results:  "
        + _c(_G,  f"{n_pass} PASS")
        + "  "
        + _c(_Y,  f"{n_warn} WARN")
        + "  "
        + _c(_R,  f"{n_fail} FAIL")
        + f"  /  {total} checks"
    )
    print(summary)
    print()

    if n_fail == 0 and n_warn == 0:
        print(_c(_G,  "  ✦  ALL SYSTEMS NOMINAL — Ready for cinematic launch."))
    elif n_fail == 0:
        print(_c(_Y,
            "  ⚠  ADVISORY WARNINGS PRESENT — Launch may proceed. "
            "Some features may use fallbacks."
        ))
    else:
        print(_c(_R,
            "  ✗  CRITICAL FAILURES DETECTED — Resolve FAIL items before launching SIG."
        ))

    print()

    return n_fail == 0


# ══════════════════════════════════════════════════════════════════════════════
#  E N T R Y   P O I N T
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ok = run_diagnostics(silent=False)
    sys.exit(0 if ok else 1)
