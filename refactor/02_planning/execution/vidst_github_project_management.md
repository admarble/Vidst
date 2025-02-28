# Vidst GitHub Project Management Plan

## Overview

This document outlines a comprehensive GitHub project management strategy for the Vidst refactoring project. It provides a structured approach to cleaning up existing issues, creating new tasks based on the refactoring checklist, and implementing automation to track progress effectively.

## 1. GitHub Repository Cleanup

### 1.1 Issue Audit and Cleanup

- [ ] **Review and categorize existing issues**
  - Identify issues related to refactoring vs. non-refactoring tasks
  - Label all issues with appropriate categories (see labeling system below)
  - Close any duplicate or outdated issues with appropriate comments

- [ ] **Archive completed issues and pull requests**
  - Close all completed items with appropriate resolution comments
  - Link related issues to their completion pull requests

- [ ] **Update issue templates**
  - Create specific templates for different issue types:
    - Bug report template
    - Feature request template
    - Refactoring task template
    - Documentation update template

### 1.2 Branch and Pull Request Cleanup

- [ ] **Review open pull requests**
  - Close or merge stale pull requests
  - Add appropriate labels to in-progress PRs

- [ ] **Define branch naming convention**
  - Format: `type/component/brief-description`
  - Examples: 
    - `refactor/twelve-labs/enhance-api-client`
    - `refactor/vector-storage/implement-pinecone`
    - `fix/documentation/consolidate-mkdocs`

- [ ] **Create branch protection rules**
  - Require pull request reviews before merging
  - Require status checks to pass before merging
  - Consider requiring linear history

## 2. GitHub Project Board Setup

### 2.1 Create Refactoring Project Board

- [ ] **Set up new project board named "Vidst Refactoring"**
  - Use GitHub Projects (Beta) for enhanced automation features
  - Configure views:
    - Kanban Board view
    - Timeline/Gantt view
    - Calendar view for deadlines
    - Table view for component tracking

- [ ] **Configure project columns**
  - Backlog: Tasks not yet started or scheduled
  - Week 1: Foundation & Twelve Labs
  - Week 2: Vector Storage
  - Week 3: Documentation & OCR
  - Week 4: Audio Transcription
  - Week 5: Integration & Testing
  - Week 6: Refinement & Validation
  - In Progress: Currently being worked on
  - Review: Awaiting code review
  - Done: Completed tasks

### 2.2 Create Custom Fields for Project Board

- [ ] **Add custom fields for tracking**
  - Priority: High, Medium, Low
  - Component: Dropdown with components from refactoring checklist
  - Estimated Effort: Story points (1, 2, 3, 5, 8)
  - Week: 1-6 (corresponding to implementation timeline)
  - Risk Level: High, Medium, Low

## 3. Labeling System

### 3.1 Component Labels (Use consistent colors - e.g., blue)

- [ ] **Create component labels**
  - `component:twelve-labs`
  - `component:vector-storage`
  - `component:ocr`
  - `component:transcription`
  - `component:documentation`
  - `component:testing`
  - `component:infrastructure`

### 3.2 Process Labels (Use consistent colors - e.g., green)

- [ ] **Create process labels**
  - `status:blocked` - For issues blocked by dependencies
  - `status:ready` - Ready for implementation
  - `status:in-progress` - Currently being worked on
  - `status:review-needed` - Awaiting review
  - `priority:high` - High priority tasks
  - `priority:medium` - Medium priority tasks
  - `priority:low` - Low priority tasks

### 3.3 Type Labels (Use consistent colors - e.g., purple)

- [ ] **Create type labels**
  - `type:refactor` - Refactoring tasks
  - `type:bug` - Bug fixes
  - `type:feature` - New features
  - `type:docs` - Documentation updates
  - `type:test` - Testing related tasks
  - `type:maintenance` - Maintenance tasks

## 4. Creating Structured Issues from Refactoring Checklist

### 4.1 Issue Creation Approach

- [ ] **Generate issues with consistent structure**
  - Title format: `[Component] Task description`
  - Include relevant section from refactoring checklist in description
  - Link to relevant documentation (refactoring plan, etc.)
  - Add acceptance criteria
  - Assign appropriate labels
  - Link to parent epic/milestone

- [ ] **Create weekly epics/milestones**
  - Create a milestone for each implementation week
  - Set milestone due dates according to project timeline

### 4.2 Task Dependency Management

- [ ] **Establish task dependencies in descriptions**
  - Use "Depends on #issue-number" in issue description
  - Link related issues with "Related to #issue-number"

- [ ] **Create parent-child relationships**
  - Use task lists in parent issues
  - Reference parent issues in child issues

## 5. Automation Setup

### 5.1 GitHub Actions for Project Automation

