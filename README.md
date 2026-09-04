# 📂 Smart File Organizer

A beginner-friendly Python tool that automatically organizes messy folders by sorting files into categorized subfolders based on their extensions. Works with **internal drives, external hard drives, and USB pendrives**.

## ✨ Features

- **Zero dependencies** – uses only Python's standard library.
- **Safe** – never deletes or modifies files; asks for confirmation before moving.
- **Duplicate handling** – renames files like `file_1.txt` if a name conflict occurs.
- **Error‑resilient** – continues processing even if some files fail.
- **Clear summary** – shows what was moved, by category, and any errors.
- **Retry on invalid path** – you can try again without restarting the program.
- **Smart skipping** – automatically skips system files, hidden files, and protected files.
- **Works anywhere** – internal drives, external HDDs, USB pendrives, and network drives.
- **Write‑protection detection** – warns you if a drive is read‑only.

## 🗂️ Supported Categories

| Category   | Extensions                                      |
|------------|-------------------------------------------------|
| Images     | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg` |
| Documents  | `.doc`, `.docx`, `.txt`, `.ppt`, `.pptx`, `.xls`, `.xlsx` |
| PDFs       | `.pdf`                                          |
| Videos     | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`         |
| Audio      | `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`         |
| Archives   | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`            |
| Others     | Any unsupported extension                       |

## 🚀 How to Run

### Prerequisites
- Python 3.6 or higher installed on your system
- No external libraries needed!

### Steps

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/yourusername/Smart-File-Organizer.git
   cd Smart-File-Organizer