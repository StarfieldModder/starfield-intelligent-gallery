r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ███████╗███████╗██╗  ██╗████████╗ ██████╗ ██████╗                  ║
║   ██╔══██╗██╔════╝██╔════╝██║ ██╔╝╚══██╔══╝██╔═══██╗██╔══██╗                 ║
║   ██║  ██║█████╗  ███████╗█████╔╝    ██║   ██║   ██║██████╔╝                 ║
║   ██║  ██║██╔══╝  ╚════██║██╔═██╗    ██║   ██║   ██║██╔═══╝                  ║
║   ██████╔╝███████╗███████║██║  ██╗   ██║   ╚██████╔╝██║                      ║
║   ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝                      ║
║                                                                              ║
║              S I G   D E S K T O P   I N S T A L L E R                       ║
║              "One click.  The Carrier Deck awaits."                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  sig_install_shortcut.py                                       ║
║  Location   :  C:\SIG\sig_install_shortcut.py                                ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineering Collaborator)               ║
║  Created    :  Thursday, July 2, 2026  6:17 AM PDT                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS DOES — run it once, never again                                   ║
║                                                                              ║
║    1. Draws the SIG hexagon icon  →  C:\SIG\Assets\SIG.ico                   ║
║    2. Writes SIG.bat              →  C:\SIG\SIG.bat  (the real launcher)     ║
║    3. Places SIG shortcut         →  Desktop\SIG.lnk  (double-click to play) ║
║    4. Places SIG shortcut         →  Start Menu\SIG.lnk  (bonus)             ║
║                                                                              ║
║  HOW TO RUN  (one time only)                                                 ║
║    (.venv) PS C:\SIG> python sig_install_shortcut.py                         ║
║                                                                              ║
║  AFTER THAT                                                                  ║
║    Double-click the ⬡ SIG icon on your Desktop.  That's it.                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import os
import struct
import sys
import zlib
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────────────────

SIG_ROOT    = Path(__file__).resolve().parent          # C:\SIG
ASSETS_DIR  = SIG_ROOT / "Assets"
ICON_PATH   = ASSETS_DIR / "SIG.ico"
BAT_PATH    = SIG_ROOT / "SIG.bat"
VENV_PYTHON = SIG_ROOT / ".venv" / "Scripts" / "python.exe"
LAUNCHER    = SIG_ROOT / "sig_launcher.py"


# ─────────────────────────────────────────────────────────────────────────────
#  Step 1 — Generate SIG.ico  (cobalt hexagon on dark background)
#           Written in pure Python — no Pillow required.
#           Falls back to Pillow if available for sharper edges.
# ─────────────────────────────────────────────────────────────────────────────

