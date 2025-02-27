# Vidst Project Management

This directory contains all resources related to the project management workflow for the Vidst Video Understanding AI project.

## Overview

The Vidst project uses GitHub Projects for task and component tracking, with a structured workflow designed for component-based development. Our approach focuses on:

1. **Component-Based Management** - Tracking progress of individual components (Scene Detection, OCR, etc.)
2. **Standardized Workflows** - Clear processes for development, review, and release
3. **Automation** - GitHub Actions to enforce conventions and reduce manual work
4. **Quality Gates** - Structured review and verification processes

## Directory Structure

- **workflows/** - GitHub Actions workflow files for automation
- **templates/** - Issue and pull request templates
- **docs/** - Detailed documentation on processes and conventions

## Key Concepts

### Component Tracking

Each development task is associated with a component from the Component Evaluation Matrix:
- Scene Detection
- Vector Storage
- OCR (Text Extraction)
- Object Detection
- Audio Transcription
- Natural Language Querying
- File Storage
- Caching
- Video Processing
- Documentation

### Project Board Layout

The project board is organized into the following views:
- **Kanban** - Work status tracking
- **Component Status** - Progress by component
- **Timeline** - Work aligned with project phases

### Development Workflow

1. Issues are created with appropriate component tags
2. Branches follow the convention: `component/issue-number/description`
3. Commits include issue references: `[#issue-number] type: description`
4. PRs link back to issues with "Closes #issue-number"
5. Automation moves cards through the project board

## Getting Started

If you're a new contributor:
1. Read the [CONTRIBUTING.md](./CONTRIBUTING.md) guide
2. Review the [workflow documentation](./docs/workflow-guide.md)
3. Check the [branch naming conventions](./docs/branch-conventions.md)

## Implementation Plan

This project management workflow is being implemented in phases:
1. ✅ Project board setup
2. ✅ Issue and PR templates
3. ⏳ Workflow automation
4. ⏳ Developer documentation
5. ⏳ Team training

## Questions or Issues

For questions about the project management workflow, please create an issue with the `project-management` label.
