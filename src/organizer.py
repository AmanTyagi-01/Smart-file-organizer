"""
organizer.py
------------
Core file organization engine for Smart File Organizer & Cleaner.
Handles scanning, categorization, duplicate detection, and moving files.

Author: Smart File Organizer Project
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

FILE_CATEGORIES: Dict[str, List[str]] = {
    "Images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
                   ".tiff", ".ico", ".heic", ".raw"],
    "Documents":  [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt",
                   ".pptx", ".odt", ".ods", ".csv", ".md", ".rtf", ".tex"],
    "Videos":     [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
                   ".m4v", ".3gp", ".mpeg", ".mpg"],
    "Audio":      [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
                   ".opus", ".aiff"],
    "Archives":   [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz",
                   ".tar.gz", ".tar.bz2"],
    "Code":       [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp",
                   ".c", ".cs", ".php", ".rb", ".go", ".rs", ".swift", ".kt",
                   ".json", ".xml", ".yaml", ".yml", ".sh", ".bat", ".sql"],
    "Others":     []   # Catch-all; populated at runtime
}


def get_category(file_extension: str) -> str:
    """
    Determine the category of a file based on its extension.

    Args:
        file_extension (str): Lowercase file extension including the dot.

    Returns:
        str: Category name.
    """
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"


class FileOrganizer:
    """
    Organizes files in a given directory into category-based subfolders.

    Attributes:
        source_dir (str): Path to the folder being organized.
        logger (logging.Logger): Logger instance for operation tracking.
        stats (dict): Running statistics for the current session.
    """

    def __init__(self, source_dir: str, logger: logging.Logger):
        self.source_dir = os.path.abspath(source_dir)
        self.logger = logger
        self.stats: Dict[str, int] = {
            "files_scanned":    0,
            "files_moved":      0,
            "files_renamed":    0,
            "folders_created":  0,
            "errors":           0,
            "skipped":          0,
        }


    def organize(self) -> Dict[str, int]:
        """
        Entry point: scan the source directory and organize all files.

        Returns:
            dict: Final statistics dictionary.
        """
        self.logger.info("=" * 60)
        self.logger.info(f"ORGANIZE JOB STARTED  →  {self.source_dir}")
        self.logger.info("=" * 60)

        if not os.path.isdir(self.source_dir):
            self.logger.error(f"Source directory not found: {self.source_dir}")
            self.stats["errors"] += 1
            return self.stats

        files = self._scan_directory()
        self.stats["files_scanned"] = len(files)
        self.logger.info(f"Found {len(files)} file(s) to process.")

        for file_path in files:
            self._process_file(file_path)

        self.logger.info("=" * 60)
        self.logger.info("ORGANIZE JOB COMPLETE")
        self.logger.info("=" * 60)
        return self.stats


    def _scan_directory(self) -> List[str]:
        """
        Return a flat list of all file paths in the source directory
        (non-recursive; skips subdirectories that are category folders).

        Returns:
            list[str]: Absolute file paths.
        """
        files = []
        category_names = set(FILE_CATEGORIES.keys())

        try:
            for entry in os.scandir(self.source_dir):
                if entry.is_file():
                    files.append(entry.path)
                elif entry.is_dir() and entry.name not in category_names:
                    pass
        except PermissionError as exc:
            self.logger.error(f"Permission denied scanning {self.source_dir}: {exc}")
            self.stats["errors"] += 1

        return files

    def _process_file(self, file_path: str) -> None:
        """
        Categorize and move a single file to the appropriate subfolder.

        Args:
            file_path (str): Absolute path of the file to process.
        """
        try:
            filename = os.path.basename(file_path)
            extension = Path(file_path).suffix.lower()
            category = get_category(extension)

            dest_dir = os.path.join(self.source_dir, category)
            self._ensure_directory(dest_dir)

            dest_path = self._resolve_destination(dest_dir, filename)
            final_name = os.path.basename(dest_path)

            if final_name != filename:
                self.logger.info(
                    f"RENAME  '{filename}'  →  '{final_name}'  (duplicate)"
                )
                self.stats["files_renamed"] += 1

            shutil.move(file_path, dest_path)
            self.logger.info(
                f"MOVED   '{filename}'  →  {category}/{final_name}"
            )
            self.stats["files_moved"] += 1

        except FileNotFoundError as exc:
            self.logger.error(f"File not found: {file_path}  |  {exc}")
            self.stats["errors"] += 1
        except PermissionError as exc:
            self.logger.error(f"Permission denied: {file_path}  |  {exc}")
            self.stats["errors"] += 1
        except shutil.Error as exc:
            self.logger.error(f"Shutil error moving {file_path}  |  {exc}")
            self.stats["errors"] += 1
        except Exception as exc:
            self.logger.error(f"Unexpected error processing {file_path}  |  {exc}")
            self.stats["errors"] += 1

    def _ensure_directory(self, dir_path: str) -> None:
        """
        Create a directory if it does not already exist.

        Args:
            dir_path (str): Directory path to create.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            self.logger.info(f"CREATED folder: {os.path.basename(dir_path)}/")
            self.stats["folders_created"] += 1

    def _resolve_destination(self, dest_dir: str, filename: str) -> str:
        """
        Return a collision-free destination path.
        If a file with the same name already exists, append an incremental
        counter before the extension:  report.pdf → report_2.pdf

        Args:
            dest_dir  (str): Target directory.
            filename  (str): Original filename.

        Returns:
            str: Full path that does not collide with existing files.
        """
        dest_path = os.path.join(dest_dir, filename)
        if not os.path.exists(dest_path):
            return dest_path

        stem = Path(filename).stem
        suffix = Path(filename).suffix
        counter = 2

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = os.path.join(dest_dir, new_name)
            if not os.path.exists(new_path):
                return new_path
            counter += 1


