# Pull Request: Configure API credentials in .env file

## Description

This PR implements a robust system for managing API credentials for all external services used in the Vidst project. It includes a structured `.env.example` template, credential management utilities, and comprehensive documentation.

Fixes #88

## Changes Made

- Created `.env.example` template with all required API credentials
- Implemented `credentials.py` utility module for secure credential loading
- Added validation to check for required credentials
- Created documentation for API credential setup
- Added unit tests for the credentials module
- Integrated credential loading with API service modules

## Testing Done

- Unit tests added for all credential loading functions
- Manually tested credential loading with various configurations
- Verified error handling for missing credentials
- Tested integration with Twelve Labs, Pinecone, and Document AI modules

## Screenshots

<!-- Add screenshots of the .env.example file and documentation -->

## Checklist

- [x] Create .env.example template
- [x] Add Twelve Labs API credentials
- [x] Add Pinecone credentials
- [x] Add Document AI credentials
- [x] Add Whisper API credentials
- [x] Document each credential's purpose and format
- [x] Add validation for required credentials
- [x] Implement secure credential loading
- [x] Write unit tests
- [x] Update documentation

## Notes for Reviewers

When reviewing this PR, please check:
- Security of credential handling
- Completeness of the .env.example template
- Quality of error messages for missing credentials
- Documentation clarity for new developers