import os
import sys

ASSET_DIR = "assets"

def main():
    if not os.path.isdir(ASSET_DIR):
        print(f"Asset directory '{ASSET_DIR}' missing.")
        sys.exit(1)

    missing = []
    for root, _, files in os.walk(ASSET_DIR):
        for f in files:
            if os.path.getsize(os.path.join(root, f)) == 0:
                missing.append(os.path.join(root, f))

    if missing:
        print("ASSET INTEGRITY CHECK FAILED:")
        for m in missing:
            print(f" - Empty or corrupted asset: {m}")
        sys.exit(1)

    print("All SIG assets validated successfully.")

if __name__ == "__main__":
    main()
