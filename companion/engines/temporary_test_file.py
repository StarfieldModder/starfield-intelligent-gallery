import sys
from pathlib import Path

# Add parent folder to Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from engines.ingestion_engine import build_gallery_db

sources = [
    r"C:\SIG\media",
    r"C:\SIG\artifact_renders"
]

output = r"C:\SIG\data\gallery_db.json"

build_gallery_db(sources, output)
print("Gallery DB written to:", output)
