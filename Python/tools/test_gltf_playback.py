from pygltflib import GLTF2
import sys
from pathlib import Path

def inspect_gltf(path):
    g = GLTF2().load(path)
    print("Scenes:", len(g.scenes or []))
    print("Nodes:", len(g.nodes or []))
    print("Meshes:", len(g.meshes or []))
    print("Animations:", len(g.animations or []))
    if g.animations:
        for i, a in enumerate(g.animations):
            print(f"Animation {i}: channels={len(a.channels or [])}, samplers={len(a.samplers or [])}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_gltf_playback.py path/to/test_character.glb")
        sys.exit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        print("File not found:", p)
        sys.exit(1)
    inspect_gltf(str(p))
