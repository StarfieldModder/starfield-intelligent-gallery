import os
import sys

EXPECTED_DIRS = [
    "sig",
    "docs",
    "tools",
    ".github"
]

EXPECTED_FILES = [
    "sig_launcher.py",
    "docs/relics-and-artifacts.md"
]

def check_dirs():
    missing = []
    for d in EXPECTED_DIRS:
        if not os.path.isdir(d):
            missing.append(d)
    return missing

def check_files():
    missing = []
    for f in EXPECTED_FILES:
        if not os.path.exists(f):
            missing.append(f)
    return missing

def main():
    missing_dirs = check_dirs()
    missing_files = check_files()

    if missing_dirs or missing_files:
        print("SIG STRUCTURE VALIDATION FAILED:")
        if missing_dirs:
            print("Missing directories:")
            for d in missing_dirs:
                print(f" - {d}")
        if missing_files:
            print("Missing files:")
            for f in missing_files:
                print(f" - {f}")
        sys.exit(1)

    print("SIG folder structure validated successfully.")

if __name__ == "__main__":
    main()
