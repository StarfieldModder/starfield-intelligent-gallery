from ..core.myth_intelligence import build_myth_for_artifacts
from ..core.accessibility_intelligence import accessibility_wrap

def run_myth_pipeline(artifacts):
    print("Running Myth Pipeline...")
    myth = build_myth_for_artifacts(artifacts)
    result = {
        "status": "ok",
        "myth_elements": myth,
    }
    return accessibility_wrap(result)
