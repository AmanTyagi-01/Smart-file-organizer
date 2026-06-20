"""
tests/test_organizer.py
-----------------------
Unit tests for the Smart File Organizer & Cleaner project.

Run with:
    pytest tests/ -v
"""

import os
import sys
import shutil
import logging
import tempfile
import unittest
from pathlib import Path

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from organizer import FileOrganizer, FileRenamer, get_category  # noqa: E402
from cleaner import FolderCleaner                               # noqa: E402


# ── Shared test logger (silent during tests) ──────────────────────────────────
def _silent_logger() -> logging.Logger:
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.NullHandler())
    return logger


# ══════════════════════════════════════════════════════════════════════════════
#  get_category()
# ══════════════════════════════════════════════════════════════════════════════
class TestGetCategory(unittest.TestCase):

    def test_image_extensions(self):
        for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            with self.subTest(ext=ext):
                self.assertEqual(get_category(ext), "Images")

    def test_document_extensions(self):
        for ext in (".pdf", ".docx", ".txt", ".xlsx", ".csv"):
            with self.subTest(ext=ext):
                self.assertEqual(get_category(ext), "Documents")

    def test_video_extensions(self):
        for ext in (".mp4", ".avi", ".mkv", ".mov"):
            with self.subTest(ext=ext):
                self.assertEqual(get_category(ext), "Videos")

    def test_audio_extensions(self):
        for ext in (".mp3", ".wav", ".flac", ".aac"):
            with self.subTest(ext=ext):
                self.assertEqual(get_category(ext), "Audio")

    def test_archive_extensions(self):
        for ext in (".zip", ".rar", ".tar", ".7z"):
            with self.subTest(ext=ext):
                self.assertEqual(get_category(ext), "Archives")

    def test_code_extensions(self):
        for ext in (".py", ".js", ".html", ".css", ".java"):
            with self.subTest(ext=ext):
                self.assertEqual(get_category(ext), "Code")

    def test_unknown_extension_returns_others(self):
        self.assertEqual(get_category(".xyz"), "Others")
        self.assertEqual(get_category(".unknown"), "Others")

    def test_case_insensitive(self):
        self.assertEqual(get_category(".JPG"), "Images")
        self.assertEqual(get_category(".PDF"), "Documents")
        self.assertEqual(get_category(".MP3"), "Audio")


