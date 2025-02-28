# Vidst Refactoring - Project Management Rules

## When to apply
@semantics Applies when dealing with GitHub project management, issue tracking, or when automation commands are mentioned.
@userMessages ".*update issue.*" ".*create issue.*" ".*project board.*" ".*track progress.*"

## GitHub Project Management

This rule provides guidance on GitHub project management for the Vidst refactoring project, including issue tracking, automation, and project board management.

## Issue Management

### Issue Creation

When creating new issues, use this format:

```bash
gh issue create \
  --title "type(component): Description" \
  --body "Implementation details and checklist" \
  --label "component:name,priority:level,status:ready"
```

Example:

```bash
gh issue create \
  --title "feat(vector-db): Implement Pinecone integration" \
  --body "Implement Pinecone vector database integration to replace FAISS.

Implementation checklist:
- [ ] Create base interface
- [ ] Implement Pinecone adapter
- [ ] Add factory
- [ ] Create migration utility
- [ ] Add tests
- [ ] Update documentation" \
  --label "component:storage,priority:high,status:ready"
```

### Issue Updates

When updating issue progress:

```bash
gh issue edit [ISSUE_NUMBER] \
  --body "Component implementation status:
  - [x] Completed items
  - [ ] In-progress items
  - [ ] Planned items"
```

Example:

```bash
gh issue edit 123 \
  --body "Implementation Status:
  - [x] Create base interface
  - [x] Implement Pinecone adapter
  - [x] Add factory
  - [ ] Create migration utility
  - [ ] Add tests
  - [ ] Update documentation"
```

## Label System

### Status Labels

```
status:ready        - Ready for work
status:blocked      - Blocked by dependencies
status:in-progress  - Currently being worked on
status:review       - Ready for review
status:completed    - Implementation completed
```

### Component Labels

```
component:video           - Video processing
component:ai              - AI/ML components
component:infrastructure  - Infrastructure
component:testing         - Testing
component:error-handling  - Error handling
component:configuration   - Configuration
component:performance     - Performance
component:pipeline        - Pipeline
component:storage         - Storage and persistence
component:documentation   - Documentation
```

### Priority Labels

```
priority:high    - Critical path/blocking
priority:medium  - Important features
priority:low     - Nice to have
```

## Progress Tracking

Use consistent progress indicators in issues:

```markdown
Component implementation status:
- [x] Core functionality
- [x] Basic testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Integration testing
```

Link related pull requests:

```markdown
Related PRs:
- #123 Initial implementation
- #124 Performance improvements
```

Track dependencies:

```markdown
Dependencies:
- Blocked by #125 (API integration)
- Required for #126 (UI implementation)
```

## Project Board Automation

### Status Update Helper Function

```bash
function update_issue_status() {
  ISSUE_NUMBER=$1
  STATUS=$2
  BODY=$3

  gh issue edit $ISSUE_NUMBER -R admarble/Vidst \
    --add-label "status:$STATUS" \
    --body "$BODY"
}

# Example usage
update_issue_status 4 "ready" "Status: Complete\nProgress: 100%\nTasks:\n- [x] Implementation\n- [x] Testing"
```

### Pre-update Validation

Always validate before updating:

```bash
# Check available labels
gh label list -R admarble/Vidst

# Verify issue exists
gh issue view [ISSUE_NUMBER] -R admarble/Vidst
```

## GitHub Workflows

### Common GitHub Commands

```bash
# Clone repository
git clone git@github.com:admarble/Vidst.git

# Create feature branch
git checkout -b feature/vector-db/pinecone-integration

# Stage changes
git add .

# Commit changes
git commit -m "feat(vector-db): Implement Pinecone integration"

# Push branch
git push -u origin feature/vector-db/pinecone-integration

# Create pull request
gh pr create --title "feat(vector-db): Implement Pinecone integration" --body "Implements #123"

# Checkout PR
gh pr checkout 45

# Review PR
gh pr review 45 --approve

# Merge PR
gh pr merge 45 --squash
```

### Commit Message Format

Use conventional commits format:

```
type(scope): Description

Additional details if needed

Refs #issue_number
```

Types:

```
feat:     New feature
fix:      Bug fix
test:     Testing
docs:     Documentation
refactor: Code restructuring
perf:     Performance improvement
```

Example:

```
feat(vector-db): Implement Pinecone integration

- Add Pinecone adapter
- Create vector storage factory
- Update documentation

Refs #123
```

## Work Prioritization

### Priority Matrix

When choosing what to work on, consider:

1. Impact vs. Effort

