# Component Tracking Guide

This guide explains how to track components in the Vidst project using the GitHub Project board and the Component Evaluation Matrix.

## Component Overview

The Vidst project is organized around these key components:

1. **Scene Detection** - Identifying scene transitions and boundaries
2. **Vector Storage** - Managing and querying vector embeddings
3. **OCR (Text Extraction)** - Extracting text from video frames
4. **Object Detection** - Identifying objects within video frames
5. **Audio Transcription** - Converting speech to text
6. **Natural Language Querying** - Processing natural language queries
7. **File Storage** - Managing video and data files
8. **Caching** - Optimizing performance through caching
9. **Video Processing** - Core video manipulation functionality
10. **Documentation** - Project documentation systems

## Component Evaluation Matrix

Each component is evaluated using the following criteria:

| Criterion | Description | Scale |
|-----------|-------------|-------|
| POC Importance | How critical is this for the proof of concept | 1-5 (5 being highest) |
| Implementation Status | Current state of implementation | 1-5 (5 being complete) |
| Complexity Burden | How complex is the current implementation | 1-5 (5 being most complex) |
| API Viability | How viable is an API alternative | 1-5 (5 being most viable) |
| Accuracy Requirements | How strict are the accuracy requirements | 1-5 (5 being highest) |
| Cost Impact | Cost efficiency of the solution | 1-5 (5 being most cost-effective) |
| Integration Effort | Effort required to integrate | 1-5 (5 being least effort) |

### Priority Score Calculation

The priority score is calculated as:
```
Priority Score = (POC Importance * 3) + ((5 - Implementation Status) * 2) + (Complexity Burden * 2) + (API Viability * 2) + Accuracy Requirements + Cost Impact + Integration Effort
```

Higher scores indicate higher priority for work or replacement.

## Tracking in GitHub Project

### Custom Fields

The GitHub Project includes these component-related custom fields:

1. **Component** - Single select field with all component options
2. **Priority Score** - Number field for the calculated priority
3. **Implementation Status** - Single select (1-5)
4. **Recommendation** - Single select with options:
   - Replace
   - Complete Current + API
   - Phase Later
   - Keep Current
   - Consolidate

### Component View

The GitHub Project includes a "Component Status" view that:
- Groups issues by component
- Shows current implementation status
- Displays priority scores
- Highlights recommendations

## Workflow for Component Work

### 1. Issue Creation

When creating an issue for component work:

1. Select the appropriate component in the issue template
2. Fill out the priority scoring fields
3. Calculate and include the priority score
4. Add the appropriate component label

### 2. Branch Creation

Create a branch using the component name:
```
component/issue-number/description
```

Example: `scene-detection/123/twelve-labs-integration`

### 3. Development

When working on a component:
1. Follow the recommendation from the evaluation matrix
2. Reference the API alternative if implementing a replacement
3. Include benchmarks for accuracy and performance

### 4. Pull Request

When creating a PR:
1. Select the component in the PR template
2. Complete the "API Alternative Implementation" section for replacements
3. Document any changes to the component's implementation status

### 5. Status Updates

After completing work:
1. Update the component's implementation status in the issue
2. Document any changes to complexity, accuracy, etc.
3. Recalculate the priority score if needed

## Reporting

Component status can be viewed and reported through:

1. **Component Status View** - GitHub Project board view
2. **Component Labels** - GitHub issue filtering
3. **Milestone Progress** - Component work grouped by milestone

## Component-Specific Guidelines

### Scene Detection
- Accuracy requirement: >90%
- Reference: Twelve Labs Marengo/Pegasus API

### Vector Storage
- Consider vector database compatibility
- Reference: Pinecone API

### OCR (Text Extraction)
- Accuracy requirement: >95%
- Reference: Google Document AI

### Audio Transcription
- Accuracy requirement: >95%
- Reference: Hybrid (Whisper + Twelve Labs)

### Natural Language Querying
- Relevance target: >85%
- Reference: Twelve Labs Semantic Search

## Questions or Issues

For questions about component tracking or suggestions for improvement, please create an issue with the `project-management` label.