def _draw_hex_png_pillow(size: int) -> bytes:
    """Generate a SIG hexagon PNG using Pillow (preferred)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (size, size), (10, 12, 20, 255))   # SIG near-black
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2
    margin = size * 0.08

    # Outer hex (cobalt fill with glow gradient effect via concentric hexes)
    for layer in range(12, 0, -1):
        r = (size / 2 - margin) * (layer / 12)
        alpha = int(30 + 200 * (layer / 12))
        blue  = min(255, 100 + int(120 * (layer / 12)))
        green = min(255, 60  + int(80  * (layer / 12)))
        pts = [
            (cx + r * math.cos(math.radians(60 * k - 30)),
             cy + r * math.sin(math.radians(60 * k - 30)))
            for k in range(6)
        ]
        draw.polygon(pts, fill=(30, green, blue, alpha))

    # Bright hex border
    r_outer = size / 2 - margin
    border_pts = [
        (cx + r_outer * math.cos(math.radians(60 * k - 30)),
         cy + r_outer * math.sin(math.radians(60 * k - 30)))
        for k in range(6)
    ]
    draw.polygon(border_pts, outline=(80, 160, 255, 255))

    # Inner smaller hex — white-silver centre
    r_inner = r_outer * 0.35
    inner_pts = [
        (cx + r_inner * math.cos(math.radians(60 * k - 30)),
         cy + r_inner * math.sin(math.radians(60 * k - 30)))
        for k in range(6)
    ]
    draw.polygon(inner_pts, fill=(200, 215, 240, 220))

    # Central dot
    dot_r = r_outer * 0.08
    draw.ellipse(
        [cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
        fill=(255, 255, 255, 255)
    )

    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_ico_from_png(png_bytes: bytes, size: int) -> bytes:
    """
    Wrap a PNG into a valid .ico file.
    ICO format: header + directory entry + PNG data.
    """
    # ICO header: signature (2), type (2=ico = 1), count (2)
    header = struct.pack("<HHH", 0, 1, 1)

    # Directory entry: w, h, colours, reserved, planes, bpp, datasize, offset
    data_size   = len(png_bytes)
    data_offset = 6 + 16                              # header + one dir entry
    w = h = size if size < 256 else 0                 # 0 means 256 in ICO spec
    dir_entry   = struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, data_size, data_offset)

    return header + dir_entry + png_bytes


def generate_icon() -> bool:
    """Generate SIG.ico and return True on success."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    for size in (256,):
        try:
            png = _draw_hex_png_pillow(size)
            ico = _make_ico_from_png(png, size)
            ICON_PATH.write_bytes(ico)
            print(f"  ✅  Icon generated  →  {ICON_PATH}")
            return True
        except ImportError:
            # Pillow not available — write a minimal 16×16 placeholder icon
            print("  ⚠️   Pillow not found — writing minimal placeholder icon.")
            print("       pip install Pillow  for the full cobalt hexagon.")
            _write_minimal_ico()
            return True
        except Exception as exc:
            print(f"  ❌  Icon generation failed: {exc}")
            return False


