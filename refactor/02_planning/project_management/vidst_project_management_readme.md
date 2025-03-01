# Vidst Project Management

This directory contains all resources related to the project management workflow for the Vidst Video Understanding AI refactoring project.

## Overview

The Vidst refactoring project uses GitHub Projects for task and component tracking, with a structured workflow designed for component-based development. Our approach focuses on:

1. **Component-Based Management** - Tracking progress of individual components (Scene Detection, Vector Storage, OCR, etc.)
2. **Standardized Workflows** - Clear processes for development, review, and release
3. **Automation** - GitHub Actions to enforce conventions and reduce manual work
4. **Quality Gates** - Structured review and verification processes

## Directory Structure

- **github/** - GitHub-specific project management resources
  - **workflows/** - GitHub Actions workflow files for automation
  - **templates/** - Issue and pull request templates
- **execution/** - Execution and tracking documents
  - **vidst_refactoring_checklist.md** - Comprehensive refactoring task checklist
  - **vidst_github_project_management.md** - GitHub project board and automation setup
- **tools/** - Project management scripts and utilities

## Key Concepts

### Component Tracking

Each development task is associated with a component from the Component Evaluation Matrix:
- Scene Detection
- Vector Storage
- OCR (Text Extraction)
- Audio Transcription
- Natural Language Querying
- File Storage
- Caching
- Video Processing
- Documentation

### Project Board Layout

The project board is organized into the following views:
- **Kanban** - Work status tracking by week
- **Component Status** - Progress by component
- **Timeline** - Work aligned with project phases

### Development Workflow

1. Issues are created with appropriate component tags
2. Branches follow the convention: `component/issue-number/description`
3. Commits include component flags: `[Component] Description of change`
4. PRs link back to issues with "Closes #issue-number"
5. Automation moves cards through the project board

## Getting Started

If you're a new contributor:
1. Read the [CONTRIBUTING.md](./github/CONTRIBUTING.md) guide
2. Review the GitHub project management setup [vidst_github_project_management.md](./execution/vidst_github_project_management.md)
3. Review the refactoring checklist [vidst_refactoring_checklist.md](./execution/vidst_refactoring_checklist.md)

## Implementation Plan

This project management workflow is being implemented in phases:
1. ✅ Project board setup
2. ✅ Issue and PR templates
3. ✅ Refactoring checklist
4. ✅ GitHub automation plan
5. ⏳ Workflow automation implementation
6. ⏳ Developer documentation
7. ⏳ Team training

## Questions or Issues

For questions about the project management workflow, please create an issue with the `project-management` label.
