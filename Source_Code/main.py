import os

from scanner.file_scanner import FileScanner
from storage.index_storage import IndexStorage
from search.search_engine import SearchEngine
from search.filters import FileFilter


def print_records(records, limit=10):
    if not records:
        print("\nNo results found.\n")
        return

    print(f"\nFound {len(records)} matching files:\n")

    for record in records[:limit]:
        print(record)

    if len(records) > limit:
        print(f"\nShowing first {limit} results only.")


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
        print("\nSearch and Filter Options:")
        print("1. Search by name")
        print("2. Search by extension")
        print("3. Search by name and extension")
        print("4. Filter by size")
        print("5. Filter by date")
        print("6. Filter by size and date")
        print("7. Show all files")
        print("8. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            keyword = input("Enter file name keyword: ").strip()
            search_engine = SearchEngine(files)
            results = search_engine.search_by_name(keyword)
            print_records(results)

        elif choice == "2":
            extension = input("Enter file extension (e.g. txt or .txt): ").strip()
            search_engine = SearchEngine(files)
            results = search_engine.search_by_extension(extension)
            print_records(results)

        elif choice == "3":
            keyword = input("Enter file name keyword: ").strip()
            extension = input("Enter file extension (e.g. txt or .txt): ").strip()
            search_engine = SearchEngine(files)
            results = search_engine.search(name_keyword=keyword, extension=extension)
            print_records(results)

        elif choice == "4":
            min_size = get_optional_int("Enter minimum size in bytes: ")
            max_size = get_optional_int("Enter maximum size in bytes: ")
            file_filter = FileFilter(files)
            results = file_filter.filter_by_size(min_size=min_size, max_size=max_size)
            print_records(results)

        elif choice == "5":
            start_date = get_optional_date("Enter start date (YYYY-MM-DD): ")
            end_date = get_optional_date("Enter end date (YYYY-MM-DD): ")
            file_filter = FileFilter(files)
            results = file_filter.filter_by_date(
                start_date=start_date,
                end_date=end_date
            )
            print_records(results)

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
            print_records(results)

        elif choice == "7":
            print_records(files)

        elif choice == "8":
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()