# ============================================================
# File        : relic_state.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Created     : May 2026
# Description : Persistent NG+ relic state storage and loading.
#               Tracks NG+ level and unlocked relic layers.
# ============================================================

import json
from pathlib import Path

class RelicState:
    def __init__(self, ng_plus_level=0, unlocked_layers=None):
        self.ng_plus_level = ng_plus_level
        self.unlocked_layers = unlocked_layers or []

    @classmethod
    def load(cls, path: Path):
        if not path.exists():
            return cls()
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            ng_plus_level=data.get("ng_plus_level", 0),
            unlocked_layers=data.get("unlocked_layers", []),
        )

    def save(self, path: Path):
        data = {
            "ng_plus_level": self.ng_plus_level,
            "unlocked_layers": self.unlocked_layers,
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
