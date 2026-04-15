#This module defines the FileScanner class, which is responsible for scanning a specified root folder and its subdirectories to collect metadata about all files.
#The class handles various file-related errors gracefully and stores any issues encountered during the scanning process. 
#It provides a method to retrieve the list of errors after the scan is complete.
import os
from pathlib import Path
from datetime import datetime

from models.file_record import FileRecord


class FileScanner:
    def __init__(self, root_folder: str):
        self.root_folder = root_folder
        self.errors = []

    def scan(self) -> list[FileRecord]:
        records = []
        self.errors = []

        for current_root, _, files in os.walk(self.root_folder, onerror=self._handle_walk_error):
            for file_name in files:
                full_path = os.path.join(current_root, file_name)

                try:
                    if not os.path.exists(full_path):
                        self.errors.append(f"Broken or missing file: {full_path}")
                        continue

                    if os.path.islink(full_path) and not os.path.exists(os.path.realpath(full_path)):
                        self.errors.append(f"Broken symbolic link: {full_path}")
                        continue

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

                except PermissionError:
                    self.errors.append(f"Permission denied: {full_path}")
                except FileNotFoundError:
                    self.errors.append(f"File not found: {full_path}")
                except OSError as error:
                    self.errors.append(f"OS error for {full_path}: {error}")

        return records

    def _handle_walk_error(self, error):
        self.errors.append(f"Directory access error: {error}")

    def get_errors(self) -> list[str]:
        return self.errors