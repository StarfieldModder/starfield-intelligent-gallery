# sig/script_player.py
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # points to C:\SIG\Python
SCRIPT_PATH = ROOT / "assets" / "script.json"

def load_script(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def play_shot(shot):
    print(f"PLAY SHOT: {shot['shot_id']}")
    print(f"  duration: {shot['duration']}s")
    print(f"  visual: {shot.get('visual')}")
    print(f"  camera: {shot.get('camera')}")
    print(f"  audio: {shot.get('audio')}")
    print(f"  notes: {shot.get('notes')}")
    # Placeholder for real rendering calls
    time.sleep(shot['duration'])

def play_scene(scene):
    print(f"\n=== SCENE: {scene['scene_id']} ===")
    for shot in scene.get("shots", []):
        play_shot(shot)

def main():
    script = load_script(SCRIPT_PATH)
    print(f"Loaded script: {script.get('title')}")
    for scene in script.get("scenes", []):
        play_scene(scene)
    print("\nScript playback complete.")

if __name__ == "__main__":
    main()
