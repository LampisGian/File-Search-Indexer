import json
import os
import sqlite3

from models.file_record import FileRecord


class IndexStorage:
    def __init__(
        self,
        json_file: str = "data/file_index.json",
        sqlite_file: str = "data/file_index.db"
    ):
        self.json_file = json_file
        self.sqlite_file = sqlite_file

    def save_to_json(self, records: list[FileRecord]) -> None:
        os.makedirs(os.path.dirname(self.json_file) or ".", exist_ok=True)

        with open(self.json_file, "w", encoding="utf-8") as file:
            json.dump(
                [record.to_dict() for record in records],
                file,
                indent=4,
                ensure_ascii=False
            )

    def load_from_json(self) -> list[FileRecord]:
        if not os.path.exists(self.json_file):
            return []

        with open(self.json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [FileRecord(**item) for item in data]

    def initialize_sqlite(self) -> None:
        os.makedirs(os.path.dirname(self.sqlite_file) or ".", exist_ok=True)

        with sqlite3.connect(self.sqlite_file) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    name TEXT,
                    extension TEXT,
                    size INTEGER,
                    modified_date TEXT
                )
            """)
            connection.commit()

    def save_to_sqlite(self, records: list[FileRecord]) -> None:
        self.initialize_sqlite()

        with sqlite3.connect(self.sqlite_file) as connection:
            cursor = connection.cursor()

            cursor.execute("DELETE FROM files")

            cursor.executemany("""
                INSERT OR REPLACE INTO files (
                    path,
                    name,
                    extension,
                    size,
                    modified_date
                )
                VALUES (?, ?, ?, ?, ?)
            """, [
                (
                    record.path,
                    record.name,
                    record.extension,
                    record.size,
                    record.modified_date
                )
                for record in records
            ])

            connection.commit()

    def load_from_sqlite(self) -> list[FileRecord]:
        self.initialize_sqlite()

        with sqlite3.connect(self.sqlite_file) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT path, name, extension, size, modified_date
                FROM files
            """)
            rows = cursor.fetchall()

        return [
            FileRecord(
                path=row[0],
                name=row[1],
                extension=row[2],
                size=row[3],
                modified_date=row[4]
            )
            for row in rows
        ]