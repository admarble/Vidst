#!/usr/bin/env python3
"""Script to reorganize documentation structure."""

import os
import shutil
from pathlib import Path


def create_directory_structure():
    """Create the new documentation directory structure."""
    base_dirs = [
        "getting_started",
        "user_guide",
        "api_reference/core",
        "api_reference/ai",
        "api_reference/storage",
        "developer_guide",
        "deployment",
        "_meta",
    ]

    docs_root = Path("docs")
    for dir_path in base_dirs:
        full_path = docs_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        # Create index.rst for each directory
        with open(full_path / "index.rst", "w") as f:
            title = dir_path.replace("/", " - ").title()
            f.write(
                f"{title}\n{'=' * len(title)}\n\n.. toctree::\n   :maxdepth: 2\n   :caption: Contents:\n\n"
            )


def create_main_index():
    """Create the main index.rst file."""
    content = """Video Understanding AI Documentation
================================

Welcome to the Video Understanding AI documentation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started/index
   user_guide/index
   api_reference/core/index
   api_reference/ai/index
   api_reference/storage/index
   developer_guide/index
   deployment/index
   _meta/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
    with open("docs/index.rst", "w") as f:
        f.write(content)


def main():
    """Main execution function."""
    # Create directory structure
    create_directory_structure()

    # Create main index
    create_main_index()

    # Move existing documentation if it exists
    if os.path.exists("DOCUMENTATION.md"):
        shutil.move("DOCUMENTATION.md", "docs/_meta/full_documentation.md")

    print("Documentation structure reorganized successfully!")


if __name__ == "__main__":
    main()
