# Release Process

This document outlines the release process for the Vidst project, covering planning, execution, and deployment.

## Release Philosophy

The Vidst project follows a structured release process that:
- Uses semantic versioning
- Provides regular, predictable releases
- Ensures quality through staged testing
- Maintains clear documentation of changes

## Release Planning

### 1. Milestone Creation

Each release begins with creating a GitHub Milestone:
- Name format: `v1.0.0`
- Due date set based on project timeline
- Description includes release goals

### 2. Issue Assignment

Issues are assigned to the milestone:
- Priority based on the Component Evaluation Matrix
- Critical bugs always prioritized
- Aligned with project phase goals

### 3. Release Board

A dedicated release view is maintained in the GitHub Project:
- Shows milestone completion progress
- Highlights blocking issues
- Groups work by component

## Versioning

The Vidst project follows [Semantic Versioning](https://semver.org/):

```
vMAJOR.MINOR.PATCH
```

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible new features
- **PATCH** version for backwards-compatible bug fixes

Additional labels for pre-releases:
- `-alpha.1` - Early testing versions
- `-beta.1` - Feature complete, testing versions
- `-rc.1` - Release candidates

## Branch Strategy

### Release Branch Creation

When ready to prepare a release:

1. Create a release branch from `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b release/v1.0.0
   ```

2. Push the branch:
   ```bash
   git push -u origin release/v1.0.0
   ```

### Allowed Changes

On release branches, only these changes are permitted:
- Bug fixes
- Documentation updates
- Version number updates
- No new features

### Version Bumping

1. Update version in `pyproject.toml`:
   ```toml
   [project]
   name = "vidst"
   version = "1.0.0"
   ```

2. Commit the change:
   ```bash
   git commit -am "[#000] chore: bump version to 1.0.0"
   ```

## Release Testing

### 1. CI Pipeline

All release branches undergo extended testing:
- Unit tests across multiple Python versions
- Integration tests
- Performance tests
- Security scans
- Documentation checks

### 2. Pre-release Validation

Before final release:
- Create a pre-release (beta/RC) if needed
- Run manual validation tests
- Verify all milestone issues are completed

## Release Execution

### 1. Final Merge

Once testing is complete:

1. Create a PR to merge `release/v1.0.0` into `main`
2. Require reviews and approvals
3. Ensure all CI checks pass
4. Squash merge to `main`

### 2. Tagging

Create a version tag:
```bash
git checkout main
git pull
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

### 3. GitHub Release

Create a GitHub Release:
1. Title: `Version 1.0.0`
2. Generate release notes from PRs
3. Highlight major changes and features
4. Attach any artifacts (wheels, etc.)
5. Mark as latest release

### 4. Back-merge

Merge changes back to `develop`:
```bash
git checkout develop
git pull
git merge --no-ff main
git push
```

## Release Artifacts

The release process produces:

1. **PyPI Package**
   - Automatically published via CI/CD
   - Both source and wheel distributions

2. **Documentation**
   - Updated automatically on release
   - Version-specific documentation preserved

3. **Release Notes**
   - Published on GitHub Releases
   - Highlights major changes
   - Lists all issues resolved

## Hotfix Process

For critical bugs in production:

1. Create a hotfix branch from `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b hotfix/v1.0.1
   ```

2. Fix the bug and update version

3. Create a PR to merge to `main`

4. After merging to `main`, also merge to `develop`

## Post-Release

After each release:

1. Close the milestone
2. Create a release retrospective
3. Review the release process for improvements
4. Plan the next release cycle

## Release Checklist

Before finalizing a release:

- [ ] All milestone issues resolved
- [ ] Version numbers updated
- [ ] Tests passing on release branch
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Release notes prepared
- [ ] Required approvals received
- [ ] Deployment plan confirmed

## Questions or Issues

For questions about the release process or suggestions for improvement, please create an issue with the `project-management` label.
