"""
Smart File Organizer
A Python script that automatically organizes files in a selected folder
by categorizing them based on their file extensions.
Works with internal drives, external hard drives, and USB pendrives.
"""

import os
import shutil
from pathlib import Path
import time

# Category definitions – plain dictionary, no classes modifying it
CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "Documents": {".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"},
    "PDFs": {".pdf"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".webm"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
}

# Use a list to preserve order in the summary
ALL_CATEGORIES = list(CATEGORIES.keys()) + ["Others"]

# Files/folders to skip (system files, temporary files, etc.)
SKIP_PATTERNS = [
    # System files
    "hiberfil.sys",
    "pagefile.sys",
    "swapfile.sys",
    "DumpStack.log",
    "DumpStack.log.tmp",
    # Windows/System files
    "System Volume Information",
    "$Recycle.Bin",
    "RECYCLER",
    "MSOCache",
    # Hidden files (starting with .)
    ".env",
    ".git",
    ".gitignore",
    ".DS_Store",
    ".Trash",
    # Thumbnails
    "Thumbs.db",
    "desktop.ini",
]


def should_skip_file(file_path: Path) -> bool:
    """
    Check if a file or folder should be skipped.
    Returns True if the item should be ignored.
    """
    name = file_path.name

    # Skip hidden files (starting with .)
    if name.startswith('.'):
        return True

    # Skip system patterns
    for pattern in SKIP_PATTERNS:
        if pattern.lower() == name.lower():
            return True

    # Skip if file is a system file (Windows hidden attribute check)
    try:
        import ctypes
        # Check if file has hidden attribute set
        if hasattr(ctypes, 'windll'):
            # Windows
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(file_path))
            if attrs != -1 and attrs & 0x2:  # FILE_ATTRIBUTE_HIDDEN
                return True
    except:
        # If we can't check, assume it's fine
        pass

    return False


def get_category(extension: str) -> str:
    """Return category name based on file extension; fallback to 'Others'."""
    ext = extension.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Others"


def unique_filename(dest_dir: Path, filename: str) -> Path:
    """
    Generate a unique path if filename already exists in dest_dir.
    Example: file.txt -> file_1.txt, file_2.txt, ...
    """
    target = dest_dir / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 1
    while target.exists():
        target = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    return target


def check_drive_writable(root: Path) -> bool:
    """
    Check if we can write to the drive/folder.
    Returns True if writable, False otherwise.
    """
    try:
        # Try to create a small test file
        test_file = root / ".organizer_test.txt"
        test_file.write_text("test")
        test_file.unlink()  # Delete the test file
        return True
    except:
        return False


