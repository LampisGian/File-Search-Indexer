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