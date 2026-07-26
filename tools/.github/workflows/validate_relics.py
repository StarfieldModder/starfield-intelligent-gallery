import sys
import os

TARGET = "docs/relics-and-artifacts.md"

REQUIRED_SECTIONS = [
    "Relics & Artifacts",
    "Gating Rules",
    "Promotion Workflow",
    "Privacy",
    "Data Model"
]

def validate_relics():
    if not os.path.exists(TARGET):
        print(f"Missing required documentation file: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    missing = []
    for section in REQUIRED_SECTIONS:
        if section.lower() not in content.lower():
            missing.append(section)

    if missing:
        print("RELIC & ARTIFACT VALIDATION FAILED:")
        print("Missing sections:")
        for m in missing:
            print(f" - {m}")
        sys.exit(1)

    print("Relics & Artifacts documentation validated successfully.")

if __name__ == "__main__":
    validate_relics()
