# ============================================================
# starfield_intelligent_gallery — Metadata Inspector 2.0
# Author: Mark J. Latsha
# Location: Brentwood, CA 94513
#
# Description:
#   Reads EXIF + XMP metadata from Starfield screenshots.
#   Adds:
#     - Structured XMP parsing
#     - Console (Xbox/PS) vs PC detection
#     - Metadata reconstruction heuristics
#     - Lightweight caching + safe-fail behavior
# ============================================================

from PIL import Image
import exifread
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from functools import lru_cache


class MetadataInspector:
    """
    Reads EXIF + XMP metadata from Starfield screenshots.
    Provides clean dictionaries for the UI to display.

    High-level fields:
      - filename
      - resolution
      - camera
      - timestamp
      - source: "pc", "xbox", "playstation", "unknown"
      - hdr: bool | None
      - aspect_ratio: "16:9", "21:9", etc.
      - xmp: {
          "raw": str | None,
          "fields": { ... parsed key/value pairs ... }
        }
      - summary: short human-readable description
    """

    def __init__(self):
        # You can extend this later (e.g., inject logger, config, etc.)
        pass

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def inspect(self, filepath):
        """
        Returns a metadata dictionary for the given image.
        Combines EXIF + XMP (if present) + heuristics.
        """

        base = {
            "filename": os.path.basename(filepath),
            "resolution": None,
            "camera": None,
            "timestamp": None,
            "source": "unknown",      # pc | xbox | playstation | unknown
            "hdr": None,              # True | False | None
            "aspect_ratio": None,     # e.g. "16:9"
            "xmp": {
                "raw": None,
                "fields": {}
            },
            "summary": None
        }

        # 1) Basic image info (resolution, aspect ratio)
        self._load_basic_image_info(filepath, base)

        # 2) EXIF (PC screenshots, photo tools, etc.)
        self._load_exif(filepath, base)

        # 3) XMP (Starfield PC screenshots, photo mode)
        self._load_xmp(filepath, base)

        # 4) Source detection (PC vs console)
        self._detect_source(filepath, base)

        # 5) Reconstruction heuristics (fill gaps)
        self._reconstruct_missing_metadata(filepath, base)

        # 6) Build a short summary string for the UI
        base["summary"] = self._build_summary(base)

        return base

    # --------------------------------------------------------
    # Step 1: Basic image info
    # --------------------------------------------------------

    def _load_basic_image_info(self, filepath, meta):
        try:
            with Image.open(filepath) as img:
                w, h = img.width, img.height
                meta["resolution"] = f"{w} x {h}"
                meta["aspect_ratio"] = self._compute_aspect_ratio(w, h)
        except Exception:
            meta["resolution"] = "Unknown"
            meta["aspect_ratio"] = None

    def _compute_aspect_ratio(self, width, height):
        if not width or not height:
            return None
        # Simple rational approximation
        from math import gcd
        g = gcd(width, height)
        num = width // g
        den = height // g
        return f"{num}:{den}"

    # --------------------------------------------------------
    # Step 2: EXIF
    # --------------------------------------------------------

    def _load_exif(self, filepath, meta):
        try:
            with open(filepath, "rb") as f:
                tags = exifread.process_file(f, details=False)

            if "EXIF DateTimeOriginal" in tags:
                meta["timestamp"] = self._normalize_timestamp(
                    str(tags["EXIF DateTimeOriginal"])
                )

            if "Image Model" in tags:
                meta["camera"] = str(tags["Image Model"])

        except Exception:
            # Silent fail: EXIF is optional
            pass

    def _normalize_timestamp(self, raw):
        """
        Normalize EXIF-style timestamps into ISO 8601 where possible.
        EXIF typical format: 'YYYY:MM:DD HH:MM:SS'
        """
        if not raw:
            return None
        raw = raw.strip()
        # Try EXIF format
        for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(raw, fmt)
                return dt.isoformat(sep=" ")
            except ValueError:
                continue
        # Fallback: return raw if we can't parse
        return raw

    # --------------------------------------------------------
    # Step 3: XMP
    # --------------------------------------------------------

    def _load_xmp(self, filepath, meta):
        xmp_path = filepath + ".xmp"
        if not os.path.exists(xmp_path):
            return

        try:
            with open(xmp_path, "r", encoding="utf-8") as xf:
                raw = xf.read()
                meta["xmp"]["raw"] = raw
                meta["xmp"]["fields"] = self._parse_xmp(raw)
        except Exception:
            meta["xmp"]["raw"] = "(Could not read XMP)"
            meta["xmp"]["fields"] = {}

    def _parse_xmp(self, raw_xmp):
        """
        Parse XMP XML into a flat dictionary of fields.
        This is intentionally generic but Starfield-friendly.

        Example keys we might surface:
          - sf:LocationName
          - sf:Planet
          - sf:System
          - sf:Biome
          - sf:Weather
          - sf:Pose
          - sf:CameraRoll / Pitch / Yaw
          - sf:FieldOfView
          - sf:DepthOfField
        """
        fields = {}
        if not raw_xmp:
            return fields

        # XMP often embeds namespaces; we parse loosely and flatten.
        try:
            # Some XMP files may have extra bytes; be defensive.
            xml_start = raw_xmp.find("<x:xmpmeta")
            if xml_start == -1:
                xml_start = raw_xmp.find("<xmpmeta")
            if xml_start > 0:
                raw_xmp = raw_xmp[xml_start:]

            root = ET.fromstring(raw_xmp)

            # Walk all elements, collect tag -> text
            for elem in root.iter():
                tag = elem.tag
                text = (elem.text or "").strip()
                if not text:
                    continue

                # Strip namespace: {uri}tag -> tag
                if "}" in tag:
                    tag = tag.split("}", 1)[1]

                # Build a simple key; if attributes exist, include them
                key = tag
                # If Starfield uses custom namespaces like sf:, they may appear in attributes
                # or as part of tag names; we keep it simple here.

                if key in fields:
                    # If duplicate, turn into list
                    existing = fields[key]
                    if isinstance(existing, list):
                        existing.append(text)
                    else:
                        fields[key] = [existing, text]
                else:
                    fields[key] = text

        except Exception:
            # If parsing fails, we just return empty dict
            return {}

        return fields

    # --------------------------------------------------------
    # Step 4: Source detection (PC vs console)
    # --------------------------------------------------------

    def _detect_source(self, filepath, meta):
        """
        Heuristic classification:
          - Uses resolution, filename patterns, and presence of EXIF/XMP.
          - This is intentionally conservative; "unknown" is allowed.
        """

        filename = os.path.basename(filepath).lower()
        resolution = meta.get("resolution") or ""
        xmp_fields = meta.get("xmp", {}).get("fields", {})
        has_xmp = bool(xmp_fields)
        has_exif = bool(meta.get("camera") or meta.get("timestamp"))

        # 1) If we have XMP with Starfield-like fields, assume PC.
        starfield_keys = {"LocationName", "Planet", "System", "Biome", "Weather"}
        if has_xmp and any(k in xmp_fields for k in starfield_keys):
            meta["source"] = "pc"
            return

        # 2) Filename hints (you can tune these to your actual patterns)
        if "xbox" in filename:
            meta["source"] = "xbox"
        elif "ps5" in filename or "playstation" in filename:
            meta["source"] = "playstation"

        # 3) Resolution-based hints (example heuristics; adjust as needed)
        if resolution:
            if "3840 x 2160" in resolution or "1920 x 1080" in resolution:
                # Could be PC or console; if no EXIF/XMP, lean console.
                if not has_exif and not has_xmp and meta["source"] == "unknown":
                    meta["source"] = "xbox"  # default console guess
            # Ultra-wide PC-ish resolutions
            if "3440 x 1440" in resolution or "2560 x 1440" in resolution:
                if meta["source"] == "unknown":
                    meta["source"] = "pc"

        # 4) If EXIF + XMP present, strongly PC
        if has_exif and has_xmp and meta["source"] == "unknown":
            meta["source"] = "pc"

        # If still unknown, we leave it as "unknown"

    # --------------------------------------------------------
    # Step 5: Reconstruction heuristics
    # --------------------------------------------------------

    def _reconstruct_missing_metadata(self, filepath, meta):
        """
        Try to fill in missing fields using filesystem info and heuristics.
        """

        # Timestamp reconstruction from file stats
        if not meta.get("timestamp"):
            try:
                stat = os.stat(filepath)
                # Use modification time as best guess
                dt = datetime.fromtimestamp(stat.st_mtime)
                meta["timestamp"] = dt.isoformat(sep=" ")
            except Exception:
                pass

        # Camera reconstruction: if none, but we know it's PC, label generically
        if not meta.get("camera"):
            if meta.get("source") == "pc":
                meta["camera"] = "Starfield PC Screenshot"
            elif meta.get("source") in ("xbox", "playstation"):
                meta["camera"] = f"Starfield {meta['source'].capitalize()} Screenshot"

        # HDR guess: if resolution is 4K and source is console, we can guess HDR=None (unknown)
        # You can later wire this to actual HDR detection if available.
        if meta.get("hdr") is None:
            meta["hdr"] = None  # explicit "unknown" for now

    # --------------------------------------------------------
    # Step 6: Summary builder
    # --------------------------------------------------------

    def _build_summary(self, meta):
        """
        Build a short, human-readable summary string for the UI.
        Example:
          "PC • 3840 x 2160 • 2025-01-01 12:34:56"
        """

        parts = []

        source = meta.get("source")
        if source and source != "unknown":
            parts.append(source.upper())

        res = meta.get("resolution")
        if res:
            parts.append(res)

        ts = meta.get("timestamp")
        if ts:
            parts.append(ts)

        if not parts:
            return None

        return " • ".join(parts)

    # --------------------------------------------------------
    # Optional: simple caching wrapper
    # --------------------------------------------------------

    @lru_cache(maxsize=512)
    def inspect_cached(self, filepath):
        """
        Cached version of inspect() for repeated lookups.
        Use this in your gallery when thumbnails are re-rendered often.
        """
        return self.inspect(filepath)
