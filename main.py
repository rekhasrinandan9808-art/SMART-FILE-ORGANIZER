"""
Smart File Organizer
A Python script that organizes the files in a folder into category subfolders
based on their file extensions, with optional detection of exact duplicate files
(by file content, not by name).

Works with internal drives, external hard drives, and USB pendrives.
Requires Python 3.8+ and nothing else (standard library only).

Safety: the script never deletes your files. It only moves them, and it asks
for confirmation before touching anything.
"""

import hashlib
import os
import shutil
import stat
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff", ".heic"},
    "Documents": {".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".rtf", ".odt"},
    "PDFs": {".pdf"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
}

# A list keeps the order stable in the summary
ALL_CATEGORIES = list(CATEGORIES.keys()) + ["Others"]

DUPLICATES_FOLDER = "Duplicates"

# Exact names to skip (compared case-insensitively)
SKIP_NAMES = {
    "hiberfil.sys", "pagefile.sys", "swapfile.sys",
    "dumpstack.log", "dumpstack.log.tmp",
    "system volume information", "$recycle.bin", "recycler", "msocache",
    "thumbs.db", "desktop.ini",
}

# Unfinished downloads / temp files: moving these can corrupt a running download
SKIP_EXTENSIONS = {".tmp", ".crdownload", ".part", ".partial", ".download"}

# Never let the script organize itself
_THIS_FILE = globals().get("__file__")
SCRIPT_PATH = Path(_THIS_FILE).resolve() if _THIS_FILE else None


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def should_skip_file(file_path: Path) -> bool:
    """Return True for hidden, system, temporary, or otherwise unsafe-to-move files."""
    name = file_path.name

    # Hidden files (.env, .gitignore, ...) and Office lock files (~$report.docx)
    if name.startswith((".", "~$")):
        return True

    if name.lower() in SKIP_NAMES:
        return True

    if file_path.suffix.lower() in SKIP_EXTENSIONS:
        return True

    # Don't move this script if it lives in the folder being organized
    if SCRIPT_PATH is not None:
        try:
            if file_path.resolve() == SCRIPT_PATH:
                return True
        except OSError:
            pass

    # Windows hidden/system attributes (st_file_attributes is 0 / missing elsewhere)
    try:
        attrs = getattr(file_path.stat(), "st_file_attributes", 0)
    except OSError:
        return True  # can't even read it, so leave it alone
    if attrs & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM):
        return True

    return False


def get_category(extension: str) -> str:
    """Return the category name for a file extension; fallback is 'Others'."""
    ext = extension.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Others"


def unique_filename(dest_dir: Path, filename: str) -> Path:
    """
    Return a path inside dest_dir that does not exist yet.
    Name conflicts only (NOT content): report.pdf -> report_1.pdf -> report_2.pdf
    """
    target = dest_dir / filename
    if not target.exists():
        return target

    stem, suffix = target.stem, target.suffix
    counter = 1
    while target.exists():
        target = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    return target


def ensure_dir(root: Path, name: str) -> Path:
    """Create root/name if needed. Fails clearly if a *file* has that name."""
    folder = root / name
    if folder.exists() and not folder.is_dir():
        raise OSError(f"a file named '{name}' already exists, so the folder can't be created")
    folder.mkdir(exist_ok=True)
    return folder


def check_drive_writable(root: Path) -> bool:
    """Try to create (and automatically delete) a temporary file in the folder."""
    try:
        with tempfile.NamedTemporaryFile(dir=str(root), prefix=".organizer_test_"):
            pass
        return True
    except OSError:
        return False


def is_protected_folder(root: Path) -> bool:
    """True for operating-system folders that must never be reorganized."""
    trees: List[Path] = []   # the folder itself AND everything inside it is protected
    exact: List[Path] = []   # only the folder itself is protected

    if os.name == "nt":
        for var in ("SystemRoot", "windir", "ProgramFiles", "ProgramFiles(x86)", "ProgramData"):
            value = os.environ.get(var)
            if value:
                trees.append(Path(value))
        system_drive = os.environ.get("SystemDrive")  # usually C:
        if system_drive:
            exact.append(Path(system_drive + "\\"))
    else:
        trees.extend(Path(p) for p in ("/bin", "/sbin", "/usr", "/etc", "/boot", "/lib", "/System"))
        exact.append(Path("/"))

    for p in exact:
        if root == p:
            return True
    for p in trees:
        if root == p or p in root.parents:
            return True
    return False


