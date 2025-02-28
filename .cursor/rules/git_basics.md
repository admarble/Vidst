# Vidst Refactoring - Git Basics

## When to apply
@semantics Applies when working with basic Git operations such as branching, committing, and pushing changes.
@userMessages ".*git.*commit.*" ".*create branch.*" ".*push changes.*" ".*commit message.*" ".*git basics.*"

## Git Basics Guidelines

This rule provides guidance on basic Git operations for the Vidst refactoring project.

## Branch Naming Convention

Follow this pattern for branch names:

```
<type>/<component>/<brief-description>
```

Example branches:
- `refactor/scene-detection/twelve-labs-integration`
- `feature/vector-storage/pinecone-api`
- `fix/ocr/error-handling`
- `docs/api/update-readme`

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Example commit messages:
```
feat(vector-storage): Add Pinecone integration

Implement vector storage using Pinecone API with the following features:
- Configuration via environment variables
- Error handling with retries
- Vector indexing and search

Closes #123
```

## Basic Git Commands

### Creating a New Branch

```bash
# Create and switch to a new branch
git checkout -b refactor/scene-detection/twelve-labs-api

# Or create from develop branch
git checkout develop
git pull
git checkout -b refactor/scene-detection/twelve-labs-api
```

### Staging and Committing Changes

```bash
# Stage all changes
git add .

# Stage specific files
git add src/video_understanding/ai/scene/twelve_labs.py

# Commit changes
git commit -m "refactor(scene-detection): Implement Twelve Labs API client"
```

### Pushing Changes

```bash
# First push (sets upstream)
git push -u origin refactor/scene-detection/twelve-labs-api

# Subsequent pushes
git push
```

### Checking Status

```bash
# View status of working directory
git status

# View commit history
git log --oneline
```

### Pulling Latest Changes

```bash
# Update current branch
git pull

# Pull from specific branch
git pull origin develop
```

## Common Git Tasks

### Amending the Last Commit

```bash
# Make changes
git add .

# Amend commit (keeps the same message)
git commit --amend --no-edit

# Amend commit with new message
git commit --amend -m "refactor(scene-detection): Implement Twelve Labs API client"

# Push amended commit
git push -f
```

### Discarding Changes

```bash
# Discard changes in working directory
git checkout -- file.py

# Discard all unstaged changes
git checkout -- .

# Discard staged changes
git reset HEAD file.py
git checkout -- file.py
```

### Stashing Changes

```bash
# Stash changes
git stash

# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply specific stash
git stash apply stash@{2}

# Drop stash after applying
git stash pop
```

## Component Refactoring Flow

For refactoring components based on the evaluation matrix:

1. Create a branch for the component
2. Implement changes
3. Add tests
4. Update documentation
5. Commit with proper message
6. Push and create PR

Example workflow:

```bash
# Create branch
git checkout -b refactor/vector-storage/pinecone-api

# Make changes and stage them
git add .

# Commit with proper message
git commit -m "refactor(vector-storage): Implement Pinecone integration

- Add PineconeConfig class
- Implement PineconeVectorStorage
- Add error handling and retry logic

Resolves #456"

# Push to remote
git push -u origin refactor/vector-storage/pinecone-api
```

## Git Best Practices

1. ✓ Pull before starting work to get latest changes
2. ✓ Create descriptive branch names
3. ✓ Write meaningful commit messages
4. ✓ Make small, focused commits
5. ✓ Push changes regularly
6. ✓ Keep branches up to date with develop
7. ✓ Reference issues in commit messages
