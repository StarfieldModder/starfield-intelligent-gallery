# C:\SIG\mission_controller\database\schema.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ImageRecord:
    path: str
    name: str
    width: Optional[int]
    height: Optional[int]

class DatabaseManager:
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._images: List[ImageRecord] = []

    def insert_image_record(self, path: str, name: str,
                            width: Optional[int], height: Optional[int]) -> None:
        self._images.append(ImageRecord(path, name, width, height))

    def get_all_images(self) -> List[ImageRecord]:
        return list(self._images)

_db: Optional[DatabaseManager] = None

def get_db(db_path: Optional[str] = None) -> DatabaseManager:
    global _db
    if _db is None:
        _db = DatabaseManager(db_path or ":memory:")
    return _db
