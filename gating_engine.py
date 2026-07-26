class Artifact:
    def __init__(self, name, tier, locked=True, requirements=None):
        self.name = name
        self.tier = tier
        self.locked = locked
        self.requirements = requirements or []

class GatingEngine:
    def __init__(self, player_state):
        self.player_state = player_state

    def can_unlock(self, artifact: Artifact):
        for req in artifact.requirements:
            if not self._check_requirement(req):
                return False
        return True

    def _check_requirement(self, req):
        key = req.get("key")
        value = req.get("value")
        return self.player_state.get(key) == value

    def unlock(self, artifact: Artifact):
        if self.can_unlock(artifact):
            artifact.locked = False
            return True
        return False

if __name__ == "__main__":
    player = {"rank": "Adept", "quest_completed": True}
    relic = Artifact(
        name="Temple Relic Alpha",
        tier="Rare",
        requirements=[
            {"key": "rank", "value": "Adept"},
            {"key": "quest_completed", "value": True},
        ],
    )
    engine = GatingEngine(player)
    if engine.unlock(relic):
        print(f"{relic.name} unlocked.")
    else:
        print(f"{relic.name} remains locked.")