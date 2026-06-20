"""
cleaner.py
----------
Folder cleaning utilities for Smart File Organizer & Cleaner.
Detects and removes empty directories with user confirmation.

Author: Smart File Organizer Project
"""

import os
import logging
from typing import List, Tuple


class FolderCleaner:
    """
    Scans a directory tree for empty folders and optionally removes them.

    Attributes:
        root_dir (str):            Root directory to scan.
        logger (logging.Logger):   Logger instance.
        removed_count (int):       Number of folders removed in this session.
        error_count (int):         Number of removal errors in this session.
    """

    def __init__(self, root_dir: str, logger: logging.Logger):
        self.root_dir = os.path.abspath(root_dir)
        self.logger = logger
        self.removed_count: int = 0
        self.error_count: int = 0

    # ── Public Interface ──────────────────────────────────────────────────────

    def find_empty_folders(self) -> List[str]:
        """
        Walk the directory tree bottom-up and collect paths of empty folders.

        Returns:
            list[str]: Sorted list of empty directory paths (deepest first).
        """
        empty_folders: List[str] = []

        try:
            # os.walk bottom-up so nested empty folders surface correctly
            for dirpath, dirnames, filenames in os.walk(self.root_dir, topdown=False):
                if dirpath == self.root_dir:
                    continue  # Never suggest removing the root itself

                # A folder is empty when it contains no files and no
                # subdirectories (or only subdirectories that are themselves
                # empty — already captured by bottom-up traversal).
                if not filenames and not os.listdir(dirpath):
                    empty_folders.append(dirpath)
                    self.logger.debug(f"Empty folder detected: {dirpath}")

        except PermissionError as exc:
            self.logger.error(f"Permission denied scanning {self.root_dir}: {exc}")
            self.error_count += 1

        return empty_folders

    def remove_empty_folders(self, folders: List[str]) -> Tuple[int, int]:
        """
        Attempt to remove each folder in the provided list.

        Args:
            folders (list[str]): Folder paths to delete.

        Returns:
            tuple[int, int]: (removed_count, error_count) for this call.
        """
        removed = 0
        errors = 0

        for folder in folders:
            try:
                os.rmdir(folder)  # Only removes if truly empty
                self.logger.info(f"DELETED  empty folder: {folder}")
                removed += 1
                self.removed_count += 1

            except FileNotFoundError:
                # Already gone — not an error in our context
                self.logger.warning(f"Folder already removed: {folder}")

            except OSError as exc:
                self.logger.error(
                    f"Failed to remove '{folder}': {exc}"
                )
                errors += 1
                self.error_count += 1

            except Exception as exc:
                self.logger.error(
                    f"Unexpected error removing '{folder}': {exc}"
                )
                errors += 1
                self.error_count += 1

        return removed, errors

    def get_folder_summary(self) -> dict:
        """
        Return a summary of the cleaner's current session statistics.

        Returns:
            dict: Session statistics.
        """
        return {
            "removed": self.removed_count,
            "errors":  self.error_count,
        }
