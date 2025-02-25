#!/usr/bin/env python3
"""Script to fix double video_understanding imports."""

import os
import re
from pathlib import Path

def fix_imports(file_path):
    """Fix imports in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace imports
    new_content = re.sub(
        r'from video_understanding\.video_understanding\.',
        'from video_understanding.',
        content
    )
    new_content = re.sub(
        r'import video_understanding\.video_understanding\.',
        'import video_understanding.',
        new_content
    )

    if new_content != content:
        print(f"Fixing imports in {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    """Main function."""
    root = Path('.')

    # Skip these directories
    skip_dirs = {'.git', '.github', 'venv', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}

    # Process Python files
    for path in root.rglob('*.py'):
        if any(skip_dir in path.parts for skip_dir in skip_dirs):
            continue
        fix_imports(path)

if __name__ == '__main__':
    main()
