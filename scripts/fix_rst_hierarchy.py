#!/usr/bin/env python3
"""RST Hierarchy Fixer - A tool to fix RST formatting and hierarchy issues.

This script provides functionality to automatically fix common reStructuredText (RST)
formatting issues including section hierarchy, inline markup, list indentation,
and more. It can process individual files or entire directories.
"""

import argparse
import os
import re
import shutil
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum, auto


class ListType(Enum):
    """Enumeration of supported list types in RST."""

    BULLET = auto()
    NUMBERED = auto()
    DEFINITION = auto()


@dataclass
class ValidationError:
    """Represents a validation error found during RST processing."""

    line_number: int
    message: str
    severity: str


class RSTProcessingError(Exception):
    """Base exception for RST processing errors."""

    def __init__(self, message: str) -> None:
        """Initialize with error message."""
        super().__init__(message)


class RSTFormatError(RSTProcessingError):
    """Exception raised for RST formatting errors."""

    def __init__(self, message: str) -> None:
        """Initialize with error message."""
        super().__init__(message)


class RSTFileError(RSTProcessingError):
    """Exception raised for file handling errors."""

    def __init__(self, message: str) -> None:
        """Initialize with error message."""
        super().__init__(message)


@dataclass
class RSTState:
    """Class to hold RST processing state."""

    # Basic state flags
    in_directive: bool = False
    in_block_quote: bool = False
    in_definition_list: bool = False
    in_transition: bool = False
    in_literal_block: bool = False
    in_inline_markup: bool = False
    is_code_fragment: bool = False
    last_line_blank: bool = True

    # Section handling
    section_level: int = 0
    section_started: bool = False

    # Indentation
    directive_indent: int = 0
    current_indent: int = 0

    # Stacks and lists
    inline_markup_stack: list[str] = field(default_factory=list)
    list_stack: list[tuple[ListType, int]] = field(default_factory=list)
    validation_errors: list[ValidationError] = field(default_factory=list)

    def reset(self) -> None:
        """Reset all state values to their defaults."""
        self.in_directive = False
        self.in_block_quote = False
        self.in_definition_list = False
        self.in_transition = False
        self.in_literal_block = False
        self.in_inline_markup = False
        self.is_code_fragment = False
        self.last_line_blank = True
        self.section_level = 0
        self.section_started = False
        self.directive_indent = 0
        self.current_indent = 0
        self.inline_markup_stack.clear()
        self.list_stack.clear()
        self.validation_errors.clear()


class RSTRegexPatterns:
    """Class to hold compiled regex patterns for RST processing."""

    def __init__(self):
        """Initialize regex patterns."""
        directive_pattern = r"^\.\.[ ]+[A-Za-z][A-Za-z0-9-_]+::(?:[ ]+|$)"
        list_pattern = r"^(?:\*|-|\+|\d+\.|[A-Za-z]\.|[IVXLCDM]+\.)[ ]+"
        self.directive = re.compile(directive_pattern)
        self.role = re.compile(r":[A-Za-z][A-Za-z0-9-_]+:`[^`]+`")
        self.list_item = re.compile(list_pattern)
        self.def_list = re.compile(r"^[^ ].*\n[ ]+[^ ]")

    def match_directive(self, line: str) -> bool:
        """Check if line matches directive pattern."""
        return bool(self.directive.match(line))

    def match_list_item(self, line: str) -> bool:
        """Check if line matches list item pattern."""
        return bool(self.list_item.match(line.lstrip()))

    def match_def_list(self, line: str) -> bool:
        """Check if line matches definition list pattern."""
        return bool(self.def_list.match(line + "\n"))


