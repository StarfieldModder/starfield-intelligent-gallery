from ..core.curation_intelligence import curate
from ..core.accessibility_intelligence import accessibility_wrap

def run_curation_pipeline(images):
    print("Running Curation Pipeline...")
    curated = curate(images)
    result = {
        "status": "ok",
        "clusters": curated["clusters"],
        "wings": curated["wings"],
    }
    return accessibility_wrap(result)
