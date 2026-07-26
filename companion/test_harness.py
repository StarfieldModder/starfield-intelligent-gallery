from companion.pipelines.creative_pipeline import run_creative_pipeline
from companion.pipelines.curation_pipeline import run_curation_pipeline
from companion.pipelines.story_pipeline import run_story_pipeline
from companion.pipelines.myth_pipeline import run_myth_pipeline

from companion.models.sig_image import SIGImage
from companion.models.sig_sequence import SIGSequence

def build_sample_images():
    return [
        SIGImage("neon_city_01.png"),
        SIGImage("temple_artifact_02.jpg"),
        SIGImage("ship_drifting_03.png"),
        SIGImage("random_scenery_04.png"),
    ]

def build_sample_sequence(images):
    return SIGSequence(
        images=images[:3],
        theme="Exploration",
        intensity="adventurous"
    )

def build_sample_artifacts():
    return [
        "Temple Relic Alpha",
        "Temple Relic Beta",
        "Glyph of the Outer Ring"
    ]

def main():
    print("\n=== SIG COMPANION MODE — TEST HARNESS ===\n")

    # Sample data
    images = build_sample_images()
    sequence = build_sample_sequence(images)
    artifacts = build_sample_artifacts()

    # Run pipelines
    print("Running Creative Pipeline...")
    creative_result = run_creative_pipeline(images)
    print("Creative Result:", creative_result, "\n")

    print("Running Curation Pipeline...")
    curation_result = run_curation_pipeline(images)
    print("Curation Result:", curation_result, "\n")

    print("Running Story Pipeline...")
    story_result = run_story_pipeline([sequence])
    print("Story Result:", story_result, "\n")

    print("Running Myth Pipeline...")
    myth_result = run_myth_pipeline(artifacts)
    print("Myth Result:", myth_result, "\n")

    print("=== TEST HARNESS COMPLETE ===\n")

if __name__ == "__main__":
    main()
