# # ════════════════════════════════════════════════════════════
#   FILE: starfield_xmp_parser.py
#
#   Author: Mark J. Latsha
#   Co-Author: Copilot (Microsoft)
#
#   Location: Brentwood, CA 94513
#   Contact: <your email here> | <your phone here>
#
#   Copyright © 2026
#
#   Description:
#       Parses XMP sidecar files associated with Starfield
#       screenshots. Extracts structured metadata for use in
#       filtering, display, and analysis within the gallery.
# ════════════════════════════════════════════════════════════
#
# starfield_xmp_parser.py  — 
# COMPLETE # ════════════════════════════════════════════════════════════
#   FILE: starfield_xmp_parser.py
#
#   Author: Mark J. Latsha
#   Co-Author: Copilot (Microsoft)
#
#   Location: Brentwood, CA 94513
#   Contact: <your email here> | <your phone here>
#
#   Copyright © 2026
#
#   Description:
#       Parses XMP sidecar files associated with Starfield
#       screenshots. Extracts structured metadata for use in
#       filtering, display, and analysis within the gallery.
# ════════════════════════════════════════════════════════════

# starfield_intelligent_gallery — Phase 4 | XMP Metadata Parser
# Reads Starfield's embedded PNG/XMP metadata natively.
# Falls back through EXIF → filename → empty dict gracefully.
# Developed: May 2026 | Mark — Brentwood, CA
# ============================================================
# INSTALL:   pip install Pillow exifread
# INTEGRATE: from starfield_xmp_parser import parse_image, scan_and_populate
# ============================================================

import struct, zlib, json, re, os, datetime
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import exifread
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False

SIDECAR_EXT = ".sfmeta.json"

