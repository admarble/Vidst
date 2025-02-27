#!/usr/bin/env python3
"""Script to fix common documentation issues."""

import os
import re
import sys
from pathlib import Path


class DocFixer:
    """Fixes common documentation issues."""

    def __init__(self, docs_dir: str):
        """Initialize with docs directory path."""
        self.docs_dir = Path(docs_dir)
        self.seen_labels: set[str] = set()
        self.section_levels: dict[str, int] = {
            "=": 1,  # Part/Book level
            "-": 2,  # Chapter level
            "~": 3,  # Section level
            "^": 4,  # Subsection level
            "*": 5,  # Sub-subsection level
            "+": 6,  # Paragraph level
        }
        self.section_markers = list(self.section_levels.keys())
        self.label_counter: dict[str, int] = {}
        self.ref_mapping: dict[str, str] = self._build_ref_mapping()

    def _build_ref_mapping(self) -> dict[str, str]:
        """Build a mapping of common reference targets."""
        # Standard Sphinx references
        sphinx_refs = {
            "/genindex": ":ref:`genindex`",
            "/modindex": ":ref:`modindex`",
            "/search": ":ref:`search`",
        }

        # API references
        api_refs = {
            f"/api/{path}": f":doc:`/api/{path}`"
            for path in [
                "core/config",
                "core/exceptions",
                "core/input",
                "storage/cache",
                "storage/vector",
                "storage/metadata",
                "ai/models",
                "ai/pipeline",
            ]
        }

        # Guide references
        guide_refs = {
            f"/guides/{path}": f":doc:`/guides/{path}`"
            for path in [
                "configuration",
                "getting_started",
                "development",
                "testing",
                "deployment",
                "troubleshooting",
            ]
        }

        return {**sphinx_refs, **api_refs, **guide_refs}

    def make_label_unique(self, file_path: Path, label: str) -> str:
        """Make a reference label unique by prefixing with normalized file path and adding a counter if needed."""
        # Convert path to string and normalize
        path_str = str(file_path.relative_to(self.docs_dir)).lower()
        # Replace path separators and file extensions with underscores
        path_str = path_str.replace("/", "_").replace(".", "_").replace("-", "_")
        # Clean the label
        label = label.strip().lower().replace(" ", "_").replace("-", "_")
        base_label = f"{path_str}__{label}"

        # Add counter if label is already seen
        if base_label in self.seen_labels:
            if base_label not in self.label_counter:
                self.label_counter[base_label] = 1
            self.label_counter[base_label] += 1
            base_label = f"{base_label}_{self.label_counter[base_label]}"

        self.seen_labels.add(base_label)
        return base_label

    def clean_rst_labels(self, content: str) -> str:
        """Remove auto-generated RST labels."""
        # Remove auto-generated RST labels
        content = re.sub(r"\.\. _[^:]+:", "", content)
        # Remove empty lines after label removal
        content = re.sub(r"\n\n+", "\n\n", content)
        return content

    def convert_mixed_format(self, content: str, file_path: Path) -> str:
        """Convert mixed Markdown/RST to proper format based on file extension."""
        is_markdown = file_path.suffix.lower() == ".md"

        if is_markdown:
            # Convert RST directives to Markdown
            content = re.sub(r"\.\. code-block:: (\w+)\n\n", r"```\1\n", content)
            content = re.sub(
                r"\.\. toctree::\n\s+:maxdepth: \d+\n\s+:caption:[^\n]*\n",
                "## Table of Contents\n\n",
                content,
            )
            content = re.sub(r"\.\. _[^:]+:", "", content)  # Remove RST labels
        else:
            # Convert Markdown to RST
            content = re.sub(r"```(\w+)\n", r".. code-block:: \1\n\n", content)
            content = re.sub(
                r"#{1,6} (.*)",
                lambda m: f"{m.group(1)}\n{'=' if len(m.group(0).split()[0]) == 1 else '-' * len(m.group(1))}",
                content,
            )

        return content

    def fix_section_hierarchy(self, content: str) -> str:
        """Fix section hierarchy to ensure proper nesting."""
        lines = content.split("\n")
        section_stack = []  # Stack to track section levels
        fixed_lines = []
        current_title = None

        for i, line in enumerate(lines):
            line = line.rstrip()

            # Skip empty lines
            if not line:
                fixed_lines.append(line)
                continue

            # Check if this is a potential section title
            if i > 0 and i < len(lines) - 1:
                next_line = lines[i + 1].rstrip()

                # Check if next line is a section marker
                if next_line and all(c == next_line[0] for c in next_line):
                    current_title = line
                    marker = next_line[0]

                    if marker in self.section_levels:
                        current_level = self.section_levels[marker]

                        # Fix hierarchy
                        while section_stack and section_stack[-1] >= current_level:
                            section_stack.pop()

                        # Determine correct level
                        if section_stack:
                            expected_level = section_stack[-1] + 1
                            if current_level != expected_level:
                                # Find the correct marker
                                for m, level in self.section_levels.items():
                                    if level == expected_level:
                                        next_line = m * len(current_title)
                                        current_level = expected_level
                                        break

                        section_stack.append(current_level)

                    fixed_lines.append(current_title)
                    fixed_lines.append(next_line)
                    continue

            if line != current_title:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_cross_references(self, content: str, file_path: Path) -> str:
        """Fix cross-references in the content."""
        # Fix absolute references using the mapping
        for old_ref, new_ref in self.ref_mapping.items():
            content = content.replace(f"`{old_ref}`_", new_ref)

        # Fix relative references with improved pattern
        content = re.sub(
            r"`(?:\.\.\/)+([^`]+)`_", lambda m: f":doc:`/{m.group(1)}`", content
        )

        # Fix local references with improved uniqueness
        content = re.sub(
            r"`([^`/]+)`_",
            lambda m: f":ref:`{self.make_label_unique(file_path, m.group(1))}`",
            content,
        )

        # Fix auto-doc references
        content = re.sub(
            r":func:`([^`]+)`", lambda m: f":py:func:`{m.group(1)}`", content
        )

        return content

    def fix_code_blocks(self, content: str) -> str:
        """Fix code block formatting."""

        def indent_content(text: str, spaces: int = 4) -> str:
            return "\n".join(
                " " * spaces + line if line.strip() else line
                for line in text.split("\n")
            )

        # Fix code blocks with missing language specifier
        content = re.sub(r"```\s*\n", "```text\n", content)

        # Fix code blocks with language and ensure proper indentation
        content = re.sub(
            r"```(\w+)\n(.*?)\n```",
            lambda m: f"```{m.group(1)}\n{indent_content(m.group(2).rstrip())}\n```",
            content,
            flags=re.DOTALL,
        )

        return content

    def fix_file(self, file_path: Path):
        """Fix documentation issues in a file."""
        try:
            print(f"Processing {file_path}")

            if not file_path.exists():
                print(f"Warning: File {file_path} does not exist")
                return

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Apply fixes
            content = self.clean_rst_labels(content)
            content = self.convert_mixed_format(content, file_path)
            content = self.fix_section_hierarchy(content)
            content = self.fix_code_blocks(content)
            content = self.fix_cross_references(content, file_path)

            # Write back fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Successfully fixed {file_path}")

            # If we have both .md and .rst versions, ensure they're in sync
            alternate_ext = ".rst" if file_path.suffix.lower() == ".md" else ".md"
            alternate_path = file_path.with_suffix(alternate_ext)
            if alternate_path.exists():
                print(
                    f"Warning: Found alternate format file {alternate_path}. Please choose one format."
                )

        except Exception as e:
            print(f"Warning: Error processing {file_path}: {e!s}")

    def process_docs(self):
        """Process all documentation files."""
        # Create index.rst if it doesn't exist
        self.create_index_file()

        # Process all rst and md files
        for ext in ["*.rst", "*.md"]:
            for file_path in self.docs_dir.rglob(ext):
                if "venv" not in str(file_path) and "_build" not in str(file_path):
                    self.fix_file(file_path)

    def create_index_file(self) -> None:
        """Create the main index.rst file if it doesn't exist."""
        index_path = self.docs_dir / "index.rst"
        if not index_path.exists():
            content = """
Video Understanding AI Documentation
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guides/index
   api/index
   development/index
   project_updates/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(content.lstrip())


def main():
    """Main entry point."""
    try:
        docs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs"
        )
        if not os.path.exists(docs_dir):
            print(f"Error: Documentation directory not found: {docs_dir}")
            sys.exit(1)

        print(f"Processing documentation in: {docs_dir}")
        fixer = DocFixer(docs_dir)
        fixer.process_docs()
    except Exception as e:
        print(f"Error: {e!s}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
