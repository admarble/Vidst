#!/bin/bash
# Setup script for Vidst project management

echo "Setting up Vidst project management..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if GitHub CLI is installed
check_github_cli() {
  if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}GitHub CLI (gh) is not installed. Some setup steps will need to be done manually.${NC}"
    echo "Install GitHub CLI from: https://cli.github.com/"
    return 1
  fi
  return 0
}

# Function to check if user is logged in to GitHub CLI
check_github_login() {
  if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Not logged in to GitHub CLI. Please login:${NC}"
    gh auth login
    if [ $? -ne 0 ]; then
      echo -e "${RED}Failed to login to GitHub CLI. Some setup steps will need to be done manually.${NC}"
      return 1
    fi
  fi
  return 0
}

# Check GitHub repository
check_github_repo() {
  echo "Checking GitHub repository..."
  
  # Get current remote origin URL
  REPO_URL=$(git config --get remote.origin.url)
  if [ -z "$REPO_URL" ]; then
    echo -e "${RED}No git remote 'origin' found!${NC}"
    return 1
  fi
  
  echo -e "${GREEN}Repository: $REPO_URL${NC}"
  return 0
}

# Copy workflow files to .github directory
setup_workflows() {
  echo "Setting up GitHub workflow files..."
  
  WORKFLOW_DIR="../../../.github/workflows"
  
  # Create .github/workflows directory if it doesn't exist
  if [ ! -d "$WORKFLOW_DIR" ]; then
    mkdir -p "$WORKFLOW_DIR"
    echo -e "${GREEN}Created .github/workflows directory${NC}"
  fi
  
  # Copy workflow files
  cp ../github/workflows/branch-validator.yml "$WORKFLOW_DIR/"
  cp ../github/workflows/commit-validator.yml "$WORKFLOW_DIR/"
  cp ../github/workflows/project-board-automation.yml "$WORKFLOW_DIR/"
  
  echo -e "${GREEN}Copied workflow files to .github/workflows/${NC}"
  return 0
}

# Setup issue templates
setup_issue_templates() {
  echo "Setting up issue templates..."
  
  TEMPLATE_DIR="../../../.github/ISSUE_TEMPLATE"
  
  # Create .github/ISSUE_TEMPLATE directory if it doesn't exist
  if [ ! -d "$TEMPLATE_DIR" ]; then
    mkdir -p "$TEMPLATE_DIR"
    echo -e "${GREEN}Created .github/ISSUE_TEMPLATE directory${NC}"
  fi
  
  # Copy issue templates
  cp ../github/templates/feature_request.md "$TEMPLATE_DIR/"
  cp ../github/templates/bug_report.md "$TEMPLATE_DIR/"
  cp ../github/templates/component_replacement.md "$TEMPLATE_DIR/"
  
  echo -e "${GREEN}Copied issue templates to .github/ISSUE_TEMPLATE/${NC}"
  return 0
}

# Setup PR template
setup_pr_template() {
  echo "Setting up pull request template..."
  
  PR_TEMPLATE="../../../.github/pull_request_template.md"
  
  # Copy PR template
  cp ../github/templates/pull_request_template.md "$PR_TEMPLATE"
  
  echo -e "${GREEN}Copied pull request template to .github/${NC}"
  return 0
}

