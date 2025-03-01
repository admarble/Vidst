# Branch Naming and Management Conventions

This document defines the branch naming conventions and management practices for the Vidst project.

## Branch Types

The Vidst repository uses the following branch types:

### Main Branches

- **`main`** - Production-ready code
- **`develop`** - Integration branch for development work
- **`release/vX.Y.Z`** - Release preparation branches

### Feature Branches

All development work occurs in feature branches using the naming convention:

```
component/issue-number/short-description
```

## Branch Naming Convention

### Format

```
component/issue-number/short-description
```

### Components

Based on the Component Evaluation Matrix, valid component names are:
- `scene-detection`
- `vector-storage`
- `ocr` (for OCR/Text Extraction)
- `object-detection`
- `audio-transcription`
- `natural-language-querying`
- `file-storage`
- `caching`
- `video-processing`
- `documentation`
- `multi` (for changes that span multiple components)

### Issue Number

This should be the GitHub issue number (without the # symbol).

### Description

A brief, hyphenated description of the change:
- Use lowercase letters and hyphens
- Be concise but descriptive
- Avoid special characters

### Examples

- `scene-detection/123/twelve-labs-integration`
- `vector-storage/145/pinecone-implementation`
- `ocr/167/document-ai-accuracy`
- `audio-transcription/189/whisper-hybrid-api`
- `multi/210/error-handling-improvements`

## Branch Management

### Creation

1. Always create branches from the latest `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b component/issue-number/description
   ```

2. Push the branch to the remote repository:
   ```bash
   git push -u origin component/issue-number/description
   ```

### Maintenance

1. Keep branches focused on a single issue or feature
2. Regularly rebase from `develop` to stay current:
   ```bash
   git checkout develop
   git pull
   git checkout your-branch
   git rebase develop
   ```

3. Squash commits before merging to keep history clean

### Lifecycle

1. **Creation** - Branch created from `develop`
2. **Development** - Work is performed on the branch
3. **Review** - PR is created and reviewed
4. **Integration** - Branch is squash merged to `develop`
5. **Cleanup** - Branch is deleted after merging

## Protection Rules

The following branches have protection rules:

### `main` Branch
- Requires pull request before merging
- Requires approvals (minimum 1)
- Requires status checks to pass
- Prevents force pushes
- Prevents deletion

### `develop` Branch
- Requires pull request before merging
- Requires status checks to pass
- Allows rebase merging

### `release/*` Branches
- Requires pull request before merging
- Requires approvals (minimum 1)
- Requires status checks to pass

## Branch Automation

The repository includes GitHub Actions to enforce branch naming conventions:

- **Branch Name Validator** - Ensures branches follow the naming convention
- **Commit Message Validator** - Ensures commit messages reference issues
- **Branch Cleanup** - Automatically deletes branches after merging

## Release Branches

Release branches follow a different naming convention:

```
release/vX.Y.Z
```

Where X.Y.Z follows semantic versioning:
- X: Major version (breaking changes)
- Y: Minor version (new features, non-breaking)
- Z: Patch version (bug fixes)

Example: `release/v1.0.0`

## Questions or Issues

For questions about branch conventions or suggestions for improvement, please create an issue with the `project-management` label.
