/**
 * Vidst GitHub Issue Creator
 * 
 * This script provides utility functions for creating properly formatted issues
 * for the Vidst project using the GitHub API.
 * 
 * Usage:
 * 1. Set your GitHub token in environment variables or config
 * 2. Import this module
 * 3. Call createComponentIssue() with appropriate parameters
 */

const { Octokit } = require("@octokit/rest");

// Configure with your GitHub information
const config = {
  owner: "your-org", // Replace with your organization or username
  repo: "vidst",     // Replace with your repository name
  token: process.env.GITHUB_TOKEN // Set your token in environment variables
};

// Initialize Octokit
const octokit = new Octokit({
  auth: config.token
});

/**
 * Components enum - matches the Component Evaluation Matrix
 */
const COMPONENTS = {
  SCENE_DETECTION: {
    name: "Scene Detection",
    label: "scene-detection",
    prefix: "SCENE-DETECTION"
  },
  VECTOR_STORAGE: {
    name: "Vector Storage",
    label: "vector-storage",
    prefix: "VECTOR-STORAGE"
  },
  OCR: {
    name: "OCR (Text Extraction)",
    label: "ocr",
    prefix: "OCR"
  },
  AUDIO_TRANSCRIPTION: {
    name: "Audio Transcription",
    label: "audio-transcription",
    prefix: "AUDIO-TRANSCRIPTION"
  },
  NL_QUERYING: {
    name: "Natural Language Querying",
    label: "nl-querying",
    prefix: "NL-QUERYING"
  },
  FILE_STORAGE: {
    name: "File Storage",
    label: "file-storage",
    prefix: "FILE-STORAGE"
  },
  CACHING: {
    name: "Caching",
    label: "caching",
    prefix: "CACHING"
  },
  VIDEO_PROCESSING: {
    name: "Video Processing",
    label: "video-processing",
    prefix: "VIDEO-PROCESSING"
  },
  DOCUMENTATION: {
    name: "Documentation",
    label: "documentation",
    prefix: "DOCUMENTATION"
  }
};

/**
 * Priority tags enum
 */
const PRIORITY_TAGS = {
  POC: "POC",     // Essential for proof-of-concept
  OPT: "OPT",     // Optional enhancement
  FUT: "FUT"      // Future work (defer beyond POC)
};

/**
 * Recommendation enum
 */
const RECOMMENDATIONS = {
  REPLACE: {
    name: "Replace",
    label: "rec-replace"
  },
  COMPLETE_API: {
    name: "Complete Current + API",
    label: "rec-complete-api"
  },
  PHASE_LATER: {
    name: "Phase Later",
    label: "rec-phase-later"
  },
  KEEP_CURRENT: {
    name: "Keep Current",
    label: "rec-keep-current"
  },
  CONSOLIDATE: {
    name: "Consolidate",
    label: "rec-consolidate"
  }
};

/**
 * Week enum
 */
const WEEKS = {
  WEEK1: {
    name: "Week 1",
    label: "week-1"
  },
  WEEK2: {
    name: "Week 2",
    label: "week-2"
  },
  WEEK3: {
    name: "Week 3",
    label: "week-3"
  },
  WEEK4: {
    name: "Week 4",
    label: "week-4"
  },
  WEEK5: {
    name: "Week 5",
    label: "week-5"
  },
  WEEK6: {
    name: "Week 6",
    label: "week-6"
  }
};

/**
 * Priority level enum
 */
const PRIORITIES = {
  HIGH: {
    name: "High Priority",
    label: "priority-high"
  },
  MEDIUM: {
    name: "Medium Priority",
    label: "priority-medium"
  },
  LOW: {
    name: "Low Priority",
    label: "priority-low"
  }
};

/**
 * Effort enum
 */
