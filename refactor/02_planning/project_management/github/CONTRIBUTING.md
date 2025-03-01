# Contributing to Vidst

This guide outlines the contribution workflow for the Vidst project. Following these guidelines helps maintain code quality and streamlines project management.

## Table of Contents
- [Issue Tracking](#issue-tracking)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Component Work](#component-work)
- [Release Process](#release-process)

## Issue Tracking

All work should be tracked via GitHub issues:

1. Check existing issues before creating a new one
2. Use the appropriate issue template:
   - Feature request
   - Bug report
   - Component replacement
   - Documentation
3. Include the component name in the issue title
4. Fill out all required fields in the issue template
5. Add appropriate labels, especially the component label

## Branch Naming Convention

Branches should follow this format:
```
component/issue-number/short-description
```

Examples:
- `scene-detection/123/twelve-labs-integration`
- `vector-storage/145/pinecone-implementation`
- `ocr/167/google-document-ai`

For branches that span multiple components, use:
```
multi/issue-number/short-description
```

## Commit Message Format

All commit messages should include the issue number and follow this format:
```
[#issue-number] type: description
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Formatting changes (whitespace, etc.)
- `refactor`: Code refactoring without functionality changes
- `test`: Adding/updating tests
- `chore`: Build process or auxiliary tool changes

Examples:
- `[#123] feat: implement Twelve Labs scene detection API`
- `[#145] refactor: optimize vector storage queries`
- `[#167] fix: improve OCR accuracy for small text`

## Pull Request Process

1. Create a PR using the template
2. Link the PR to the corresponding issue using "Closes #issue-number"
3. Ensure the PR title follows the commit message format
4. Assign appropriate reviewers
5. All CI checks must pass
6. Meet the acceptance criteria specified in the issue
7. Update documentation as needed

After approval:
- Squash merge to keep history clean
- Delete branch after merging

## Code Standards

- Follow the project's coding style guidelines
- Ensure code passes all linters
- Write tests for new features
- Maintain or improve test coverage (>85%)
- Document public APIs and complex functions

## Component Work

For components identified in the Component Evaluation Matrix:

1. Check the component's priority score
2. Follow the recommendation (Replace, Keep Current, Phase Later)
3. Reference the API alternative if implementing a replacement
4. Update implementation status in the issue when complete

Component data should match fields in the Component Evaluation Matrix:
- Priority Score
- Implementation Status (1-5)
- Complexity Burden
- API Viability
- Accuracy Requirements

## Release Process

We use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Incompatible API changes
- MINOR: New features (backward-compatible)
- PATCH: Bug fixes (backward-compatible)

Release process:
1. Create a release branch: `release/vX.Y.Z`
2. Only bug fixes get merged to release branches
3. Merge to main AND back to develop when ready
4. Tag the release with the version number
5. Generate release notes from PR descriptions