# Vidst TDD Testing Strategy

## Document Status

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | February 26, 2025 | Vidst Team | Draft |

**Related Documents:**
- [Vidst Refactoring Master Plan](../vidst_refactoring_master_plan.md)
- [Vidst API Integration Strategy](../vidst_api_integration_strategy.md)
- [Vidst Implementation Timeline](../vidst_implementation_timeline.md)
- [Vidst TDD Implementation Guide](./vidst_tdd_implementation_guide.md)
- [Vidst Test Fixtures Reference](./vidst_test_fixtures_reference.md)

## 1. Executive Summary

This document outlines the Test-Driven Development (TDD) strategy for the Vidst video understanding system refactoring project. The strategy is designed to support the project's primary goals of simplifying architecture, completing critical features, meeting performance targets, and adhering to the 6-week POC timeline.

The TDD approach employs a phased testing strategy that prioritizes high-impact components identified in the Component Evaluation Matrix. It provides a framework for validating that API-based implementations meet or exceed the performance of custom implementations while significantly reducing architectural complexity.

### Key Strategic Elements

1. **Interface-First Testing**: Define and test component interfaces before implementation
2. **Progressive Testing**: Start with unit tests using mocks, then add integration tests with real APIs
3. **Performance Validation**: Verify all implementations meet or exceed established performance targets
4. **Phased Approach**: Align testing efforts with the 3-phase refactoring implementation plan
5. **Fallback Validation**: Test graceful degradation and error handling

By following this TDD strategy, the refactoring project will maintain functional quality while achieving a ~60% reduction in architectural complexity and ensuring all critical features are properly implemented.

## 2. TDD Approach and Principles

### 2.1 Test-Driven Development in Context

For this refactoring project, TDD serves as both a validation mechanism and a design tool. The traditional TDD cycle is adapted as follows:

1. **Define Interface Tests**: Write tests that define the expected interface for a component
2. **Write Unit Tests**: Create tests for specific behaviors using mocks for external dependencies
3. **Implement Component**: Write the minimum code needed to satisfy the tests
4. **Integration Testing**: Test the component against real dependencies
5. **Refine and Optimize**: Improve implementation while maintaining test coverage

This approach is particularly valuable for this refactoring effort because:

- It validates that simplified API-based implementations provide the same or better functionality
- It ensures consistent interfaces across the system, even as implementations change
- It provides confidence in the refactored components, reducing risk
- It documents expected behavior through executable tests

### 2.2 Core Testing Principles

The testing strategy is guided by the following principles:

#### Interface Stability
- Define clear interfaces that remain stable regardless of implementation
- Test interfaces first to establish expected behavior
- Use abstract base classes and protocols to enforce interface compliance

#### Component Isolation
- Test components in isolation using mocks and stubs
- Separate unit tests (with mocks) from integration tests (with real dependencies)
- Use dependency injection to facilitate testing

#### Progressive Integration
- Start with unit tests using mocks
- Add integration tests with real APIs
- Create end-to-end tests for complete workflows

#### Performance Focus
- Include specific tests for performance metrics
- Benchmark refactored components against established targets
- Automate performance testing in the CI pipeline

#### Error Handling
- Test failure modes and error conditions
- Verify fallback mechanisms work as expected
- Ensure graceful degradation when services are unavailable

## 3. Testing Categories and Approach

### 3.1 Unit Testing

Unit tests focus on testing individual components in isolation, using mocks for external dependencies.

#### Key Characteristics
- Fast execution (milliseconds)
- No external dependencies
- Tests one component at a time
- Uses mocks for API calls
- Runs on every code change

#### Implementation Approach
- Use pytest as the testing framework
- Implement mock factories for API responses
- Use dependency injection to replace real dependencies with mocks
- Validate functional correctness, not performance

#### Example: TwelveLabsEnhancedModel Unit Test
```python
def test_detect_scenes_with_mock(model, mock_client):
    """Test scene detection with mocked response."""
    # Setup mock
    mock_client.search.query.return_value = {
        "groups": [
            {"start_time": 0, "end_time": 10.5, "confidence": 0.93},
            {"start_time": 10.5, "end_time": 25.2, "confidence": 0.87}
        ]
    }
    
    # Call method
    scenes = await model.detect_scenes("test_index_123")
    
    # Verify results
    assert len(scenes) == 2
    assert scenes[0]["start_time"] == 0
    assert scenes[0]["end_time"] == 10.5
    assert scenes[0]["confidence"] == 0.93
```