const EFFORTS = {
  SMALL: {
    name: "Small (1-3 days)",
    label: "effort-small"
  },
  MEDIUM: {
    name: "Medium (3-5 days)",
    label: "effort-medium"
  },
  LARGE: {
    name: "Large (1-2 weeks)",
    label: "effort-large"
  }
};

/**
 * Type enum
 */
const TYPES = {
  FEATURE: {
    name: "Feature",
    label: "feature"
  },
  ENHANCEMENT: {
    name: "Enhancement",
    label: "enhancement"
  },
  REFACTOR: {
    name: "Refactor",
    label: "refactor"
  },
  BUG: {
    name: "Bug",
    label: "bug"
  },
  DOCUMENTATION: {
    name: "Documentation",
    label: "documentation"
  },
  INFRASTRUCTURE: {
    name: "Infrastructure",
    label: "infrastructure"
  }
};

/**
 * Status enum
 */
const STATUSES = {
  BACKLOG: {
    name: "Backlog",
    label: "backlog"
  },
  SCHEDULED: {
    name: "Scheduled",
    label: "scheduled"
  },
  IN_PROGRESS: {
    name: "In Progress",
    label: "in-progress"
  },
  BLOCKED: {
    name: "Blocked",
    label: "blocked"
  },
  REVIEW: {
    name: "In Review",
    label: "review"
  },
  TESTING: {
    name: "In Testing",
    label: "testing"
  },
  DONE: {
    name: "Done",
    label: "done"
  }
};

/**
 * Creates a properly formatted GitHub issue for a Vidst component
 * 
 * @param {Object} options - Issue options
 * @param {string} options.component - Component key from COMPONENTS enum
 * @param {string} options.description - Brief description for title and body
 * @param {string} options.currentImplementation - Current implementation description
 * @param {string} options.apiAlternative - API alternative description
 * @param {number} options.priorityScore - Priority score from component matrix
 * @param {string} options.recommendation - Recommendation key from RECOMMENDATIONS enum
 * @param {string} options.priorityTag - Priority tag from PRIORITY_TAGS enum
 * @param {string} options.pocJustification - Justification for POC inclusion
 * @param {string} options.week - Week key from WEEKS enum
 * @param {string} options.type - Type key from TYPES enum
 * @param {string} options.priority - Priority key from PRIORITIES enum
 * @param {string} options.effort - Effort key from EFFORTS enum
 * @param {string} options.status - Status key from STATUSES (defaults to BACKLOG)
 * @param {Array<string>} options.acceptanceCriteria - List of acceptance criteria
 * @param {Array<string>} options.implementationSteps - List of implementation steps
 * @param {Array<{number: number, description: string}>} options.dependencies - List of dependency issue numbers and descriptions
 * @param {string} options.additionalInformation - Any additional information for the issue
 * @returns {Promise<Object>} - Created issue data
 */
