# Vidst Refactoring - PR Workflow

## When to apply
@semantics Applies when creating pull requests, reviewing code, and managing the PR workflow.
@userMessages ".*pull request.*" ".*PR.*" ".*code review.*" ".*merge request.*" ".*review guidelines.*"

## Pull Request Guidelines

This rule provides guidance on the pull request workflow for the Vidst refactoring project.

## PR Title Format

Follow this format for PR titles:

```
[<type>] <component>: <description>
```

Examples:
- `[Refactor] Scene Detection: Replace OpenCV with Twelve Labs API`
- `[Feature] Vector Storage: Implement Pinecone integration`
- `[Fix] OCR: Handle image format errors`
- `[Docs] API: Update documentation for Twelve Labs integration`

## PR Description Template

Use this template for PR descriptions:

```markdown
## Description

Brief description of what this PR does.

## Changes

- Added [specific component/feature]
- Updated [specific component/feature]
- Fixed [specific issue]

## Testing

- Added unit tests for [component]
- Added integration tests for [feature]
- Manual testing completed for [scenario]

## Related Issues

- Closes #123
- Addresses #456

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows project style
- [ ] All CI checks pass
```

## Creating a Pull Request

1. Push your branch to GitHub
2. Go to the repository on GitHub
3. Click "Pull Requests" and then "New Pull Request"
4. Select your branch and the target branch (usually `develop`)
5. Fill in the PR template with details
6. Assign reviewers
7. Link to related issues

## PR Size Guidelines

Keep PRs manageable:

- Aim for < 300 lines of code changes 
- Focus on a single component or feature
- If changes are large, consider splitting into multiple PRs
- Include only relevant changes (avoid mixing unrelated changes)

## Code Review Process

### Requesting Reviews

- Assign at least one reviewer with domain knowledge
- Add context in comments if certain parts need attention
- Respond to feedback promptly

### Conducting Reviews

When reviewing PRs, focus on:

1. **Correctness**: Does the code work as intended?
2. **Architecture**: Does it follow the project architecture?
3. **Test Coverage**: Are there sufficient tests?
4. **Documentation**: Is it well-documented?
5. **Error Handling**: Is error handling comprehensive?
6. **Security**: Are there any security concerns?
7. **Performance**: Any performance issues?
8. **Code Style**: Does it follow the project style?

### Providing Feedback

- Be specific and actionable
- Explain why a change is needed
- Suggest alternatives when possible
- Use GitHub's review features (comments, suggestions)
- Be constructive and respectful

## Responding to Feedback

- Address all feedback
- Respond to comments
- Make requested changes
- Re-request review when changes are complete
- Discuss if you disagree with feedback

## Merging Guidelines

Before merging, ensure:

1. PR has required approvals (minimum 1)
2. All CI checks pass
3. Feedback has been addressed
4. Branch is up to date with target branch

### Merge Options

- **Squash and merge**: Combine all commits into one (preferred for feature/fix branches)
- **Create a merge commit**: Preserve commit history (use for release branches)

## After Merging

- Delete the branch after merging
- Update any related issues
- Deploy changes if necessary
- Notify team members if relevant

## Example PR Workflow

For replacing a component with API alternative:

1. Create branch: `refactor/scene-detection/twelve-labs-integration`
2. Implement changes following architecture guidelines
3. Add tests with API mocking
4. Update documentation
5. Push changes and create PR with title:
   `[Refactor] Scene Detection: Replace OpenCV with Twelve Labs API`
6. Fill in the PR template with details
7. Address feedback from reviewers
8. Ensure CI checks pass
9. Squash and merge
10. Delete the branch

## PR Review Checklist

When reviewing PRs for API integrations:

- [ ] Proper error handling is implemented
- [ ] API credentials are properly managed
- [ ] Retry logic is included
- [ ] Circuit breaker pattern is used when appropriate
- [ ] Tests mock API calls correctly
- [ ] Documentation is complete
- [ ] Configuration is flexible
- [ ] Factory pattern is used for component creation