# ── Starfield XMP Namespace Map ────────────────────────────
NS = {
    "rdf":   "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xmp":   "http://ns.adobe.com/xap/1.0/",
    "dc":    "http://purl.org/dc/elements/1.1/",
    "exif":  "http://ns.adobe.com/exif/1.0/",
    "tiff":  "http://ns.adobe.com/tiff/1.0/",
    "photoshop":"http://ns.adobe.com/photoshop/1.0/",
    # Bethesda may use custom namespace — handle generically
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

# ── Starfield filter ID → display name ─────────────────────
FILTER_MAP = {
    "0": "None", "1": "Mercury Era", "2": "Gemini Era",
    "3": "Apollo Era", "4": "Dusty", "5": "Binary",
    "6": "Astral", "7": "Cinematic", "8": "Noir",
    "9": "Sepia", "10": "Vivid", "11": "Muted",
    "12": "Cool", "13": "Warm", "14": "High Contrast",
    "15": "Soft", "16": "Vintage", "17": "Neon",
}
CAMERA_MAP = {"0":"POV","1":"Orbital","2":"Free","3":"Selfie"}
POSE_MAP = {
    "0":"None","1":"Boxer","2":"Hands-on Hips",
    "3":"Jump","4":"Sit","5":"Wave",
}

IMAGE_EXTS = {".jpg",".jpeg",".png",".bmp",".gif",".tif",".tiff",".webp"}


# ══════════════════════════════════════════════════════════
#  PNG CHUNK READER
# ══════════════════════════════════════════════════════════

def _read_png_chunks(path: str) -> list[tuple[bytes, bytes]]:
    """Return list of (chunk_type, chunk_data) from a PNG file."""
    chunks = []
    try:
        with open(path, "rb") as f:
            sig = f.read(8)
            if sig != b"\x89PNG\r\n\x1a\n":
                return chunks
            while True:
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    break
                length = struct.unpack(">I", length_bytes)[0]
                chunk_type = f.read(4)
                data = f.read(length)
                _crc = f.read(4)
                chunks.append((chunk_type, data))
                if chunk_type == b"IEND":
                    break
    except Exception:
        pass
    return chunks


def _extract_xmp_from_png(path: str) -> Optional[str]:
    """Extract raw XMP XML string embedded in a PNG file."""
    for chunk_type, data in _read_png_chunks(path):
        # iTXt chunk: keyword + data (keyword may be "XML:com.adobe.xmp")
        if chunk_type == b"iTXt":
            try:
                null = data.index(b"\x00")
                keyword = data[:null].decode("latin-1")
                if "xmp" in keyword.lower() or "adobe" in keyword.lower():
                    rest = data[null + 1:]
                    compressed = rest[0]
                    if compressed:
                        rest = rest[2:]
                        null2 = rest.index(b"\x00")
                        rest = rest[null2 + 1:]
                        null3 = rest.index(b"\x00")
                        payload = rest[null3 + 1:]
                        try:
                            payload = zlib.decompress(payload)
                        except Exception:
                            pass
                    else:
                        rest = rest[2:]
                        null2 = rest.index(b"\x00")
                        rest = rest[null2 + 1:]
                        null3 = rest.index(b"\x00")
                        payload = rest[null3 + 1:]
                    xmp = payload.decode("utf-8", errors="replace")
                    if "<rdf:" in xmp or "<x:xmpmeta" in xmp:
                        return xmp
            except Exception:
                pass
        elif chunk_type in (b"tEXt", b"zTXt"):
            try:
                null = data.index(b"\x00")
                keyword = data[:null].decode("latin-1")
                if "xmp" in keyword.lower():
                    payload = data[null + 1:]
                    if chunk_type == b"zTXt":
                        payload = zlib.decompress(payload[1:])
                    xmp = payload.decode("utf-8", errors="replace")
                    if "<rdf:" in xmp:
                        return xmp
            except Exception:
                pass
    return None


# ══════════════════════════════════════════════════════════
#  XMP PARSER
# ══════════════════════════════════════════════════════════

def _xml_find(root, *tags) -> Optional[str]:
    """Search XML tree for a tag value across all namespaces."""
    for elem in root.iter():
        local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if local in tags:
            text = (elem.text or "").strip()
            if text:
                return text
        for attr_name, attr_val in elem.attrib.items():
            local_attr = attr_name.split("}")[-1]
            if local_attr in tags and attr_val.strip():
                return attr_val.strip()
    return None


def _parse_xmp(xmp_string: str) -> dict:
    """Parse XMP XML and extract Starfield-relevant fields."""
    result = {}
    try:
        root = ET.fromstring(xmp_string)
    except Exception:
        return result

    for tag in ("DateTimeOriginal", "CreateDate", "ModifyDate",
                "DateTime", "date"):
        val = _xml_find(root, tag)
        if val:
            result["xmp_date"] = val
            break

    for tag in ("description", "Description", "caption", "title"):
        val = _xml_find(root, tag)
        if val:
            result["xmp_description"] = val
            break

    val = _xml_find(root, "creator", "Creator", "Author")
    if val:
        result["xmp_creator"] = val

    val = _xml_find(root, "CreatorTool", "Software", "software")
    if val:
        result["xmp_software"] = val

    val = _xml_find(root, "Rating", "rating")
    if val:
        result["xmp_rating"] = val

    for elem in root.iter():
        local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        ns    = elem.tag.split("{")[1].split("}")[0] if "{" in elem.tag else ""
        if "bethesda" in ns.lower() or "starfield" in ns.lower():
            text = (elem.text or "").strip()
            if text:
                result[f"sf_xmp_{local.lower()}"] = text
            for attr_k, attr_v in elem.attrib.items():
                ak = attr_k.split("}")[-1]
                if attr_v.strip():
                    result[f"sf_xmp_{ak.lower()}"] = attr_v.strip()

    for key in ("sf_xmp_filterid", "sf_xmp_filter"):
        if key in result:
            result["sf_filter"] = FILTER_MAP.get(result[key], result[key])
    for key in ("sf_xmp_cameraid", "sf_xmp_camera"):
        if key in result:
            result["sf_camera"] = CAMERA_MAP.get(result[key], result[key])
    for key in ("sf_xmp_poseid", "sf_xmp_pose"):
        if key in result:
            result["sf_pose"] = POSE_MAP.get(result[key], result[key])

    return result


# ══════════════════════════════════════════════════════════
#  EXIF FALLBACK
# ══════════════════════════════════════════════════════════

def _parse_exif_fallback(path: str) -> dict:
    """Extract basic EXIF data as fallback if XMP unavailable."""
    result = {}
    if not EXIF_AVAILABLE:
        return result
    try:
        with open(path, "rb") as f:
            tags = exifread.process_file(f, details=False)
        for exif_tag, our_key in [
            ("Image Make",            "exif_make"),
            ("Image Model",           "exif_model"),
            ("EXIF DateTimeOriginal", "xmp_date"),
            ("Image Software",        "xmp_software"),
        ]:
            if exif_tag in tags:
                result[our_key] = str(tags[exif_tag])
    except Exception:
        pass
    return result


# ══════════════════════════════════════════════════════════
#  FILENAME PARSER
# ══════════════════════════════════════════════════════════

def _parse_filename(path: str) -> dict:
    """
    Starfield names screenshots like:
    StarfieldPhoto_2024-07-15_182345.png
    Extract date/time when possible.
    """
    result = {}
    stem = Path(path).stem
    m = re.search(r"(\d{4}[-_]\d{2}[-_]\d{2})[-_T](\d{6}|\d{2}:\d{2}:\d{2})?",
                  stem)
    if m:
        date_str = m.group(1).replace("_", "-")
        time_str = m.group(2) or ""
        if time_str and len(time_str) == 6:
            time_str = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
        result["filename_date"] = f"{date_str} {time_str}".strip()
    return result


# ══════════════════════════════════════════════════════════
#  PILLOW IMAGE INFO
# ══════════════════════════════════════════════════════════

def _parse_pillow_info(path: str) -> dict:
    """Extract metadata from Pillow's image.info dict."""
    result = {}
    if not PIL_AVAILABLE:
        return result
    try:
        with Image.open(path) as img:
            info = img.info or {}
            for key, val in info.items():
                k = str(key).lower()
                v = str(val)
                if k in ("title", "description", "comment", "author",
                         "software", "creation time", "source"):
                    result[f"png_{k.replace(' ','_')}"] = v
            if "xmp" in info:
                xmp_data = info["xmp"]
                if isinstance(xmp_data, bytes):
                    xmp_data = xmp_data.decode("utf-8", errors="replace")
                result.update(_parse_xmp(xmp_data))
            result["img_width"]  = str(img.width)
            result["img_height"] = str(img.height)
            result["img_format"] = img.format or "—"
            result["img_mode"]   = img.mode
    except Exception:
        pass
    return result


# ══════════════════════════════════════════════════════════
#  MAIN PARSE FUNCTION
# ══════════════════════════════════════════════════════════

def parse_image(path: str) -> dict:
    """
    Parse all available metadata from a Starfield screenshot.

    Returns a merged dict from (in priority order):
      1. XMP embedded in PNG iTXt/tEXt chunks
      2. Pillow image.info metadata
      3. EXIF fallback (via exifread)
      4. Filename-based date extraction

    Usage:
        from starfield_xmp_parser import parse_image
        meta = parse_image("path/to/photo.png")
        print(meta.get("sf_filter", "No filter data"))
    """
    result = {}
    p = Path(path)

    try:
        stat = p.stat()
        result["file_size"]     = stat.st_size
        result["file_modified"] = datetime.datetime.fromtimestamp(
            stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    if p.suffix.lower() == ".png":
        xmp_str = _extract_xmp_from_png(str(path))
        if xmp_str:
            result["xmp_found"] = True
            result.update(_parse_xmp(xmp_str))
        else:
            result["xmp_found"] = False

    result.update(_parse_pillow_info(str(path)))

    if "xmp_date" not in result:
        result.update(_parse_exif_fallback(str(path)))

    result.update(_parse_filename(str(path)))

    result["best_date"] = (
        result.get("xmp_date") or
        result.get("exif_date") or
        result.get("filename_date") or
        result.get("file_modified") or "—"
    )
    return result


# ══════════════════════════════════════════════════════════
#  SIDECAR AUTO-POPULATION
# ══════════════════════════════════════════════════════════

def populate_sidecar(image_path: str,
                     overwrite: bool = False) -> dict:
    """
    Parse image metadata and write/update its .sfmeta.json sidecar.
    If sidecar exists and overwrite=False, only fills EMPTY fields.
    Returns the final sidecar dict.
    """
    sp = str(Path(image_path).with_suffix("")) + SIDECAR_EXT
    existing = {}
    if Path(sp).exists():
        try:
            with open(sp, encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass

    meta = parse_image(image_path)

    mapping = {
        "sf_filter":  "sf_filter",
        "sf_camera":  "sf_angle",
        "sf_pose":    "sf_pose",
        "xmp_date":   "sf_date",
        "best_date":  "sf_date",
        "img_width":  "_img_width",
        "img_height": "_img_height",
        "img_format": "_img_format",
        "xmp_software": "_software",
    }
    for src_key, dst_key in mapping.items():
        val = meta.get(src_key, "")
        if not val:
            continue
        if overwrite or not existing.get(dst_key):
            existing[dst_key] = val

    existing["_xmp_parsed"] = {
        k: v for k, v in meta.items()
        if k.startswith("xmp_") or k.startswith("sf_xmp_")
           or k.startswith("png_")
    }
    existing["_xmp_scan_time"] = datetime.datetime.now().isoformat(
        timespec="seconds")
    existing["_image_path"] = image_path
    if "_version" not in existing:
        existing["_version"] = "1.0"

    try:
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        print(f"[XMP] Could not write sidecar: {e}")

    return existing


# ══════════════════════════════════════════════════════════
#  BATCH SCAN
# ══════════════════════════════════════════════════════════

def scan_folder(folder: str,
                overwrite: bool = False,
                on_progress=None) -> dict:
    """
    Scan all images in a folder, populate sidecars from XMP.
    on_progress(current, total, path) for UI progress bars.
    Returns summary: {"scanned":n, "xmp_found":n, "errors":n}
    """
    p = Path(folder)
    if not p.is_dir():
        return {"scanned": 0, "xmp_found": 0, "errors": 0}

    images = sorted(
        f for f in p.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS)

    total     = len(images)
    xmp_found = 0
    errors    = 0

    for i, img_path in enumerate(images):
        if on_progress:
            on_progress(i + 1, total, str(img_path))
        try:
            sidecar = populate_sidecar(str(img_path), overwrite=overwrite)
            if sidecar.get("_xmp_parsed"):
                xmp_found += 1
        except Exception as e:
            print(f"[XMP] Error processing {img_path.name}: {e}")
            errors += 1

    return {"scanned": total, "xmp_found": xmp_found, "errors": errors}


# ══════════════════════════════════════════════════════════
#  STANDALONE
# ══════════════════════════════════════════════════════════
# ============================================================
#  COMPATIBILITY WRAPPER FOR GALLERYAPP
# ============================================================

def extract_starfield_metadata(path: str) -> dict:
    """
    Compatibility wrapper expected by starfield_gallery.py.
    Safely returns parsed metadata or {} on failure.
    """
    try:
        return parse_image(path)
    except Exception:
        return {}

if __name__ == "__main__":
    import sys
    from tkinter import filedialog, Tk

    root = Tk(); root.withdraw()
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = filedialog.askopenfilename(
            title="Choose a Starfield screenshot to parse",
            filetypes=[("Images","*.png *.jpg *.jpeg *.bmp"),
                       ("All","*.*")])
    if not target:
        print("No file selected."); sys.exit()

    print(f"\n◈ Parsing: {Path(target).name}")
    print("─" * 56)
    meta = parse_image(target)
    for k, v in sorted(meta.items()):
        if k.startswith("_xmp_parsed"):
            continue
        print(f"  {k:<28} {v}")
    print("─" * 56)
    sidecar = populate_sidecar(target)
    print(f"  Sidecar written: {Path(target).stem}.sfmeta.json")
    print(f"  XMP found: {meta.get('xmp_found','N/A')}")
    print(f"  Best date: {meta.get('best_date','—')}")