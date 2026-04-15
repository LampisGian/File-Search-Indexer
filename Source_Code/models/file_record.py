#This module defines the FileRecord class, which represents a file's metadata and provides methods for formatting and displaying that information.  
#It uses the dataclass decorator to simplify the class definition and includes methods for converting the record to a dictionary, formatting the file size,    
#and providing a string representation of the record.
from dataclasses import dataclass, asdict

@dataclass
class FileRecord:
    path: str
    name: str
    extension: str
    size: int
    modified_date: str

    def to_dict(self) -> dict:
        return asdict(self)

    def formatted_size(self) -> str:
        size = float(self.size)
        units = ["bytes", "KB", "MB", "GB", "TB"]
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"

        return f"{size:.2f} {units[unit_index]}"

    def display_extension(self) -> str:
        return self.extension if self.extension else "(no extension)"

    def __str__(self) -> str:
        return (
            f"Name: {self.name} | "
            f"Extension: {self.display_extension()} | "
            f"Size: {self.formatted_size()} | "
            f"Modified: {self.modified_date} | "
            f"Path: {self.path}"
        )