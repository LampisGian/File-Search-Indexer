#This module defines the FileFilter class, which provides methods for filtering a list of FileRecord objects based on file size and 
# modification date.
#The class includes methods to filter by size, filter by date, and a combined filter method that applies both size and date filters 
# sequentially. The filtering methods return a new list of FileRecord objects that match the specified criteria.
from datetime import datetime

from models.file_record import FileRecord


class FileFilter:
    def __init__(self, records: list[FileRecord]):
        self.records = records

    def filter_by_size(
        self,
        min_size: int | None = None,
        max_size: int | None = None
    ) -> list[FileRecord]:
        results = self.records

        if min_size is not None:
            results = [record for record in results if record.size >= min_size]

        if max_size is not None:
            results = [record for record in results if record.size <= max_size]

        return results

    def filter_by_date(
        self,
        start_date: str | None = None,
        end_date: str | None = None
    ) -> list[FileRecord]:
        results = self.records

        start_dt = (
            datetime.strptime(start_date, "%Y-%m-%d")
            if start_date else None
        )
        end_dt = (
            datetime.strptime(end_date, "%Y-%m-%d")
            if end_date else None
        )

        filtered_records = []

        for record in results:
            record_dt = datetime.strptime(record.modified_date, "%Y-%m-%d %H:%M:%S")

            if start_dt and record_dt < start_dt:
                continue

            if end_dt and record_dt > end_dt:
                continue

            filtered_records.append(record)

        return filtered_records

    def filter(
        self,
        min_size: int | None = None,
        max_size: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None
    ) -> list[FileRecord]:
        results = self.filter_by_size(min_size=min_size, max_size=max_size)
        temp_filter = FileFilter(results)
        return temp_filter.filter_by_date(start_date=start_date, end_date=end_date)