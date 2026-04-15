#This module defines the Paginator class, which is responsible for managing the pagination of file records in the search results.
#The class takes a list of FileRecord objects and a page size as input and provides methods to calculate the total number of pages and retrieve a specific page of results based on the current page number. 
#The pagination logic ensures that the correct subset of records is returned for each page, and it handles edge cases such as invalid page numbers and empty record lists gracefully.
from models.file_record import FileRecord


class Paginator:
    def __init__(self, records: list[FileRecord], page_size: int = 10):
        self.records = records
        self.page_size = page_size if page_size > 0 else 10

    def get_total_pages(self) -> int:
        if not self.records:
            return 0

        return (len(self.records) + self.page_size - 1) // self.page_size

    def get_page(self, page_number: int) -> list[FileRecord]:
        total_pages = self.get_total_pages()

        if total_pages == 0:
            return []

        if page_number < 1 or page_number > total_pages:
            return []

        start_index = (page_number - 1) * self.page_size
        end_index = start_index + self.page_size

        return self.records[start_index:end_index]