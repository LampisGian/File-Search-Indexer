#This module defines the FileSorter class, which provides methods for sorting a list of FileRecord objects based on different criteria such as name, size, and modified date.
#The class includes methods to sort by name, sort by size, sort by date, and a general sort method that takes a sorting criterion as input and applies the appropriate sorting logic. 
#The sorting methods return a new list of FileRecord objects sorted according to the specified criteria, allowing for flexible and efficient organization of file metadata in the search results.   
from datetime import datetime

from models.file_record import FileRecord


class FileSorter:
    def __init__(self, records: list[FileRecord]):
        self.records = records

    def sort_by_name(self, reverse: bool = False) -> list[FileRecord]:
        return sorted(
            self.records,
            key=lambda record: record.name.lower(),
            reverse=reverse
        )

    def sort_by_size(self, reverse: bool = False) -> list[FileRecord]:
        return sorted(
            self.records,
            key=lambda record: record.size,
            reverse=reverse
        )

    def sort_by_date(self, reverse: bool = False) -> list[FileRecord]:
        return sorted(
            self.records,
            key=lambda record: datetime.strptime(
                record.modified_date,
                "%Y-%m-%d %H:%M:%S"
            ),
            reverse=reverse
        )

    def sort(self, sort_by: str, reverse: bool = False) -> list[FileRecord]:
        sort_by = sort_by.lower().strip()

        if sort_by == "name":
            return self.sort_by_name(reverse=reverse)
        if sort_by == "size":
            return self.sort_by_size(reverse=reverse)
        if sort_by == "date":
            return self.sort_by_date(reverse=reverse)

        return self.records