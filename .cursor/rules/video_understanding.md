# Video Understanding AI - Cursor Rules

## Project Overview

This is a proof-of-concept system for analyzing educational and technical video content using AI models.

## Code Style & Standards

### Python Version & Environment

- Use Python 3.10+ for all development
- Maintain virtual environment using `venv`
- All dependencies must be listed in `requirements.txt` with pinned versions

### Code Formatting

- Use Black formatter with 88 character line length
- Enable format on save
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values

### Project Structure

- Follow the established directory structure:

  ```
  src/
  ├── core/          # Core processing components
  ├── ai/            # AI model integration
  └── storage/       # Data persistence
  ```

- Place tests in corresponding `tests/` directory structure

### Component Development

- All components must inherit from `BaseComponent`
- Implement both `process()` and `validate()` methods
- Use custom exceptions for error handling
- Document all public methods and classes

### Testing Requirements

- Maintain >90% test coverage
- Include unit tests for all components
- Use pytest fixtures for test setup
- Mock external API calls in tests
- Include integration tests for critical paths

### Performance Guidelines

- Maximum video file size: 2GB
- Process videos within 2x video duration
- Query response time < 2 seconds
- Memory limit: 4GB per job
- Maximum concurrent jobs: 3

### Error Handling

- Use custom exception classes
- Implement proper error logging
- Include retry mechanisms for API calls
- Queue long-running tasks appropriately

### AI Model Integration

- Support for multiple models:
  - OpenAI GPT-4V
  - Google Gemini Pro Vision
  - Twelve Labs
  - Whisper v3
- Implement proper API key management
- Handle rate limits and quotas

### Security

- Never commit API keys or credentials
- Use environment variables for sensitive data
- Validate all input data
- Implement proper access controls

### Documentation

- Document all new features
- Update API documentation
- Include usage examples
- Document known limitations

### Sphinx Documentation

- Add Sphinx documentation for every new implementation:

  ```python
  def process_video(file_path: str) -> Dict[str, Any]:
      """Process a video file and extract relevant information.

      This function handles the core video processing pipeline including
      scene detection, audio transcription, and text extraction.

      Args:
          file_path (str): Path to the video file to process.

      Returns:
          Dict[str, Any]: A dictionary containing:
              - scenes (List[Scene]): Detected scene information
              - transcription (Dict[str, str]): Timestamped transcriptions
              - text_content (List[TextBlock]): Extracted text content

      Raises:
          VideoProcessingError: If video processing fails
          VideoFormatError: If video format is not supported

      Example:
          >>> processor = VideoProcessor()
          >>> result = processor.process_video("lecture.mp4")
          >>> print(f"Found {len(result['scenes'])} scenes")
      """
      pass
  ```

- Follow RST formatting for module documentation:

  ```rst
  Video Processing Module
  ======================

  .. module:: video_processing
      :synopsis: Core video processing functionality

  .. moduleauthor:: Your Name <email@example.com>

  Module Description
  -----------------
  This module implements the core video processing pipeline...

  Classes
  -------
  .. autoclass:: VideoProcessor
      :members:
      :undoc-members:
      :show-inheritance:
  ```

- Document all parameters using type hints and docstrings
- Include working code examples in docstrings
- Add cross-references to related components
- Document any configuration options
- Include performance considerations
- List all possible exceptions
- Add version information for API changes

### Documentation Build Process

- Build and test documentation locally before committing:

  ```bash
  cd docs
  make html
  make doctest
  ```

- Ensure no Sphinx warnings or errors
- Verify all cross-references are valid
- Check external links are working
- Test code examples in documentation
- Update table of contents when adding new pages

### Documentation Organization

- Follow the established documentation structure:

  ```
  docs/
  ├── api/              # API reference documentation
  ├── guides/           # User and developer guides
  ├── examples/         # Code examples and tutorials
  ├── architecture/     # System architecture docs
  └── deployment/       # Deployment and ops guides
  ```

- Keep related documentation together
- Maintain consistent formatting
- Use proper heading hierarchy
- Include diagrams when helpful

### Git Workflow

- Branch naming: `feature/component/description`
- Descriptive commit messages
- Link issues in PRs
- Get code review before merging

### GitHub Project Board Management

- Update project board after significant changes:

  ```bash
  # Update issue status
  gh issue edit [ISSUE_NUMBER] \
    -R admarble/Vidst \
    --add-label "status:ready,component:[COMPONENT]"

  # Update progress tracking
  gh issue edit [ISSUE_NUMBER] \
    -R admarble/Vidst \
    --body "Implementation Status:
    - [x] Completed tasks
    - [ ] Pending tasks
    - [ ] Future tasks"
  ```

