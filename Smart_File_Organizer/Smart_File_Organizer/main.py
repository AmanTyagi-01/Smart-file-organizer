#!/usr/bin/env python3
"""
main.py
-------
Smart File Organizer & Cleaner — Command-Line Interface

Entry point for the application. Provides a menu-driven CLI that exposes
all organizer, renamer, and cleaner features with proper error handling
and a live statistics dashboard.

Usage:
    python main.py

Author : Smart File Organizer Project
Version: 1.0.0
"""

import os
import sys
import time
from datetime import datetime

# ── Local imports ─────────────────────────────────────────────────────────────
# Allow `python main.py` from the project root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from logger_config import setup_logger          # noqa: E402
from organizer import FileOrganizer, FileRenamer  # noqa: E402
from cleaner import FolderCleaner               # noqa: E402

# ── ANSI Color Helpers ────────────────────────────────────────────────────────
# Gracefully degrade on terminals that don't support ANSI codes.

def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class Color:
    RESET  = "\033[0m"  if _supports_color() else ""
    BOLD   = "\033[1m"  if _supports_color() else ""
    GREEN  = "\033[92m" if _supports_color() else ""
    CYAN   = "\033[96m" if _supports_color() else ""
    YELLOW = "\033[93m" if _supports_color() else ""
    RED    = "\033[91m" if _supports_color() else ""
    BLUE   = "\033[94m" if _supports_color() else ""
    DIM    = "\033[2m"  if _supports_color() else ""


# ── UI Helpers ────────────────────────────────────────────────────────────────

BANNER = rf"""
{Color.CYAN}{Color.BOLD}
  ╔══════════════════════════════════════════════════════════╗
  ║        Smart File Organizer & Cleaner  v1.0.0           ║
  ║           Python Automation Portfolio Project            ║
  ╚══════════════════════════════════════════════════════════╝
{Color.RESET}"""

MENU = f"""
{Color.BOLD}  ┌─────────────────────────────────────────┐{Color.RESET}
{Color.BOLD}  │              MAIN MENU                  │{Color.RESET}
{Color.BOLD}  ├─────────────────────────────────────────┤{Color.RESET}
  │  {Color.GREEN}1{Color.RESET}  Organize Files into Categories       │
  │  {Color.GREEN}2{Color.RESET}  Rename Files (Timestamp)             │
  │  {Color.GREEN}3{Color.RESET}  Rename Files (Sequential)            │
  │  {Color.GREEN}4{Color.RESET}  Detect & Remove Empty Folders        │
  │  {Color.GREEN}5{Color.RESET}  View Session Statistics               │
  │  {Color.GREEN}6{Color.RESET}  Change Working Directory              │
  │  {Color.RED}0{Color.RESET}  Exit                                 │
{Color.BOLD}  └─────────────────────────────────────────┘{Color.RESET}
"""


def print_banner() -> None:
    """Print the application banner."""
    print(BANNER)
    print(f"  {Color.DIM}Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.RESET}\n")


def print_menu() -> None:
    """Print the main menu."""
    print(MENU)


def separator(char: str = "─", width: int = 54) -> str:
    return f"  {Color.DIM}{char * width}{Color.RESET}"


def prompt_directory(current: str) -> str:
    """
    Prompt the user to enter or confirm a directory path.

    Args:
        current (str): Currently selected directory.

    Returns:
        str: Validated absolute directory path.
    """
    print(separator())
    print(f"\n  {Color.YELLOW}Current directory:{Color.RESET}  {current or '(none)'}\n")
    raw = input("  Enter folder path (or press Enter to keep current): ").strip()

    if not raw:
        return current

    path = os.path.abspath(raw)

    if not os.path.isdir(path):
        print(f"\n  {Color.RED}✗  Directory not found:{Color.RESET} {path}")
        return current

    print(f"\n  {Color.GREEN}✓  Directory set:{Color.RESET} {path}")
    return path


def print_stats(stats: dict) -> None:
    """
    Render a formatted statistics dashboard.

    Args:
        stats (dict): Aggregated statistics dictionary.
    """
    print(f"\n{separator()}")
    print(f"\n  {Color.BOLD}{Color.CYAN}SESSION STATISTICS{Color.RESET}\n")
    rows = [
        ("Files scanned",        stats.get("files_scanned",    0), Color.BLUE),
        ("Files moved",          stats.get("files_moved",       0), Color.GREEN),
        ("Files renamed",        stats.get("files_renamed",     0), Color.GREEN),
        ("Folders created",      stats.get("folders_created",   0), Color.CYAN),
        ("Empty folders removed",stats.get("folders_removed",   0), Color.YELLOW),
        ("Errors encountered",   stats.get("errors",            0), Color.RED),
    ]
    for label, value, color in rows:
        bar_width = min(value * 2, 30)
        bar = "█" * bar_width
        print(f"  {label:<26} {color}{value:>4}{Color.RESET}  {Color.DIM}{bar}{Color.RESET}")

    print(f"\n{separator()}\n")


def confirm(prompt: str) -> bool:
    """
    Ask the user a yes/no question.

    Args:
        prompt (str): Question text.

    Returns:
        bool: True if the user answers 'y' or 'yes'.
    """
    ans = input(f"\n  {Color.YELLOW}{prompt}{Color.RESET} [y/N]: ").strip().lower()
    return ans in ("y", "yes")


# ── Main Application ──────────────────────────────────────────────────────────