class FileRenamer:
    """
    Batch-renames files in a directory using timestamp or sequential numbering.
    """

    def __init__(self, target_dir: str, logger: logging.Logger):
        self.target_dir = os.path.abspath(target_dir)
        self.logger = logger
        self.renamed_count = 0
        self.error_count = 0

    def rename_with_timestamp(self, prefix: str = "file") -> Tuple[int, int]:
        """
        Rename all files in the target directory by prepending a timestamp.

        Args:
            prefix (str): Optional prefix before the timestamp.

        Returns:
            tuple[int, int]: (renamed_count, error_count)
        """
        self.logger.info(f"RENAME-TIMESTAMP job started in: {self.target_dir}")

        try:
            entries = [
                e for e in os.scandir(self.target_dir) if e.is_file()
            ]
        except PermissionError as exc:
            self.logger.error(f"Cannot read directory: {exc}")
            return 0, 1

        for idx, entry in enumerate(entries, start=1):
            try:
                ext = Path(entry.name).suffix
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{prefix}_{ts}_{idx:03d}{ext}"
                new_path = os.path.join(self.target_dir, new_name)

                os.rename(entry.path, new_path)
                self.logger.info(f"RENAMED  '{entry.name}'  →  '{new_name}'")
                self.renamed_count += 1

            except PermissionError as exc:
                self.logger.error(f"Permission denied: {entry.path}  |  {exc}")
                self.error_count += 1
            except Exception as exc:
                self.logger.error(f"Rename failed: {entry.path}  |  {exc}")
                self.error_count += 1

        return self.renamed_count, self.error_count

    def rename_sequentially(self, prefix: str = "file") -> Tuple[int, int]:
        """
        Rename files as prefix_001.ext, prefix_002.ext, …

        Args:
            prefix (str): Base name for renamed files.

        Returns:
            tuple[int, int]: (renamed_count, error_count)
        """
        self.logger.info(f"RENAME-SEQUENTIAL job started in: {self.target_dir}")

        try:
            entries = sorted(
                [e for e in os.scandir(self.target_dir) if e.is_file()],
                key=lambda e: e.name
            )
        except PermissionError as exc:
            self.logger.error(f"Cannot read directory: {exc}")
            return 0, 1

        for idx, entry in enumerate(entries, start=1):
            try:
                ext = Path(entry.name).suffix
                new_name = f"{prefix}_{idx:04d}{ext}"
                new_path = os.path.join(self.target_dir, new_name)

                if entry.path == new_path:
                    continue  # Already correctly named

                os.rename(entry.path, new_path)
                self.logger.info(f"RENAMED  '{entry.name}'  →  '{new_name}'")
                self.renamed_count += 1

            except Exception as exc:
                self.logger.error(f"Rename failed: {entry.path}  |  {exc}")
                self.error_count += 1

        return self.renamed_count, self.error_count