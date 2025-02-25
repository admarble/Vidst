#!/usr/bin/env python3
"""Cross-reference checker and fixer for documentation."""

import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class CrossRefFixer:
    """Checks and fixes cross-references in documentation."""

    def __init__(self, docs_dir: str):
        """Initialize with docs directory path."""
        self.docs_dir = Path(docs_dir)
        self.refs: Dict[str, List[str]] = defaultdict(list)
        self.broken_refs: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        self.duplicate_refs: Dict[str, List[str]] = defaultdict(list)

    def scan_references(self):
        """Scan all documentation files for references."""
        # Patterns for different types of references
        patterns = {
            "label": re.compile(r"^\.\. _([^:]+):"),  # Reference labels
            "ref": re.compile(r":(?:ref|doc):`([^`]+)`"),  # Reference usage
            "class": re.compile(r":(?:class|exc|obj):`([^`]+)`"),  # Class references
            "module": re.compile(r":mod:`([^`]+)`"),  # Module references
            "function": re.compile(r":func:`([^`]+)`"),  # Function references
        }

        # Scan all rst and md files
        for ext in [".rst", ".md"]:
            for file in self.docs_dir.rglob(f"*{ext}"):
                if "_build" not in str(file):
                    rel_path = str(file.relative_to(self.docs_dir))
                    content = file.read_text()

                    # Find all reference definitions
                    for match in patterns["label"].finditer(content):
                        ref_name = match.group(1)
                        self.refs[ref_name].append(rel_path)

                    # Find all reference usages
                    for pattern_type, pattern in patterns.items():
                        if pattern_type != "label":
                            for match in pattern.finditer(content):
                                ref_name = match.group(1)
                                if not self._ref_exists(ref_name):
                                    self.broken_refs[rel_path].append(
                                        (ref_name, pattern_type)
                                    )

    def _ref_exists(self, ref_name: str) -> bool:
        """Check if a reference exists."""
        # Check in our collected references
        if ref_name in self.refs:
            return True

        # Check for built-in Python types
        if ref_name.startswith(
            ("str", "int", "float", "bool", "list", "dict", "tuple")
        ):
            return True

        # Check for common external references
        common_externals = {
            "numpy",
            "pandas",
            "torch",
            "tensorflow",
            "sklearn",
            "pathlib",
            "datetime",
            "typing",
            "collections",
        }
        if any(ref_name.startswith(ext) for ext in common_externals):
            return True

        return False

    def find_duplicate_refs(self):
        """Find duplicate reference definitions."""
        for ref_name, files in self.refs.items():
            if len(files) > 1:
                self.duplicate_refs[ref_name] = files

    def suggest_fixes(self) -> List[Tuple[str, str, str]]:
        """Generate suggestions for fixing broken references."""
        suggestions = []

        for file, refs in self.broken_refs.items():
            for ref_name, ref_type in refs:
                # Try to find similar existing references
                similar_refs = self._find_similar_refs(ref_name)

                if similar_refs:
                    # Suggest using an existing similar reference
                    suggestions.append(
                        (
                            file,
                            f"Broken {ref_type} reference: {ref_name}",
                            f"Consider using one of: {', '.join(similar_refs)}",
                        )
                    )
                else:
                    # Suggest creating a new reference
                    suggestions.append(
                        (
                            file,
                            f"Missing {ref_type} reference: {ref_name}",
                            f"Add '.. _{ref_name}:' to appropriate documentation file",
                        )
                    )

        return suggestions

    def _find_similar_refs(self, ref_name: str, threshold: float = 0.7) -> List[str]:
        """Find similar existing references using string similarity."""
        similar_refs = []

        for existing_ref in self.refs.keys():
            # Simple similarity check - can be enhanced with better algorithms
            similarity = self._string_similarity(ref_name, existing_ref)
            if similarity > threshold:
                similar_refs.append(existing_ref)

        return similar_refs

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity ratio."""
        # Simple Levenshtein distance-based similarity
        # Can be enhanced with more sophisticated algorithms
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        distances = range(len(s2) + 1)
        for i1, c1 in enumerate(s1):
            distances_ = [i1 + 1]
            for i2, c2 in enumerate(s2):
                if c1 == c2:
                    distances_.append(distances[i2])
                else:
                    distances_.append(
                        1 + min((distances[i2], distances[i2 + 1], distances_[-1]))
                    )
            distances = distances_

        max_len = max(len(s1), len(s2))
        return 1 - (distances[-1] / max_len)

    def print_report(self):
        """Print a detailed report of reference issues."""
        print("\nCross-Reference Check Report")
        print("===========================\n")

        if not any([self.broken_refs, self.duplicate_refs]):
            print("✅ No cross-reference issues found!")
            return

        # Report broken references
        if self.broken_refs:
            print("\nBroken References:")
            print("-----------------")
            for file, refs in self.broken_refs.items():
                print(f"\nIn {file}:")
                for ref_name, ref_type in refs:
                    print(f"  ❌ {ref_type}: {ref_name}")

        # Report duplicate references
        if self.duplicate_refs:
            print("\nDuplicate References:")
            print("-------------------")
            for ref_name, files in self.duplicate_refs.items():
                print(f"\nReference '{ref_name}' defined in:")
                for file in files:
                    print(f"  ⚠️  {file}")

        # Print suggestions
        print("\nSuggested Fixes:")
        print("---------------")
        for file, issue, suggestion in self.suggest_fixes():
            print(f"\nIn {file}:")
            print(f"  Problem: {issue}")
            print(f"  Suggestion: {suggestion}")


def main():
    """Main entry point."""
    docs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixer = CrossRefFixer(docs_dir)
    fixer.scan_references()
    fixer.find_duplicate_refs()
    fixer.print_report()


if __name__ == "__main__":
    main()