- [ ] **Create workflow for issue management**
  - Automatically label new issues based on title or content
  - Move newly created issues to appropriate column based on milestone/week
  - Notify team members of high-priority issues

```yaml
# .github/workflows/issue-management.yml
name: Issue Management
on:
  issues:
    types: [opened, edited, labeled, unlabeled]

jobs:
  process_issues:
    runs-on: ubuntu-latest
    steps:
      - name: Auto-label issues
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const issue = context.payload.issue;
            
            // Auto-label based on title
            if (issue.title.toLowerCase().includes('twelve labs')) {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                labels: ['component:twelve-labs']
              });
            }
            
            // Add more logic for other components and types
            
            // Move to appropriate project column based on week tag
            if (issue.title.toLowerCase().includes('[week 1]')) {
              // Move to Week 1 column
            }
```

- [ ] **Create workflow for PR management**
  - Auto-link PRs to issues based on branch name or PR description
  - Move linked issues to "In Progress" when PR is opened
  - Move linked issues to "Review" when PR is ready for review
  - Move linked issues to "Done" when PR is merged

```yaml
# .github/workflows/pr-management.yml
name: PR Management
on:
  pull_request:
    types: [opened, edited, ready_for_review, closed]

jobs:
  process_prs:
    runs-on: ubuntu-latest
    steps:
      - name: Update linked issues
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const pr = context.payload.pull_request;
            
            // Extract issue numbers from PR description
            const issueRegex = /#(\d+)/g;
            const matches = pr.body.match(issueRegex) || [];
            const issueNumbers = matches.map(match => parseInt(match.substring(1)));
            
            for (const issueNumber of issueNumbers) {
              // Update issue status based on PR status
              if (context.payload.action === 'opened') {
                // Move issue to In Progress
              } else if (context.payload.action === 'ready_for_review') {
                // Move issue to Review
              } else if (context.payload.action === 'closed' && pr.merged) {
                // Move issue to Done
              }
            }
```

### 5.2 Project Board Automation Rules

- [ ] **Configure column automation rules**
  - When issues are assigned, move to "In Progress"
  - When PRs are merged, move linked issues to "Done"
  - When issues are labeled with "status:blocked", add to "Blocked" view

- [ ] **Set up progress tracking automation**
  - Calculate and display completion percentage for each week/milestone
  - Create burndown chart for the project
  - Generate weekly progress reports

## 6. Implementing Component Flags and Progress Tracking

### 6.1 Component Flag System

- [ ] **Implement component flags in commit messages**
  - Format: `[Component] Description of change`
  - Examples:
    - `[TwelveLabs] Enhance API client with retry mechanisms`
    - `[VectorStorage] Implement Pinecone adapter`

- [ ] **Create GitHub Action to track component progress**
  - Parse commit messages for component flags
  - Update progress tracking for each component
  - Generate component status reports

```yaml
# .github/workflows/component-tracker.yml
name: Component Progress Tracker
on:
  push:
    branches: [main, develop]

jobs:
  track_progress:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Update component progress
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            // Get recent commits
            const { execSync } = require('child_process');
            const commits = execSync('git log --format="%s" -n 50').toString().split('\n');
            
            // Parse for component flags
            const componentRegex = /\[([\w-]+)\]/;
            const componentCounts = {};
            
            for (const commit of commits) {
              const match = commit.match(componentRegex);
              if (match) {
                const component = match[1];
                componentCounts[component] = (componentCounts[component] || 0) + 1;
              }
            }
            
            // Update project or create comment with component progress
            console.log('Component activity:', componentCounts);
            
            // Could update a project field, create an issue comment, etc.
```

### 6.2 Automated Board Updates

- [ ] **Configure automated status reports**
  - Schedule weekly status report generation
  - Update project board with component progress
  - Generate visualization of progress by component

- [ ] **Set up Slack/Teams integration for notifications**
  - Send daily progress summaries
  - Notify about blocked issues
  - Highlight upcoming deadlines

## 7. Issue Creation From Refactoring Checklist

### 7.1 Batch Issue Creation Script

- [ ] **Create a script to generate issues from the checklist**

```javascript
// scripts/create-github-issues.js
const fs = require('fs');
const axios = require('axios');

// GitHub configuration
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = 'owner';
const REPO_NAME = 'vidst';

// Read the checklist file
const checklist = fs.readFileSync('../vidst_refactoring_checklist.md', 'utf8');

// Parse the checklist sections
const sections = parseChecklistSections(checklist);

// Create issues for each task
async function createIssues() {
  for (const section of sections) {
    // Create milestone/epic for section
    const milestoneId = await createMilestone(section.title, section.description);
    
    // Create issues for each task
    for (const task of section.tasks) {
      await createIssue({
        title: `[${section.component}] ${task.title}`,
        body: `## Description\n${task.description}\n\n## Acceptance Criteria\n${task.criteria}\n\n## Milestone\nPart of ${section.title}`,
        labels: [`component:${section.component}`, 'type:refactor'],
        milestone: milestoneId
      });
    }
  }
}