#### Label System

- Status Labels:

  ```
  status:ready   - Ready for development
  status:blocked - Blocked by dependencies
  ```

- Component Labels:

  ```
  component:video          - Video processing
  component:ai            - AI/ML components
  component:infrastructure - Infrastructure
  component:testing       - Testing
  component:error-handling - Error handling
  component:configuration  - Configuration
  component:performance    - Performance
  component:pipeline      - Pipeline
  ```

- Priority Labels:

  ```
  priority:high   - Critical path items
  priority:medium - Important but not blocking
  priority:low    - Nice to have
  ```

#### Progress Tracking

- Use consistent progress indicators:

  ```markdown
  Component implementation status:
  - [x] Core functionality
  - [x] Basic testing
  - [ ] Performance optimization
  - [ ] Documentation
  - [ ] Integration testing
  ```

- Link related pull requests:

  ```markdown
  Related PRs:
  - #123 Initial implementation
  - #124 Performance improvements
  ```

- Track dependencies:

  ```markdown
  Dependencies:
  - Blocked by #125 (API integration)
  - Required for #126 (UI implementation)
  ```

#### Update Frequency

- After each significant commit
- When completing milestones
- When status changes
- When dependencies change
- Before and after code review

### Resource Management

- Implement proper cleanup in destructors
- Use context managers for resource handling
- Cache intermediate results
- Monitor memory usage

### Success Metrics

Must maintain:

- Scene Detection Accuracy: >90%
- OCR Accuracy: >95%
- Speech Transcription Accuracy: >95%
- Processing Speed: Maximum 2x video duration
- Query Response Time: <2 seconds

### API Design & Standards

- Follow RESTful API design principles
- Use consistent endpoint naming conventions:

  ```
  GET    /api/v1/videos              # List videos
  POST   /api/v1/videos              # Upload video
  GET    /api/v1/videos/{id}         # Get video details
  DELETE /api/v1/videos/{id}         # Delete video
  POST   /api/v1/videos/{id}/analyze # Start analysis
  ```

- Version all APIs (v1, v2, etc.)
- Include rate limiting headers
- Implement proper pagination
- Return consistent error responses:

  ```json
  {
    "error": {
      "code": "VIDEO_NOT_FOUND",
      "message": "Video with ID 123 not found",
      "details": {...}
    }
  }
  ```

### Logging Standards

- Use structured logging:

  ```python
  logger.info("Processing video", extra={
      "video_id": video.id,
      "duration": video.duration,
      "format": video.format
  })
  ```

- Log levels:
  - ERROR: Application errors requiring immediate attention
  - WARNING: Unexpected situations that don't break functionality
  - INFO: Important business events and milestones
  - DEBUG: Detailed technical information for debugging
- Include request ID in all logs
- Log all API requests and responses
- Implement proper log rotation
- Never log sensitive information

### Monitoring & Metrics

- Track key performance indicators:
  - API response times
  - Video processing duration
  - Model inference times
  - Error rates by type
  - Resource utilization
- Set up alerts for:
  - Error rate spikes
  - Processing time anomalies
  - Resource exhaustion
  - API availability issues
- Use prometheus-style metric names:

  ```
  video_processing_duration_seconds
  model_inference_duration_seconds
  api_request_duration_seconds
  ```

- Include proper metric labels and tags

### Data Management

- Video Storage:
  - Use cloud storage for raw videos
  - Implement lifecycle policies
  - Enable versioning for processed results
- Database:
  - Use migrations for schema changes
  - Index frequently queried fields
  - Implement proper backup strategy
- Caching:
  - Cache processed results
  - Use Redis for temporary storage
  - Implement proper TTL policies
- Data Retention:
  - Define retention periods by data type
  - Implement automated cleanup
  - Maintain audit logs

### CI/CD Pipeline

- Required checks before merge:

  ```yaml
  - lint:
      - black --check
      - pylint
      - mypy
  - test:
      - pytest
      - coverage
  - security:
      - bandit
      - dependency-check
  - docs:
      - sphinx-build
      - doc8
  ```

- Automated deployment stages:
  - dev: Automatic on merge to develop
  - staging: Manual trigger
  - production: Manual trigger with approval
- Version tagging:
  - Follow semantic versioning
  - Generate changelogs
  - Tag releases in git

### Development Environment

- Required IDE extensions:
  - Python
  - Black Formatter
  - Pylint
  - Git Lens
  - Docker
