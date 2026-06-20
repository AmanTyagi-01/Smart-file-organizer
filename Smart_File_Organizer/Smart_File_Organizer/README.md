# 🗂️ Smart File Organizer & Cleaner

> A professional Python automation project for organizing, renaming, and cleaning files — built with only the Python Standard Library.

---

## 📋 Project Overview

**Smart File Organizer & Cleaner** is a command-line automation tool that brings order to chaotic directories. Point it at any folder and it will:

- **Sort** files into labelled category subfolders automatically
- **Rename** duplicates without data loss
- **Detect** and clean empty directories on demand
- **Log** every action with timestamps for a full audit trail
- **Report** a live statistics dashboard after every operation

Designed as an internship-level portfolio project demonstrating real-world Python engineering practices: OOP, logging, exception handling, modular design, and clean CLI UX.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📁 File Organizer | Sorts files into Images, Documents, Videos, Audio, Archives, Code, Others |
| 🔄 Duplicate Handling | Auto-renames collisions: `report.pdf` → `report_2.pdf` |
| 🏷️ Batch Renamer | Timestamp-based or sequential renaming with custom prefix |
| 🧹 Folder Cleaner | Detects and removes empty folders with confirmation |
| 📝 Logging System | Full audit log saved to `logs/operations.log` |
| 📊 Stats Dashboard | Live per-session counters with visual bar chart in terminal |
| 🎨 ANSI CLI | Color-coded, menu-driven interface (degrades gracefully) |

---

## 🛠️ Technologies Used

| Module | Purpose |
|---|---|
| `os` | Directory scanning, path resolution, folder creation |
| `shutil` | Safe file move operations |
| `logging` | Dual-handler logging (file + console) |
| `datetime` | Timestamps in logs and renamed filenames |
| `pathlib` | Extension parsing and path manipulation |
| `sys` | Exit codes and ANSI detection |
| `time` | UX pacing between menu re-renders |

> **Zero third-party dependencies.** Runs on any Python 3.8+ installation.

---

## 📁 Project Structure

```
Smart_File_Organizer/
│
├── main.py                 ← Entry point & CLI
│
├── src/
│   ├── organizer.py        ← FileOrganizer + FileRenamer classes
│   ├── cleaner.py          ← FolderCleaner class
│   └── logger_config.py    ← Logging setup
│
├── data/                   ← Put test files here before running
├── output/                 ← Organized files destination (optional)
├── logs/
│   └── operations.log      ← Generated at runtime
├── screenshots/            ← Add your demo screenshots here
│
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Smart_File_Organizer.git
cd Smart_File_Organizer

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. No pip install needed — standard library only!
```

---

## 🚀 How to Run

```bash
python main.py
```

You'll see the main menu:

```
  ╔══════════════════════════════════════════════════════════╗
  ║        Smart File Organizer & Cleaner  v1.0.0           ║
  ║           Python Automation Portfolio Project            ║
  ╚══════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────┐
  │              MAIN MENU                  │
  ├─────────────────────────────────────────┤
  │  1  Organize Files into Categories       │
  │  2  Rename Files (Timestamp)             │
  │  3  Rename Files (Sequential)            │
  │  4  Detect & Remove Empty Folders        │
  │  5  View Session Statistics               │
  │  6  Change Working Directory             │
  │  0  Exit                                 │
  └─────────────────────────────────────────┘
```

---

## 💡 Sample Input / Output

### Input: Messy Downloads Folder

```
~/Downloads/
├── photo.jpg
├── photo.jpg          ← duplicate!
├── resume.pdf
├── budget.xlsx
├── song.mp3
├── lecture.mp4
├── archive.zip
└── notes.txt
```

### After Running Option 1 (Organize)

```
~/Downloads/
├── Images/
│   ├── photo.jpg
│   └── photo_2.jpg    ← duplicate renamed
├── Documents/
│   ├── resume.pdf
│   ├── budget.xlsx
│   └── notes.txt
├── Audio/
│   └── song.mp3
├── Videos/
│   └── lecture.mp4
└── Archives/
    └── archive.zip
```

### Log Output (`logs/operations.log`)

```
2025-06-15 14:32:01 | INFO     | Logger initialized. Log file: logs/operations_20250615_143201.log
2025-06-15 14:32:05 | INFO     | ============================================================
2025-06-15 14:32:05 | INFO     | ORGANIZE JOB STARTED  →  /home/user/Downloads
2025-06-15 14:32:05 | INFO     | ============================================================
2025-06-15 14:32:05 | INFO     | Found 8 file(s) to process.
2025-06-15 14:32:05 | INFO     | CREATED folder: Images/
2025-06-15 14:32:05 | INFO     | MOVED   'photo.jpg'  →  Images/photo.jpg
2025-06-15 14:32:05 | INFO     | RENAME  'photo.jpg'  →  'photo_2.jpg'  (duplicate)
2025-06-15 14:32:05 | INFO     | MOVED   'photo.jpg'  →  Images/photo_2.jpg
2025-06-15 14:32:05 | INFO     | CREATED folder: Documents/
2025-06-15 14:32:05 | INFO     | MOVED   'resume.pdf'  →  Documents/resume.pdf
...
2025-06-15 14:32:05 | INFO     | ORGANIZE JOB COMPLETE
```

### Statistics Dashboard

```
  SESSION STATISTICS

  Files scanned              8       ████████████████
  Files moved                8       ████████████████
  Files renamed              1       ██
  Folders created            5       ██████████
  Empty folders removed      0
  Errors encountered         0
```

---

## 🗂️ File Categories

| Category | Extensions |
|---|---|
| Images | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.svg` `.webp` `.tiff` `.heic` |
| Documents | `.pdf` `.doc` `.docx` `.txt` `.xls` `.xlsx` `.ppt` `.pptx` `.csv` `.md` |
| Videos | `.mp4` `.avi` `.mkv` `.mov` `.wmv` `.flv` `.webm` `.m4v` |
| Audio | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.wma` `.m4a` |
| Archives | `.zip` `.rar` `.tar` `.gz` `.7z` `.bz2` `.xz` |
| Code | `.py` `.js` `.html` `.css` `.java` `.cpp` `.json` `.sql` … |
| Others | Anything not matched above |

---

## 🔮 Future Improvements

- [ ] Recursive organization (scan all subfolders)
- [ ] GUI version using `tkinter` or `PyQt`
- [ ] Undo/rollback functionality using a JSON move-log
- [ ] Scheduled auto-organize via `cron` / Task Scheduler
- [ ] Duplicate detection by file hash (not just filename)
- [ ] File size reporting in statistics
- [ ] Export stats to CSV / HTML report

---

## 🧪 Running Tests

```bash
# Install dev dependencies first
pip install pytest

# Run tests (add your test files to tests/)
pytest tests/ -v
```

---

## 📸 Screenshots

> _Add screenshots of your terminal output here._

Place `.png` files inside the `screenshots/` folder and reference them:

```markdown
![Main Menu](screenshots/main_menu.png)
![Organize Output](screenshots/organize_output.png)
![Stats Dashboard](screenshots/stats_dashboard.png)
```

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

> _Built as a portfolio project demonstrating Python automation engineering skills._
