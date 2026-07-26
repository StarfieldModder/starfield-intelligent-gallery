from ..models.sig_image import SIGImage
from core.diagnostic_reporter import record_error


def analyze_image(image: SIGImage):
    """
    Basic creative analysis:
    - Tags based on filename
    - Simple theme guess
    - Placeholder emotion
    """
    try:
        name = image.path.lower()

        tags = []
        themes = []
        emotion = None

        if "neon" in name:
            tags.append("city")
            themes.append("urban")
            emotion = "electric"
        if "temple" in name:
            tags.append("artifact")
            themes.append("mystic")
            emotion = "mysterious"
        if "ship" in name:
            tags.append("spacecraft")
            themes.append("exploration")
            emotion = "adventurous"

        image.tags.extend(tags)
        image.themes.extend(themes)
        image.emotion = image.emotion or emotion

        return image

    except Exception as exc:
        record_error(
            module="creative_intelligence",
            function="analyze_image",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="warning",
            exc=exc,
        )
        return image


def analyze_images(images):
    try:
        return [analyze_image(img) for img in images]
    except Exception as exc:
        record_error(
            module="creative_intelligence",
            function="analyze_images",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="critical",
            exc=exc,
        )
        return []