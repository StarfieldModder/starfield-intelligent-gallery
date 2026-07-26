class SIGStoryNode:
    def __init__(self, title, summary, emotion=None, images=None):
        self.title = title
        self.summary = summary
        self.emotion = emotion
        self.images = images or []

    def __repr__(self):
        return f"SIGStoryNode(title={self.title}, emotion={self.emotion}, images={len(self.images)})"
