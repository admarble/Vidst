# Vidst Project Tagging Convention

This document outlines the tagging conventions for the Vidst project. These conventions are designed to provide clarity on issue priority, component focus, and work status in our GitHub project management system.

## Issue Title Format

All issues should follow this format for clear identification:
```
[COMPONENT] Brief description of task
```

Example: `[SCENE-DETECTION] Implement Twelve Labs API integration`

## Priority Tags

Priority tags should be included in the issue description to indicate importance relative to POC goals:

| Tag | Meaning | Description |
|-----|---------|-------------|
| `[POC]` | Proof of Concept Essential | Task is critical for the 6-week POC and must be completed |
| `[OPT]` | Optional Enhancement | Improves the POC but not essential for core functionality |
| `[FUT]` | Future Work | Work that can be deferred beyond the POC phase |

## Component Labels

Each issue should be labeled with one primary component label:

| Label | Component | Description |
|-------|-----------|-------------|
| `scene-detection` | Scene Detection | Scene detection and analysis capabilities |
| `vector-storage` | Vector Storage | Embedding storage and retrieval |
| `ocr` | OCR | Text extraction from video frames |
| `audio-transcription` | Audio Transcription | Speech to text and speaker identification |
| `nl-querying` | Natural Language Querying | Query interface and semantic understanding |
| `file-storage` | File Storage | Video and data file management |
| `caching` | Caching | Caching mechanisms |
| `video-processing` | Video Processing | Core video processing pipeline |
| `documentation` | Documentation | Documentation system and content |

## Status Labels

Status labels track the current state of an issue:

| Label | Status | Description |
|-------|--------|-------------|
| `backlog` | Backlog | Not yet scheduled for implementation |
| `scheduled` | Scheduled | Planned for implementation in a specific week |
| `in-progress` | In Progress | Currently being worked on |
| `blocked` | Blocked | Cannot proceed due to dependencies or issues |
| `review` | In Review | Implemented and awaiting review |
| `testing` | In Testing | Under testing and validation |
| `done` | Done | Completed and verified |

## Type Labels

Type labels indicate the nature of the work:

| Label | Type | Description |
|-------|------|-------------|
| `feature` | Feature | New capability or functionality |
| `enhancement` | Enhancement | Improvement to existing functionality |
| `refactor` | Refactor | Code restructuring without changing behavior |
| `bug` | Bug | Bug fix |
| `documentation` | Documentation | Documentation-related work |
| `infrastructure` | Infrastructure | Development environment, CI/CD, etc. |

## Week Labels

Week labels track which week of the 6-week POC timeline the issue belongs to:

| Label | Timeline | Description |
|-------|----------|-------------|
| `week-1` | Week 1 | Foundation & Twelve Labs Integration |
| `week-2` | Week 2 | Core Functionality & Vector Storage Integration |
| `week-3` | Week 3 | OCR Integration & Documentation Completion |
| `week-4` | Week 4 | Audio Transcription Enhancement |
| `week-5` | Week 5 | Integration & Comprehensive Testing |
| `week-6` | Week 6 | Refinement & Final Validation |

## Priority Labels

Priority labels indicate implementation urgency:

| Label | Priority | Description |
|-------|----------|-------------|
| `priority-high` | High Priority | Critical for POC success, should be addressed immediately |
| `priority-medium` | Medium Priority | Important but not blocking, should be addressed soon |
| `priority-low` | Low Priority | Nice to have, can be addressed if time permits |

## Effort Labels

Effort labels indicate estimated implementation effort:

| Label | Effort | Description |
|-------|--------|-------------|
| `effort-small` | Small | 1-3 days of work |
| `effort-medium` | Medium | 3-5 days of work |
| `effort-large` | Large | 1-2 weeks of work |

## Recommendation Labels

Recommendation labels align with the Component Evaluation Matrix:

| Label | Recommendation | Description |
|-------|----------------|-------------|
| `rec-replace` | Replace | Replace current implementation with API alternative |
| `rec-complete-api` | Complete + API | Complete current implementation and add API integration |
| `rec-phase-later` | Phase Later | Continue with current implementation for POC, consider API later |
| `rec-keep-current` | Keep Current | Maintain current implementation without changes |
| `rec-consolidate` | Consolidate | Simplify or consolidate existing implementation |

## Branch Naming Convention

When creating branches for issues, use the following format:
```
component/issue-number/brief-description
```

Example: `scene-detection/42/twelve-labs-integration`

## GitHub API Reference

For junior developers using the GitHub API to create issues, here's a reference for applying these labels:

```javascript
// Example of creating an issue with appropriate labels using GitHub API
const createIssue = async (title, body, labels) => {
  const response = await octokit.issues.create({
    owner: 'organization-name',
    repo: 'vidst',
    title: title,
    body: body,
    labels: labels
  });
  return response.data;
};

// Example usage
createIssue(
  '[SCENE-DETECTION] Implement Twelve Labs API integration',
  issueBody, // Use template from issue_template.md
  ['scene-detection', 'feature', 'week-1', 'priority-high', 'effort-medium', 'rec-replace']
);
```

## Automation Recommendations

Consider implementing these GitHub Actions for automated labeling:
1. Automatically add `backlog` to new issues without a status label
2. Automatically add appropriate component label based on title prefix
3. Automatically move issues on project board based on label changes

## Example Issue

**Title:** `[SCENE-DETECTION] Implement Twelve Labs API integration`

**Labels:**
- `scene-detection` (component)
- `feature` (type)
- `week-1` (timeline)
- `priority-high` (priority)
- `effort-medium` (effort)
- `rec-replace` (recommendation)
- `backlog` (status)

**Body:** Include the completed issue template with `[POC]` priority tag in the POC Alignment section.
