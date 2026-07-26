import os
import sys

BANNER_LINE = "=" * 63
REQUIRED_FIELDS = [
    "File:",
    "Author:",
    "Co-Author:",
    "Created:",
    "Description:"
]

def validate_header(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    if len(lines) < 2:
        return False, "File too short to contain header."

    if lines[0].strip() != BANNER_LINE:
        return False, "Missing or incorrect top banner line."

    if lines[-1].strip() != BANNER_LINE:
        return False, "Missing or incorrect bottom banner line."

    missing = []
    for field in REQUIRED_FIELDS:
        if not any(field in line for line in lines):
            missing.append(field)

    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    return True, "Header OK."

def scan_repo():
    failures = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py") or file.endswith(".md"):
                path = os.path.join(root, file)
                ok, msg = validate_header(path)
                if not ok:
                    failures.append((path, msg))

    if failures:
        print("CINEMATIC HEADER VALIDATION FAILED:")
        for path, msg in failures:
            print(f" - {path}: {msg}")
        sys.exit(1)
    else:
        print("All cinematic headers validated successfully.")

if __name__ == "__main__":
    scan_repo()
