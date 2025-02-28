# Vidst Refactoring - Project Navigation

## When to apply
@semantics Applies when navigating or referencing project directories, files, or components. Helps understand the project structure.
@userMessages ".*where (is|are) the.*" ".*find.*file.*" ".*navigate to.*" ".*structure of.*" ".*show me the.*component.*"

## Project Navigation Guide

This rule provides guidance on navigating the Vidst project structure during refactoring.

## Directory Structure

The Vidst project follows this structure:

```
/Users/tony/Documents/Vidst/
├── refactor/                  # Refactoring documentation and plans
│   ├── 01_analysis/           # Initial analysis of current system
│   ├── 02_planning/           # Strategic planning documents
│   ├── 03_implementation_guides/ # Implementation guides for components
│   ├── 04_documentation/      # Documentation standards and templates
│   ├── 05_testing/            # Testing strategies and frameworks
│   ├── 06_references/         # Reference materials
│   └── 07_backup/             # Backup files and templates
├── src/                       # Source code
│   └── video_understanding/   # Main video processing library
├── docs/                      # Project documentation
├── tests/                     # Test files
└── .cursor/                   # Cursor rules directory
    └── rules/                 # Project-specific rules
```

## Key Navigation Points

### Finding Component Implementations

Components are located in `src/video_understanding/` organized by functionality:

| Component | Directory | Key Files |
|-----------|-----------|-----------|
| Scene Detection | `src/video_understanding/ai/scene/` | `base.py`, `opencv_detector.py`, `twelve_labs.py` |
| Vector Storage | `src/video_understanding/storage/vector/` | `base.py`, `faiss.py`, `pinecone.py` |
| OCR | `src/video_understanding/ai/ocr/` | `base.py`, `easyocr.py`, `document_ai.py` |
| Object Detection | `src/video_understanding/ai/object/` | `base.py`, `yolo.py`, `rekognition.py` |
| Audio Transcription | `src/video_understanding/ai/audio/` | `base.py`, `whisper.py` |
| Natural Language Querying | `src/video_understanding/query/` | `base.py`, `semantic_search.py` |
| File Storage | `src/video_understanding/storage/file/` | `base.py`, `local.py`, `s3.py` |
| Caching | `src/video_understanding/cache/` | `base.py`, `redis.py`, `momento.py` |
| Video Processing | `src/video_understanding/processor/` | `base.py`, `ffmpeg.py`, `mediaconvert.py` |

### Finding Documentation

Documentation is organized as follows:

- API documentation: `docs/api/`
- Component documentation: `docs/components/`
- Getting started guides: `docs/`
- Architecture documentation: `docs/architecture/`

### Finding Refactoring Plans

Refactoring plans and documentation are in the `refactor/` directory:

- Master plan: `refactor/02_planning/vidst_refactoring_master_plan.md`
- Implementation timeline: `refactor/02_planning/vidst_implementation_timeline.md`
- Architecture transition: `refactor/02_planning/vidst_architecture_transition.md`
- API integration strategies: `refactor/03_implementation_guides/`

### Finding Tests

Tests are organized by component in the `tests/` directory:

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- API tests: `tests/api/`
- Fixtures: `tests/fixtures/`

## Component Reference

Use this quick reference for components from the evaluation matrix:

1. **Scene Detection**
   - Current: Custom OpenCV-based implementation
   - API Alternative: Twelve Labs Marengo/Pegasus
   - Recommendation: Replace

2. **Vector Storage**
   - Current: Self-hosted FAISS
   - API Alternative: Pinecone API
   - Recommendation: Replace

3. **OCR (Text Extraction)**
   - Current: pytesseract/easyocr
   - API Alternative: Google Document AI
   - Recommendation: Replace

4. **Object Detection**
   - Current: YOLOv8 via ultralytics
   - API Alternative: Amazon Rekognition
   - Recommendation: Phase Later

5. **Audio Transcription**
   - Current: Whisper (placeholder)
   - API Alternative: Hybrid (Whisper + Twelve Labs)
   - Recommendation: Complete Current + API

6. **Natural Language Querying**
   - Current: Backend exists, interface missing
   - API Alternative: Twelve Labs Semantic Search
   - Recommendation: Replace

7. **File Storage**
   - Current: Local file management
   - API Alternative: AWS S3 + Lambda
   - Recommendation: Phase Later

8. **Caching**
   - Current: Redis-based caching
   - API Alternative: Momento Cache
   - Recommendation: Keep Current

9. **Video Processing**
   - Current: Custom processing pipeline with ffmpeg
   - API Alternative: AWS Elemental MediaConvert
   - Recommendation: Keep Current

10. **Documentation**
    - Current: Dual systems (Sphinx + MkDocs)
    - API Alternative: N/A
    - Recommendation: Consolidate

## Navigation Commands

When asked about specific parts of the project, provide file paths and explain their purpose:

### "Where is the Vector Storage implementation?"

The Vector Storage implementation can be found in:
- Base interface: `src/video_understanding/storage/vector/base.py`
- FAISS implementation: `src/video_understanding/storage/vector/faiss.py`
- Pinecone implementation: `src/video_understanding/storage/vector/pinecone.py`

According to the component evaluation matrix, this component is recommended for replacement with Pinecone API.

### "Show me the documentation standards"

Documentation standards are located in:
- Docstring standards: `refactor/04_documentation/vidst_docstring_implementation_guide.md`
- Documentation consolidation plan: `refactor/04_documentation/vidst_documentation_consolidation_plan.md`
- Documentation templates: `refactor/04_documentation/docs_templates/`

### "Where is the test strategy defined?"

The test strategy is defined in:
- TDD testing strategy: `refactor/05_testing/vidst_tdd_testing_strategy.md`
- Test implementation guide: `refactor/05_testing/vidst_tdd_implementation_guide.md`
- Test fixtures reference: `refactor/05_testing/vidst_test_fixtures_reference.md`