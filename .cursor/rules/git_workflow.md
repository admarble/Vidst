# Vidst Refactoring - Git Workflow Rules

## When to apply
@semantics Applies when working with Git operations, branches, commits, pull requests, and other version control aspects of the project.
@userMessages ".*git.*commit.*" ".*branch.*" ".*pull request.*" ".*merge.*" ".*PR.*" ".*version control.*"

## Git Workflow Overview

This rule provides guidance on the Git workflow for the Vidst refactoring project, ensuring consistency in branch naming, commit messages, and pull request processes.

## Branch Naming Convention

Follow these branch naming conventions:

```
<type>/<component>/<brief-description>
```

Where:
- `<type>` is one of:
  - `refactor`: For refactoring existing code
  - `feature`: For adding new features
  - `fix`: For bug fixes
  - `docs`: For documentation changes
  - `test`: For adding or modifying tests
  - `chore`: For maintenance tasks
- `<component>` is one of:
  - `scene-detection`
  - `vector-storage`
  - `ocr`
  - `object-detection`
  - `audio`
  - `nlq` (Natural Language Querying)
  - `file-storage`
  - `caching`
  - `video-processing`
  - `docs` (Documentation)
- `<brief-description>` is a brief, hyphenated description of the change

Examples:
- `refactor/scene-detection/twelve-labs-integration`
- `feature/vector-storage/pinecone-api`
- `fix/ocr/error-handling`
- `docs/scene-detection/api-documentation`

## Commit Message Format

Follow this commit message format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Where:
- `<type>` is one of:
  - `refactor`: For refactoring existing code
  - `feat`: For adding new features
  - `fix`: For bug fixes
  - `docs`: For documentation changes
  - `test`: For adding or modifying tests
  - `chore`: For maintenance tasks
- `<scope>` is the component affected (e.g., `scene-detection`, `vector-storage`)
- `<subject>` is a short description of the change
- `<body>` is a detailed description of the change (optional)
- `<footer>` is for referencing issues (e.g., `Closes #123`) (optional)

Examples:
- `refactor(scene-detection): Replace OpenCV with Twelve Labs API`
- `feat(vector-storage): Implement Pinecone integration`
- `fix(ocr): Handle image format errors`
- `docs(scene-detection): Add Twelve Labs API documentation`

## Pull Request Process

### PR Title Format

Follow this PR title format:

```
[<type>] <component>: <description>
```

Examples:
- `[Refactor] Scene Detection: Replace OpenCV with Twelve Labs API`
- `[Feature] Vector Storage: Implement Pinecone integration`
- `[Fix] OCR: Handle image format errors`
- `[Docs] Scene Detection: Add Twelve Labs API documentation`

### PR Description Template

Use this template for PR descriptions:

```markdown
## Description

Brief description of the changes.

## Changes

- Detailed list of changes
- Another change

## Testing

- How the changes were tested
- Test results

## Related Issues

- Closes #123
- Addresses #456

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows project style
- [ ] All CI checks pass
```

## Component Replacement Process

When replacing a component with API alternative, follow this Git workflow:

1. Create a branch: `refactor/<component>/<api-name>-integration`
2. Implement the API client
3. Add tests with API mocking
4. Update documentation
5. Commit changes with proper messages
6. Create PR with proper title and description
7. Address review comments
8. Merge PR

Example:

```bash
# Create a branch
git checkout -b refactor/scene-detection/twelve-labs-integration

# Make changes
# ...

# Commit changes
git add .
git commit -m "refactor(scene-detection): Replace OpenCV with Twelve Labs API

- Implemented TwelveLabsSceneDetector
- Added API client with error handling and retries
- Added tests with mocked API responses
- Updated documentation

Closes #123"

# Push branch
git push -u origin refactor/scene-detection/twelve-labs-integration

# Create PR with title:
# [Refactor] Scene Detection: Replace OpenCV with Twelve Labs API
```

## Code Review Guidelines

### Reviewer Guidelines

When reviewing PRs, focus on:

1. **Correctness**: Does the code work as intended?
2. **Architecture**: Does the code follow the project's architecture?
3. **Test Coverage**: Are there sufficient tests?
4. **Documentation**: Is the code properly documented?
5. **Performance**: Are there any performance concerns?
6. **Security**: Are there any security concerns?
7. **Error Handling**: Is error handling comprehensive?
8. **Code Style**: Does the code follow the project's style?

### Approval Process

PRs require at least one approval before merging.

## Branch Protection Rules

Main branches (`main`, `develop`) are protected:

1. PRs are required before merging
2. At least one approval is required
3. CI checks must pass
4. No direct pushes allowed

## Continuous Integration

CI checks will run on all PRs:

1. Linting: Check code style
2. Type Checking: Check type annotations
3. Unit Tests: Run unit tests
4. Integration Tests: Run integration tests
5. Documentation: Build documentation

## Release Process

### Release Branches

Create release branches for each release:

```
release/v<major>.<minor>.<patch>
```

Example: `release/v1.2.0`

