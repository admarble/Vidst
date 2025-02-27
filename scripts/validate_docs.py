#!/usr/bin/env python3
"""Documentation validation script to check for common issues."""

import os
import re
import sys
from pathlib import Path


class DocValidator:
    """Validates documentation files and structure."""

    def __init__(self, docs_dir: str):
        """Initialize the validator with docs directory path."""
        self.docs_dir = Path(docs_dir)
        self.issues: dict[str, list[str]] = {
            "missing_refs": [],
            "duplicate_refs": [],
            "orphaned_files": [],
            "bad_code_blocks": [],
            "section_hierarchy": [],
            "sphinx_refs": [],
        }
        self.all_files: set[str] = set()
        self.referenced_files: set[str] = set()
        # Standard Sphinx pages that should have references
        self.standard_sphinx_pages = {"genindex", "modindex", "search"}
        # Map of section markers to their hierarchy level
        self.section_levels = {
            "=": 0,  # Top level
            "-": 1,  # Second level
            "~": 2,  # Third level
            "^": 3,  # Fourth level
            "*": 4,  # Fifth level
        }

    def validate_all(self) -> dict[str, list[str]]:
        """Run all validation checks."""
        self._collect_files()
        self._check_toctree_references()
        self._check_cross_references()
        self._check_code_blocks()
        self._check_section_hierarchy()
        self._check_references()
        self._check_sphinx_references()
        return self.issues

    def _collect_files(self):
        """Collect all documentation files."""
        for ext in [".rst", ".md"]:
            for file in self.docs_dir.rglob(f"*{ext}"):
                if "_build" not in str(file):
                    self.all_files.add(str(file.relative_to(self.docs_dir)))

    def _check_toctree_references(self):
        """Check toctree directives for missing references."""
        toctree_pattern = re.compile(r".. toctree::(.*?)(?=\n\n|\Z)", re.DOTALL)

        for file in self.all_files:
            content = (self.docs_dir / file).read_text()

            # Find all toctree directives
            for toctree in toctree_pattern.finditer(content):
                toctree_content = toctree.group(1)
                referenced_files = re.findall(
                    r"^\s*(\S+)\s*$", toctree_content, re.MULTILINE
                )

                for ref in referenced_files:
                    if not ref.startswith(":"):  # Skip toctree options
                        self.referenced_files.add(ref)
                        # Check if file exists (with .rst or .md extension)
                        if not any(
                            (self.docs_dir / f"{ref}{ext}").exists()
                            for ext in [".rst", ".md"]
                        ):
                            self.issues["missing_refs"].append(
                                f"Missing file referenced in {file}: {ref}"
                            )

    def _check_cross_references(self):
        """Check for broken cross-references and improve error reporting."""
        ref_pattern = re.compile(r":(?:ref|doc):`([^`]+)`")
        label_pattern = re.compile(r"\.\. _([^:]+):")

        # First pass: collect all reference labels
        reference_labels = set()
        for file in self.all_files:
            try:
                content = (self.docs_dir / file).read_text()
                for match in label_pattern.finditer(content):
                    label = match.group(1).strip()
                    if label in reference_labels:
                        self.issues["duplicate_refs"].append(
                            f"Duplicate reference label '{label}' found in {file}"
                        )
                    reference_labels.add(label)
            except Exception as e:
                self.issues["missing_refs"].append(
                    f"Error reading file {file} for labels: {e!s}"
                )

        # Second pass: check all references
        for file in self.all_files:
            try:
                content = (self.docs_dir / file).read_text()
                line_number = 1
                for line in content.split("\n"):
                    for match in ref_pattern.finditer(line):
                        ref_name = match.group(1).strip()
                        if (
                            ref_name not in reference_labels
                            and ref_name not in self.standard_sphinx_pages
                        ):
                            self.issues["missing_refs"].append(
                                f"Broken cross-reference '{ref_name}' in {file}:{line_number}"
                            )
                    line_number += 1
            except Exception as e:
                self.issues["missing_refs"].append(
                    f"Error checking cross-references in {file}: {e!s}"
                )

    def _check_code_blocks(self):
        """Check for common code block issues."""
        code_block_pattern = re.compile(r"```.*?```|::\n\s+", re.DOTALL)

        for file in self.all_files:
            content = (self.docs_dir / file).read_text()

            # Check for potential code block issues
            for block in code_block_pattern.finditer(content):
                block_content = block.group(0)
                if "├" in block_content or "└" in block_content:
                    self.issues["bad_code_blocks"].append(
                        f"Directory tree in code block should use .. code-block:: text in {file}"
                    )

    def _check_section_hierarchy(self):
        """Check section hierarchy and structure in RST files."""
        for file in self.all_files:
            if not file.endswith(".rst"):
                continue

            try:
                content = (self.docs_dir / file).read_text()
                lines = content.split("\n")
                line_number = 0
                section_stack = []  # Track section levels for hierarchy validation

                while line_number < len(lines) - 1:  # Ensure we can look ahead one line
                    current_line = lines[line_number].rstrip()
                    if not current_line:  # Skip empty lines
                        line_number += 1
                        continue

                    # Look ahead for potential section underline
                    next_line = lines[line_number + 1].rstrip()
                    if not next_line:  # No underline found
                        line_number += 1
                        continue

                    # Check if next line is a valid section marker
                    if self._is_section_marker(current_line, next_line):
                        marker = next_line[0]
                        current_level = self.section_levels.get(marker)

                        if current_level is not None:
                            # Check hierarchy
                            if section_stack and current_level <= section_stack[-1]:
                                self.issues["section_hierarchy"].append(
                                    f"Section hierarchy error in {file} at line {line_number + 2}: "
                                    f"'{current_line}' (level {current_level}) should be deeper "
                                    f"than previous section (level {section_stack[-1]})"
                                )

                            # Update section stack
                            while section_stack and section_stack[-1] >= current_level:
                                section_stack.pop()
                            section_stack.append(current_level)

                            line_number += 2  # Skip the underline
                            continue

                    line_number += 1

            except Exception as e:
                self.issues["section_hierarchy"].append(
                    f"Error checking section hierarchy in {file}: {e!s}"
                )

    def _is_section_marker(self, title_line: str, marker_line: str) -> bool:
        """Check if a line pair represents a valid section marker."""
        if not title_line or not marker_line:
            return False

        # Check if marker line consists of a single repeated character
        if not all(c == marker_line[0] for c in marker_line):
            return False

        # Check if marker is a valid section marker
        if marker_line[0] not in self.section_levels:
            return False

        # Check if marker line is at least as long as the title
        return len(marker_line) >= len(title_line)

    def _check_sphinx_references(self):
        """Check for standard Sphinx page references."""
        index_file = self.docs_dir / "index.rst"
        if not index_file.exists():
            self.issues["sphinx_refs"].append("Missing index.rst file")
            return

        content = index_file.read_text()
        for page in self.standard_sphinx_pages:
            if f":ref:`{page}`" not in content and f".. _{page}:" not in content:
                self.issues["sphinx_refs"].append(
                    f"Missing reference for standard Sphinx page: {page}"
                )

    def _reference_exists(self, ref_name: str) -> bool:
        """Check if a reference exists in any documentation file."""
        if ref_name in self.standard_sphinx_pages:
            return True

        label_pattern = re.compile(rf"\.\. _{re.escape(ref_name)}:")
        for file in self.all_files:
            try:
                content = (self.docs_dir / file).read_text()
                if label_pattern.search(content):
                    return True
            except Exception:
                continue
        return False

    def _check_references(self):
        """Check for missing references."""
        # Add standard Sphinx pages to referenced files
        self.referenced_files.update(self.standard_sphinx_pages)

        for ref in self.referenced_files:
            if not self._reference_exists(ref):
                self.issues["missing_refs"].append(
                    f"Missing reference in documentation: {ref}"
                )

    def print_report(self):
        """Print validation report with improved formatting."""
        print("\nDocumentation Validation Report")
        print("==============================\n")

        total_issues = sum(len(issues) for issues in self.issues.values())

        if total_issues == 0:
            print("✅ No issues found!")
            return

        # Sort issues by category for better readability
        for category in sorted(self.issues.keys()):
            issues = self.issues[category]
            if issues:
                print(f"\n{category.replace('_', ' ').title()}:")
                # Sort issues for consistent output
                for issue in sorted(issues):
                    print(f"  ❌ {issue}")

        print(f"\nTotal issues found: {total_issues}")
        if total_issues > 0:
            print(
                "\nPlease fix the above issues to ensure proper documentation structure."
            )


def main():
    """Main entry point with improved error handling."""
    try:
        docs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        validator = DocValidator(docs_dir)
        validator.validate_all()
        validator.print_report()

        # Exit with error code if issues found
        sys.exit(1 if any(validator.issues.values()) else 0)
    except Exception as e:
        print(f"Error running documentation validation: {e!s}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
