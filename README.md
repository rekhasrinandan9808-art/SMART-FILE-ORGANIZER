
# 📂 Smart File Organizer using Python

**Automatically organize your files into categorized folders using Python.** 🐍

Built by **GENESYNTECH — Where Intelligence Begins.**

---

## 🚀 About the Project

The **Smart File Organizer** is a Python automation project that helps organize messy folders by sorting files into separate folders based on their file extensions.

Instead of manually moving files one by one, this program automates the process and provides a summary of the results.

## ✨ Features

- 📁 **Automatic Organization** — Sorts files by their extensions.
- 🖼️ **Image Sorting** — Organizes image files into an Images folder.
- 📄 **Document Sorting** — Groups documents into a Documents folder.
- 📕 **PDF Sorting** — Separates PDF files.
- 🎬 **Video Sorting** — Organizes video files.
- 🎵 **Audio Sorting** — Groups audio files.
- 📦 **Archive Sorting** — Organizes compressed files.
- 🛡️ **Filename Conflict Handling** — Creates a different filename if the destination already contains a file with the same name.
- 👻 **Hidden File Filtering** — Skips certain hidden and system files.
- 📊 **Organization Summary** — Displays the results after processing.
- ✅ **Confirmation Before Moving** — Allows you to review the operation before files are moved.

## 🗂️ Supported File Types

| Category | Extensions |
|---|---|
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg` |
| Documents | `.doc`, `.docx`, `.txt`, `.ppt`, `.pptx`, `.xls`, `.xlsx` |
| PDFs | `.pdf` |
| Videos | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm` |
| Audio | `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg` |
| Archives | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
| Others | Other file extensions |

## 🛠️ Technologies Used

- **Python 3.10 or newer**
- `os` — File and directory operations
- `shutil` — Moving files
- `pathlib` — Handling filesystem paths
- `time` — Time-related operations

No third-party Python packages are required.

## 📋 Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux
- A folder containing files to organize

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/rekhasrinandan9808-art/SMART-FILE-ORGANIZER.git
```

### 2. Open the project folder

```bash
cd SMART-FILE-ORGANIZER
```

### 3. Run the program

If the Python file is named `main.py`, run:

```bash
python main.py
```

If your file has a different name, replace `main.py` with the actual filename.

## 🧑‍💻 How to Use

1. Run the Python program.
2. Enter the path of the folder you want to organize.
3. Review the files detected by the program.
4. Confirm the operation when prompted.
5. Let Python move files into their corresponding category folders.
6. Review the final organization summary.

## 📸 Example

### Before

```text
Downloads/
├── photo.jpg
├── notes.txt
├── presentation.pptx
├── video.mp4
├── song.mp3
├── report.pdf
└── archive.zip
```

### After

```text
Downloads/
├── Images/
│   └── photo.jpg
├── Documents/
│   ├── notes.txt
│   └── presentation.pptx
├── PDFs/
│   └── report.pdf
├── Videos/
│   └── video.mp4
├── Audio/
│   └── song.mp3
└── Archives/
    └── archive.zip
```

*This is an illustrative example. Actual results depend on the files in the selected folder.*

## ⚠️ Important Safety Notes

- The program **moves files** into category folders; it does not simply copy them.
- Test it on a temporary folder containing sample files before using it on important data.
- Back up important files before running the program.
- There is no built-in undo feature.
- If a filename already exists in the destination, the program generates a different filename to avoid overwriting that file.
- Hidden-file filtering does not guarantee that every protected or system file will be detected.
- The program organizes files in the selected folder; it does not recursively organize every subfolder.

## 🎯 Project Goals

This project demonstrates how Python can be used for:

- File handling and directory management
- Automation of repetitive tasks
- Working with filesystem paths
- Exception handling
- Building practical command-line tools

## 🔮 Future Improvements

- 🖥️ Graphical user interface (GUI)
- ↩️ Undo and restore functionality
- 🔍 Duplicate-content detection
- 📂 Optional recursive folder organization
- ⚙️ Custom file categories
- 📈 Detailed logging and reports

*These are planned improvements and are not all implemented in the current version.*

## 👨‍💻 About GENESYNTECH

**GENESYNTECH — Where Intelligence Begins.**

Exploring AI, Python, automation, software development, and emerging technologies through practical projects.

Follow the journey and discover what you can build with technology.

## 📜 License

No license has been specified yet. Unless a license is added, others should not assume they have permission to reuse, modify, or distribute this project's code.

---

⭐ **If you find this project useful, consider starring the repository!**

🐍 Built with Python | 🚀 Created by GENESYNTECH
