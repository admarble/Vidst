#!/usr/bin/env python3
"""
Vidst Backup Helper

This script provides utilities for backing up files during the Vidst refactoring
process. It can be imported as a module or run as a standalone script.
"""

import os
import shutil
import datetime
import argparse
import glob


def backup_file(file_path, backup_dir=None):
    """Back up a single file with timestamp.

    Args:
        file_path: Path to the file to back up
        backup_dir: Optional custom backup directory

    Returns:
        The path to the backup file

    Raises:
        FileNotFoundError: If source file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    # Get just the filename
    filename = os.path.basename(file_path)

    # Create backup directory if it doesn't exist
    if backup_dir is None:
        backup_dir = os.path.join("refactor", "07_backup", "file_backups")

    os.makedirs(backup_dir, exist_ok=True)

    # Create timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup path with timestamp
    name, ext = os.path.splitext(filename)
    backup_filename = f"{name}_{timestamp}{ext}.bak"
    backup_path = os.path.join(backup_dir, backup_filename)

    # Copy the file
    shutil.copy2(file_path, backup_path)

    return backup_path


def backup_directory(directory_path, backup_dir=None):
    """Back up an entire directory.

    Args:
        directory_path: Path to the directory to back up
        backup_dir: Optional custom backup directory

    Returns:
        The path to the backup directory

    Raises:
        NotADirectoryError: If source is not a directory
    """
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"Source is not a directory: {directory_path}")

    # Get directory name
    dirname = os.path.basename(directory_path)

    # Create backup directory if it doesn't exist
    if backup_dir is None:
        backup_dir = os.path.join("refactor", "07_backup", "directory_backups")

    os.makedirs(backup_dir, exist_ok=True)

    # Create timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup path with timestamp
    backup_dirname = f"{dirname}_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_dirname)

    # Copy the directory (ignoring .git and venv directories)
    shutil.copytree(
        directory_path,
        backup_path,
        ignore=shutil.ignore_patterns(".git", "venv", "__pycache__", "*.pyc", "*.pyo"),
    )

    return backup_path


def backup_by_pattern(pattern, backup_dir=None):
    """Back up files matching a pattern.

    Args:
        pattern: Glob pattern for files to back up
        backup_dir: Optional custom backup directory

    Returns:
        List of paths to backup files

    Raises:
        ValueError: If no files match the pattern
    """
    # Find files matching pattern
    files = glob.glob(pattern, recursive=True)

    if not files:
        raise ValueError(f"No files match the pattern: {pattern}")

    # Back up each file
    backup_paths = []
    for file_path in files:
        if os.path.isfile(file_path):
            backup_path = backup_file(file_path, backup_dir)
            backup_paths.append(backup_path)

    return backup_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vidst backup helper")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # File backup command
    file_parser = subparsers.add_parser("file", help="Back up a single file")
    file_parser.add_argument("file_path", help="Path to the file to back up")
    file_parser.add_argument("--backup-dir", help="Custom backup directory")

    # Directory backup command
    dir_parser = subparsers.add_parser("dir", help="Back up a directory")
    dir_parser.add_argument("dir_path", help="Path to the directory to back up")
    dir_parser.add_argument("--backup-dir", help="Custom backup directory")

    # Pattern backup command
    pattern_parser = subparsers.add_parser(
        "pattern", help="Back up files matching a pattern"
    )
    pattern_parser.add_argument("pattern", help="Glob pattern for files to back up")
    pattern_parser.add_argument("--backup-dir", help="Custom backup directory")

    args = parser.parse_args()

    try:
        if args.command == "file":
            backup_path = backup_file(args.file_path, args.backup_dir)
            print(f"File backed up to: {backup_path}")
        elif args.command == "dir":
            backup_path = backup_directory(args.dir_path, args.backup_dir)
            print(f"Directory backed up to: {backup_path}")
        elif args.command == "pattern":
            backup_paths = backup_by_pattern(args.pattern, args.backup_dir)
            print(f"Backed up {len(backup_paths)} files:")
            for path in backup_paths:
                print(f"  - {path}")
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {str(e)}")
