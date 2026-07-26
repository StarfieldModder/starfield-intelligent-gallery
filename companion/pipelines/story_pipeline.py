from ..core.story_intelligence import build_story
from ..core.accessibility_intelligence import accessibility_wrap

def run_story_pipeline(sequences):
    print("Running Story Pipeline...")
    story_nodes = build_story(sequences)
    result = {
        "status": "ok",
        "story_nodes": story_nodes,
    }
    return accessibility_wrap(result)
