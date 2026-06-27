class TagManager:
    def __init__(self):
        self.tags = {}

    def add_tag(self, photo_id, tag):
        if photo_id not in self.tags:
            self.tags[photo_id] = []
        self.tags[photo_id].append(tag)

    def get_tags(self, photo_id):
        return self.tags.get(photo_id, [])

    def remove_tag(self, photo_id, tag):
        if photo_id in self.tags and tag in self.tags[photo_id]:
            self.tags[photo_id].remove(tag)

    def clear_tags(self, photo_id):
        if photo_id in self.tags:
            self.tags[photo_id] = []
