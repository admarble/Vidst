#!/usr/bin/env python3
"""Documentation structure generator and maintainer."""

import os
import re
from pathlib import Path
from typing import Dict, List, Set


class DocsStructureGenerator:
    """Generates and maintains documentation structure."""

    def __init__(self, docs_dir: str):
        """Initialize with docs directory path."""
        self.docs_dir = Path(docs_dir)
        self.structure: Dict[str, List[str]] = {
            "Getting Started": [],
            "API Reference": [],
            "Development": [],
            "Project Updates": [],
        }

    def scan_directory(self):
        """Scan directory and categorize files."""
        # Scan for API documentation
        api_dir = self.docs_dir / "api"
        if api_dir.exists():
            for file in api_dir.rglob("*.rst"):
                if file.stem != "index":
                    self.structure["API Reference"].append(
                        str(file.relative_to(self.docs_dir)).replace(".rst", "")
                    )

        # Scan for guides
        guides_dir = self.docs_dir / "guides"
        if guides_dir.exists():
            for file in guides_dir.rglob("*.*"):
                if file.suffix in [".rst", ".md"] and file.stem != "index":
                    self.structure["Getting Started"].append(
                        str(file.relative_to(self.docs_dir)).replace(file.suffix, "")
                    )

        # Scan for development docs
        dev_dir = self.docs_dir / "development"
        if dev_dir.exists():
            for file in dev_dir.rglob("*.*"):
                if file.suffix in [".rst", ".md"] and file.stem != "index":
                    self.structure["Development"].append(
                        str(file.relative_to(self.docs_dir)).replace(file.suffix, "")
                    )

        # Add root level documentation
        for file in self.docs_dir.glob("*.*"):
            if file.suffix in [".rst", ".md"] and file.stem not in ["index", "conf"]:
                if any(
                    keyword in file.stem for keyword in ["issue", "update", "changelog"]
                ):
                    self.structure["Project Updates"].append(file.stem)
                elif any(
                    keyword in file.stem for keyword in ["dev", "test", "ci", "cd"]
                ):
                    self.structure["Development"].append(file.stem)
                else:
                    self.structure["Getting Started"].append(file.stem)

    def generate_index_rst(self) -> str:
        """Generate content for index.rst."""
        content = [
            "Video Understanding AI Documentation",
            "================================",
            "",
            "Welcome to the Video Understanding AI documentation. This documentation covers the installation, usage, and development of the Video Understanding AI system.",
            "",
        ]

        # Add toctree for each section
        for section, files in self.structure.items():
            if files:
                content.extend(
                    [
                        ".. toctree::",
                        "   :maxdepth: 2",
                        f"   :caption: {section}",
                        "",
                    ]
                )

                # Sort files to ensure consistent order
                for file in sorted(files):
                    content.append(f"   {file}")
                content.append("")

        # Add indices section
        content.extend(
            [
                "Indices and Tables",
                "==================",
                "",
                "* :ref:`genindex`",
                "* :ref:`modindex`",
                "* :ref:`search`",
            ]
        )

        return "\n".join(content)

    def generate_section_index(self, section: str, files: List[str]) -> str:
        """Generate content for section index files."""
        title = section.replace(" ", " ")
        content = [
            title,
            "=" * len(title),
            "",
            f"This section contains {section.lower()} documentation.",
            "",
            ".. toctree::",
            "   :maxdepth: 2",
            "",
        ]

        for file in sorted(files):
            if "/" in file:
                content.append(f"   {file.split('/')[-1]}")
            else:
                content.append(f"   {file}")

        return "\n".join(content)

    def update_structure(self):
        """Update documentation structure."""
        # Scan directory first
        self.scan_directory()

        # Update main index.rst
        index_content = self.generate_index_rst()
        index_path = self.docs_dir / "index.rst"
        index_path.write_text(index_content)

        # Update section index files
        for section, files in self.structure.items():
            if files:
                section_dir = section.lower().replace(" ", "_")
                section_path = self.docs_dir / section_dir
                section_path.mkdir(exist_ok=True)

                index_content = self.generate_section_index(section, files)
                (section_path / "index.rst").write_text(index_content)

    def create_missing_files(self):
        """Create missing documentation files with templates."""
        templates = {
            "api": """{title}
{underline}

.. module:: {module}

Module Description
----------------

This module provides...

Classes
-------

.. autoclass:: {class_name}
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: {function_name}
""",
            "guide": """{title}
{underline}

Overview
--------

This guide covers...

Prerequisites
------------

Before you begin, ensure you have:

* Requirement 1
* Requirement 2

Steps
-----

1. First step
2. Second step
3. Third step

Examples
--------

Here's a basic example:

.. code-block:: python

    # Example code here

Additional Resources
------------------

* Link 1
* Link 2
""",
        }

        for section, files in self.structure.items():
            for file in files:
                file_path = self.docs_dir / f"{file}.rst"
                if not file_path.exists():
                    template = (
                        templates["api"] if "api/" in file else templates["guide"]
                    )
                    title = file.split("/")[-1].replace("_", " ").title()
                    content = template.format(
                        title=title,
                        underline="=" * len(title),
                        module="module.name",
                        class_name="ClassName",
                        function_name="function_name",
                    )
                    file_path.write_text(content)


def main():
    """Main entry point."""
    docs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    generator = DocsStructureGenerator(docs_dir)
    generator.update_structure()
    generator.create_missing_files()
    print("✅ Documentation structure updated successfully!")


if __name__ == "__main__":
    main()
