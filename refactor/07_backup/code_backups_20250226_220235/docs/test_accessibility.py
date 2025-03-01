"""Test script to verify accessibility and style fixes in documentation."""

from pathlib import Path
from typing import List, Dict, Union

from bs4 import BeautifulSoup, Tag


def test_html_file(file_path: Union[str, Path]) -> List[str]:
    """Test a single HTML file for accessibility and style issues."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        issues: List[str] = []

        # Test 1: Check for inline styles
        elements_with_style = soup.find_all(attrs={"style": True})
        if elements_with_style:
            issues.append(
                f"Found {len(elements_with_style)} elements with inline styles"
            )
            for elem in elements_with_style[:3]:  # Show first 3 examples
                if isinstance(elem, Tag):
                    issues.append(f"  - {elem.name}: {elem.get('style', '')}")

        # Test 2: Check for duplicate viewport meta tags
        viewport_tags = soup.find_all("meta", attrs={"name": "viewport"})
        if len(viewport_tags) > 1:
            issues.append(
                f"Found {len(viewport_tags)} viewport meta tags (should be 1)"
            )

        # Test 3: Check headings for ARIA attributes
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        headings_without_aria = []
        for h in headings:
            if isinstance(h, Tag) and not h.get("aria-level"):
                headings_without_aria.append(h)

        if headings_without_aria:
            issues.append(
                f"Found {len(headings_without_aria)} headings without aria-level"
            )
            for h in headings_without_aria[:3]:
                if isinstance(h, Tag):
                    text = h.get_text()[:50]
                    issues.append(f"  - {h.name}: {text}...")

        # Test 4: Check form inputs for labels
        inputs = soup.find_all(
            "input", attrs={"type": ["text", "search", "email", "tel", "number"]}
        )
        for input_elem in inputs:
            if isinstance(input_elem, Tag):
                input_id = input_elem.get("id")
                if input_id:
                    label = soup.find("label", attrs={"for": input_id})
                    aria_label = input_elem.get("aria-label")
                    if not (label or aria_label):
                        issues.append(f"Input missing label: id={input_id}")

        # Test 5: Check for skip-to-content link
        skip_links = soup.find_all("a", attrs={"class": "skip-to-content"})
        if not skip_links:
            issues.append("Missing skip-to-content link")

        return issues


def main() -> None:
    """Run tests on all HTML files in the _build/html directory."""
    build_dir = Path("_build/html")
    if not build_dir.exists():
        print("Error: _build/html directory not found. Run 'make html' first.")
        return

    all_issues: Dict[str, List[str]] = {}
    html_files = list(build_dir.rglob("*.html"))

    print(f"Testing {len(html_files)} HTML files...")
    for file_path in html_files:
        rel_path = file_path.relative_to(build_dir)
        issues = test_html_file(file_path)
        if issues:
            all_issues[str(rel_path)] = issues

    if all_issues:
        print("\nIssues found:")
        for file_path, issues in all_issues.items():
            print(f"\n{file_path}:")
            for issue in issues:
                print(f"  {issue}")
    else:
        print("\nNo issues found! All tests passed.")


if __name__ == "__main__":
    main()