def file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """SHA-256 of the file content, read in chunks so big videos don't fill RAM."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def find_duplicates(files: List[Path]) -> Dict[Path, Path]:
    """
    Find files with identical CONTENT. Returns {duplicate_file: original_file}.
    Only files of the same size are hashed, so most files are never read.
    Empty (0-byte) files are ignored.
    """
    by_size: Dict[int, List[Path]] = defaultdict(list)
    for f in files:
        try:
            size = f.stat().st_size
        except OSError:
            continue
        if size > 0:
            by_size[size].append(f)

    duplicates: Dict[Path, Path] = {}
    for group in by_size.values():
        if len(group) < 2:
            continue
        by_hash: Dict[str, List[Path]] = defaultdict(list)
        for f in group:
            try:
                by_hash[file_hash(f)].append(f)
            except OSError:
                continue  # unreadable file: treat as unique, never as a duplicate
        for same in by_hash.values():
            if len(same) < 2:
                continue
            # Keep the shortest name as the "original" (report.pdf beats report (1).pdf)
            same.sort(key=lambda p: (len(p.name), p.name.lower()))
            for dup in same[1:]:
                duplicates[dup] = same[0]
    return duplicates


def ask_yes_no(prompt: str) -> bool:
    """Ask a y/N question. Anything except y/yes (including no input) means No."""
    try:
        return input(prompt).strip().lower() in ("y", "yes")
    except EOFError:
        return False


def normalize_path(raw: str) -> Path:
    """Clean what the user typed: quotes, ~, %VARS%, and a bare drive letter like E:"""
    cleaned = raw.strip().strip("'\"")
    cleaned = os.path.expandvars(os.path.expanduser(cleaned))
    # On Windows, "E:" alone means "the current folder on drive E", not the drive root
    if os.name == "nt" and len(cleaned) == 2 and cleaned[1] == ":":
        cleaned += "\\"
    return Path(cleaned).resolve()


# --------------------------------------------------------------------------
# Main workflow
# --------------------------------------------------------------------------

def organize_folder(root: Path) -> None:
    """Scan, preview, confirm, move files, and print a summary."""
    if is_protected_folder(root):
        print(f"\n⛔ '{root}' is a system folder. Organizing it could break your computer.")
        print("   Please choose a normal folder (Downloads, Desktop, a USB drive, ...).")
        return

    if not check_drive_writable(root):
        print(f"\n⚠️  Warning: '{root}' may be read-only or write-protected.")
        print("   Files on write-protected drives (like some pendrives) cannot be organized.")
        print("   Please check that the drive is not locked or write-protected.\n")
        if not ask_yes_no("Do you want to continue anyway? (y/N): "):
            print("\n❌ Operation cancelled.")
            return

    try:
        all_files = [f for f in root.iterdir() if f.is_file()]
    except OSError as e:
        print(f"\n❌ Cannot read this folder: {e}")
        return

    files = [f for f in all_files if not should_skip_file(f)]
    skipped = len(all_files) - len(files)

    if not files:
        if skipped:
            print("\n📭 No user files found to organize.")
            print(f"   ({skipped} system/hidden file(s) were automatically skipped)")
        else:
            print("\n📭 No files found to organize.")
        return

    print(f"\n📊 Found {len(files)} file(s) to organize in: {root}")
    if skipped:
        print(f"   ({skipped} system/hidden file(s) skipped)")

    # Preview: what will go where
    preview: Dict[str, int] = defaultdict(int)
    for f in files:
        preview[get_category(f.suffix)] += 1
    print("\nPreview:")
    for cat in ALL_CATEGORIES:
        if preview[cat]:
            print(f"  • {cat:<10}: {preview[cat]}")

    # Optional: exact-duplicate detection by content
    duplicates: Dict[Path, Path] = {}
    if len(files) > 1 and ask_yes_no(
        f"\nAlso move exact duplicates (same content) into a '{DUPLICATES_FOLDER}' folder? (y/N): "
    ):
        print("🔍 Comparing file contents...")
        duplicates = find_duplicates(files)
        print(f"   Found {len(duplicates)} duplicate file(s).")

    if not ask_yes_no("\nDo you want to proceed? (y/N): "):
        print("\n❌ Operation cancelled.")
        return

    start_time = time.time()
    moved = 0
    errors: List[tuple] = []
    counts: Dict[str, int] = defaultdict(int)

    print("\n🔄 Organizing files...\n")

    for src in files:
        is_duplicate = src in duplicates
        category = DUPLICATES_FOLDER if is_duplicate else get_category(src.suffix)
        try:
            dest_dir = ensure_dir(root, category)
            dest_path = unique_filename(dest_dir, src.name)
            shutil.move(str(src), str(dest_path))
            moved += 1
            counts[category] += 1
            note = f"  (same content as {duplicates[src].name})" if is_duplicate else ""
            print(f"  ✅ Moved: {src.name} → {category}/{note}")
        except OSError as e:  # includes PermissionError and shutil.Error
            reason = "Access denied" if isinstance(e, PermissionError) else (e.strerror or str(e))
            errors.append((src.name, reason))
            print(f"  ❌ Failed: {src.name} ({reason})")
        except Exception as e:  # last-resort safety net: one bad file must not stop the rest
            errors.append((src.name, str(e)))
            print(f"  ❌ Failed: {src.name} ({e})")

    # Summary
    print("\n" + "=" * 50)
    print("📊 ORGANIZATION SUMMARY")
    print("=" * 50)
    print(f"Files found          : {len(all_files)}")
    print(f"System files skipped : {skipped}")
    print(f"Files moved          : {moved}")
    print(f"Errors               : {len(errors)}")
    print("-" * 50)
    print("Files by category:")
    for cat in ALL_CATEGORIES + [DUPLICATES_FOLDER]:
        if counts[cat]:
            print(f"  • {cat:<10}: {counts[cat]}")
    if errors:
        print("-" * 50)
        print("Error details:")
        for name, msg in errors:
            print(f"  • {name}: {msg}")
    print("=" * 50)
    if errors:
        print(f"⚠️  Done, but {len(errors)} file(s) could not be moved.")
    else:
        print("✨ Done! Your files are now organized.")
    print(f"⏱️  Time taken: {time.time() - start_time:.2f} seconds")


def get_valid_path() -> Optional[Path]:
    """
    Ask for a folder path until a valid one is given.
    Returns a Path, or None if the user wants to quit.
    """
    while True:
        try:
            raw = input("\n📂 Enter folder path (or type 'quit' to exit): ")
        except EOFError:
            return None

        if raw.strip().strip("'\"").lower() in ("quit", "exit", "q"):
            return None

        if not raw.strip():
            print("❌ No path entered. Please try again or type 'quit'.")
            continue

        try:
            path = normalize_path(raw)
        except (OSError, ValueError):
            print("❌ That doesn't look like a valid path. Please try again.")
            continue

        if path.exists() and path.is_dir():
            return path
        print(f"❌ Invalid folder: '{raw.strip()}' doesn't exist or isn't a directory.")
        print("   Please try again or type 'quit' to exit.")


def main() -> None:
    """CLI entry point with a friendly banner."""
    # Avoid crashes on consoles that can't display emojis
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

    print("=" * 50)
    print("        📂 SMART FILE ORGANIZER")
    print("=" * 50)
    print("This tool sorts the files in a folder into subfolders")
    print("based on their extension, and can find exact duplicates.")
    print("Works with internal drives, external drives, and USB pendrives.")
    print("It never deletes files and always asks before moving anything.")
    print("Type 'quit' at any time to exit.")

    try:
        while True:
            folder = get_valid_path()
            if folder is None:
                break
            organize_folder(folder)
    except KeyboardInterrupt:
        print("\n\n⛔ Interrupted. Files already moved stay where they are.")

    print("\n👋 Exiting. Goodbye!")


if __name__ == "__main__":
    main()