### 3.2 Integration Testing

Integration tests verify that components work correctly with real dependencies, particularly external APIs.

#### Key Characteristics
- Slower execution (seconds to minutes)
- Connects to real external services
- Tests component interactions
- Validates actual API behavior
- Runs on major code changes

#### Implementation Approach
- Use pytest with pytest-asyncio for async testing
- Create test fixtures for real API credentials
- Implement test skipping when credentials aren't available
- Use small test datasets to minimize API costs

#### Example: PineconeVectorStorage Integration Test
```python
@pytest.mark.asyncio
async def test_store_and_search_real_api(storage, test_vectors):
    """Test storing and searching vectors with the real Pinecone API."""
    # Store the vectors
    result = await storage.store(test_vectors)
    
    # Verify storage was successful
    assert "upserted_count" in result
    
    # Search for one of the vectors
    search_vector = test_vectors[0]["vector"]
    search_results = await storage.search(search_vector, top_k=3)
    
    # Verify search results
    assert "matches" in search_results
    assert len(search_results["matches"]) > 0
```

### 3.3 End-to-End Testing

End-to-end tests validate complete workflows through the system, ensuring components work together correctly.

#### Key Characteristics
- Slowest execution (minutes)
- Tests complete workflows
- Validates system behavior
- Runs on significant changes

#### Implementation Approach
- Define key workflows to test (e.g., complete video analysis pipeline)
- Use real but small test videos
- Verify end-to-end results against expected outputs
- Run these tests less frequently due to time and cost

### 3.4 Performance Testing

Performance tests verify that components meet or exceed established performance targets.

#### Key Characteristics
- Focused on specific metrics
- Compares against benchmarks
- Validates non-functional requirements

#### Implementation Approach
- Use pytest-benchmark for repeatable measurements
- Define specific test fixtures with performance metrics
- Compare results against established baselines
- Automate performance regression detection

#### Performance Metrics to Test
| Component | Metric | Target | Test Method |
|-----------|--------|--------|------------|
| Scene Detection | Accuracy | >90% | Compare against labeled dataset |
| OCR | Accuracy | >95% | Compare against ground truth text |
| Speech Transcription | Accuracy | >95% | Compare against manual transcriptions |
| Query Response Time | Latency | <2 seconds | Time query operations |
| Query Relevance | Relevance | >85% | Compare against human relevance ratings |

## 4. Testing Strategy by Component

Based on the Component Evaluation Matrix, the testing strategy prioritizes high-impact components first.

### 4.1 Phase 1: High Priority Components (Weeks 1-2)

#### Scene Detection (Twelve Labs)
- **Interface Tests**: Define the scene detection interface
- **Unit Tests**: Test TwelveLabsEnhancedModel with mocked responses
- **Integration Tests**: Test with sample videos against real API
- **Performance Tests**: Verify 94.2% accuracy against labeled dataset

#### Vector Storage (Pinecone)
- **Interface Tests**: Define vector storage and retrieval interface
- **Unit Tests**: Test PineconeVectorStorage with mocked responses
- **Integration Tests**: Test vector operations against real API
- **Performance Tests**: Benchmark query performance
- **Migration Tests**: Verify data migration from FAISS

### 4.2 Phase 2: Enhanced Capabilities (Weeks 3-4)

#### OCR / Text Extraction (Google Document AI)
- **Interface Tests**: Define text extraction interface
- **Unit Tests**: Test DocumentAIModel with mocked responses
- **Integration Tests**: Test with sample images
- **Performance Tests**: Verify >95% accuracy against ground truth

#### Natural Language Querying (Twelve Labs)
- **Interface Tests**: Define query/response interface
- **Unit Tests**: Test semantic search with mocks
- **Integration Tests**: Test end-to-end query flow
- **Performance Tests**: Verify >85% query relevance

#### Audio Transcription (Hybrid Approach)
- **Interface Tests**: Define transcription interface
- **Unit Tests**: Test WhisperModel and TwelveLabsModel with mocks
- **Integration Tests**: Test with sample audio files
- **Performance Tests**: Verify >95% transcription accuracy
- **Selection Tests**: Verify transcription selection logic

### 4.3 Phase 3: System Integration (Weeks 5-6)

