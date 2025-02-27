#!/usr/bin/env python3
"""Script to automatically fix RST and documentation formatting issues."""

import sys
from pathlib import Path

import yaml


class FixReport:
    """Tracks fixes applied to a file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.fixes: set[str] = set()
        self.details: list[str] = []

    def add_fix(self, fix_type: str, detail: str | None = None):
        """Add a fix to the report."""
        self.fixes.add(fix_type)
        if detail:
            self.details.append(f"  - {detail}")

    def has_fixes(self) -> bool:
        """Check if any fixes were applied."""
        return len(self.fixes) > 0

    def __str__(self) -> str:
        """Generate a string report of all fixes."""
        if not self.has_fixes():
            return f"No fixes needed in {self.file_path}"

        fixes_list = list(self.fixes)
        fixes_list.sort()
        report = [f"Fixed in {self.file_path}:"]
        for fix in fixes_list:
            report.append(f"- {fix}")
        if self.details:
            report.extend(self.details)
        return "\n".join(report)


class RSTFixer:
    """Fixes common RST formatting issues."""

    def __init__(self):
        # Define hierarchy levels and their characters
        self.hierarchy = {
            "part": ("#", True),  # True means use both overline and underline
            "chapter": ("*", True),
            "section": ("=", False),  # False means use only underline
            "subsection": ("-", False),
            "subsubsection": ("^", False),
            "paragraph": ('"', False),
        }
        self.report: FixReport | None = None

    def detect_title_level(
        self, lines: list[str], index: int
    ) -> tuple[str, bool] | None:
        """Detect the heading level based on context and current line."""
        if index >= len(lines):
            return None

        line = lines[index].strip()
        if not line:
            return None

        # Check if it's a title line
        if index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if not next_line or not all(c == next_line[0] for c in next_line):
                return None

            # Check if it has an overline
            has_overline = False
            if index > 0:
                prev_line = lines[index - 1].strip()
                if prev_line and all(c == prev_line[0] for c in prev_line):
                    has_overline = True

            # Determine level based on character and overline presence
            for level, (char, requires_overline) in self.hierarchy.items():
                if next_line[0] == char:
                    if requires_overline == has_overline:
                        return (level, has_overline)

        return None

    def fix_underlines(self, content: str) -> str:
        """Fix RST title underlines to match their title lengths and enforce hierarchy."""
        lines = content.splitlines()
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                fixed_lines.append(line)
                i += 1
                continue

            # Detect title level
            level_info = self.detect_title_level(lines, i)

            if level_info:
                level, has_overline = level_info
                char, requires_overline = self.hierarchy[level]
                title = lines[i].rstrip()
                title_len = len(title)
                line_str = char * title_len

                # Handle overline + title + underline
                if requires_overline:
                    if not has_overline:
                        fixed_lines.append(line_str)
                        if self.report:
                            self.report.add_fix(
                                "Added missing overline",
                                f"Added overline for {level}: '{title}'",
                            )
                    fixed_lines.append(title)
                    fixed_lines.append(line_str)
                    i += 2 if has_overline else 1
                # Handle title + underline only
                else:
                    fixed_lines.append(title)
                    fixed_lines.append(line_str)
                    i += 2

                if self.report:
                    self.report.add_fix(
                        f"Fixed {level} formatting",
                        f"Applied correct formatting for: '{title}'",
                    )
            else:
                fixed_lines.append(line)
                i += 1

        return "\n".join(fixed_lines) + "\n"

    def fix_blank_lines(self, content: str) -> str:
        """Fix missing blank lines after explicit markup and between sections."""
        lines = content.splitlines()
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)

            # Add blank line after sections
            level_info = self.detect_title_level(lines, i)
            if level_info and i + 2 < len(lines):
                if lines[i + 2].strip():  # If next line after heading isn't blank
                    fixed_lines.append("")
                    if self.report:
                        self.report.add_fix(
                            "Added section spacing",
                            f"Added blank line after section: '{line.strip()}'",
                        )

            # Add blank line before sections
            if i + 1 < len(lines):
                next_level = self.detect_title_level(lines, i + 1)
                if next_level and fixed_lines and fixed_lines[-1].strip():
                    fixed_lines.append("")
                    if self.report:
                        self.report.add_fix(
                            "Added section spacing", "Added blank line before section"
                        )

            i += 1

        return "\n".join(fixed_lines) + "\n"

    def fix_indentation(self, content: str) -> str:
        """Fix inconsistent indentation in RST files."""
        lines = content.splitlines()
        fixed_lines = []
        fixed_count = 0

        for line in lines:
            stripped = line.lstrip()
            if not stripped:  # Empty line
                fixed_lines.append(line)
                continue

            # Calculate indentation level
            indent = len(line) - len(stripped)
            if indent > 0:
                # Normalize to multiples of 3 spaces
                normalized_indent = ((indent + 2) // 3) * 3
                if normalized_indent != indent:
                    fixed_count += 1
                    if self.report:
                        self.report.add_fix(
                            "Indentation normalization",
                            f"Changed indent from {indent} to {normalized_indent} spaces: '{line.strip()}'",
                        )
                fixed_lines.append(" " * normalized_indent + stripped)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines) + "\n"

    def fix_title_overline_mismatch(self, content: str) -> str:
        """Fix title overline and underline mismatches."""
        lines = content.splitlines()
        fixed_lines = []
        i = 0

        while i < len(lines):
            # Check for potential title with overline
            if (
                i + 2 < len(lines)
                and lines[i].strip()
                and lines[i + 1].strip()
                and lines[i + 2].strip()
            ):

                # Check if it's a title pattern
                first_char = lines[i][0]
                for _, (char, requires_overline) in self.hierarchy.items():
                    if first_char == char and requires_overline:
                        title = lines[i + 1]
                        title_len = len(title.rstrip())
                        line = char * title_len

                        if line != lines[i].strip() or line != lines[i + 2].strip():
                            if self.report:
                                self.report.add_fix(
                                    "Title overline/underline mismatch",
                                    f"Fixed overline/underline for: '{title.strip()}'",
                                )
                        fixed_lines.extend([line, title, line])
                        i += 3
                        break
                else:
                    fixed_lines.append(lines[i])
                    i += 1
            else:
                fixed_lines.append(lines[i])
                i += 1

        return "\n".join(fixed_lines) + "\n"


class YAMLFixer:
    """Fixes common YAML formatting issues."""

    def __init__(self):
        # Map of Python constructors to their string representations
        self.constructor_map = {
            "materialx.emoji.twemoji": "materialx.emoji.twemoji",
            "materialx.emoji.to_svg": "materialx.emoji.to_svg",
            "pymdownx.superfences.fence_code_format": "pymdownx.superfences.fence_code_format",
            "pymdownx.superfences.fence_div_format": "pymdownx.superfences.fence_div_format",
            "pymdownx.arithmatex.fence_mathjax_format": "pymdownx.arithmatex.fence_mathjax_format",
        }
        self.report: FixReport | None = None

    def fix_yaml(self, content: str) -> str:
        """Fix YAML formatting issues."""
        try:
            original_content = content

            # Handle all Python constructors before parsing
            for constructor in self.constructor_map:
                pattern = f"!!python/name:{constructor}"
                if pattern in content:
                    content = content.replace(
                        pattern, self.constructor_map[constructor]
                    )
                    if self.report:
                        self.report.add_fix(
                            "Python constructor",
                            f"Removed constructor from: {constructor}",
                        )

            # Parse YAML content
            data = yaml.safe_load(content)

            # Fix markdown extensions configuration
            if "markdown_extensions" in data:
                extensions = data["markdown_extensions"]
                for i, ext in enumerate(extensions):
                    if not isinstance(ext, dict):
                        continue

                    # Fix materialx.emoji configuration
                    if "materialx.emoji" in ext:
                        emoji_config = ext["materialx.emoji"]
                        if "emoji_index" in emoji_config:
                            old_val = emoji_config["emoji_index"]
                            emoji_config["emoji_index"] = "materialx.emoji.twemoji"
                            if self.report and old_val != "materialx.emoji.twemoji":
                                self.report.add_fix(
                                    "Emoji index configuration",
                                    f"Updated emoji_index from {old_val}",
                                )
                        if "emoji_generator" in emoji_config:
                            old_val = emoji_config["emoji_generator"]
                            emoji_config["emoji_generator"] = "materialx.emoji.to_svg"
                            if self.report and old_val != "materialx.emoji.to_svg":
                                self.report.add_fix(
                                    "Emoji generator configuration",
                                    f"Updated emoji_generator from {old_val}",
                                )

                    # Fix pymdownx.superfences configuration
                    if "pymdownx.superfences" in ext:
                        fence_config = ext["pymdownx.superfences"]
                        if "custom_fences" in fence_config:
                            for fence in fence_config["custom_fences"]:
                                if "format" in fence:
                                    format_val = fence["format"]
                                    # Convert any Python constructor to string
                                    if (
                                        isinstance(format_val, str)
                                        and "!!" in format_val
                                    ):
                                        for constructor in self.constructor_map:
                                            if constructor in format_val:
                                                old_val = fence["format"]
                                                fence["format"] = constructor
                                                if self.report:
                                                    self.report.add_fix(
                                                        "Fence format configuration",
                                                        f"Updated format from {old_val} to {constructor}",
                                                    )

            # Dump back to YAML with proper formatting
            return yaml.dump(data, sort_keys=False, allow_unicode=True)

        except yaml.YAMLError as e:
            print(f"Error fixing YAML: {e}", file=sys.stderr)
            return content


def process_file(file_path: Path) -> FixReport | None:
    """Process a single file and fix formatting issues."""
    try:
        content = file_path.read_text()
        original_content = content
        report = FixReport(file_path)

        if file_path.suffix == ".rst":
            fixer = RSTFixer()
            fixer.report = report
            # Apply all RST fixes
            content = fixer.fix_underlines(content)
            content = fixer.fix_blank_lines(content)
            content = fixer.fix_indentation(content)
            content = fixer.fix_title_overline_mismatch(content)

        elif file_path.name == "mkdocs.yml":
            fixer = YAMLFixer()
            fixer.report = report
            content = fixer.fix_yaml(content)

        if content != original_content:
            file_path.write_text(content)
            return report if report.has_fixes() else None

        return None

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return None


def main():
    """Main entry point."""
    # Get all documentation files
    docs_dir = Path("docs")
    rst_files = list(docs_dir.rglob("*.rst"))
    yaml_files = [Path("mkdocs.yml")] if Path("mkdocs.yml").exists() else []

    reports = []
    for file_path in rst_files + yaml_files:
        report = process_file(file_path)
        if report:
            reports.append(report)

    if reports:
        print("\nDetailed fix report:")
        for report in reports:
            print(f"\n{report}")
        print(f"\nFixed formatting in {len(reports)} files")
    else:
        print("\nNo files needed fixing")


if __name__ == "__main__":
    main()
