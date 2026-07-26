class SIGImage:
    def __init__(self, path, tags=None, themes=None, emotion=None):
        self.path = path
        self.tags = tags or []
        self.themes = themes or []
        self.emotion = emotion

    def __repr__(self):
        return f"SIGImage(path={self.path}, tags={self.tags}, themes={self.themes}, emotion={self.emotion})"
