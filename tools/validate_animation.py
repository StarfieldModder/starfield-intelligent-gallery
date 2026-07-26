import json
import sys

ANIMATION_FILE = "sig/temple_artifact_animation.json"

def main():
    if not os.path.exists(ANIMATION_FILE):
        print(f"Missing animation file: {ANIMATION_FILE}")
        sys.exit(1)

    with open(ANIMATION_FILE, "r") as f:
        data = json.load(f)

    required_fields = ["outer_ring", "glyphs", "rotation_speed", "drift"]

    missing = [f for f in required_fields if f not in data]
    if missing:
        print("TEMPLE ARTIFACT ANIMATION VALIDATION FAILED:")
        for m in missing:
            print(f" - Missing field: {m}")
        sys.exit(1)

    print("Temple Artifact animation validated successfully.")

if __name__ == "__main__":
    main()
