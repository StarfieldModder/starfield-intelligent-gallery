from sig.gating_engine import Artifact, GatingEngine

def main():
    print("=== SIG ARTIFACT UNLOCK SIMULATOR ===")

    player_state = {
        "rank": "Adept",
        "quest_completed": True,
    }

    relics = [
        Artifact("Temple Relic Alpha", "Rare", True, [
            {"key": "rank", "value": "Adept"},
            {"key": "quest_completed", "value": True},
        ]),
        Artifact("Temple Relic Beta", "Epic", True, [
            {"key": "rank", "value": "Master"},
        ]),
    ]

    engine = GatingEngine(player_state)

    for relic in relics:
        if engine.unlock(relic):
            print(f"- {relic.name} UNLOCKED")
        else:
            print(f"- {relic.name} LOCKED")

if __name__ == "__main__":
    main()
