#!/usr/bin/env python3
"""Documentation validation script to check for common issues."""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class DocValidator:
    """Validates documentation files and structure."""

    def __init__(self, docs_dir: str):
        """Initialize the validator with docs directory path."""
        self.docs_dir = Path(docs_dir)
        self.issues: Dict[str, List[str]] = {
            "missing_refs": [],
            "duplicate_refs": [],
            "orphaned_files": [],
            "bad_code_blocks": [],
            "missing_sections": [],
        }
        self.all_files: Set[str] = set()
        self.referenced_files: Set[str] = set()

    def validate_all(self) -> Dict[str, List[str]]:
        """Run all validation checks."""
        self._collect_files()
        self._check_toctree_references()
        self._check_cross_references()
        self._check_code_blocks()
        self._check_section_hierarchy()
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
        """Check for broken cross-references."""
        ref_pattern = re.compile(r":(?:ref|doc):`([^`]+)`")

        for file in self.all_files:
            content = (self.docs_dir / file).read_text()

            # Find all cross-references
            for ref in ref_pattern.finditer(content):
                ref_name = ref.group(1)
                if not self._reference_exists(ref_name):
                    self.issues["missing_refs"].append(
                        f"Broken cross-reference in {file}: {ref_name}"
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
        """Check section hierarchy in RST files."""
        for file in self.all_files:
            if file.endswith(".rst"):
                content = (self.docs_dir / file).read_text()
                lines = content.split("\n")

                # Check for proper section markers
                prev_level = None
                for i, line in enumerate(lines):
                    if set(line).issubset(set("=-~^")):
                        if i > 0 and len(line) >= len(lines[i - 1]):
                            level = "=-~^".index(line[0]) if line[0] in "=-~^" else None
                            if prev_level is not None and level is not None:
                                if level > prev_level + 1:
                                    self.issues["missing_sections"].append(
                                        f"Improper section hierarchy in {file} at line {i+1}"
                                    )
                            prev_level = level

    def _reference_exists(self, ref_name: str) -> bool:
        """Check if a reference exists in any documentation file."""
        # This is a simplified check - you might want to enhance it
        for file in self.all_files:
            content = (self.docs_dir / file).read_text()
            if f".. _{ref_name}:" in content:
                return True
        return False

    def print_report(self):
        """Print validation report."""
        print("\nDocumentation Validation Report")
        print("==============================\n")

        total_issues = sum(len(issues) for issues in self.issues.values())

        if total_issues == 0:
            print("✅ No issues found!")
            return

        for category, issues in self.issues.items():
            if issues:
                print(f"\n{category.replace('_', ' ').title()}:")
                for issue in issues:
                    print(f"  ❌ {issue}")

        print(f"\nTotal issues found: {total_issues}")


def main():
    """Main entry point."""
    docs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    validator = DocValidator(docs_dir)
    validator.validate_all()
    validator.print_report()

    # Exit with error code if issues found
    sys.exit(1 if any(validator.issues.values()) else 0)


if __name__ == "__main__":
    main()