class RSTLineProcessor:
    """Class to handle line-by-line RST processing."""

    def __init__(self, state: RSTState, patterns: RSTRegexPatterns):
        """Initialize with state and patterns."""
        self.state = state
        self.patterns = patterns

    def process_line(
        self, line: str, fixed_lines: list[str], next_line: str | None = None
    ) -> bool:
        """Process a single line of RST content.

        Args:
            line: The line to process
            fixed_lines: List of processed lines
            next_line: The next line in the document, if any

        Returns:
            True if the line was handled, False otherwise
        """
        # Handle empty lines
        if not line.strip():
            fixed_lines.append(line)
            self.state.last_line_blank = True
            return True

        # Handle directives
        if self.patterns.match_directive(line):
            if not self.state.last_line_blank:
                fixed_lines.append("")
            self.state.in_directive = True
            self.state.directive_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            if next_line and next_line.strip():
                fixed_lines.append("")
            self.state.last_line_blank = False
            return True

        # Handle lists
        if self.patterns.match_list_item(line):
            fixed_lines.append(line)
            self.state.last_line_blank = False
            return True

        # Handle block quotes
        if line.startswith("    "):
            if not self.state.in_block_quote:
                fixed_lines.append("")
            self.state.in_block_quote = True
            fixed_lines.append(line)
            return True

        # Handle definition lists
        if self.patterns.match_def_list(line):
            if not self.state.in_definition_list:
                fixed_lines.append("")
            self.state.in_definition_list = True
            fixed_lines.append(line)
            return True

        # Default handling
        fixed_lines.append(line)
        self.state.last_line_blank = False
        return False