# ══════════════════════════════════════════════════════════════════════════════
#  FileOrganizer
# ══════════════════════════════════════════════════════════════════════════════
class TestFileOrganizer(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory with sample files before each test."""
        self.test_dir = tempfile.mkdtemp(prefix="sfo_test_")
        self.logger = _silent_logger()

        # Create sample files
        self.sample_files = {
            "photo.jpg":      "image content",
            "report.pdf":     "pdf content",
            "song.mp3":       "audio content",
            "video.mp4":      "video content",
            "archive.zip":    "archive content",
            "script.py":      "python content",
            "unknown.xyz":    "unknown content",
        }
        for name, content in self.sample_files.items():
            path = os.path.join(self.test_dir, name)
            with open(path, "w") as f:
                f.write(content)

    def tearDown(self):
        """Remove the temporary directory after each test."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_files_moved_to_correct_categories(self):
        organizer = FileOrganizer(self.test_dir, self.logger)
        organizer.organize()

        expected = {
            "photo.jpg":   "Images",
            "report.pdf":  "Documents",
            "song.mp3":    "Audio",
            "video.mp4":   "Videos",
            "archive.zip": "Archives",
            "script.py":   "Code",
            "unknown.xyz": "Others",
        }
        for filename, category in expected.items():
            dest = os.path.join(self.test_dir, category, filename)
            self.assertTrue(
                os.path.exists(dest),
                f"Expected {filename} in {category}/ but not found."
            )

    def test_category_folders_created(self):
        organizer = FileOrganizer(self.test_dir, self.logger)
        stats = organizer.organize()
        self.assertGreater(stats["folders_created"], 0)

    def test_files_moved_count(self):
        organizer = FileOrganizer(self.test_dir, self.logger)
        stats = organizer.organize()
        self.assertEqual(stats["files_moved"], len(self.sample_files))

    def test_files_scanned_count(self):
        organizer = FileOrganizer(self.test_dir, self.logger)
        stats = organizer.organize()
        self.assertEqual(stats["files_scanned"], len(self.sample_files))

    def test_zero_errors_on_clean_input(self):
        organizer = FileOrganizer(self.test_dir, self.logger)
        stats = organizer.organize()
        self.assertEqual(stats["errors"], 0)

    def test_duplicate_file_renamed(self):
        """If two files share a name, the second must be renamed."""
        # Create a duplicate: photo.jpg already exists; add it to Images/
        images_dir = os.path.join(self.test_dir, "Images")
        os.makedirs(images_dir, exist_ok=True)
        with open(os.path.join(images_dir, "photo.jpg"), "w") as f:
            f.write("pre-existing image")

        organizer = FileOrganizer(self.test_dir, self.logger)
        stats = organizer.organize()

        # Both photo.jpg and photo_2.jpg should exist in Images/
        self.assertTrue(os.path.exists(os.path.join(images_dir, "photo.jpg")))
        self.assertTrue(os.path.exists(os.path.join(images_dir, "photo_2.jpg")))
        self.assertGreaterEqual(stats["files_renamed"], 1)

    def test_invalid_directory_returns_error(self):
        organizer = FileOrganizer("/nonexistent/path/xyz", self.logger)
        stats = organizer.organize()
        self.assertGreater(stats["errors"], 0)


# ══════════════════════════════════════════════════════════════════════════════
#  FileRenamer
# ══════════════════════════════════════════════════════════════════════════════
class TestFileRenamer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sfr_test_")
        self.logger = _silent_logger()

        for i in range(5):
            path = os.path.join(self.test_dir, f"file_{i}.txt")
            with open(path, "w") as f:
                f.write(f"content {i}")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_sequential_rename_count(self):
        renamer = FileRenamer(self.test_dir, self.logger)
        renamed, errors = renamer.rename_sequentially("doc")
        self.assertEqual(renamed, 5)
        self.assertEqual(errors, 0)

    def test_sequential_rename_format(self):
        renamer = FileRenamer(self.test_dir, self.logger)
        renamer.rename_sequentially("doc")
        files = sorted(os.listdir(self.test_dir))
        self.assertEqual(files[0], "doc_0001.txt")
        self.assertEqual(files[4], "doc_0005.txt")

    def test_timestamp_rename_count(self):
        renamer = FileRenamer(self.test_dir, self.logger)
        renamed, errors = renamer.rename_with_timestamp("img")
        self.assertEqual(renamed, 5)
        self.assertEqual(errors, 0)

    def test_timestamp_rename_prefix(self):
        renamer = FileRenamer(self.test_dir, self.logger)
        renamer.rename_with_timestamp("img")
        files = os.listdir(self.test_dir)
        for f in files:
            self.assertTrue(f.startswith("img_"), f"File {f} missing prefix")


# ══════════════════════════════════════════════════════════════════════════════
#  FolderCleaner
# ══════════════════════════════════════════════════════════════════════════════
class TestFolderCleaner(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sfc_test_")
        self.logger = _silent_logger()

        # Create some empty dirs
        self.empty1 = os.path.join(self.test_dir, "empty_a")
        self.empty2 = os.path.join(self.test_dir, "empty_b")
        os.makedirs(self.empty1)
        os.makedirs(self.empty2)

        # Create a non-empty dir
        self.nonempty = os.path.join(self.test_dir, "has_files")
        os.makedirs(self.nonempty)
        with open(os.path.join(self.nonempty, "keep.txt"), "w") as f:
            f.write("keep")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_detects_empty_folders(self):
        cleaner = FolderCleaner(self.test_dir, self.logger)
        empty = cleaner.find_empty_folders()
        self.assertIn(self.empty1, empty)
        self.assertIn(self.empty2, empty)

    def test_does_not_detect_non_empty_folder(self):
        cleaner = FolderCleaner(self.test_dir, self.logger)
        empty = cleaner.find_empty_folders()
        self.assertNotIn(self.nonempty, empty)

    def test_removes_empty_folders(self):
        cleaner = FolderCleaner(self.test_dir, self.logger)
        empty = cleaner.find_empty_folders()
        removed, errors = cleaner.remove_empty_folders(empty)
        self.assertEqual(removed, 2)
        self.assertEqual(errors, 0)
        self.assertFalse(os.path.exists(self.empty1))
        self.assertFalse(os.path.exists(self.empty2))

    def test_non_empty_folder_not_removed(self):
        """os.rmdir should fail on non-empty directories."""
        cleaner = FolderCleaner(self.test_dir, self.logger)
        # Attempt to remove the non-empty folder directly
        removed, errors = cleaner.remove_empty_folders([self.nonempty])
        self.assertEqual(removed, 0)
        self.assertEqual(errors, 1)
        self.assertTrue(os.path.exists(self.nonempty))


# ── Test runner ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)