- Recommended VS Code settings:

  ```json
  {
    "python.analysis.typeCheckingMode": "strict",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true
  }
  ```

- Local development tools:
  - Docker Desktop
  - Make
  - pre-commit hooks

### Dependency Management

- Pin all dependencies with exact versions
- Maintain separate requirements files:

  ```
  requirements.txt          # Production dependencies
  requirements-dev.txt      # Development dependencies
  requirements-test.txt     # Testing dependencies
  ```

- Regular dependency updates:
  - Weekly security updates
  - Monthly minor version updates
  - Quarterly major version updates
- Dependency audit process:
  - Check for known vulnerabilities
  - Verify license compliance
  - Test compatibility

### Project Board Automation

#### Issue Management

- Create issues with proper structure:

  ```bash
  gh issue create \
    --title "type(component): Description" \
    --body "Implementation details and checklist" \
    --label "component:name,priority:level,status:ready"
  ```

- Update issue progress regularly:

  ```bash
  gh issue edit [NUMBER] \
    --body "Component implementation status:
    - [x] Completed items
    - [ ] In-progress items
    - [ ] Planned items"
  ```

- Use consistent labels:

  ```
  Status:
  - status:ready        - Ready for work
  - status:blocked      - Blocked by dependencies
  - status:in-progress  - Currently being worked on

  Components:
  - component:video          - Video processing
  - component:ai             - AI/ML components
  - component:infrastructure - Infrastructure
  - component:testing        - Testing
  - component:error-handling - Error handling
  - component:configuration  - Configuration
  - component:performance    - Performance
  - component:pipeline       - Pipeline
  - component:storage        - Storage and persistence

  Priority:
  - priority:high    - Critical path/blocking
  - priority:medium  - Important features
  - priority:low     - Nice to have
  ```

#### Commit Messages

- Link issues in commits:

  ```
  type(component): Description #issue_number

  - Detailed change 1
  - Detailed change 2
  ```

- Types:

  ```
  feat:     New feature
  fix:      Bug fix
  test:     Testing
  docs:     Documentation
  refactor: Code restructuring
  perf:     Performance improvement
  ```

### Work Prioritization

#### Selection Criteria

1. Priority Level
   - High: Critical path items blocking other work
   - Medium: Important features needed soon
   - Low: Nice-to-have improvements

2. Dependencies
   - Blocked issues should be addressed first
   - Consider dependency chain impact
   - Unblock other developers' work

3. Component Health
   - Test coverage below threshold
   - Known bugs or issues
   - Technical debt
   - Performance bottlenecks

4. Resource Availability
   - Required API access
   - Development environment setup
   - Team expertise
   - Time constraints

#### Decision Matrix

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

3. Test Coverage

   ```
   <50%  → Critical Priority
   <80%  → High Priority
   <90%  → Medium Priority
   ≥90%  → Maintain
   ```

#### Implementation Order

1. Critical Path
   - Core functionality
   - Blocking issues
   - Data persistence
   - Error handling

2. Feature Development
   - AI model integration
   - Performance optimization
   - User experience
   - Documentation

3. Maintenance
   - Test coverage
   - Code quality
   - Documentation
   - Performance monitoring

#### Progress Tracking

- Update issue status regularly
- Link related issues and PRs
- Document blockers and dependencies
- Track test coverage metrics
- Monitor performance benchmarks

### Project Board Status Updates

#### Command Structure and Guidelines

When updating project board items, follow these specific guidelines to avoid common issues:

```bash
# Basic status update
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --add-label "status:ready"

# Multiple labels
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --add-label "status:ready,component:metrics"

# Body update with newlines
gh issue edit [ISSUE_NUMBER] -R admarble/Vidst --body "Status: Complete\nProgress: 100%"
```

#### Common Issues and Solutions

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

#### Status Update Helper Function

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

#### Pre-update Validation

Always validate before updating:

```bash
# Check available labels
gh label list -R admarble/Vidst

# Verify issue exists
gh issue view [ISSUE_NUMBER] -R admarble/Vidst
```

#### Best Practices

1. **Formatting**
   - Use `\n` for line breaks
   - Escape special characters
   - Keep updates concise
   - Use consistent formatting

2. **Progress Tracking**
   - Use checkboxes: `- [x]` completed, `- [ ]` pending
   - Include percentage complete
   - List specific accomplishments
   - Note any blockers

3. **Label Usage**
   - Verify label existence
   - Use correct label format
   - Combine labels appropriately
   - Update component labels

4. **Body Content**
   - Structure updates consistently
   - Include relevant context
   - Reference related PRs
   - Note any dependencies
