
Project Board Automation


























.. contents:: Table of Contents

   :local:
   :depth: 2

Overview


























The project board automation system automatically updates GitHub issues and project boards based on code changes and commit messages. It helps maintain accurate project status tracking with minimal manual intervention.

.. py:class:: ProjectBoardUpdater

   :no-index:

   The main class that handles project board automation.

   .. py:method:: __init__(self)

      :no-index:

      Initialize the project board updater.

   .. py:method:: determine_components(self, files: List[str]) -> List[str]

      :no-index:

      Determine affected components from modified files.

   .. py:method:: format_component_progress(self, components: List[str]) -> str

      :no-index:

      Format component progress for issue body.

   .. py:method:: generate_progress_body(self, components: List[str], commit_info: str) -> str

      :no-index:

      Generate the full issue body with progress information.

   .. py:method:: get_current_branch(self) -> str

      :no-index:

      Get the name of the current git branch.

   .. py:method:: get_issue_number(self) -> Optional[int]

      :no-index:

      Extract issue number from branch name or commit message.

   .. py:method:: get_issue_status(self, issue_number: int) -> str

      :no-index:

      Get the current status of an issue.

   .. py:method:: get_latest_commit_info(self) -> str

      :no-index:

      Get information about the latest commit.

   .. py:method:: get_modified_files(self) -> List[str]

      :no-index:

      Get list of modified files in the current branch.

   .. py:method:: load_state(self) -> Dict[str, Any]

      :no-index:

      Load the current state from state file.

   .. py:method:: parse_branch_name(self, branch_name: str) -> Dict[str, str]

      :no-index:

      Parse branch name into components.

   .. py:method:: run(self) -> None

      :no-index:

      Run the project board update process.

   .. py:method:: run_gh_command(self, command: str) -> str

      :no-index:

      Run a GitHub CLI command.

   .. py:method:: save_state(self, state: Dict[str, Any]) -> None

      :no-index:

      Save the current state to state file.

   .. py:method:: update_issue_status(self, issue_number: int, components: List[str]) -> None

      :no-index:

      Update the status of an issue.

Features

































\* Issue status and label management*







\* Detailed logging*




Installation


























1. Ensure you have the GitHub CLI installed and authenticated:

   .. code-block:: bash

      Install GitHub CLI








=





=









=





=









=





=









=





=

      Authenticate








=





=


2. Set up the git hooks:

   .. code-block:: bash

      chmod +x .git/hooks/pre-push

Usage


























Branch Naming Convention


------------------------





------------------------





------------------------





------------------------





------------------------




Follow this pattern for branch names:

.. code-block:: text

   <type>/<component>/<description>

   Types:

   - feature: New features
   - fix: Bug fixes
   - chore: Maintenance tasks

   Components:

   - video
   - ai
   - infrastructure
   - testing
   - error-handling
   - configuration
   - performance
   - pipeline

   Example:
   feature/video/scene-detection

Commit Message Format


---------------------





---------------------





---------------------





---------------------





---------------------




Include the issue number in your commit message:

.. code-block:: text

   <type>(<component>): <description> #<issue-number>

   Example:
   feat(video): implement scene detection #75

Automatic Updates


-----------------





-----------------





-----------------





-----------------





-----------------




The system will automatically:

1. Detect modified components based on file changes
2. Update issue labels
3. Track implementation progress
4. Link related commits

Example of an automated update:

.. code-block:: json

   {

      "last_commit": "abc123 - feat(video): implement scene detection",
      "updated_issues": {
         "75": {
               "last_update": "abc123 - feat(video): implement scene detection",
               "components": ["video", "ai"]
         }
      }

   }

Component Mapping


-----------------





-----------------





-----------------





-----------------





-----------------




The system maps file paths to components:

.. code-block:: python

   components = {

      "video": ["src/core/video", "src/core/processing/video"],
      "ai": ["src/ai", "src/models"],
      "infrastructure": ["src/storage", "src/core/config"],
      "testing": ["tests"],
      "error-handling": ["src/core/exceptions"],
      "configuration": ["src/core/config"],
      "performance": ["src/core/performance"],
      "pipeline": ["src/core/pipeline"]

   }

Labels


























The system manages the following label types:

Component Labels


----------------





----------------





----------------





----------------





----------------




- ``component:video`` - Video processing components
- ``component:ai`` - AI/ML components

See Also





























\* :doc:`/guides/automation`*


---------------------------




Indices and Tables





























\* :ref:`modindex`*
