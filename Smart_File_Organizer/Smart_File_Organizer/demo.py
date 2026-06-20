#!/usr/bin/env python3
"""
demo.py
-------
Automated demonstration of Smart File Organizer & Cleaner.
Creates a realistic sample folder, runs every feature, and prints results.

Usage:
    python demo.py
"""

import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from logger_config import setup_logger
from organizer import FileOrganizer, FileRenamer
from cleaner import FolderCleaner

# ── ANSI helpers ──────────────────────────────────────────────────────────────
G  = "\033[92m"
C  = "\033[96m"
Y  = "\033[93m"
R  = "\033[91m"
B  = "\033[94m"
DIM= "\033[2m"
BO = "\033[1m"
X  = "\033[0m"


def section(title: str) -> None:
    print(f"\n{C}{BO}{'─'*60}{X}")
    print(f"{C}{BO}  {title}{X}")
    print(f"{C}{BO}{'─'*60}{X}\n")


def tree(root: str, indent: int = 0) -> None:
    """Print a simple ASCII directory tree."""
    prefix = "  " * indent
    try:
        entries = sorted(os.scandir(root), key=lambda e: (e.is_file(), e.name))
    except PermissionError:
        return
    for entry in entries:
        icon = "📄" if entry.is_file() else "📁"
        print(f"{prefix}  {icon}  {DIM}{entry.name}{X}")
        if entry.is_dir():
            tree(entry.path, indent + 1)


def main() -> None:
    print(f"\n{C}{BO}")
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║       Smart File Organizer & Cleaner — DEMO RUN         ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print(f"{X}")

    # ── Setup ─────────────────────────────────────────────────────────────────
    demo_dir = tempfile.mkdtemp(prefix="SFO_demo_")
    log_dir  = os.path.join(demo_dir, "logs")
    logger   = setup_logger(log_dir)
    logger.info("DEMO RUN STARTED")

    # ── 1. Create messy sample directory ─────────────────────────────────────
    section("STEP 1 — Creating messy sample folder")

    sample_files = [
        # Images
        ("vacation.jpg",     "jpeg data"),
        ("screenshot.png",   "png data"),
        ("avatar.webp",      "webp data"),
        # Duplicate image
        ("vacation.jpg",     "duplicate jpeg"),   # will be handled as dup
        # Documents
        ("resume.pdf",       "pdf content"),
        ("notes.txt",        "text content"),
        ("budget.xlsx",      "excel content"),
        ("report.docx",      "word content"),
        # Audio
        ("song.mp3",         "mp3 data"),
        ("podcast.wav",      "wav data"),
        # Video
        ("lecture.mp4",      "mp4 data"),
        ("clip.mkv",         "mkv data"),
        # Archives
        ("backup.zip",       "zip content"),
        ("source.tar.gz",    "tar content"),
        # Code
        ("script.py",        "python code"),
        ("index.html",       "html code"),
        ("styles.css",       "css code"),
        # Others
        ("mystery.xyz",      "unknown format"),
        ("data.bin",         "binary blob"),
    ]

    # Write files — handle intended duplicate
    seen = set()
    for filename, content in sample_files:
        if filename in seen:
            # Write a second copy with slightly different name to simulate dup
            base, ext = os.path.splitext(filename)
            filename = f"{base}_copy{ext}"
        seen.add(filename)
        with open(os.path.join(demo_dir, filename), "w") as f:
            f.write(content)

    # Add some empty folders for cleaner demo
    for empty_name in ("old_project", "temp_stuff", "unused"):
        os.makedirs(os.path.join(demo_dir, empty_name), exist_ok=True)

    print(f"  Created demo folder: {DIM}{demo_dir}{X}")
    print(f"\n  {Y}Before organization:{X}\n")
    tree(demo_dir)

    # ── 2. Organize files ─────────────────────────────────────────────────────
    section("STEP 2 — Organizing files into categories")

    organizer = FileOrganizer(demo_dir, logger)
    org_stats  = organizer.organize()

    print(f"\n  {Y}After organization:{X}\n")
    tree(demo_dir)

    # ── 3. Detect & remove empty folders ─────────────────────────────────────
    section("STEP 3 — Detecting & removing empty folders")

    cleaner     = FolderCleaner(demo_dir, logger)
    empty_found = cleaner.find_empty_folders()

    print(f"  Found {Y}{len(empty_found)}{X} empty folder(s):")
    for f in empty_found:
        print(f"    {DIM}• {os.path.relpath(f, demo_dir)}{X}")

    removed, rm_errors = cleaner.remove_empty_folders(empty_found)
    print(f"\n  {G}✓  Removed {removed} folder(s).{X}")

    # ── 4. Rename files in Documents/ sequentially ────────────────────────────
    section("STEP 4 — Renaming Documents sequentially")

    docs_dir = os.path.join(demo_dir, "Documents")
    if os.path.isdir(docs_dir):
        renamer = FileRenamer(docs_dir, logger)
        renamed, rn_errors = renamer.rename_sequentially("doc")
        print(f"  {G}✓  Renamed {renamed} document(s).{X}")
        print(f"\n  {Y}Documents/ after rename:{X}\n")
        tree(docs_dir)
    else:
        renamed, rn_errors = 0, 0
        print(f"  {R}No Documents/ folder found — skipping.{X}")

    # ── 5. Statistics dashboard ───────────────────────────────────────────────
    section("STEP 5 — Session Statistics")

    total_stats = {
        "Files scanned":         org_stats.get("files_scanned", 0),
        "Files moved":           org_stats.get("files_moved", 0),
        "Files renamed":         org_stats.get("files_renamed", 0) + renamed,
        "Folders created":       org_stats.get("folders_created", 0),
        "Empty folders removed": removed,
        "Errors encountered":    org_stats.get("errors", 0) + rm_errors + rn_errors,
    }

    max_val = max(total_stats.values()) or 1
    for label, value in total_stats.items():
        bar_len = int((value / max_val) * 28)
        bar     = "█" * bar_len
        color   = R if label == "Errors encountered" and value > 0 else G
        print(f"  {label:<28} {color}{value:>3}{X}  {DIM}{bar}{X}")

    # ── 6. Log location ───────────────────────────────────────────────────────
    section("STEP 6 — Log file preview (last 20 lines)")

    log_path = os.path.join(log_dir, "operations.log")
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as fh:
            lines = fh.readlines()
        preview = lines[-20:] if len(lines) > 20 else lines
        for line in preview:
            level = "INFO" if "INFO" in line else ("ERROR" if "ERROR" in line else "DEBUG")
            col   = G if level == "INFO" else (R if level == "ERROR" else DIM)
            print(f"  {col}{line.rstrip()}{X}")
        print(f"\n  {DIM}Full log: {log_path}{X}")
    else:
        print(f"  {R}Log file not found.{X}")

    # ── Cleanup notice ────────────────────────────────────────────────────────
    print(f"\n{C}{BO}{'─'*60}{X}")
    print(f"\n  {G}✓  Demo complete!{X}")
    print(f"  Demo folder: {DIM}{demo_dir}{X}")
    print(f"  Cleaning up... ", end="")
    shutil.rmtree(demo_dir, ignore_errors=True)
    print(f"{G}done.{X}\n")


if __name__ == "__main__":
    main()
