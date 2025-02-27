#!/usr/bin/env python
"""
Coverage Prioritizer

This script analyzes your current test coverage report and identifies which files to prioritize
for increasing coverage most efficiently.
"""

import xml.etree.ElementTree as ET
import csv
import os
import math
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class FileCoverage:
    filename: str
    lines_total: int
    lines_covered: int
    branches_total: int
    branches_covered: int
    coverage_pct: float
    missing_lines: int

    @property
    def impact_score(self) -> float:
        """Calculate an impact score to prioritize files.
        Higher score means higher priority for testing.
        """
        # Files with 0% coverage get highest priority
        if self.coverage_pct == 0:
            base_score = 100
        else:
            base_score = 95 - self.coverage_pct

        # Scale by the number of lines that would be covered if fully tested
        weighted_score = base_score * math.log10(self.missing_lines + 1)
        return weighted_score


def parse_coverage_xml(xml_path: str) -> List[FileCoverage]:
    """Parse coverage.xml file and extract coverage data."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    result = []
    for clazz in root.findall(".//class"):
        filename = clazz.get("filename")
        line_rate = float(clazz.get("line-rate", "0"))
        branch_rate = float(clazz.get("branch-rate", "0"))

        lines_valid = int(clazz.get("lines-valid", "0"))
        lines_covered = int(round(lines_valid * line_rate))

        branches_valid = int(clazz.get("branches-valid", "0"))
        branches_covered = int(round(branches_valid * branch_rate))

        coverage_pct = line_rate * 100
        missing_lines = lines_valid - lines_covered

        result.append(
            FileCoverage(
                filename=filename,
                lines_total=lines_valid,
                lines_covered=lines_covered,
                branches_total=branches_valid,
                branches_covered=branches_covered,
                coverage_pct=coverage_pct,
                missing_lines=missing_lines,
            )
        )

    return result


def identify_test_priorities(coverage_data: List[FileCoverage]) -> List[FileCoverage]:
    """Sort files by priority for testing."""
    return sorted(coverage_data, key=lambda x: x.impact_score, reverse=True)


def format_recommendations(
    prioritized_files: List[FileCoverage], limit: int = 20
) -> str:
    """Format recommendations for display."""
    result = []
    result.append("\nTEST COVERAGE PRIORITY RECOMMENDATIONS")
    result.append("=" * 80)
    result.append(f"{'FILENAME':<50} {'COVERAGE':<10} {'MISSING':<10} {'IMPACT':<10}")
    result.append("-" * 80)

    for i, file in enumerate(prioritized_files[:limit], 1):
        result.append(
            f"{i:2}. {file.filename:<47} {file.coverage_pct:>8.1f}% {file.missing_lines:>9} {file.impact_score:>9.1f}"
        )

    # Calculate potential coverage improvement
    total_lines = sum(f.lines_total for f in coverage_data)
    covered_lines = sum(f.lines_covered for f in coverage_data)

    current_coverage = (covered_lines / total_lines) * 100 if total_lines else 0

    # Estimate coverage if we fully test the top 10 files
    additional_covered = sum(f.missing_lines for f in prioritized_files[:10])
    new_covered = covered_lines + additional_covered
    new_coverage = (new_covered / total_lines) * 100 if total_lines else 0

    result.append("\nCOVERAGE IMPACT ANALYSIS")
    result.append("=" * 80)
    result.append(f"Current coverage: {current_coverage:.2f}%")
    result.append(f"Estimated coverage after testing top 10 files: {new_coverage:.2f}%")
    result.append(f"Coverage improvement: {new_coverage - current_coverage:.2f}%")

    return "\n".join(result)


def export_to_csv(prioritized_files: List[FileCoverage], output_path: str) -> None:
    """Export prioritized files to a CSV file."""
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Priority", "Filename", "Coverage %", "Missing Lines", "Impact Score"]
        )

        for i, file in enumerate(prioritized_files, 1):
            writer.writerow(
                [
                    i,
                    file.filename,
                    f"{file.coverage_pct:.1f}%",
                    file.missing_lines,
                    f"{file.impact_score:.1f}",
                ]
            )

    print(f"Exported priorities to {output_path}")


if __name__ == "__main__":
    coverage_xml_path = "coverage.xml"

    # Check if coverage.xml exists
    if not os.path.exists(coverage_xml_path):
        print(f"Error: {coverage_xml_path} not found. Run pytest with coverage first.")
        exit(1)

    # Parse coverage data
    coverage_data = parse_coverage_xml(coverage_xml_path)

    # Identify priorities
    prioritized_files = identify_test_priorities(coverage_data)

    # Print recommendations
    print(format_recommendations(prioritized_files))

    # Export to CSV
    export_path = "test_priorities.csv"
    export_to_csv(prioritized_files, export_path)
