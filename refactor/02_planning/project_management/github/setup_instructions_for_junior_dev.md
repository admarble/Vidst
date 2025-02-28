# Setting Up Initial Issues for Vidst GitHub Project Board

This guide will walk you through the process of setting up the initial set of issues for the Vidst project board using the GitHub API and our custom issue creator script.

## Prerequisites

1. Make sure you have:
   - Node.js installed on your computer
   - GitHub personal access token with repo permissions
   - Access to the Vidst repository on GitHub

2. Relevant files to review before starting:
   - `/refactor/02_planning/project_management/github/vidst_tagging_convention.md` - Understand our tagging system
   - `/refactor/02_planning/project_management/github/github_api_issue_creator.js` - The issue creator script
   - `/refactor/02_planning/execution/vidst_refactoring_checklist.md` - The source of tasks to create issues for

## Step 1: Set Up Your Environment

1. Create a new directory for the script:

   ```bash
   mkdir -p ~/vidst-issue-setup
   cd ~/vidst-issue-setup
   ```

2. Initialize a new Node.js project:

   ```bash
   npm init -y
   ```

3. Install required dependencies:

   ```bash
   npm install @octokit/rest dotenv
   ```

4. Copy the issue creator script to your directory:

   ```bash
   cp /Users/tony/Documents/Vidst/refactor/02_planning/project_management/github/github_api_issue_creator.js ./
   ```

5. Create a `.env` file to store your GitHub token:

   ```bash
   touch .env
   ```

6. Edit the `.env` file to add your GitHub token:

   ```
   GITHUB_TOKEN=your_github_token_here
   ```

## Step 2: Configure the Script

1. Create a new file called `setup_issues.js`:

   ```bash
   touch setup_issues.js
   ```

2. Open `setup_issues.js` in your code editor and add the following code:

```javascript
// Import required modules
require('dotenv').config();
const issueCreator = require('./github_api_issue_creator');
const fs = require('fs');

// Update these values with your repository information
const config = {
  owner: "admarble", // Replace with your GitHub username or organization
  repo: "vidst"               // Replace with your repository name
};

// Modify the config in the issue creator script
const originalScript = fs.readFileSync('./github_api_issue_creator.js', 'utf8');
const updatedScript = originalScript
  .replace(/owner: "your-org"/, `owner: "${config.owner}"`)
  .replace(/repo: "vidst"/, `repo: "${config.repo}"`);

fs.writeFileSync('./github_api_issue_creator.js', updatedScript);

// Re-import after updating
delete require.cache[require.resolve('./github_api_issue_creator')];
const {
  createComponentIssue,
  COMPONENTS,
  PRIORITY_TAGS,
  RECOMMENDATIONS,
  WEEKS,
  PRIORITIES,
  EFFORTS,
  TYPES
} = require('./github_api_issue_creator');

// Function to create all initial issues
async function createInitialIssues() {
  try {
    console.log("Creating initial issues for Vidst project...");

    // First set of issues (Week 1)
    await createSceneDetectionIssues();
    await createDocumentationIssues();
    await createVectorStorageIssues();

    // You can add more issue creation functions here

    console.log("Initial issues created successfully!");
  } catch (error) {
    console.error("Error creating issues:", error);
  }
}

// Create Scene Detection issues
async function createSceneDetectionIssues() {
  console.log("Creating Scene Detection issues...");

  // Create Twelve Labs implementation issue
  await createComponentIssue({
    component: "SCENE_DETECTION",
    description: "Implement Twelve Labs API integration",
    currentImplementation: "Custom OpenCV-based implementation",
    apiAlternative: "Twelve Labs Marengo/Pegasus",
    priorityScore: 29,
    recommendation: "REPLACE",
    priorityTag: PRIORITY_TAGS.POC,
    pocJustification: "Required to meet 90% accuracy target for POC",
    week: "WEEK1",
    type: "FEATURE",
    priority: "HIGH",
    effort: "MEDIUM",
    acceptanceCriteria: [
      "Twelve Labs API client is implemented and configured",
      "Scene detection achieves >90% accuracy",
      "Error handling for API failures is implemented",
      "Unit tests verify API interaction"
    ],
    implementationSteps: [
      "Set up Twelve Labs API client with authentication",
      "Implement scene detection endpoint integration",
      "Create fallback mechanism for API failures",
      "Add test suite for validation"
    ],
    additionalInformation: "Twelve Labs significantly exceeds accuracy targets (94.2% vs 90% requirement) while reducing implementation complexity."
  });

  // Create fallback mechanism issue
  await createComponentIssue({
    component: "SCENE_DETECTION",
    description: "Implement fallback mechanisms for API failures",
    currentImplementation: "No current fallback implementation",
    apiAlternative: "N/A",
    priorityScore: 29,
    recommendation: "REPLACE",
    priorityTag: PRIORITY_TAGS.POC,
    pocJustification: "Essential for reliability in POC demo",
    week: "WEEK1",
    type: "FEATURE",
    priority: "MEDIUM",
    effort: "SMALL",
    acceptanceCriteria: [
      "Circuit breaker pattern is implemented",
      "Fallback to local implementation when API fails",
      "Automatic retry mechanism with exponential backoff",
      "Error events are properly logged"
    ],
    implementationSteps: [
      "Implement circuit breaker using utils/circuit_breaker.py",
      "Configure retry mechanisms with utils/retry.py",
      "Create fallback logic to use local implementation",
      "Test API failure scenarios"
    ]
  });
}

// Create Documentation issues
async function createDocumentationIssues() {
  console.log("Creating Documentation issues...");

  // Documentation consolidation issue
  await createComponentIssue({
    component: "DOCUMENTATION",
    description: "Consolidate documentation system to MkDocs",
    currentImplementation: "Dual systems (Sphinx + MkDocs)",
    apiAlternative: "N/A",
    priorityScore: 24,
    recommendation: "CONSOLIDATE",
    priorityTag: PRIORITY_TAGS.POC,
    pocJustification: "Simplification needed to maintain clear POC documentation",
    week: "WEEK1",
    type: "REFACTOR",
    priority: "HIGH",
    effort: "MEDIUM",
    acceptanceCriteria: [
      "Single documentation system (MkDocs) configured",
      "Essential content migrated from Sphinx",
      "Documentation build process streamlined",
      "Unnecessary documentation archived"
    ],
    implementationSteps: [
      "Evaluate current documentation in both systems",
      "Set up enhanced MkDocs configuration",
      "Migrate critical content from Sphinx to MkDocs",
      "Archive Sphinx configuration and unused docs",
      "Update README with new documentation instructions"
    ],
    additionalInformation: "Per scope realignment plan, documentation consolidation should be prioritized early to avoid maintenance overhead."
  });
}

// Create Vector Storage issues
async function createVectorStorageIssues() {
  console.log("Creating Vector Storage issues...");

  // Create Pinecone implementation issue
  await createComponentIssue({
    component: "VECTOR_STORAGE",
    description: "Implement Pinecone vector database integration",
    currentImplementation: "Self-hosted FAISS",
    apiAlternative: "Pinecone API",
    priorityScore: 31,
    recommendation: "REPLACE",
    priorityTag: PRIORITY_TAGS.POC,
    pocJustification: "Required for simplified and reliable vector storage in POC",
    week: "WEEK2",
    type: "FEATURE",
    priority: "HIGH",
    effort: "MEDIUM",
    acceptanceCriteria: [
      "Pinecone client is implemented and configured",
      "Vector operations (add, search, delete) are implemented",
      "Performance meets or exceeds current FAISS implementation",
      "Integration tests verify functionality"
    ],
    implementationSteps: [
      "Set up Pinecone client with authentication",
      "Implement vector operations interface",
      "Create migration utility for existing vectors",
      "Add batch operations support",
      "Implement metadata filtering"
    ],
    additionalInformation: "Eliminates infrastructure management while improving capabilities. Free tier available for POC."
  });

  // Add more Vector Storage issues as needed
}

// Function to add additional component issues
// You can create more functions similar to the ones above for other components

// Run the script
createInitialIssues();
```

