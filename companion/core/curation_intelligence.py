
from core.diagnostic_reporter import record_error


def cluster_by_theme(images):
    """
    Very simple theme clustering:
    Groups images by their first theme tag.
    """
    clusters = {}

    for img in images:
        theme = img.themes[0] if img.themes else "unknown"
        clusters.setdefault(theme, []).append(img)

    return clusters


def build_gallery_wings(clusters):
    """
    Converts clusters into 'wings' — named sections of the gallery.
    """
    wings = {}

    for theme, imgs in clusters.items():
        wings[theme] = {
            "count": len(imgs),
            "preview": imgs[:3],  # first three images
        }

    return wings


def curate(images):
    """
    Main curation pipeline:
    - Cluster images by theme
    - Build gallery wings
    """
    try:
        clusters = cluster_by_theme(images)
        wings = build_gallery_wings(clusters)

        return {
            "clusters": clusters,
            "wings": wings,
        }

    except Exception as exc:
        record_error(
            module="curation_intelligence",
            function="curate",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="warning",
            exc=exc,
        )
        return {
            "clusters": {},
            "wings": {},
        }