# Update main README with project management info
update_readme() {
  echo "Updating main README with project management info..."
  
  README_PATH="../../../README.md"
  
  if [ ! -f "$README_PATH" ]; then
    echo -e "${RED}Main README.md not found!${NC}"
    return 1
  fi
  
  # Check if project management section already exists
  if grep -q "## Project Management" "$README_PATH"; then
    echo -e "${YELLOW}Project management section already exists in README.${NC}"
  else
    # Add project management section to README
    cat << 'EOF' >> "$README_PATH"

## Project Management

### Development Workflow

For contributors:
1. Issues are tracked in the [GitHub Project Board](https://github.com/users/admarble/projects/1)
2. Follow the branch naming convention: `component/issue-number/description`
3. Commit messages must include issue reference: `[#123] type: description`
4. Pull requests must link to issues using "Closes #123" syntax

See the [Project Management documentation](./refactor/02_planning/project_management) for details.

EOF
    echo -e "${GREEN}Added project management section to README${NC}"
  fi
  
  return 0
}

# Create component labels
create_component_labels() {
  echo "Checking GitHub CLI for label creation..."
  
  if ! check_github_cli; then
    echo -e "${YELLOW}Skipping label creation. Please create component labels manually.${NC}"
    return 0
  fi
  
  if ! check_github_login; then
    echo -e "${YELLOW}Skipping label creation. Please create component labels manually.${NC}"
    return 0
  fi
  
  echo "Creating component labels..."
  
  # Define labels with colors
  declare -A LABELS=(
    ["component:scene-detection"]="#0075ca"
    ["component:vector-storage"]="#a2eeef"
    ["component:ocr"]="#7057ff"
    ["component:object-detection"]="#008672"
    ["component:audio-transcription"]="#e4e669"
    ["component:natural-language-querying"]="#d876e3"
    ["component:file-storage"]="#fbca04"
    ["component:caching"]="#1d76db"
    ["component:video-processing"]="#b60205"
    ["component:documentation"]="#0e8a16"
    ["priority:high"]="#d93f0b"
    ["priority:medium"]="#fbca04"
    ["priority:low"]="#0e8a16"
    ["status:ready"]="#0075ca"
    ["status:in-progress"]="#fbca04"
    ["status:blocked"]="#b60205"
    ["type:feature"]="#0e8a16"
    ["type:bug"]="#d73a4a"
    ["type:replacement"]="#a2eeef"
    ["type:refactor"]="#1d76db"
  )
  
  # Get repo info from git remote
  REPO_URL=$(git config --get remote.origin.url)
  REPO_PATH=$(echo "$REPO_URL" | sed -E 's|.*github.com[:/]([^/]+/[^/]+)(\.git)?$|\1|')
  
  for LABEL in "${!LABELS[@]}"; do
    COLOR="${LABELS[$LABEL]}"
    DESCRIPTION="$(echo "$LABEL" | sed 's/:/: /')"
    
    # Create/update label using GitHub CLI
    if gh label create "$LABEL" --color "${COLOR:1}" --description "$DESCRIPTION" --force 2>/dev/null; then
      echo -e "${GREEN}Created/updated label: $LABEL${NC}"
    else
      echo -e "${RED}Failed to create label: $LABEL${NC}"
    fi
  done
  
  echo -e "${GREEN}Component and status labels created/updated${NC}"
  return 0
}

# Setup component flag tracking
setup_component_tracking() {
  echo "Setting up component flag tracking..."
  
  WORKFLOW_DIR="../../../.github/workflows"
  
  # Create component-tracker.yml from the template in the GitHub management doc
  cat << 'EOF' > "$WORKFLOW_DIR/component-tracker.yml"
name: Component Progress Tracker
on:
  push:
    branches: [main, develop]

jobs:
  track_progress:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Update component progress
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            // Get recent commits
            const { execSync } = require('child_process');
            const commits = execSync('git log --format="%s" -n 50').toString().split('\n');
            
            // Parse for component flags
            const componentRegex = /\[([\w-]+)\]/;
            const componentCounts = {};
            
            for (const commit of commits) {
              const match = commit.match(componentRegex);
              if (match) {
                const component = match[1];
                componentCounts[component] = (componentCounts[component] || 0) + 1;
              }
            }
            
            // Update project or create comment with component progress
            console.log('Component activity:', componentCounts);
            
            // Could update a project field, create an issue comment, etc.
EOF
  
  echo -e "${GREEN}Component tracking workflow created in .github/workflows/component-tracker.yml${NC}"
  return 0
}

# Main execution
echo "== Vidst Project Management Setup =="
echo ""

# Check if we're in the right directory
if [[ ! $(pwd) == */refactor/02_planning/project_management/tools ]]; then
  echo -e "${RED}Error: Must run this script from the project_management/tools directory!${NC}"
  exit 1
fi

check_github_repo
setup_workflows
setup_issue_templates
setup_pr_template
update_readme
create_component_labels
setup_component_tracking

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Next steps:"
echo "1. Review the GitHub workflow files in .github/workflows/"
echo "2. Verify issue templates in .github/ISSUE_TEMPLATE/"
echo "3. Review the project management documentation"
echo "4. Ensure your GitHub Project board is set up with the recommended columns"
echo "5. Share the new workflow with your team"
echo ""
echo "For more information, see the project management documentation"