#### Pipeline Integration
- **End-to-End Tests**: Test complete video analysis workflow
- **Error Handling Tests**: Verify system responds correctly to failures
- **Cross-Component Tests**: Verify data flows correctly between components

#### Performance Validation
- **System-Level Benchmarks**: Measure end-to-end performance
- **Resource Utilization**: Monitor CPU, memory, and API usage
- **Comparison Tests**: Compare against baseline measurements

## 5. Testing Infrastructure and Environment

### 5.1 Test Directory Structure

The test code will be organized following the existing structure:

```
tests/
├── unit/                 # Unit tests
│   ├── ai/               # AI model tests
│   │   ├── models/       # Individual model tests
│   │   └── pipeline.py   # AI pipeline tests
│   ├── storage/          # Storage tests
│   │   └── vector/       # Vector storage tests
│   └── ...
├── integration/          # Integration tests
│   ├── ai/               # AI integration tests
│   ├── storage/          # Storage integration tests
│   └── ...
├── e2e/                  # End-to-end tests
├── performance/          # Performance tests
│   └── benchmarks/       # Benchmark definitions
├── fixtures/             # Test fixtures
│   ├── video_samples/    # Test videos
│   ├── text_samples/     # Test images with text
│   └── mock_responses/   # Mock API responses
└── utils/                # Test utilities
    ├── mock_factory.py   # Mock response factory
    └── assertions.py     # Custom assertions
```

### 5.2 Test Environment Configuration

Testing will use environment-based configuration to separate test settings from code:

- Store API keys as environment variables
- Use a consistent naming scheme (e.g., `TWELVE_LABS_API_KEY`)
- Create a test configuration module for common settings
- Support local test configuration overrides

### 5.3 CI/CD Integration

The testing strategy will integrate with CI/CD processes:

- Run unit tests on every pull request
- Run integration tests on merge to main branch
- Run performance tests on a scheduled basis
- Use test recording/replay for API-dependent tests in CI

## 6. Documentation and Maintenance

### 6.1 Test Documentation

All tests will be documented following a consistent approach:

- Clear docstrings explaining test purpose and expectations
- Comments for complex test logic
- Descriptive test method names following a consistent pattern
- Test classes grouped by functionality

Example of well-documented test:

```python
@pytest.mark.asyncio
async def test_analyze_video_success(self, model, mock_client):
    """
    Test successful video analysis with Twelve Labs API.
    
    This test verifies that:
    1. The analyze_video method correctly processes the video file
    2. The method properly handles the API response 
    3. The returned object contains the expected fields
    
    Args:
        model: The TwelveLabsEnhancedModel fixture
        mock_client: A mock of the Twelve Labs client
    """
    # Test implementation...
```

### 6.2 Test Maintenance

To ensure long-term test maintainability:

- Regularly update test fixtures and mocks as APIs evolve
- Periodically review and update performance benchmarks
- Refactor tests when implementation patterns change
- Monitor test execution time and optimize slow tests

## 7. Success Criteria

The testing strategy will be considered successful if it enables:

### 7.1 Functional Success Criteria
- All refactored components pass their test suites
- No regression in functionality during refactoring
- Test coverage of >90% for all new and refactored code
- All critical features fully tested

### 7.2 Performance Success Criteria
- All components meet or exceed their performance targets
- Performance tests run automatically in CI pipeline
- Performance regressions are detected and addressed
- System maintains performance under various conditions

### 7.3 Process Success Criteria
- Tests are written before implementation (following TDD)
- Testing approach is consistent across components
- Tests provide clear feedback on failures
- Testing doesn't impede development velocity

## 8. Conclusion

This TDD testing strategy provides a comprehensive framework for ensuring the successful refactoring of the Vidst system. By adopting a test-first approach that prioritizes high-impact components, we can verify that the simplified architecture meets or exceeds the functionality and performance of the current implementation.

The phased testing approach aligns with the overall implementation timeline, ensuring that testing efforts are focused on the most critical components first while providing a clear path for comprehensive test coverage.

**Next Steps:**
1. Set up the test environment and infrastructure
2. Create initial interface tests for high-priority components
3. Implement test fixtures and mock responses
4. Begin the TDD cycle for Phase 1 components

For detailed implementation guidance, refer to the [Vidst TDD Implementation Guide](./vidst_tdd_implementation_guide.md) and [Vidst Test Fixtures Reference](./vidst_test_fixtures_reference.md).
