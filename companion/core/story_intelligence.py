from ..models.sig_sequence import SIGSequence
from ..models.sig_story_node import SIGStoryNode
from core.diagnostic_reporter import record_error


def sequence_to_story_node(seq: SIGSequence, index: int):
    """
    Converts a SIGSequence into a SIGStoryNode.
    """
    try:
        title = f"Chapter {index + 1}: {seq.theme or 'Untitled Sequence'}"
        summary = f"This sequence contains {len(seq.images)} images."
        emotion = seq.intensity or "neutral"

        return SIGStoryNode(
            title=title,
            summary=summary,
            emotion=emotion,
            images=seq.images
        )

    except Exception as exc:
        record_error(
            module="story_intelligence",
            function="sequence_to_story_node",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="warning",
            exc=exc,
        )
        return None


def build_story(sequences):
    """
    Builds a list of SIGStoryNodes from SIGSequences.
    """
    try:
        nodes = []
        for i, seq in enumerate(sequences):
            node = sequence_to_story_node(seq, i)
            if node:
                nodes.append(node)
        return nodes

    except Exception as exc:
        record_error(
            module="story_intelligence",
            function="build_story",
            line=0,
            error_type=type(exc).__name__,
            message=str(exc),
            severity="critical",
            exc=exc,
        )
        return []