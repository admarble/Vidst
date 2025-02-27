# Test Suite Documentation

## Directory Structure

```text
tests/
├── unit/                  # Unit tests
│   ├── test_video.py     # Video processing tests
│   ├── test_ai_models.py # AI model tests
│   └── ...
├── integration/          # Integration tests
│   └── test_video_pipeline.py
├── e2e/                 # End-to-end tests
├── performance/         # Performance tests
│   ├── test_performance.py
│   └── README.md        # Performance testing guide
├── fixtures/            # Test fixtures
│   ├── video_samples/
│   │   ├── valid/
│   │   └── invalid/
│   ├── audio_samples/
│   │   ├── clean/
│   │   └── noisy/
│   └── mock_responses/
│       ├── gpt4v/
│       ├── whisper/
│       └── twelvelabs/
├── utils/               # Test utilities
│   ├── test_helpers.py
│   ├── mock_factory.py
│   └── assertions.py
├── conftest.py         # pytest configuration
└── README.md           # This file

## Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
pytest tests/performance/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_video.py
```

## Test Categories

### Unit Tests
Individual component testing with mocked dependencies.

### Integration Tests
Testing component interactions and data flow.

### End-to-End Tests
Complete pipeline testing with real data.

### Performance Tests
Benchmarking and resource usage tests. See [Performance Testing Guide](performance/README.md) for:
- Detailed test categories
- Performance metrics and thresholds
- Mock implementations
- Best practices
- Troubleshooting guide

## Test Utilities

### test_helpers.py
Common helper functions for tests.

### mock_factory.py
Factory for generating test data.

### assertions.py
Custom test assertions.

## Fixtures

### Video Samples
- `valid/`: Known good video files
- `invalid/`: Corrupted/invalid video files

### Audio Samples
- `clean/`: High-quality audio
- `noisy/`: Audio with background noise

### Mock Responses
Mock API responses for:
- GPT-4V
- Whisper
- Twelve Labs

## Contributing

1. Add tests for new features
2. Update fixtures as needed
3. Use provided utilities
4. Follow naming conventions
5. Maintain >90% coverage

## Documentation

- [Performance Testing Guide](performance/README.md)
- [Mock Implementations](utils/mocks.py)
- [Custom Exceptions](utils/exceptions.py)
- [Test Configuration](conftest.py)
