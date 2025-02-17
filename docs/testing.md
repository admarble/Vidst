# Testing Guide

This guide covers the testing setup, configuration, and best practices for the Video Understanding AI project.

## Table of Contents
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Code Coverage](#code-coverage)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Setup

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-cov coverage-badge
```

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── conftest.py    # Shared test fixtures
```

## Running Tests

### Run All Tests
```bash
# Run all tests with coverage
pytest

# Run specific test types
pytest tests/unit/
pytest tests/integration/
```

### Test Markers
We use the following test markers:
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.slow`: Slow-running tests

```bash
# Run tests by marker
pytest -m integration
pytest -m "not slow"
```

## Code Coverage

### Coverage Configuration
Coverage settings are configured in `pyproject.toml`:

- Minimum coverage threshold: 85%
- Branch coverage enabled
- Excludes:
  - `tests/*`
  - `**/__init__.py`
  - `**/conftest.py`
  - `src/core/config.py`

### Generate Coverage Reports
```bash
# Terminal report
pytest --cov

# HTML report
pytest --cov --cov-report=html

# XML report (for CI)
pytest --cov --cov-report=xml

# Generate coverage badge
coverage-badge -o coverage.svg
```

Reports are generated in:
- HTML: `coverage_html/`
- XML: `coverage.xml`
- Badge: `coverage.svg`

### Coverage Exclusions
Add `# pragma: no cover` to exclude specific lines from coverage. The following are automatically excluded:
- `__repr__` methods
- `if __name__ == '__main__'` blocks
- Abstract methods
- Type checking blocks
- `NotImplementedError` raises

## CI/CD Integration

### GitHub Actions
Coverage reports are automatically:
- Generated during CI runs
- Uploaded to Codecov
- Commented on PRs
- Stored as artifacts

### PR Coverage Comments
Coverage comments on PRs include:
- Overall coverage percentage
- File-by-file breakdown
- Visual indicators:
  - 🟢 Green: ≥85%
  - 🟡 Orange: ≥70%
  - 🔴 Red: <70%

### Codecov Integration
Coverage reports are uploaded to Codecov with:
- Separate flags for unit and integration tests
- Fail-on-error enabled
- Detailed reporting enabled

## Best Practices

### Writing Tests
1. Follow the AAA pattern:
   - Arrange: Set up test data
   - Act: Execute the code under test
   - Assert: Verify the results

2. Use descriptive test names:
```python
def test_video_processor_handles_invalid_format():
    # Test implementation
```

3. Use fixtures for common setup:
```python
@pytest.fixture
def sample_video():
    return "tests/fixtures/sample.mp4"
```

### Coverage Best Practices
1. Don't write tests just to increase coverage
2. Focus on testing business logic and edge cases
3. Use meaningful assertions
4. Keep tests focused and atomic

### Maintaining Coverage
1. Write tests alongside new features
2. Review coverage reports regularly
3. Address coverage drops in PRs
4. Document complex test scenarios

### Common Issues
1. **Missing Coverage**: Check excluded files and patterns
2. **False Positives**: Review pragmas and exclusions
3. **Slow Tests**: Use appropriate markers
4. **Flaky Tests**: Isolate and fix timing/dependency issues 