class RSTHierarchyFixer:
    """A class to fix RST formatting and hierarchy issues.

    This class provides methods to fix common RST formatting issues including:
    - Section hierarchy and markers
    - Inline markup
    - List indentation and nesting
    - Block quotes and directives
    - Definition lists
    - Transitions

    Attributes:
        dry_run (bool): If True, validate without making changes
        state (RSTState): Current processing state
        section_level (int): Current section hierarchy level
        in_directive (bool): Whether currently processing a directive
        in_block_quote (bool): Whether currently in a block quote
        in_definition_list (bool): Whether currently in a definition list
        in_transition (bool): Whether currently processing a transition
        section_started (bool): Whether a section has been started
        directive_indent (int): Current directive indentation level
        last_line_blank (bool): Whether the last line was blank
        in_literal_block (bool): Whether currently in a literal block
        in_inline_markup (bool): Whether currently processing inline markup
        inline_markup_stack (List[str]): Stack of inline markup being processed
        list_stack (List[Tuple[ListType, int]]): Stack of active lists and their indentation
        current_indent (int): Current indentation level
        is_code_fragment (bool): Whether processing a code fragment
        validation_errors (List[ValidationError]): List of validation errors found
    """

    def __init__(self, dry_run: bool = False) -> None:
        """Initialize the RST Hierarchy Fixer.

        Args:
            dry_run: If True, validate without making changes
        """
        self.dry_run = dry_run
        self.state = RSTState()
        self.patterns = RSTRegexPatterns()
        self.line_processor = RSTLineProcessor(self.state, self.patterns)

        # Standard RST section markers in order of hierarchy
        self.section_markers = ["=", "-", "~", "^", '"', "'", ".", "_", "*", "+", "#"]

    def calculate_indent(self, line: str) -> int:
        """Calculate the indentation level of a line.

        Args:
            line: The line to calculate indentation for

        Returns:
            The number of spaces at the start of the line
        """
        return len(line) - len(line.lstrip())

    def is_section_marker(self, line: str) -> bool:
        """Check if a line is a section marker.

        Args:
            line: The line to check

        Returns:
            True if the line is a valid section marker, False otherwise
        """
        stripped = line.strip()
        return (
            bool(stripped)
            and len(stripped) > 1
            and len(set(stripped)) == 1
            and stripped[0] in self.section_markers
        )

    def is_transition(self, line: str) -> bool:
        """Check if a line is a transition marker.

        Args:
            line: The line to check

        Returns:
            True if the line is a valid transition marker, False otherwise
        """
        stripped = line.strip()
        return bool(
            stripped
            and len(stripped) >= 4
            and len(set(stripped)) == 1
            and stripped[0] in "=-~"
        )

    def is_directive(self, line: str) -> bool:
        """Check if a line starts a directive.

        Args:
            line: The line to check

        Returns:
            True if the line starts a directive, False otherwise
        """
        return bool(self.patterns.directive.match(line))

    def is_block_quote(self, line: str) -> bool:
        """Check if a line is part of a block quote.

        Args:
            line: The line to check

        Returns:
            True if the line is part of a block quote, False otherwise
        """
        return (
            line.startswith("    ")
            and not self.state.in_directive
            and not self.state.list_stack
        )

    def is_list_item(self, line: str) -> ListType | None:
        """Check if a line starts a list item and return its type.

        Args:
            line: The line to check

        Returns:
            The ListType if the line starts a list item, None otherwise
        """
        if self.patterns.list_item.match(line.lstrip()):
            if line.lstrip()[0] in "*-+":
                return ListType.BULLET
            return ListType.NUMBERED
        return None

    def is_definition_list(self, line: str) -> bool:
        """Check if a line starts a definition list.

        Args:
            line: The line to check

        Returns:
            True if the line starts a definition list, False otherwise
        """
        if not line:
            return False
        return bool(self.patterns.def_list.match(line + "\n"))

    def fix_inline_markup(self, line: str) -> str:
        """Fix inline markup issues with proper handling of nested structures.

        Args:
            line: The line containing inline markup to fix

        Returns:
            The line with fixed inline markup
        """
        # Handle escaped characters
        line = re.sub(r"\\([*`|_])", lambda m: f"__ESCAPED_{ord(m.group(1))}__", line)

        # Fix interpreted text/phrase references with roles
        line = re.sub(r":([^:]+):`([^`]+)(?!`)", r":\1:`\2`", line)
        line = re.sub(r"`([^`]*)`(?!_)", r"`\1`_", line)

        # Fix inline literals with proper spacing
        line = re.sub(r"(?<!`)``([^`]*)(?!``)", r"``\1``", line)

        # Fix strong emphasis with proper spacing
        line = re.sub(r"(?<!\*)\*\*([^*]+)(?!\*\*)", r"**\1**", line)

        # Fix emphasis with proper spacing
        line = re.sub(r"(?<!\*)\*([^*]+)(?!\*)", r"*\1*", line)

        # Restore escaped characters
        line = re.sub(r"__ESCAPED_(\d+)__", lambda m: chr(int(m.group(1))), line)

        return line

    def handle_list_indentation(self, line: str, list_type: ListType | None) -> str:
        """Handle list indentation and nesting.

        Args:
            line: The line to handle indentation for
            list_type: The type of list item, if any

        Returns:
            The line with corrected indentation
        """
        indent = self.calculate_indent(line)

        # Update list stack based on indentation
        while self.state.list_stack and self.state.list_stack[-1][1] >= indent:
            self.state.list_stack.pop()

        if list_type:
            self.state.list_stack.append((list_type, indent))

        # Ensure proper indentation for nested lists
        if self.state.list_stack:
            expected_indent = self.state.list_stack[-1][1]
            if indent < expected_indent:
                line = " " * expected_indent + line.lstrip()

        return line

    def _handle_empty_line(self, line: str, fixed_lines: list[str]) -> bool:
        """Handle empty line processing."""
        if not line.strip():
            fixed_lines.append(line)
            self.state.last_line_blank = True
            return True
        return False

    def _handle_transition(
        self, line: str, fixed_lines: list[str], content_started: bool
    ) -> tuple[bool, bool]:
        """Handle transition line processing."""
        if not self.is_transition(line):
            return content_started, False

        if not content_started:
            return content_started, True

        if not self.state.last_line_blank:
            fixed_lines.append("")
        fixed_lines.append(line)
        fixed_lines.append("")
        self.state.last_line_blank = True
        return True, True

    def _handle_directive(
        self, line: str, fixed_lines: list[str], next_line: str | None
    ) -> bool:
        """Handle directive line processing.

        Args:
            line: The line to process
            fixed_lines: List of processed lines
            next_line: The next line in the document, if any

        Returns:
            True if the line was handled as a directive, False otherwise
        """
        if not self.patterns.match_directive(line):
            return False

        if not self.state.last_line_blank:
            fixed_lines.append("")
        self.state.in_directive = True
        self.state.directive_indent = self.calculate_indent(line)
        fixed_lines.append(line)
        if next_line and next_line.strip():
            fixed_lines.append("")
        self.state.last_line_blank = False
        return True

    def _handle_list(self, line: str, fixed_lines: list[str]) -> bool:
        """Handle list item processing."""
        list_type = self.is_list_item(line)
        if not list_type:
            return False

        line = self.handle_list_indentation(line, list_type)
        if not self.state.list_stack and not self.state.last_line_blank:
            fixed_lines.append("")
        fixed_lines.append(line)
        return True

    def _handle_block_quote(self, line: str, fixed_lines: list[str]) -> None:
        """Handle block quote processing."""
        if self.is_block_quote(line):
            if not self.state.in_block_quote and not self.state.last_line_blank:
                fixed_lines.append("")
            self.state.in_block_quote = True
            fixed_lines.append(line)
        else:
            if self.state.in_block_quote:
                fixed_lines.append("")
            self.state.in_block_quote = False

    def _handle_definition_list(self, line: str, fixed_lines: list[str]) -> None:
        """Handle definition list processing."""
        if self.is_definition_list(line):
            if not self.state.in_definition_list and not self.state.last_line_blank:
                fixed_lines.append("")
            self.state.in_definition_list = True
            fixed_lines.append(line)
        else:
            if self.state.in_definition_list:
                fixed_lines.append("")
            self.state.in_definition_list = False

    def _handle_section_marker(self, line: str, fixed_lines: list[str]) -> bool:
        """Handle section marker processing."""
        if not self.is_section_marker(line):
            return False

        if not self.state.last_line_blank:
            fixed_lines.append("")

        title_line = fixed_lines[-1] if fixed_lines else ""
        marker = line.strip()[0]
        marker_length = len(title_line.strip())

        # Ensure proper section hierarchy
        if not self.state.section_started:
            self.state.section_started = True
            marker = self.section_markers[0]
        else:
            current_level = self.section_markers.index(marker)
            if current_level > self.state.section_level + 1:
                marker = self.section_markers[self.state.section_level + 1]
            self.state.section_level = self.section_markers.index(marker)

        # Add overline for top-level sections
        if marker == self.section_markers[0]:
            fixed_lines.insert(-1, marker * marker_length)

        fixed_lines.append(marker * marker_length)
        fixed_lines.append("")
        self.state.last_line_blank = True
        return True

    def fix_lines(self, lines: list[str]) -> list[str]:
        """Fix RST formatting issues in the given lines.

        Args:
            lines: List of lines to fix

        Returns:
            List of fixed lines with proper RST formatting

        Raises:
            RSTProcessingError: If there is an error processing the lines
        """
        try:
            if self.state.is_code_fragment or any(
                line.startswith("#!") for line in lines[:2]
            ):
                return lines

            fixed_lines = []
            content_started = False

            for i, line in enumerate(lines):
                try:
                    # Handle empty lines
                    if self._handle_empty_line(line, fixed_lines):
                        continue

                    # Handle transitions
                    content_started, handled = self._handle_transition(
                        line, fixed_lines, content_started
                    )
                    if handled:
                        continue

                    # Handle directives
                    next_line = lines[i + 1] if i + 1 < len(lines) else None
                    if self._handle_directive(line, fixed_lines, next_line):
                        content_started = True
                        continue

                    # Handle lists
                    if self._handle_list(line, fixed_lines):
                        content_started = True
                        continue

                    # Handle block quotes
                    self._handle_block_quote(line, fixed_lines)
                    if self.state.in_block_quote:
                        content_started = True
                        continue

                    # Handle definition lists
                    self._handle_definition_list(line, fixed_lines)
                    if self.state.in_definition_list:
                        content_started = True
                        continue

                    # Handle section markers
                    if self._handle_section_marker(line, fixed_lines):
                        content_started = True
                        continue

                    # Fix inline markup
                    if not self.state.in_directive and not self.state.in_block_quote:
                        line = self.fix_inline_markup(line)

                    content_started = True
                    fixed_lines.append(line)
                    self.state.last_line_blank = False

                except Exception as e:
                    self.state.validation_errors.append(
                        ValidationError(i + 1, f"Error processing line: {e!s}", "error")
                    )

            # Ensure file ends with a blank line
            if fixed_lines and fixed_lines[-1].strip():
                fixed_lines.append("")

            return fixed_lines

        except Exception as e:
            raise RSTProcessingError(f"Error processing lines: {e!s}") from e

    def validate_only(self, filepath: str) -> list[ValidationError]:
        """Validate RST file without modifying it.

        Args:
            filepath: Path to the RST file to validate

        Returns:
            List of validation errors found in the file
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            self.state.validation_errors = []
            lines = content.splitlines()
            self.fix_lines(lines)
            return self.state.validation_errors

        except Exception as e:
            return [ValidationError(0, f"Error reading file: {e!s}", "error")]

    def fix_file(self, filepath: str) -> None:
        """Fix RST formatting in a single file.

        Args:
            filepath: Path to the RST file to fix

        Raises:
            RSTFileError: If there is an error reading or writing the file
            RSTProcessingError: If there is an error processing the RST content
        """
        try:
            # Create backup if not in dry run mode
            if not self.dry_run:
                backup_path = f"{filepath}.bak"
                shutil.copy2(filepath, backup_path)

            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Reset state for each file
            self.state.reset()

            lines = content.splitlines()
            fixed_lines = self.fix_lines(lines)

            if not self.dry_run:
                fixed_content = "\n".join(fixed_lines)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

            print(f"Fixed RST formatting in {filepath}")
            if self.state.validation_errors:
                print(f"Warnings/Errors in {filepath}:")
                for error in self.state.validation_errors:
                    msg = f"  Line {error.line_number}: " f"{error.message}"
                    print(msg)

        except OSError as e:
            msg = f"Error handling file {filepath}: {e!s}"
            raise RSTFileError(msg) from e
        except Exception as e:
            msg = f"Error processing {filepath}: {e!s}"
            raise RSTProcessingError(msg) from e

    def fix_directory(self, dirpath: str) -> None:
        """Fix RST formatting in all RST files in a directory using parallel processing.

        Args:
            dirpath: Path to the directory containing RST files to fix
        """
        rst_files = []
        for root, _, files in os.walk(dirpath):
            rst_files.extend(
                os.path.join(root, file) for file in files if file.endswith(".rst")
            )

        with ProcessPoolExecutor() as executor:
            executor.map(self.fix_file, rst_files)


def main() -> None:
    """Main function to run the RST hierarchy fixer.

    This function parses command line arguments and runs the RST hierarchy fixer
    on the specified files or directories. It supports:
    - Processing individual files or entire directories
    - Dry run mode to validate without making changes
    - Validation-only mode to report issues without fixes
    """
    parser = argparse.ArgumentParser(
        description="Fix RST hierarchy and formatting issues."
    )
    parser.add_argument("targets", nargs="+", help="Files or directories to process")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without making changes"
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Report issues without fixes"
    )
    args = parser.parse_args()

    fixer = RSTHierarchyFixer(dry_run=args.dry_run)

    for target in args.targets:
        if not os.path.exists(target):
            print(f"Error: {target} does not exist")
            continue

        if args.validate_only:
            if os.path.isfile(target):
                errors = fixer.validate_only(target)
                if errors:
                    print(f"\nValidation errors in {target}:")
                    for error in errors:
                        print(f"  Line {error.line_number}: {error.message}")
            else:
                print("Error: --validate-only works only with individual files")
        else:
            if os.path.isdir(target):
                fixer.fix_directory(target)
            elif os.path.isfile(target):
                fixer.fix_file(target)


if __name__ == "__main__":
    main()
