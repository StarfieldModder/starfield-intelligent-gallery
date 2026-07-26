from ..core.creative_intelligence import analyze_images
from ..core.accessibility_intelligence import accessibility_wrap

def run_creative_pipeline(images):
    print("Running Creative Pipeline...")
    analyzed = analyze_images(images)
    result = {
        "status": "ok",
        "images_processed": len(analyzed),
        "images": analyzed,
    }
    return accessibility_wrap(result)

