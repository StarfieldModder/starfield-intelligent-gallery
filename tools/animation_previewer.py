import json
import os

ANIMATION_FILE = "sig/temple_artifact_animation.json"

def main():
    print("=== TEMPLE ARTIFACT ANIMATION PREVIEWER ===")

    if not os.path.exists(ANIMATION_FILE):
        print(f"Missing animation file: {ANIMATION_FILE}")
        return

    with open(ANIMATION_FILE, "r") as f:
        data = json.load(f)

    print("Outer ring:", data.get("outer_ring"))
    print("Glyphs:", data.get("glyphs"))
    print("Rotation speed:", data.get("rotation_speed"))
    print("Drift:", data.get("drift"))

    print("Preview complete (text mode).")

if __name__ == "__main__":
    main()
