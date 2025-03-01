#!/usr/bin/env python3
"""Script to fix cross-references in documentation files."""

import os
import re
from pathlib import Path


def fix_markdown_refs(file_path):
    """Fix cross-references in Markdown files."""
    with open(file_path, "r") as f:
        content = f.read()

    # Common reference fixes
    fixes = {
        r"\[([^\]]+)\]\(([^)]+)\.md\)": r"[\\1](\\2.rst)",  # Convert .md to .rst
        r"\[([^\]]+)\]\(\.\.\/api\/modules\.md\)": r"[\\1](../api/index.rst)",  # Fix API reference
        r"\[([^\]]+)\]\(\.\/FAQ\.md\)": r"[\\1](faq.rst)",  # Fix FAQ reference
        r"\[([^\]]+)\]\(\.\/api\/README\.md\)": r"[\\1](api/index.rst)",  # Fix API README reference
    }

    for pattern, replacement in fixes.items():
        content = re.sub(pattern, replacement, content)

    with open(file_path, "w") as f:
        f.write(content)


def fix_rst_refs(file_path):
    """Fix cross-references in RST files."""
    with open(file_path, "r") as f:
        content = f.read()

    # Common reference fixes
    fixes = {
        r":doc:`/api/([^`]+)`": r":doc:`../api/\\1`",  # Fix absolute API references
        r":doc:`/guides/([^`]+)`": r":doc:`../guides/\\1`",  # Fix absolute guide references
    }

    for pattern, replacement in fixes.items():
        content = re.sub(pattern, replacement, content)

    with open(file_path, "w") as f:
        f.write(content)


def ensure_api_index():
    """Ensure API index.rst exists and is properly structured."""
    api_dir = Path(__file__).parent.parent / "api"
    api_dir.mkdir(exist_ok=True)

    index_content = """API Reference
============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   core/index
   ai/index
   storage/index
"""

    index_path = api_dir / "index.rst"
    index_path.write_text(index_content)


def main():
    """Main function to fix all cross-references."""
    docs_dir = Path(__file__).parent.parent

    # Fix Markdown files
    for md_file in docs_dir.rglob("*.md"):
        print(f"Processing Markdown file: {md_file}")
        fix_markdown_refs(md_file)

    # Fix RST files
    for rst_file in docs_dir.rglob("*.rst"):
        print(f"Processing RST file: {rst_file}")
        fix_rst_refs(rst_file)

    # Ensure API documentation structure
    ensure_api_index()


if __name__ == "__main__":
    main()
