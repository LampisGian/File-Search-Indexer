import os

from scanner.file_scanner import FileScanner


def main():
    folder_path = input("Enter folder path to scan: ").strip()

    if not os.path.isdir(folder_path):
        print("Invalid folder path.")
        return

    scanner = FileScanner(folder_path)
    files = scanner.scan()

    print(f"\nTotal files found: {len(files)}\n")

    for file_record in files[:10]:
        print(file_record)

    if len(files) > 10:
        print("\nShowing first 10 results only.")


if __name__ == "__main__":
    main()