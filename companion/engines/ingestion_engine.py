# ingestion_engine.py

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif",
                        ".mp4", ".mov", ".mkv", ".avi"}

from core.diagnostic_reporter import record_error


def compute_content_hash(file_path, chunk_size=8192):
    """Compute a stable content hash for a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def scan_media_sources(source_paths):
    """
    Scan one or more folders and return a list of media items.
    source_paths: list of strings or Path objects.
    """
    media_items = []

    for source in source_paths:
        source = Path(source)
        if not source.exists():
            continue

        for root, dirs, files in os.walk(source):
            for name in files:
                ext = Path(name).suffix.lower()
                if ext not in SUPPORTED_EXTENSIONS:
                    continue

                full_path = Path(root) / name
                stat = full_path.stat()

                item = {
                    "id": compute_content_hash(full_path),
                    "path": str(full_path),
                    "type": "video" if ext in {".mp4", ".mov", ".mkv", ".avi"} else "image",
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }

                media_items.append(item)

    return media_items

def save_gallery_db(media_items, output_path):
    """
    Save media items to a JSON database file.
    """
    output_path = Path(output_path)
    db = {
        "media": media_items,
        "generated_at": datetime.now().isoformat(),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


def build_gallery_db(source_paths, output_path):
    try:
        media_items = scan_media_sources(source_paths)
        save_gallery_db(media_items, output_path)
        return output_path

    except Exception as exc:
        record_error(
            module="ingestion_engine",
            function="build_gallery_db",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="critical",
            exc=exc,
        )
        return None