def main() -> None:
    """Application entry point."""
    print_banner()

    # ── Initialize logger ─────────────────────────────────────────────────────
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    logger = setup_logger(log_dir)
    logger.info("Application started.")

    # ── Aggregated session statistics ─────────────────────────────────────────
    session_stats: dict = {
        "files_scanned":    0,
        "files_moved":      0,
        "files_renamed":    0,
        "folders_created":  0,
        "folders_removed":  0,
        "errors":           0,
    }

    # ── Working directory ─────────────────────────────────────────────────────
    working_dir: str = ""

    # ── Main loop ─────────────────────────────────────────────────────────────
    while True:
        print_menu()
        choice = input(f"  {Color.BOLD}Select an option:{Color.RESET} ").strip()

        # ── Option 0: Exit ────────────────────────────────────────────────────
        if choice == "0":
            print(f"\n  {Color.GREEN}Thank you for using Smart File Organizer!{Color.RESET}")
            print(f"  Log saved to: {log_dir}/operations.log\n")
            logger.info("Application exited by user.")
            sys.exit(0)

        # ── Option 1: Organize ────────────────────────────────────────────────
        elif choice == "1":
            working_dir = prompt_directory(working_dir)
            if not working_dir:
                print(f"\n  {Color.RED}Please set a directory first.{Color.RESET}")
                continue

            print(f"\n  {Color.CYAN}Scanning and organizing files...{Color.RESET}\n")
            organizer = FileOrganizer(working_dir, logger)

            try:
                stats = organizer.organize()
                # Merge into session totals
                for key in ("files_scanned", "files_moved",
                            "files_renamed", "folders_created", "errors"):
                    session_stats[key] += stats.get(key, 0)

                print(f"\n  {Color.GREEN}✓  Organization complete!{Color.RESET}")
                print_stats(session_stats)

            except Exception as exc:
                logger.error(f"Unexpected error during organize: {exc}")
                print(f"\n  {Color.RED}✗  An error occurred: {exc}{Color.RESET}")
                session_stats["errors"] += 1

        # ── Option 2: Rename — Timestamp ──────────────────────────────────────
        elif choice == "2":
            working_dir = prompt_directory(working_dir)
            if not working_dir:
                print(f"\n  {Color.RED}Please set a directory first.{Color.RESET}")
                continue

            prefix = input("  Enter filename prefix (default: 'file'): ").strip() or "file"

            if not confirm(f"Rename all files in '{working_dir}' with timestamp?"):
                print(f"  {Color.YELLOW}Operation cancelled.{Color.RESET}")
                continue

            renamer = FileRenamer(working_dir, logger)
            renamed, errors = renamer.rename_with_timestamp(prefix)

            session_stats["files_renamed"] += renamed
            session_stats["errors"] += errors

            print(f"\n  {Color.GREEN}✓  Renamed {renamed} file(s).{Color.RESET}")
            if errors:
                print(f"  {Color.RED}✗  {errors} error(s) encountered.{Color.RESET}")

        # ── Option 3: Rename — Sequential ─────────────────────────────────────
        elif choice == "3":
            working_dir = prompt_directory(working_dir)
            if not working_dir:
                print(f"\n  {Color.RED}Please set a directory first.{Color.RESET}")
                continue

            prefix = input("  Enter filename prefix (default: 'file'): ").strip() or "file"

            if not confirm(f"Rename all files in '{working_dir}' sequentially?"):
                print(f"  {Color.YELLOW}Operation cancelled.{Color.RESET}")
                continue

            renamer = FileRenamer(working_dir, logger)
            renamed, errors = renamer.rename_sequentially(prefix)

            session_stats["files_renamed"] += renamed
            session_stats["errors"] += errors

            print(f"\n  {Color.GREEN}✓  Renamed {renamed} file(s).{Color.RESET}")
            if errors:
                print(f"  {Color.RED}✗  {errors} error(s) encountered.{Color.RESET}")

        # ── Option 4: Clean empty folders ─────────────────────────────────────
        elif choice == "4":
            working_dir = prompt_directory(working_dir)
            if not working_dir:
                print(f"\n  {Color.RED}Please set a directory first.{Color.RESET}")
                continue

            print(f"\n  {Color.CYAN}Scanning for empty folders...{Color.RESET}")
            cleaner = FolderCleaner(working_dir, logger)
            empty = cleaner.find_empty_folders()

            if not empty:
                print(f"  {Color.GREEN}✓  No empty folders found.{Color.RESET}")
                continue

            print(f"\n  Found {Color.YELLOW}{len(empty)}{Color.RESET} empty folder(s):\n")
            for folder in empty:
                rel = os.path.relpath(folder, working_dir)
                print(f"    {Color.DIM}• {rel}{Color.RESET}")

            if confirm(f"Delete these {len(empty)} empty folder(s)?"):
                removed, errors = cleaner.remove_empty_folders(empty)
                session_stats["folders_removed"] += removed
                session_stats["errors"] += errors

                print(f"\n  {Color.GREEN}✓  Removed {removed} folder(s).{Color.RESET}")
                if errors:
                    print(f"  {Color.RED}✗  {errors} error(s) encountered.{Color.RESET}")
            else:
                print(f"  {Color.YELLOW}Operation cancelled.{Color.RESET}")

        # ── Option 5: View stats ──────────────────────────────────────────────
        elif choice == "5":
            print_stats(session_stats)

        # ── Option 6: Change directory ────────────────────────────────────────
        elif choice == "6":
            working_dir = prompt_directory("")

        else:
            print(f"\n  {Color.RED}Invalid option. Please enter 0-6.{Color.RESET}")

        # Small pause so the user can read the output before menu re-renders
        time.sleep(0.3)


# ── Entry guard ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Color.YELLOW}Interrupted by user. Exiting...{Color.RESET}\n")
        sys.exit(0)
