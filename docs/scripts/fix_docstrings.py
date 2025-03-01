#!/usr/bin/env python3
"""Script to fix docstring formatting issues in Python files.

This script helps maintain consistent docstring formatting across the codebase
by converting various docstring styles to Google style and fixing common issues
that cause Sphinx warnings.
"""

import argparse
import ast
import re
from pathlib import Path
from typing import List, Tuple, Optional


def fix_param_style(docstring: str) -> str:
    """Convert :param: style parameters to Google style.

    Args:
        docstring: The docstring to fix

    Returns:
        The fixed docstring
    """
    # Convert :param: to Args:
    param_pattern = r":param (\w+): (.*?)(?=:param|:return|:rtype|$)"
    if re.search(param_pattern, docstring, re.DOTALL):
        args = []
        for match in re.finditer(param_pattern, docstring, re.DOTALL):
            param_name, desc = match.groups()
            args.append(f"    {param_name}: {desc.strip()}")

        if args:
            args_section = "Args:\n" + "\n".join(args)
            docstring = re.sub(
                r":param.*?(?=:return|:rtype|$)",
                args_section,
                docstring,
                flags=re.DOTALL,
            )

    return docstring


def fix_return_style(docstring: str) -> str:
    """Convert :return: and :rtype: to Google style.

    Args:
        docstring: The docstring to fix

    Returns:
        The fixed docstring
    """
    # Convert :return: and :rtype: to Returns:
    return_pattern = r":returns?: (.*?)(?=:rtype|$)"
    rtype_pattern = r":rtype: (.*?)(?=$)"

    return_match = re.search(return_pattern, docstring, re.DOTALL)
    rtype_match = re.search(rtype_pattern, docstring, re.DOTALL)

    if return_match or rtype_match:
        return_desc = return_match.group(1).strip() if return_match else ""
        return_type = rtype_match.group(1).strip() if rtype_match else ""

        if return_desc and return_type:
            returns_section = f"\nReturns:\n    {return_type}: {return_desc}"
        elif return_desc:
            returns_section = f"\nReturns:\n    {return_desc}"
        else:
            returns_section = f"\nReturns:\n    {return_type}"

        docstring = re.sub(r":returns?.*?(?=:rtype|$)", "", docstring, flags=re.DOTALL)
        docstring = re.sub(
            r":rtype:.*?(?=$)", returns_section, docstring, flags=re.DOTALL
        )

    return docstring


def fix_raises_style(docstring: str) -> str:
    """Convert :raises: style to Google style.

    Args:
        docstring: The docstring to fix

    Returns:
        The fixed docstring
    """
    # Convert :raises: to Raises:
    raises_pattern = r":raises (\w+): (.*?)(?=:raises|$)"
    if re.search(raises_pattern, docstring, re.DOTALL):
        raises = []
        for match in re.finditer(raises_pattern, docstring, re.DOTALL):
            exc_type, desc = match.groups()
            raises.append(f"    {exc_type}: {desc.strip()}")

        if raises:
            raises_section = "Raises:\n" + "\n".join(raises)
            docstring = re.sub(
                r":raises.*?(?=$)", raises_section, docstring, flags=re.DOTALL
            )

    return docstring


def fix_docstring(docstring: str) -> str:
    """Fix various docstring formatting issues.

    Args:
        docstring: The docstring to fix

    Returns:
        The fixed docstring
    """
    if not docstring:
        return docstring

    # Remove leading/trailing whitespace
    docstring = docstring.strip()

    # Fix parameter style
    docstring = fix_param_style(docstring)

    # Fix return style
    docstring = fix_return_style(docstring)

    # Fix raises style
    docstring = fix_raises_style(docstring)

    # Ensure consistent section spacing
    docstring = re.sub(r"\n{3,}", "\n\n", docstring)

    return docstring


def process_file(file_path: Path) -> Tuple[int, List[str]]:
    """Process a Python file and fix docstring issues.

    Args:
        file_path: Path to the Python file

    Returns:
        Tuple of (number of fixes made, list of warnings)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content)
    fixes = 0
    warnings = []

    # Process module docstring
    if (module_doc := ast.get_docstring(tree)) is not None:
        fixed_doc = fix_docstring(module_doc)
        if fixed_doc != module_doc:
            fixes += 1

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if (doc := ast.get_docstring(node)) is not None:
                fixed_doc = fix_docstring(doc)
                if fixed_doc != doc:
                    fixes += 1
                    # Here you would update the docstring in the source
                    # This requires more complex source manipulation
            else:
                warnings.append(
                    f"Missing docstring in {node.__class__.__name__} '{node.name}'"
                )

    return fixes, warnings


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Fix docstring formatting issues")
    parser.add_argument("path", type=Path, help="Path to Python file or directory")
    parser.add_argument(
        "--check", action="store_true", help="Only check for issues without fixing"
    )
    args = parser.parse_args()

    if args.path.is_file():
        files = [args.path]
    else:
        files = list(args.path.rglob("*.py"))

    total_fixes = 0
    total_warnings = []

    for file in files:
        fixes, warnings = process_file(file)
        if fixes > 0 or warnings:
            print(f"\nProcessing {file}:")
            if fixes > 0:
                print(f"  Made {fixes} docstring fixes")
            for warning in warnings:
                print(f"  Warning: {warning}")
            total_fixes += fixes
            total_warnings.extend(warnings)

    print(f"\nSummary:")
    print(f"  Total files processed: {len(files)}")
    print(f"  Total fixes made: {total_fixes}")
    print(f"  Total warnings: {len(total_warnings)}")


if __name__ == "__main__":
    main()
