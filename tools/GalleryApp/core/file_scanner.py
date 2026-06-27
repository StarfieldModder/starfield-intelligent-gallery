import os
from pathlib import Path

# Default Starfield screenshot directory (can be overridden in settings)
DEFAULT_SCREENSHOT_DIR = Path.home() / "Documents" / "My Games" / "Starfield" / "Data" / "Textures" / "Photos"

def find_screenshots(directory: Path = DEFAULT_SCREENSHOT_DIR):
    """
    Scan the given directory for Starfield screenshot files.
    Returns a list of absolute file paths.
    """

    if not directory.exists():
        return []

    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tga"}

    screenshots = []

    for root, _, files in os.walk(directory):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in valid_extensions:
                screenshots.append(Path(root) / file)

    return screenshots
