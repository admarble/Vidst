# Vidst GitHub Workflow Guide

This guide provides a comprehensive overview of the Vidst project's GitHub workflow - from issue creation to release deployment.

## Table of Contents
- [Project Board Overview](#project-board-overview)
- [Development Workflow](#development-workflow)
- [Release Workflow](#release-workflow)
- [Automation](#automation)
- [Best Practices](#best-practices)

## Project Board Overview

The Vidst project uses a GitHub Project board with multiple views:

### 1. Kanban View
The main workflow view with columns:
- **Backlog** - Planned but not ready for development
- **Ready** - Fully specified and ready for development
- **In Progress** - Currently being worked on
- **Code Review** - Pull requests under review
- **Testing** - Changes being tested
- **Done** - Completed work

### 2. Component Status View
This table view tracks the status of different components as defined in the Component Evaluation Matrix, showing:
- Current implementation status
- Planned replacements
- Priority scores
- Assigned developers

### 3. Timeline View
This roadmap view aligns work with project phases:
- Phase 1: Basic Pipeline (2 weeks)
- Phase 2: Enhanced Features (2 weeks)
- Phase 3: Integration (1 week)
- Testing & Documentation (1 week)

## Development Workflow

### 1. Issue Creation
1. **Create an issue** using the appropriate template:
   - Feature request
   - Bug report
   - Component replacement
2. **Add required details**:
   - Component selection
   - Priority information
   - Implementation details
3. **Label appropriately** with component labels
4. Issue will automatically be added to the project board

### 2. Branch Creation
1. **Create a branch** from `develop` using the naming convention:
   ```
   component/issue-number/short-description
   ```
   Example: `scene-detection/123/twelve-labs-integration`

2. **Push the branch** to the repository

### 3. Development
1. **Make code changes** following the project's coding standards
2. **Commit regularly** using the format:
   ```
   [#issue-number] type: description
   ```
   Example: `[#123] feat: implement Twelve Labs scene detection API`

3. **Run tests locally** to ensure quality

### 4. Pull Request
1. **Create a Pull Request** to merge into `develop`
2. **Use the PR template** and fill out all sections
3. **Link to the issue** using "Closes #123" syntax
4. **Request reviews** from appropriate team members
5. **Address review feedback** through conversation and code updates
6. **Ensure all CI checks pass**

### 5. Merge
1. **Squash merge** the PR once approved
2. **Delete the branch** after merging
3. Automation will move the linked issue to "Done"

## Release Workflow

### 1. Release Planning
1. **Create a milestone** for the release
2. **Assign issues** to the milestone
3. **Track progress** on the project board

### 2. Release Branch
1. **Create a release branch** from `develop` when ready:
   ```
   release/vX.Y.Z
   ```
   Example: `release/v1.0.0`

2. **Only bug fixes** should be merged to the release branch

### 3. Final Testing
1. **Run comprehensive tests** on the release branch
2. **Fix any critical issues** that emerge

### 4. Release Deployment
1. **Merge release branch to `main`**
2. **Create a GitHub Release** with:
   - Version tag
   - Release notes
   - Binary artifacts (if applicable)
3. **Merge changes back to `develop`**

## Automation

The workflow is supported by several automated processes:

### 1. Branch Validation
- Validates branch names match the required format
- Ensures branches are linked to components

### 2. Commit Validation
- Ensures commit messages include issue references
- Validates commit message format

### 3. Project Board Automation
- Automatically adds issues and PRs to the project
- Moves cards between columns based on status changes
- Links PRs to issues based on "Closes #X" syntax

### 4. CI/CD Pipeline
- Runs tests for different Python versions
- Checks code formatting and linting
- Performs security scans
- Builds and validates packages

## Best Practices

### For Issue Management
- **Be specific** in issue descriptions
- **Link related issues** when relevant
- **Keep issues focused** on a single component when possible
- **Update issue status** if working on it

### For Development
- **Pull latest `develop`** before creating new branches
- **Create focused branches** for specific features or fixes
- **Commit regularly** with descriptive messages
- **Reference the issue number** in every commit

### For Pull Requests
- **Keep PRs focused** on a single issue
- **Write descriptive PR titles**
- **Fill out the PR template** completely
- **Respond promptly** to review comments

### For Code Review
- **Be thorough but constructive**
- **Check against acceptance criteria**
- **Verify tests are adequate**
- **Ensure documentation is updated**

## Questions or Issues

For questions about the workflow or suggestions for improvement, please create an issue with the `project-management` label.
