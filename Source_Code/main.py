import os

from scanner.file_scanner import FileScanner
from storage.index_storage import IndexStorage
from search.search_engine import SearchEngine
from search.filters import FileFilter
from search.sorter import FileSorter
from search.paginator import Paginator


def print_records(records):
    if not records:
        print("\nNo results found.\n")
        return

    for record in records:
        print(record)


def display_paginated(records):
    if not records:
        print("\nNo results found.\n")
        return

    page_size_input = input("Enter results per page: ").strip()

    if not page_size_input.isdigit() or int(page_size_input) <= 0:
        page_size = 10
    else:
        page_size = int(page_size_input)

    paginator = Paginator(records, page_size)
    total_pages = paginator.get_total_pages()
    current_page = 1

    while True:
        page_records = paginator.get_page(current_page)

        print(f"\nPage {current_page} of {total_pages}\n")
        print_records(page_records)

        if total_pages == 1:
            break

        print("\nNavigation:")
        print("n - Next page")
        print("p - Previous page")
        print("q - Quit pagination")

        action = input("Choose an option: ").strip().lower()

        if action == "n":
            if current_page < total_pages:
                current_page += 1
            else:
                print("You are already on the last page.")

        elif action == "p":
            if current_page > 1:
                current_page -= 1
            else:
                print("You are already on the first page.")

        elif action == "q":
            break

        else:
            print("Invalid option.")


def get_optional_int(prompt):
    value = input(prompt).strip()
    return int(value) if value else None


def get_optional_date(prompt):
    value = input(prompt).strip()
    return value if value else None


def get_sort_order():
    order = input("Choose order (asc/desc): ").strip().lower()
    return order == "desc"


def main():
    folder_path = input("Enter folder path to scan: ").strip()

    if not os.path.isdir(folder_path):
        print("Invalid folder path.")
        return

    scanner = FileScanner(folder_path)
    files = scanner.scan()

    storage = IndexStorage(
        json_file="data/file_index.json",
        sqlite_file="data/file_index.db"
    )

    storage.save_to_json(files)
    storage.save_to_sqlite(files)

    print(f"\nTotal files indexed: {len(files)}")
    print("Index saved to JSON: data/file_index.json")
    print("Index saved to SQLite: data/file_index.db")

    while True:
        print("\nSearch, Filter, Sort and Pagination Options:")
        print("1. Search by name")
        print("2. Search by extension")
        print("3. Search by name and extension")
        print("4. Filter by size")
        print("5. Filter by date")
        print("6. Filter by size and date")
        print("7. Sort by name")
        print("8. Sort by size")
        print("9. Sort by date")
        print("10. Show all files")
        print("11. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            keyword = input("Enter file name keyword: ").strip()
            search_engine = SearchEngine(files)
            results = search_engine.search_by_name(keyword)
            display_paginated(results)

        elif choice == "2":
            extension = input("Enter file extension (e.g. txt or .txt): ").strip()
            search_engine = SearchEngine(files)
            results = search_engine.search_by_extension(extension)
            display_paginated(results)

        elif choice == "3":
            keyword = input("Enter file name keyword: ").strip()
            extension = input("Enter file extension (e.g. txt or .txt): ").strip()
            search_engine = SearchEngine(files)
            results = search_engine.search(name_keyword=keyword, extension=extension)
            display_paginated(results)

        elif choice == "4":
            min_size = get_optional_int("Enter minimum size in bytes: ")
            max_size = get_optional_int("Enter maximum size in bytes: ")
            file_filter = FileFilter(files)
            results = file_filter.filter_by_size(min_size=min_size, max_size=max_size)
            display_paginated(results)

        elif choice == "5":
            start_date = get_optional_date("Enter start date (YYYY-MM-DD): ")
            end_date = get_optional_date("Enter end date (YYYY-MM-DD): ")
            file_filter = FileFilter(files)
            results = file_filter.filter_by_date(
                start_date=start_date,
                end_date=end_date
            )
            display_paginated(results)

        elif choice == "6":
            min_size = get_optional_int("Enter minimum size in bytes: ")
            max_size = get_optional_int("Enter maximum size in bytes: ")
            start_date = get_optional_date("Enter start date (YYYY-MM-DD): ")
            end_date = get_optional_date("Enter end date (YYYY-MM-DD): ")

            file_filter = FileFilter(files)
            results = file_filter.filter(
                min_size=min_size,
                max_size=max_size,
                start_date=start_date,
                end_date=end_date
            )
            display_paginated(results)

        elif choice == "7":
            reverse = get_sort_order()
            sorter = FileSorter(files)
            results = sorter.sort_by_name(reverse=reverse)
            display_paginated(results)

        elif choice == "8":
            reverse = get_sort_order()
            sorter = FileSorter(files)
            results = sorter.sort_by_size(reverse=reverse)
            display_paginated(results)

        elif choice == "9":
            reverse = get_sort_order()
            sorter = FileSorter(files)
            results = sorter.sort_by_date(reverse=reverse)
            display_paginated(results)

        elif choice == "10":
            display_paginated(files)

        elif choice == "11":
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()