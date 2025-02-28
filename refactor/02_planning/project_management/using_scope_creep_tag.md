# Using the Scope Creep Tag in Issue Tracking

## Overview

This guide explains how to use the `scope:creep` tag and related scope management tags in the Vidst issue tracking system. These tags are designed to help the team identify, discuss, and manage features or tasks that may exceed the defined scope of the POC.

## Available Scope Tags

- **`scope:creep`**: Indicates features or tasks that potentially exceed the minimum viable implementation defined for the POC
- **`scope:deferred`**: Used for features that have been explicitly deferred to a post-POC phase
- **`scope:adjusted`**: Applied when a feature's scope has been adjusted to fit within POC constraints

## Automated Scope Creep Detection

A GitHub workflow automatically scans new issues and pull requests for keywords that might indicate scope creep (e.g., "advanced features", "comprehensive", "optimization"). When detected:

1. The issue is automatically labeled with `scope:creep`
2. A comment is added explaining why it was flagged
3. The team is prompted to review against the Minimum Viable Component Definitions

## How to Use Scope Tags

### During Issue Creation

1. **Self-assessment**: Before creating an issue, review the [Minimum Viable Component Definitions](/Users/tony/Documents/Vidst/refactor/02_planning/vidst_minimum_viable_components.md) document
2. **Proper labeling**: If you're aware that a feature exceeds POC scope but want to document it, add the `scope:deferred` label

### During Daily Scope Checks

1. **Review flagged issues**: In daily standups, review any issues tagged with `scope:creep`
2. **Make explicit decisions**:
   - If the feature is within scope, remove the `scope:creep` tag
   - If out of scope but important to document, change to `scope:deferred`
   - If scope needs adjustment, add `scope:adjusted` and update the issue description

### When Working on Issues

1. **Stay vigilant**: If during implementation you realize a task is expanding beyond POC requirements, add the `scope:creep` tag yourself
2. **Document carefully**: Always note scope decisions in issue comments

## Scope Management Process

When an issue is flagged with `scope:creep`:

1. **Assessment**: Team reviews against Minimum Viable Component Definitions
2. **Discussion**: Brief discussion in daily standup or issue comments
3. **Decision**:
   - **Proceed as-is**: Remove scope:creep tag if determined to be within scope
   - **Simplify**: Adjust requirements to fit POC scope and add `scope:adjusted`
   - **Defer**: Move to backlog for future implementation and add `scope:deferred`
   - **Split**: Break into "POC essential" and "future enhancement" issues

## Weekly Scope Review

In addition to daily checks, conduct a weekly scope review:

1. Search for all issues with scope tags
2. Review decisions and ensure alignment with project timeline
3. Update documentation as needed

## Example Workflow

1. New issue created: "Implement advanced speaker identification with accent detection"
2. Automated workflow adds `scope:creep` tag based on keywords
3. During standup, team reviews against minimum viable component definition
4. Team determines speaker identification is out of scope for POC
5. Issue is labeled `scope:deferred` and moved to backlog
6. A simplified issue is created for basic transcription that fits POC requirements

## Reporting

The project dashboard includes a "Scope Management" section that displays:

1. Current count of issues by scope tag
2. Trend of scope tags over time
3. Components with highest scope creep detection

This reporting helps the team maintain awareness of scope management throughout the project.

## Best Practices

- Always refer to the Minimum Viable Component Definitions document when making scope decisions
- Document scope decisions in issue comments for future reference
- Be proactive in identifying scope creep in your own work
- Use scope tags consistently to maintain visibility
- Review scope:creep issues promptly to avoid implementation delays

## Conclusion

Effective scope management is critical for completing the POC within the 6-week timeline. The scope tag system provides visibility and consistent decision-making around feature scope, helping the team stay focused on delivering the essential functionality that demonstrates the core value proposition.
