# Tests

This directory contains all test files for the project.

## Structure

- `unit/` - Unit tests
- `integration/` - Integration tests
- `e2e/` - End-to-end tests

## Running Tests

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run e2e tests only
npm run test:e2e
```

## Writing Tests

Please follow these guidelines when writing tests:
1. Name test files with `.test.js` or `.spec.js` extension
2. Group related tests in describe blocks
3. Use clear test descriptions
4. Follow the AAA pattern (Arrange, Act, Assert) 