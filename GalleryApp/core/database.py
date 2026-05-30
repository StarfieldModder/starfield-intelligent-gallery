import sqlite3

class PhotoDatabase:
    def __init__(self, db_path="photos.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT NOT NULL,
                metadata TEXT,
                tags TEXT
            )
        """)
        self.conn.commit()

    def insert_photo(self, filepath, metadata, tags):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO photos (filepath, metadata, tags) VALUES (?, ?, ?)",
            (filepath, metadata, tags)
        )
        self.conn.commit()

    def get_all_photos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM photos")
        return cursor.fetchall()