def organize_folder(folder_path: str) -> None:
    """Main orchestrator: scan, categorize, move files, and show summary."""
    root = Path(folder_path).resolve()

    if not root.exists() or not root.is_dir():
        print(f"\n❌ Error: '{folder_path}' is not a valid directory.")
        return

    # Check if drive is writable
    if not check_drive_writable(root):
        print(f"\n⚠️  Warning: '{root}' may be read-only or write-protected.")
        print("   Files on write-protected drives (like some pendrives) cannot be organized.")
        print("   Please check if the drive is not locked or write-protected.\n")
        
        confirm = input("Do you want to continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("\n❌ Operation cancelled.")
            return

    # Only process files (skip directories)
    all_files = [f for f in root.iterdir() if f.is_file()]
    
    # Filter out system/hidden files
    files = [f for f in all_files if not should_skip_file(f)]
    
    skipped_system = len(all_files) - len(files)

    if not files:
        if skipped_system > 0:
            print(f"\n📭 No user files found to organize.")
            print(f"   ({skipped_system} system/hidden file(s) were automatically skipped)")
        else:
            print("\n📭 No files found to organize.")
        return

    print(f"\n📊 Found {len(files)} file(s) to organize in: {root}")
    if skipped_system > 0:
        print(f"   ({skipped_system} system/hidden file(s) skipped)")
    
    confirm = input("Do you want to proceed? (y/N): ").strip().lower()
    if confirm != 'y':
        print("\n❌ Operation cancelled.")
        return

    # Statistics
    stats = {"scanned": len(files), "moved": 0, "errors": 0, "skipped": skipped_system}
    category_counts = {cat: 0 for cat in ALL_CATEGORIES}
    error_log = []

    print("\n🔄 Organizing files...\n")

    for file_path in files:
        try:
            category = get_category(file_path.suffix)
            dest_dir = root / category
            
            # Try to create directory, handle permission errors
            try:
                dest_dir.mkdir(exist_ok=True)
            except PermissionError:
                print(f"  ❌ Permission denied: Cannot create '{category}' folder.")
                stats["errors"] += 1
                error_log.append((file_path.name, "Cannot create category folder"))
                continue

            dest_path = unique_filename(dest_dir, file_path.name)
            
            # Try to move the file
            try:
                shutil.move(str(file_path), str(dest_path))
                stats["moved"] += 1
                category_counts[category] += 1
                print(f"  ✅ Moved: {file_path.name} → {category}/")
            except PermissionError:
                stats["errors"] += 1
                error_log.append((file_path.name, "Access denied"))
                print(f"  ❌ Failed: {file_path.name} (Access denied)")
            except shutil.Error as e:
                stats["errors"] += 1
                error_log.append((file_path.name, str(e)))
                print(f"  ❌ Failed: {file_path.name}")

        except Exception as e:
            stats["errors"] += 1
            error_log.append((file_path.name, str(e)))
            print(f"  ❌ Failed: {file_path.name}")

    # Final summary
    print("\n" + "=" * 50)
    print("📊 ORGANIZATION SUMMARY")
    print("=" * 50)
    print(f"Total files scanned : {stats['scanned'] + stats['skipped']}")
    print(f"User files processed : {stats['scanned']}")
    print(f"System files skipped : {stats['skipped']}")
    print(f"Files moved         : {stats['moved']}")
    print(f"Errors encountered  : {stats['errors']}")
    print("-" * 50)
    print("Files by category:")
    for cat in ALL_CATEGORIES:
        count = category_counts[cat]
        if count:
            print(f"  • {cat:<10}: {count}")
    if error_log:
        print("-" * 50)
        print("Error details:")
        for name, msg in error_log:
            print(f"  • {name}: {msg}")
    print("=" * 50)
    print("✨ Done! Your files are now organized.")


def get_valid_path() -> Path | None:
    """
    Repeatedly ask the user for a folder path until a valid one is provided,
    or they choose to quit.
    Returns a Path object if valid, or None if user quits.
    """
    while True:
        path_input = input("\n📂 Enter folder path (or type 'quit' to exit): ").strip()
        clean_path = path_input.strip("'\"")

        if clean_path.lower() in ("quit", "exit", "q"):
            return None

        if clean_path:
            path_obj = Path(clean_path).resolve()
            if path_obj.exists() and path_obj.is_dir():
                return path_obj
            else:
                print(f"❌ Invalid folder: '{clean_path}' doesn't exist or isn't a directory.")
                print("   Please try again or type 'quit' to exit.")
        else:
            print("❌ No path entered. Please try again or type 'quit'.")


def main():
    """CLI entry point with a friendly banner."""
    print("=" * 50)
    print("        📂 SMART FILE ORGANIZER")
    print("=" * 50)
    print("This tool sorts files in a folder into subfolders")
    print("based on their extension.")
    print("Works with internal drives, external drives, and USB pendrives.")
    print("Type 'quit' at any time to exit.\n")

    folder_path = get_valid_path()
    if folder_path is None:
        print("\n👋 Exiting. Goodbye!")
        return

    start_time = time.time()
    organize_folder(str(folder_path))
    print(f"\n⏱️  Time taken: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()