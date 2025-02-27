#!/usr/bin/env python3
"""Project board automation script for Vidst project.
This script automates the process of updating GitHub project board status
based on commit messages and code changes.
"""

import json
import logging
import re
import subprocess
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("project_board_updates.log"),
    ],
)
logger = logging.getLogger(__name__)


class ProjectBoardUpdater:
    def __init__(self, repo: str = "admarble/Vidst"):
        self.repo = repo
        self.components = {
            "video": ["src/core/video", "src/core/processing/video"],
            "ai": ["src/ai", "src/models"],
            "infrastructure": ["src/storage", "src/core/config"],
            "testing": ["tests"],
            "error-handling": ["src/core/exceptions"],
            "configuration": ["src/core/config"],
            "performance": ["src/core/performance"],
            "pipeline": ["src/core/pipeline"],
        }
        self.state_file = Path(".cursor/project_board_state.json")
        self.load_state()

    def load_state(self):
        """Load the previous state of updates."""
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    self.state = json.load(f)
            else:
                self.state = {"last_commit": None, "updated_issues": {}}
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            self.state = {"last_commit": None, "updated_issues": {}}

    def save_state(self):
        """Save the current state of updates."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def run_gh_command(self, command: list[str]) -> str:
        """Run a GitHub CLI command and return the output."""
        try:
            logger.debug(f"Running GitHub command: gh {' '.join(command)}")
            result = subprocess.run(
                ["gh"] + command, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"GitHub command failed: {e.stderr}")
            raise

    def get_current_branch(self) -> str:
        """Get the name of the current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get current branch: {e}")
            raise

    def parse_branch_name(self, branch: str) -> dict[str, str]:
        """Parse branch name to extract component and feature info."""
        pattern = r"(?:feature|fix|chore)/(?P<component>[^/]+)/(?P<description>.+)"
        match = re.match(pattern, branch)
        if match:
            return match.groupdict()
        logger.warning(f"Branch name '{branch}' doesn't match expected pattern")
        return {}

    def get_modified_files(self) -> list[str]:
        """Get list of modified files in the current commit."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD^", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            files = result.stdout.strip().split("\n")
            logger.info(f"Modified files: {files}")
            return files
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get modified files: {e}")
            return []

    def determine_components(self, files: list[str]) -> list[str]:
        """Determine which components were modified based on file paths."""
        affected_components = set()
        for file in files:
            for component, paths in self.components.items():
                if any(file.startswith(path) for path in paths):
                    affected_components.add(component)
                    logger.debug(f"File {file} matches component {component}")
        return list(affected_components)

    def get_issue_number(self) -> str | None:
        """Extract issue number from branch name or commit message."""
        try:
            branch_info = self.parse_branch_name(self.get_current_branch())
            if not branch_info:
                return None

            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                check=True,
            )
            commit_msg = result.stdout.strip()
            issue_match = re.search(r"#(\d+)", commit_msg)

            if issue_match:
                issue_number = issue_match.group(1)
                logger.info(f"Found issue number: {issue_number}")
                return issue_number

            logger.warning("No issue number found in commit message")
            return None
        except Exception as e:
            logger.error(f"Error getting issue number: {e}")
            return None

    def get_issue_status(self, issue_number: str) -> dict:
        """Get current status of an issue."""
        try:
            result = self.run_gh_command(
                [
                    "issue",
                    "view",
                    issue_number,
                    "-R",
                    self.repo,
                    "--json",
                    "title,body,labels",
                ]
            )
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error getting issue status: {e}")
            return {}

    def update_issue_status(self, issue_number: str, components: list[str]):
        """Update the issue status and labels on GitHub."""
        try:
            # Get current issue status
            current_status = self.get_issue_status(issue_number)

            # Add component labels
            for component in components:
                label = f"component:{component}"
                if label not in [
                    l.get("name") for l in current_status.get("labels", [])
                ]:
                    logger.info(f"Adding label {label} to issue #{issue_number}")
                    self.run_gh_command(
                        [
                            "issue",
                            "edit",
                            issue_number,
                            "-R",
                            self.repo,
                            "--add-label",
                            label,
                        ]
                    )

            # Update issue body with progress
            body = self.generate_progress_body(
                components, current_status.get("body", "")
            )
            logger.info(f"Updating body for issue #{issue_number}")
            self.run_gh_command(
                ["issue", "edit", issue_number, "-R", self.repo, "--body", body]
            )

            # Update state
            self.state["updated_issues"][issue_number] = {
                "last_update": self.get_latest_commit_info(),
                "components": components,
            }
            self.save_state()

        except Exception as e:
            logger.error(f"Error updating issue status: {e}")
            raise

    def generate_progress_body(
        self, components: list[str], current_body: str = ""
    ) -> str:
        """Generate a progress tracking body for the issue."""
        # Preserve existing content above the status section
        existing_content = current_body.split("Component implementation status:", 1)[
            0
        ].strip()

        new_content = f"""{"" if not existing_content else existing_content + "\n\n"}Component implementation status:
{self.format_component_progress(components)}

Related Changes:
- Latest update: {self.get_latest_commit_info()}
"""
        return new_content

    def format_component_progress(self, components: list[str]) -> str:
        """Format the component progress section."""
        progress = []
        for component in components:
            progress.append(f"- [x] {component.title()} component updates")
        return "\n".join(progress)

    def get_latest_commit_info(self) -> str:
        """Get the latest commit information."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%h - %s"],
                capture_output=True,
                text=True,
                check=True,
            )
            commit_info = result.stdout.strip()
            self.state["last_commit"] = commit_info
            return commit_info
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get commit info: {e}")
            return "Unknown commit"

    def run(self):
        """Main execution flow."""
        logger.info("🔄 Starting project board update...")

        try:
            # Get issue number
            issue_number = self.get_issue_number()
            if not issue_number:
                logger.warning("❌ No issue number found in branch or commit message")
                return

            # Get modified files and determine components
            modified_files = self.get_modified_files()
            affected_components = self.determine_components(modified_files)

            if not affected_components:
                logger.warning("❌ No relevant components found in changes")
                return

            logger.info(f"📋 Updating issue #{issue_number}")
            logger.info(f"🔍 Affected components: {', '.join(affected_components)}")

            # Update issue
            self.update_issue_status(issue_number, affected_components)
            logger.info("✅ Project board updated successfully")

        except Exception as e:
            logger.error(f"❌ Error updating project board: {e}")
            raise


if __name__ == "__main__":
    try:
        updater = ProjectBoardUpdater()
        updater.run()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)