// Helper functions for creating milestones and issues
async function createMilestone(title, description) {
  // Implementation...
}

async function createIssue(issueData) {
  // Implementation...
}

// Run the script
createIssues().catch(console.error);
```

### 7.2 Issue Templates

- [ ] **Create refactoring task issue template**

```
---
name: Refactoring Task
about: Tasks related to the Vidst refactoring project
title: "[Component] Task description"
labels: type:refactor
assignees: ''
---

## Description
<!-- Brief description of the refactoring task -->

## Refactoring Checklist Reference
<!-- Link or quote from the refactoring checklist -->

## Implementation Details
<!-- Any specific implementation requirements or notes -->

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests added/updated
- [ ] Documentation updated

## Dependencies
<!-- List any dependent issues with #issue-number format -->

## Related Documentation
<!-- Links to relevant documentation -->
```

## 8. Progress Monitoring and Reporting

### 8.1 Scheduled Progress Reports

- [ ] **Set up automated weekly progress reports**
  - Create GitHub Action to run on schedule
  - Generate progress summary based on completed tasks
  - Compare actual progress with planned timeline

```yaml
# .github/workflows/progress-report.yml
name: Weekly Progress Report
on:
  schedule:
    - cron: '0 9 * * MON'  # Every Monday at 9 AM

jobs:
  generate_report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate progress report
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            // Query milestones and calculate progress
            const milestones = await github.rest.issues.listMilestones({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open'
            });
            
            let report = '# Weekly Progress Report\n\n';
            
            for (const milestone of milestones.data) {
              const issues = await github.rest.issues.listForRepo({
                owner: context.repo.owner,
                repo: context.repo.repo,
                milestone: milestone.number,
                state: 'all'
              });
              
              const totalIssues = issues.data.length;
              const closedIssues = issues.data.filter(issue => issue.state === 'closed').length;
              const progress = totalIssues > 0 ? (closedIssues / totalIssues * 100).toFixed(2) : 0;
              
              report += `## ${milestone.title}\n`;
              report += `- Progress: ${progress}% (${closedIssues}/${totalIssues})\n`;
              report += `- Due: ${milestone.due_on ? new Date(milestone.due_on).toDateString() : 'No due date'}\n\n`;
            }
            
            // Create issue with the report
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Weekly Progress Report - ${new Date().toDateString()}`,
              body: report,
              labels: ['type:docs', 'status:report']
            });
```

### 8.2 Dashboard Creation

- [ ] **Create project dashboard**
  - Set up GitHub Pages site for visualizing project progress
  - Create burndown charts and component progress visualizations
  - Display risk assessments and blocker information

## 9. Implementation Plan

### 9.1 Phase 1: Initial Setup (1-2 days)

1. Clean up existing issues and PRs
2. Create labeling system
3. Set up project board structure
4. Create issue templates

### 9.2 Phase 2: Automation Setup (2-3 days)

1. Implement GitHub Actions for issue/PR management
2. Configure project board automation
3. Set up component flag tracking
4. Create progress reporting workflows

### 9.3 Phase 3: Issue Creation (1-2 days)

1. Create weekly milestones
2. Generate issues from refactoring checklist
3. Establish dependencies between issues
4. Assign initial priorities and estimates

### 9.4 Phase 4: Ongoing Management

1. Run weekly progress reviews
2. Update project board with current status
3. Adjust priorities and assignments as needed
4. Maintain and refine automation rules

## 10. Best Practices for Team Usage

### 10.1 Issue Management Guidelines

- Always link PRs to issues using `Fixes #issue-number` or `Resolves #issue-number` in PR description
- Keep issue descriptions and acceptance criteria up-to-date
- Use component flags in commit messages consistently
- Add comments to issues when blockers are encountered
- Update issue status when starting work (assign to yourself)

### 10.2 Pull Request Guidelines

- Use the PR template
- Reference the issue(s) being addressed
- Keep PRs focused on a single component or feature
- Request reviews from appropriate team members
- Address all review comments before merging

### 10.3 Communication Guidelines

- Use issue comments for technical discussions
- Update progress in weekly team meetings
- Tag relevant team members when blockers arise
- Document important decisions in issues or wiki

## Conclusion

This GitHub project management plan provides a comprehensive framework for organizing and tracking the Vidst refactoring project. By implementing these practices and automation, the team will have clear visibility into progress, component status, and project health throughout the refactoring effort.

The combination of structured issues, component flags, and automated tracking will ensure that the project stays on schedule and that all team members have a clear understanding of priorities and dependencies.