3. Update the repository information in the script:
   - Replace `"your-organization"` with your GitHub username or organization name
   - Verify "vidst" is the correct repository name or update it as needed

## Step 3: Run the Script to Create Initial Issues

1. Run the script to create the initial set of issues:

   ```bash
   node setup_issues.js
   ```

2. The script will create:
   - Scene Detection issues for Week 1
   - Documentation consolidation issue for Week 1
   - Vector Storage issues for Week 2

3. Verify the issues are created correctly in your GitHub repository.

## Step 4: Creating Additional Issues

To create additional issues based on the refactoring checklist, follow these steps:

1. Review the refactoring checklist at `/refactor/02_planning/execution/vidst_refactoring_checklist.md`

2. Create new issue creation functions in `setup_issues.js` for each component, following the pattern of the existing functions.

3. For each major section in the checklist, create corresponding issues with:
   - Appropriate component assignment
   - Correct week label
   - POC/OPT/FUT priority tags based on the updated checklist
   - Relevant acceptance criteria and implementation steps

4. Update the `createInitialIssues()` function to call your new issue creation functions.

5. Run the script again to create the additional issues:

   ```bash
   node setup_issues.js
   ```

## Step 5: Setting Up the Project Board

After creating the issues, set up the GitHub project board:

1. Go to your GitHub repository
2. Click on "Projects" tab
3. Click "New project"
4. Select "Board" as the template
5. Name the project "Vidst Refactoring"
6. Add columns:
   - Backlog
   - Scheduled (Week 1-6)
   - In Progress
   - Review
   - Testing
   - Done

7. Add all your created issues to the appropriate columns:
   - Week 1 issues should go in "Scheduled (Week 1-6)"
   - All other issues should go in "Backlog"

## Example Issue Creation for Other Components

Here's an example of how to create issues for another component (Natural Language Querying):

```javascript
// Create Natural Language Querying issues
async function createNLQueryingIssues() {
  console.log("Creating Natural Language Querying issues...");

  // Implementation issue
  await createComponentIssue({
    component: "NL_QUERYING",
    description: "Implement Twelve Labs Semantic Search integration",
    currentImplementation: "Backend exists, interface missing",
    apiAlternative: "Twelve Labs Semantic Search",
    priorityScore: 30,
    recommendation: "REPLACE",
    priorityTag: PRIORITY_TAGS.POC,
    pocJustification: "Core functionality required for POC demonstration",
    week: "WEEK2",
    type: "FEATURE",
    priority: "HIGH",
    effort: "MEDIUM",
    acceptanceCriteria: [
      "Twelve Labs Semantic Search API client implemented",
      "Query interface connected to API",
      "Relevance metrics meet 85% target",
      "Response time under 2 seconds for typical queries"
    ],
    implementationSteps: [
      "Implement Semantic Search API client",
      "Create query interface for natural language inputs",
      "Connect to vector storage for efficient searching",
      "Implement response formatting and ranking",
      "Add performance monitoring"
    ],
    additionalInformation: "Twelve Labs exceeds relevance target (92.3% vs 85% requirement) with significantly simpler implementation."
  });

  // Add more NL Querying issues as needed
}

// Don't forget to add this to the createInitialIssues() function
```

## Tips for Creating Effective Issues

1. **Be Specific**: Each issue should focus on a single, clear task
2. **Prioritize Correctly**: Use the Component Evaluation Matrix to set priorities
3. **Tag Appropriately**: Apply [POC], [OPT], or [FUT] tags consistently
4. **Include Acceptance Criteria**: Clear, testable criteria for completion
5. **Link to Documentation**: Reference relevant documentation or specifications
6. **Follow Week Structure**: Create issues according to the 6-week timeline

## Troubleshooting

If you encounter issues:

1. **GitHub API Rate Limits**: If you hit rate limits, add delays between API calls
2. **Authentication Errors**: Double-check your GitHub token has repo permissions
3. **Validation Errors**: Ensure all required fields for issues are provided
4. **Repository Access**: Verify you have write access to the repository

## Need Help?

If you encounter any issues or have questions, please reach out to the senior developer or project manager.