async function createComponentIssue(options) {
  // Validate required parameters
  if (!options.component || !COMPONENTS[options.component]) {
    throw new Error(`Invalid component: ${options.component}`);
  }
  
  if (!options.description) {
    throw new Error("Description is required");
  }
  
  const component = COMPONENTS[options.component];
  const recommendation = options.recommendation ? RECOMMENDATIONS[options.recommendation] : null;
  const week = options.week ? WEEKS[options.week] : null;
  const priority = options.priority ? PRIORITIES[options.priority] : PRIORITIES.MEDIUM;
  const effort = options.effort ? EFFORTS[options.effort] : EFFORTS.MEDIUM;
  const type = options.type ? TYPES[options.type] : TYPES.FEATURE;
  const status = options.status ? STATUSES[options.status] : STATUSES.BACKLOG;
  const priorityTag = options.priorityTag || PRIORITY_TAGS.POC;
  
  // Create title
  const title = `[${component.prefix}] ${options.description}`;
  
  // Create issue body using template
  const acceptanceCriteria = options.acceptanceCriteria ? 
    options.acceptanceCriteria.map(c => `- [ ] ${c}`).join('\n') : 
    "- [ ] TBD";
    
  const implementationSteps = options.implementationSteps ? 
    options.implementationSteps.map((s, i) => `${i+1}. ${s}`).join('\n') : 
    "1. TBD";
    
  const dependencies = options.dependencies ? 
    options.dependencies.map(d => `- Depends on #${d.number} (${d.description})`).join('\n') : 
    "- None";
  
  const body = `## Component Details
- **Component Name**: ${component.name}
- **Current Implementation**: ${options.currentImplementation || "TBD"}
- **API Alternative**: ${options.apiAlternative || "N/A"}
- **Priority Score**: ${options.priorityScore || "TBD"}
- **Recommendation**: ${recommendation ? recommendation.name : "TBD"}

## Task Description
${options.description}

## Acceptance Criteria
${acceptanceCriteria}

## Implementation Plan
${implementationSteps}

## POC Alignment
- **Priority Tag**: [${priorityTag}]
- **POC Justification**: ${options.pocJustification || "TBD"}

## Dependencies
${dependencies}

## Testing Strategy
- [ ] Integration tests
${options.includePerformanceTest ? '- [ ] Performance benchmark tests' : ''}
- [ ] Validation against success metrics

## Documentation Needs
- [ ] Implementation documentation
- [ ] Usage examples

## Timeline
- **Week**: ${week ? week.name : "TBD"}
- **Estimated Effort**: ${effort.name}

## Additional Information
${options.additionalInformation || ""}`;

  // Collect all relevant labels
  const labels = [
    component.label,
    type.label,
    priority.label,
    effort.label,
    status.label
  ];
  
  if (week) labels.push(week.label);
  if (recommendation) labels.push(recommendation.label);
  labels.push("component-work");

  // Create the issue
  try {
    const response = await octokit.issues.create({
      owner: config.owner,
      repo: config.repo,
      title: title,
      body: body,
      labels: labels
    });
    
    console.log(`Issue created: ${response.data.html_url}`);
    return response.data;
  } catch (error) {
    console.error("Error creating issue:", error.message);
    throw error;
  }
}

/**
 * Example usage of the createComponentIssue function
 */
async function example() {
  try {
    // Example: Create an issue for Scene Detection
    const issue = await createComponentIssue({
      component: "SCENE_DETECTION",
      description: "Implement Twelve Labs API integration",
      currentImplementation: "Custom OpenCV-based implementation",
      apiAlternative: "Twelve Labs Marengo/Pegasus",
      priorityScore: 29,
      recommendation: "REPLACE",
      priorityTag: PRIORITY_TAGS.POC,
      pocJustification: "Required to meet Scene Detection accuracy targets",
      week: "WEEK1",
      type: "FEATURE",
      priority: "HIGH",
      effort: "MEDIUM",
      acceptanceCriteria: [
        "Twelve Labs API client is implemented",
        "Scene detection achieves >90% accuracy",
        "Integration with video processing pipeline",
        "Error handling for API failures is implemented"
      ],
      implementationSteps: [
        "Set up Twelve Labs API client",
        "Implement scene detection endpoint integration",
        "Create fallback mechanism for API failures",
        "Connect to video processing pipeline",
        "Add test suite for validation"
      ],
      dependencies: [
        { number: 42, description: "API credentials setup" }
      ],
      includePerformanceTest: true,
      additionalInformation: "See the Component Evaluation Matrix for details on accuracy requirements."
    });
    
    console.log("Issue created successfully:", issue.number);
  } catch (error) {
    console.error("Example failed:", error);
  }
}

// Export functions and enums
module.exports = {
  createComponentIssue,
  COMPONENTS,
  PRIORITY_TAGS,
  RECOMMENDATIONS,
  WEEKS,
  PRIORITIES,
  EFFORTS,
  TYPES,
  STATUSES
};

// Uncomment to run example:
// example();