```
High Impact, Low Effort  → Do First
High Impact, High Effort → Plan Carefully
Low Impact, Low Effort   → Quick Wins
Low Impact, High Effort  → Defer
```

2. Component Priority

```
Core Pipeline     → Highest
AI Integration    → High
Storage/Caching   → Medium
Documentation     → Ongoing
```

3. Dependency Chain

```
Components with many dependents → Higher Priority
Components with many dependencies → Lower Priority
```

### Implementation Order

1. Critical Path
   - Core functionality
   - Blocking issues
   - Data persistence
   - Error handling

2. Feature Development
   - API model integration
   - Performance optimization
   - User experience
   - Documentation

3. Maintenance
   - Test coverage
   - Code quality
   - Documentation
   - Performance monitoring

## Status Update Guidelines

When updating project board items, follow these guidelines to avoid common issues:

### Command Structure

```bash
# Basic status update
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --add-label "status:ready"

# Multiple labels
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --add-label "status:ready,component:metrics"

# Body update with newlines
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --body "Status: Complete\nProgress: 100%"
```

### Common Issues and Solutions

1. **Multi-line Body Text**

```bash
# INCORRECT ❌
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --body "Status: Complete
Progress: 100%
Tasks:
- Task 1"

# CORRECT ✅
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --body "Status: Complete\nProgress: 100%\nTasks:\n- Task 1"
```

2. **Label Validation**

```bash
# INCORRECT ❌
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --add-label "status:done"

# CORRECT ✅
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --add-label "status:ready"
```

3. **Special Characters**

```bash
# INCORRECT ❌
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --body "Progress: 100% | Status: Done"

# CORRECT ✅
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --body "Progress: 100%% | Status: Done"
```

## Progress Tracking Templates

### Component Implementation Template

```markdown
## Component: [Component Name]

### Implementation Status
- [x] Create base interface
- [x] Implement concrete classes
- [ ] Add factory
- [ ] Add resilience patterns
- [ ] Add configuration
- [ ] Add tests
- [ ] Add documentation

### Dependencies
- Depends on #123 (Base framework)
- Blocks #456 (Integration pipeline)

### Progress
- ✅ Interface design completed (Feb 25)
- ✅ Basic implementation completed (Feb 26)
- 🔄 Factory implementation in progress (Est: Feb 27)
- ⏱️ Testing planned (Est: Feb 28)
```

### Integration Template

```markdown
## API Integration: [API Name]

### Implementation Status
- [x] Create configuration class
- [x] Implement API client
- [x] Add authentication
- [x] Add circuit breaker
- [ ] Add retry patterns
- [ ] Create fallback mechanism
- [ ] Add comprehensive testing
- [ ] Add documentation

### Dependencies
- Depends on #123 (Resilience framework)
- Blocks #456 (Pipeline integration)

### Progress
- ✅ API client implemented (Feb 25)
- ✅ Authentication working (Feb 26)
- 🔄 Circuit breaker implementation in progress (Est: Feb 27)
- ⏱️ Testing planned (Est: Feb 28)
```

### Refactoring Template

```markdown
## Refactoring: [Component Name]

### Implementation Status
- [x] Analyze current implementation
- [x] Design new architecture
- [x] Create interfaces
- [ ] Implement concrete classes
- [ ] Add factory pattern
- [ ] Migrate existing data
- [ ] Update tests
- [ ] Update documentation

### Dependencies
- Depends on #123 (Base framework)
- Blocks #456 (Integration pipeline)

### Progress
- ✅ Analysis completed (Feb 25)
- ✅ Architecture design completed (Feb 26)
- 🔄 Interface implementation in progress (Est: Feb 27)
- ⏱️ Data migration planned (Est: Feb 28)
```

## Release Management

### Release Checklist

```markdown
## Release [Version]

### Checklist
- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Performance testing completed
- [ ] Security review completed
- [ ] Change log updated
- [ ] Version bumped
- [ ] Release notes prepared

### Components
- ✅ Component A
- ✅ Component B
- 🔄 Component C (in progress)
- ⏱️ Component D (planned)
```

### Release Command

```bash
# Create release
gh release create v1.0.0 \
  --title "v1.0.0: Initial Release" \
  --notes "Release notes:
- Added Pinecone integration
- Added Document AI integration
- Added Twelve Labs integration
- Added circuit breaker pattern
- Updated documentation"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Lint with black
        run: black --check src tests
      - name: Lint with pylint
        run: pylint src

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Test with pytest
        run: pytest tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/pylint
    rev: v2.16.0
    hooks:
      - id: pylint
        args: [--rcfile=.pylintrc]
```
