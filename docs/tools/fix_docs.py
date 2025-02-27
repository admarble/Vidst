#!/usr/bin/env python3
"""Main script to fix documentation issues."""

import subprocess
from pathlib import Path


def main():
    """Run all documentation fixes."""
    tools_dir = Path(__file__).parent

    print("1. Fixing title underlines...")
    subprocess.run(["python", str(tools_dir / "fix_underlines.py")])

    print("\n2. Generating module stubs...")
    subprocess.run(["python", str(tools_dir / "generate_stubs.py")])

    print("\n3. Fixing cross-references...")
    subprocess.run(["python", str(tools_dir / "fix_refs.py")])

    print("\n4. Building documentation...")
    docs_dir = tools_dir.parent
    subprocess.run(["make", "clean"], cwd=docs_dir)
    subprocess.run(["make", "html"], cwd=docs_dir)

    print("\nAll fixes completed. Please check _build/html for the results.")


if __name__ == "__main__":
    main()
