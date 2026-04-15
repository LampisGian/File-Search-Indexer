#This module defines the SearchEngine class, which provides methods for searching through a list of FileRecord objects based on file name keywords and file extensions.
#The class includes methods to search by name, search by extension, and a combined search method that applies both criteria sequentially. 
#The search methods return a new list of FileRecord objects that match the specified search criteria, allowing for 
#flexible and efficient searching of file metadata.
from models.file_record import FileRecord


class SearchEngine:
    def __init__(self, records: list[FileRecord]):
        self.records = records

    def search_by_name(self, keyword: str) -> list[FileRecord]:
        keyword = keyword.lower().strip()

        if not keyword:
            return self.records

        return [
            record
            for record in self.records
            if keyword in record.name.lower()
        ]

    def search_by_extension(self, extension: str) -> list[FileRecord]:
        extension = extension.lower().strip()

        if not extension:
            return self.records

        if not extension.startswith("."):
            extension = f".{extension}"

        return [
            record
            for record in self.records
            if record.extension == extension
        ]

    def search(self, name_keyword: str = "", extension: str = "") -> list[FileRecord]:
        results = self.records

        if name_keyword.strip():
            results = [
                record
                for record in results
                if name_keyword.lower().strip() in record.name.lower()
            ]

        if extension.strip():
            normalized_extension = extension.lower().strip()

            if not normalized_extension.startswith("."):
                normalized_extension = f".{normalized_extension}"

            results = [
                record
                for record in results
                if record.extension == normalized_extension
            ]

        return results