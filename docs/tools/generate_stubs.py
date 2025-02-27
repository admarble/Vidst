#!/usr/bin/env python3
"""Script to generate module documentation stubs."""

import importlib
import inspect
import os
import sys
from pathlib import Path


def create_module_stub(module_name, output_dir):
    """Create a documentation stub for a module."""
    try:
        # Import the module
        module = importlib.import_module(module_name)

        # Create stub content
        content = [
            f"{module_name}",
            "=" * len(module_name),
            "",
            ".. currentmodule:: " + module_name,
            "",
            ".. automodule:: " + module_name,
            "   :members:",
            "   :undoc-members:",
            "   :show-inheritance:",
            "",
            "Module Contents",
            "--------------",
            "",
        ]

        # Add classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module_name:
                content.extend(
                    [
                        f".. autoclass:: {name}",
                        "   :members:",
                        "   :undoc-members:",
                        "   :show-inheritance:",
                        "",
                    ]
                )

        # Add functions
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ == module_name:
                content.extend(
                    [
                        f".. autofunction:: {name}",
                        "",
                    ]
                )

        # Write to file
        stub_path = output_dir / f"{module_name.replace('.', '_')}.rst"
        stub_path.parent.mkdir(parents=True, exist_ok=True)
        stub_path.write_text("\n".join(content))
        print(f"Created stub for {module_name} at {stub_path}")

    except ImportError as e:
        print(f"Could not import {module_name}: {e}")
    except Exception as e:
        print(f"Error processing {module_name}: {e}")


def main():
    """Main function to generate stubs for all modules."""
    # Add src to Python path
    src_dir = Path(__file__).parent.parent.parent / "src"
    sys.path.insert(0, str(src_dir))

    # Output directory for stubs
    output_dir = Path(__file__).parent.parent / "_autosummary"
    output_dir.mkdir(exist_ok=True)

    # List of modules to document
    modules = [
        "src.core.input",
        "src.core.output",
        "src.core.processing",
        "src.core.exceptions",
        "src.core.config",
        "src.ai.models",
        "src.ai.pipeline",
        "src.storage.cache",
        "src.storage.vector",
        "src.storage.metadata",
    ]

    for module in modules:
        create_module_stub(module, output_dir)


if __name__ == "__main__":
    main()
