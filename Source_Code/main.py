import os

from scanner.file_scanner import FileScanner
from storage.index_storage import IndexStorage


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

    print(f"\nTotal files found: {len(files)}")
    print("Index saved to JSON: data/file_index.json")
    print("Index saved to SQLite: data/file_index.db\n")

    json_records = storage.load_from_json()
    sqlite_records = storage.load_from_sqlite()

    print(f"Loaded {len(json_records)} records from JSON.")
    print(f"Loaded {len(sqlite_records)} records from SQLite.\n")

    print("First 5 records from JSON:")
    for record in json_records[:5]:
        print(record)

    print("\nFirst 5 records from SQLite:")
    for record in sqlite_records[:5]:
        print(record)


if __name__ == "__main__":
    main()