def _write_minimal_ico() -> None:
    """
    Minimal 16×16 ICO with a cobalt pixel field.
    No external dependencies.
    """
    size = 16
    # Build a raw BGRA pixel array (16×16, cobalt blue)
    row = bytes([50, 130, 200, 255] * size)   # BGRA cobalt
    pixels = row * size

    # BITMAPINFOHEADER (40 bytes)
    bih = struct.pack(
        "<IiiHHIIiiII",
        40,         # header size
        size,       # width
        size * 2,   # height (doubled for ICO: XOR + AND mask)
        1,          # planes
        32,         # bpp
        0,          # compression (BI_RGB)
        0,          # image size (0 = uncompressed)
        0, 0,       # X/Y pixels per metre
        0, 0,       # colours used / important
    )

    xor_mask = pixels
    and_mask = bytes(size * ((size + 7) // 8))  # all opaque

    dib     = bih + xor_mask + and_mask
    header  = struct.pack("<HHH", 0, 1, 1)
    dir_ent = struct.pack(
        "<BBBBHHII",
        size, size,
        0, 0, 1, 32,
        len(dib),
        6 + 16,
    )
    ICON_PATH.write_bytes(header + dir_ent + dib)
    print(f"  ✅  Minimal icon written  →  {ICON_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
#  Step 2 — Write SIG.bat
# ─────────────────────────────────────────────────────────────────────────────

def write_bat() -> bool:
    """
    Write a .bat launcher that activates the venv and runs sig_launcher.py.
    The window title shows SIG so it's recognisable in the taskbar.
    """
    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else "python"

    bat_lines = [
        "@echo off",
        f'title Starfield Intelligent Gallery',
        f'cd /d "{SIG_ROOT}"',
    ]

    if VENV_PYTHON.exists():
        bat_lines += [
            f'call "{SIG_ROOT}\\.venv\\Scripts\\activate.bat"',
        ]
    else:
        bat_lines += [
            "rem  .venv not found at C:\\SIG\\.venv — using system Python",
        ]

    bat_lines += [
        f'"{python_exe}" "{LAUNCHER}"',
        "exit",
    ]

    BAT_PATH.write_text("\r\n".join(bat_lines), encoding="utf-8")
    print(f"  ✅  Launcher script   →  {BAT_PATH}")
    return True


# ─────────────────────────────────────────────────────────────────────────────
#  Step 3 — Create Desktop & Start Menu Shortcuts
# ─────────────────────────────────────────────────────────────────────────────

def _get_special_folder(csidl: int) -> Path:
    """Return a Windows special folder path using ctypes (no pywin32 needed)."""
    import ctypes
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf)
    return Path(buf.value)


def create_shortcut_via_pywin32(target_path: Path, shortcut_path: Path) -> bool:
    """Create shortcut using pywin32 (preferred — gives full .lnk support)."""
    try:
        import win32com.client
        shell    = win32com.client.Dispatch("WScript.Shell")
        lnk      = shell.CreateShortcut(str(shortcut_path))
        lnk.TargetPath       = str(target_path)
        lnk.WorkingDirectory = str(SIG_ROOT)
        lnk.IconLocation     = f"{ICON_PATH},0"
        lnk.Description      = "Starfield Intelligent Gallery"
        lnk.WindowStyle      = 1     # normal window
        lnk.Save()
        return True
    except ImportError:
        return False
    except Exception as exc:
        print(f"  ⚠️   pywin32 error: {exc}")
        return False


def create_shortcut_via_ps(target_path: Path, shortcut_path: Path) -> bool:
    """Fallback: create shortcut via PowerShell (no extra packages needed)."""
    import subprocess
    icon_str = str(ICON_PATH).replace("\\", "\\\\")
    ps_script = (
        f'$ws = New-Object -ComObject WScript.Shell; '
        f'$sc = $ws.CreateShortcut("{shortcut_path}"); '
        f'$sc.TargetPath = "{target_path}"; '
        f'$sc.WorkingDirectory = "{SIG_ROOT}"; '
        f'$sc.IconLocation = "{icon_str},0"; '
        f'$sc.Description = "Starfield Intelligent Gallery"; '
        f'$sc.WindowStyle = 1; '
        f'$sc.Save()'
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True
    )
    return result.returncode == 0


def install_shortcuts() -> None:
    """Install Desktop and Start Menu shortcuts."""
    DESKTOP_CSIDL    = 0x0010   # CSIDL_DESKTOPDIRECTORY
    STARTMENU_CSIDL  = 0x000B   # CSIDL_STARTMENU

    locations = []
    try:
        desktop   = _get_special_folder(DESKTOP_CSIDL)
        start_menu = _get_special_folder(STARTMENU_CSIDL) / "Programs"
        start_menu.mkdir(parents=True, exist_ok=True)
        locations = [
            (desktop   / "SIG.lnk",  "Desktop"),
            (start_menu / "SIG.lnk", "Start Menu"),
        ]
    except Exception as exc:
        print(f"  ⚠️   Could not locate Desktop/Start Menu: {exc}")
        # Fallback: put shortcut next to this script
        locations = [(SIG_ROOT / "SIG.lnk", "C:\\SIG folder")]

    for shortcut_path, label in locations:
        success = create_shortcut_via_pywin32(BAT_PATH, shortcut_path)
        if not success:
            success = create_shortcut_via_ps(BAT_PATH, shortcut_path)
        if success:
            print(f"  ✅  Shortcut installed  →  {label}  ({shortcut_path.name})")
        else:
            print(f"  ❌  Could not create shortcut in {label}")
            print(f"      Manually create a shortcut to:  {BAT_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

BANNER = """
  ╔══════════════════════════════════════════════════════╗
  ║    ⬡  SIG Desktop Installer                         ║
  ║    Starfield Intelligent Gallery  —  July 2, 2026   ║
  ╚══════════════════════════════════════════════════════╝
"""

def main() -> None:
    print(BANNER)

    # ── Step 1 ─────────────────────────────────────────────────────────────
    print("  [ 1 / 3 ]  Generating SIG icon...")
    generate_icon()

    # ── Step 2 ─────────────────────────────────────────────────────────────
    print("\n  [ 2 / 3 ]  Writing launcher script...")
    write_bat()

    # ── Step 3 ─────────────────────────────────────────────────────────────
    print("\n  [ 3 / 3 ]  Installing shortcuts...")
    install_shortcuts()

    # ── Summary ────────────────────────────────────────────────────────────
    print("""
  ══════════════════════════════════════════════════════
  ✅  Done!

  Look for the  ⬡ SIG  icon on your Desktop.
  Double-click it at any time to launch SIG.

  No terminal needed.  No commands to remember.
  One icon.  One click.  The Carrier Deck awaits.
  ══════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    main()

