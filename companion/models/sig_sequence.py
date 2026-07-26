class SIGSequence:
    def __init__(self, images=None, theme=None, intensity=None):
        self.images = images or []
        self.theme = theme
        self.intensity = intensity

    def __repr__(self):
        return f"SIGSequence(theme={self.theme}, intensity={self.intensity}, images={len(self.images)} images)"
