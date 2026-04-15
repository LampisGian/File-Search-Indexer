#This is the main entry point of the File Search and Indexing application. It orchestrates the scanning of a specified folder, indexing of file metadata, and provides a command-line interface for searching, filtering, and sorting the indexed files. 
# The program handles user input for various search and filter criteria, displays results in a paginated format, and manages any errors encountered during the scanning process. It also saves the indexed data to both JSON and SQLite formats for persistence.
import os

from scanner.file_scanner import FileScanner
from storage.index_storage import IndexStorage
from search.search_engine import SearchEngine
from search.filters import FileFilter
from search.sorter import FileSorter
from search.paginator import Paginator


def print_header(title):
    print(f"\n{title}")
    print("=" * 100)


def print_records(records):
    if not records:
        print("\nNo files found.\n")
        return

    print_header("Indexed Files")

    for index, record in enumerate(records, start=1):
        print(f"{index}. {record}")

    print("-" * 100)
    print(f"Total files: {len(records)}\n")


def print_errors(errors):
    if not errors:
        return

    print_header("Skipped / Problematic Files")

    for index, error in enumerate(errors, start=1):
        print(f"{index}. {error}")

    print("-" * 100)
    print(f"Total issues: {len(errors)}\n")


def display_paginated(records):
    if not records:
        print("\nNo results found.\n")
        return

    page_size_input = input("Enter results per page: ").strip()
    page_size = int(page_size_input) if page_size_input.isdigit() and int(page_size_input) > 0 else 10

    paginator = Paginator(records, page_size)
    total_pages = paginator.get_total_pages()
    current_page = 1

    while True:
        page_records = paginator.get_page(current_page)

        print_header(f"Page {current_page} of {total_pages}")
        for index, record in enumerate(page_records, start=1):
            print(f"{index}. {record}")

        if total_pages == 1:
            break

        print("\nOptions: [n] Next | [p] Previous | [q] Quit")
        action = input("Choose: ").strip().lower()

        if action == "n":
            if current_page < total_pages:
                current_page += 1
            else:
                print("Already on last page.")
        elif action == "p":
            if current_page > 1:
                current_page -= 1
            else:
                print("Already on first page.")
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


def main():
    folder_path = input("Enter folder path to scan: ").strip()

    if not os.path.isdir(folder_path):
        print("Invalid folder path.")
        return

    scanner = FileScanner(folder_path)
    files = scanner.scan()
    errors = scanner.get_errors()

    storage = IndexStorage(
        json_file="data/file_index.json",
        sqlite_file="data/file_index.db"
    )

    storage.save_to_json(files)
    storage.save_to_sqlite(files)

    print_header("Scan Summary")
    print(f"Indexed files: {len(files)}")
    print(f"Problematic items: {len(errors)}")
    print("JSON index: data/file_index.json")
    print("SQLite index: data/file_index.db")

    if errors:
        print("\nScan completed with some issues.")
    else:
        print("\nScan completed successfully.")

    while True:
        print("\nMenu")
        print("1. Show all files")
        print("2. Search by name")
        print("3. Search by extension")
        print("4. Search by name and extension")
        print("5. Filter by size")
        print("6. Filter by date")
        print("7. Filter by size and date")
        print("8. Sort by name")
        print("9. Sort by size")
        print("10. Sort by date")
        print("11. Show scan issues")
        print("12. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            display_paginated(files)

        elif choice == "2":
            keyword = input("Enter file name keyword: ").strip()
            results = SearchEngine(files).search_by_name(keyword)
            display_paginated(results)

        elif choice == "3":
            extension = input("Enter file extension: ").strip()
            results = SearchEngine(files).search_by_extension(extension)
            display_paginated(results)

        elif choice == "4":
            keyword = input("Enter file name keyword: ").strip()
            extension = input("Enter file extension: ").strip()
            results = SearchEngine(files).search(name_keyword=keyword, extension=extension)
            display_paginated(results)

        elif choice == "5":
            min_size = get_optional_int("Enter minimum size in bytes: ")
            max_size = get_optional_int("Enter maximum size in bytes: ")
            results = FileFilter(files).filter_by_size(min_size=min_size, max_size=max_size)
            display_paginated(results)

        elif choice == "6":
            start_date = get_optional_date("Enter start date (YYYY-MM-DD): ")
            end_date = get_optional_date("Enter end date (YYYY-MM-DD): ")
            results = FileFilter(files).filter_by_date(start_date=start_date, end_date=end_date)
            display_paginated(results)

        elif choice == "7":
            min_size = get_optional_int("Enter minimum size in bytes: ")
            max_size = get_optional_int("Enter maximum size in bytes: ")
            start_date = get_optional_date("Enter start date (YYYY-MM-DD): ")
            end_date = get_optional_date("Enter end date (YYYY-MM-DD): ")
            results = FileFilter(files).filter(
                min_size=min_size,
                max_size=max_size,
                start_date=start_date,
                end_date=end_date
            )
            display_paginated(results)

        elif choice == "8":
            reverse = input("Order (asc/desc): ").strip().lower() == "desc"
            results = FileSorter(files).sort_by_name(reverse=reverse)
            display_paginated(results)

        elif choice == "9":
            reverse = input("Order (asc/desc): ").strip().lower() == "desc"
            results = FileSorter(files).sort_by_size(reverse=reverse)
            display_paginated(results)

        elif choice == "10":
            reverse = input("Order (asc/desc): ").strip().lower() == "desc"
            results = FileSorter(files).sort_by_date(reverse=reverse)
            display_paginated(results)

        elif choice == "11":
            print_errors(errors)

        elif choice == "12":
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()