### Release Commit Message

Follow this format for release commits:

```
chore(release): v1.2.0

- List of changes
- Another change
```

### Release Tagging

Tag releases with version number:

```
git tag -a v1.2.0 -m "Version 1.2.0"
git push origin v1.2.0
```

## Hotfix Process

For urgent fixes to production code:

1. Create a branch from the release tag: `fix/<component>/<brief-description>`
2. Make the fix
3. Create a PR
4. Merge to both `main` and `develop`

Example:

```bash
# Create a branch from the release tag
git checkout -b fix/scene-detection/api-timeout v1.2.0

# Make the fix
# ...

# Commit changes
git add .
git commit -m "fix(scene-detection): Increase API timeout

Fixes issue with API timeout during large video processing.

Closes #789"

# Push branch
git push -u origin fix/scene-detection/api-timeout

# Create PR with title:
# [Fix] Scene Detection: Increase API timeout
```

## Merge Strategies

Use squash merging for feature/fix branches to keep history clean.

Use merge commits for release branches to preserve history.

## Refactoring Workflow Example

When refactoring a component according to the Component Evaluation Matrix:

1. Create a branch: `refactor/<component>/<api-name>-integration`
2. Create a feature branch for each phase: `refactor/<component>/<phase-name>`
3. Implement the changes for each phase
4. Create a PR for each phase
5. Merge phases into the main refactoring branch
6. Create a final PR for the component refactoring

Example for Vector Storage refactoring:

```bash
# Create main refactoring branch
git checkout -b refactor/vector-storage/pinecone-integration

# Create phase 1 branch
git checkout -b refactor/vector-storage/phase1-api-client

# Implement API client
# ...

# Commit and push
git add .
git commit -m "refactor(vector-storage): Implement Pinecone API client

- Created PineconeConfig
- Implemented PineconeVectorStorage
- Added error handling and retries

Part of #456"
git push -u origin refactor/vector-storage/phase1-api-client

# Create PR for phase 1

# Create phase 2 branch
git checkout refactor/vector-storage/pinecone-integration
git checkout -b refactor/vector-storage/phase2-factory

# Update factory
# ...

# Commit and push
git add .
git commit -m "refactor(vector-storage): Update factory for Pinecone

- Updated VectorStorageFactory
- Added configuration handling

Part of #456"
git push -u origin refactor/vector-storage/phase2-factory

# Create PR for phase 2

# Create phase 3 branch
git checkout refactor/vector-storage/pinecone-integration
git checkout -b refactor/vector-storage/phase3-tests

# Add tests
# ...

# Commit and push
git add .
git commit -m "test(vector-storage): Add tests for Pinecone integration

- Added unit tests with mocked API
- Added integration tests

Part of #456"
git push -u origin refactor/vector-storage/phase3-tests

# Create PR for phase 3

# Create phase 4 branch
git checkout refactor/vector-storage/pinecone-integration
git checkout -b refactor/vector-storage/phase4-docs

# Update documentation
# ...

# Commit and push
git add .
git commit -m "docs(vector-storage): Add Pinecone API documentation

- Added API documentation
- Updated usage examples

Part of #456"
git push -u origin refactor/vector-storage/phase4-docs

# Create PR for phase 4

# Merge all phases into the main refactoring branch
git checkout refactor/vector-storage/pinecone-integration
git merge refactor/vector-storage/phase1-api-client
git merge refactor/vector-storage/phase2-factory
git merge refactor/vector-storage/phase3-tests
git merge refactor/vector-storage/phase4-docs

# Create final PR for the component refactoring
git push -u origin refactor/vector-storage/pinecone-integration

# Create PR with title:
# [Refactor] Vector Storage: Replace FAISS with Pinecone API
```

## Project Board Integration

PRs are automatically linked to the project board:

1. Create an issue for each component refactoring
2. Reference the issue in PR descriptions (`Closes #123`)
3. PRs will automatically move through the project board columns

## Common Git Commands

### Starting a New Feature

```bash
# Create a branch
git checkout -b feature/vector-storage/pinecone-api

# Make changes
# ...

# Commit changes
git add .
git commit -m "feat(vector-storage): Implement Pinecone API integration"

# Push branch
git push -u origin feature/vector-storage/pinecone-api
```

### Updating a Branch

```bash
# Update branch
git fetch origin
git rebase origin/develop

# Resolve conflicts if any
# ...

# Continue rebase
git rebase --continue

# Force push
git push -f origin feature/vector-storage/pinecone-api
```

### Amending Commits

```bash
# Amend last commit
git add .
git commit --amend -m "feat(vector-storage): Implement Pinecone API integration"

# Force push
git push -f origin feature/vector-storage/pinecone-api
```

### Creating a PR

Use the GitHub UI to create a PR with the proper title and description.

### Reviewing a PR

Use the GitHub UI to review a PR, add comments, and approve or request changes.

### Merging a PR

Use the GitHub UI to merge a PR, selecting squash merge for feature/fix branches and merge commit for release branches.