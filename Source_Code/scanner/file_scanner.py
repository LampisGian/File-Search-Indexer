import os
from pathlib import Path
from datetime import datetime

from models.file_record import FileRecord


class FileScanner:
    def __init__(self, root_folder: str):
        self.root_folder = root_folder

    def scan(self) -> list[FileRecord]:
        records = []

        for current_root, _, files in os.walk(self.root_folder):
            for file_name in files:
                full_path = os.path.join(current_root, file_name)

                try:
                    stats = os.stat(full_path)
                    path_obj = Path(full_path)

                    record = FileRecord(
                        path=str(path_obj.resolve()),
                        name=path_obj.name,
                        extension=path_obj.suffix.lower(),
                        size=stats.st_size,
                        modified_date=datetime.fromtimestamp(
                            stats.st_mtime
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    )

                    records.append(record)

                except (PermissionError, FileNotFoundError, OSError) as error:
                    print(f"Skipping file: {full_path} | Error: {error}")

        return records