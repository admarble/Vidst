#!/usr/bin/env python3
"""Script to fix RST title underlines."""

import os
import re
from pathlib import Path


def fix_title_underlines(file_path):
    """Fix title underlines in an RST file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Split into lines while preserving line endings
    lines = content.splitlines(True)
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # If we have a next line and it contains only decoration characters
        if i + 1 < len(lines) and re.match(r"^[-=~`]+\s*$", lines[i + 1].strip()):
            title_line = line.rstrip()
            underline = lines[i + 1].rstrip()
            decoration_char = underline[0]
            # Create new underline matching title length
            new_underline = decoration_char * len(title_line) + "\n"

            fixed_lines.append(title_line + "\n")
            fixed_lines.append(new_underline)
            i += 2
        else:
            fixed_lines.append(line)
            i += 1

    # Write back to file
    with open(file_path, "w") as f:
        f.writelines(fixed_lines)


def main():
    """Main function to process all RST files."""
    docs_dir = Path(__file__).parent.parent

    # Process all RST files
    for rst_file in docs_dir.rglob("*.rst"):
        print(f"Processing {rst_file}")
        fix_title_underlines(rst_file)


if __name__ == "__main__":
    main()
