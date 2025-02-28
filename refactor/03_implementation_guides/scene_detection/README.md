# Scene Detection Implementation Guides

This directory contains implementation guides for the scene detection components of the Vidst project. These guides provide detailed instructions for various scene detection implementations as part of our refactoring strategy.

## Key Components

As outlined in the Component Evaluation Matrix, we are transitioning from a custom OpenCV-based scene detection implementation to the Twelve Labs API which offers higher accuracy and simpler implementation.

| Component | Current Implementation | API Alternative | Priority Score | Recommendation |
|-----------|------------------------|-----------------|----------------|----------------|
| Scene Detection | Custom OpenCV-based implementation | Twelve Labs Marengo/Pegasus | 29 | Replace |

## Implementation Guides

- [Twelve Labs Scene Detection (Issue #108)](./twelve_labs_scene_detection_issue_108.md) - Detailed implementation instructions for replacing our custom implementation with Twelve Labs API.
- [Twelve Labs Scene Detection (Simplified)](./twelve_labs_scene_detection_issue_108_simplified.md) - Streamlined implementation instructions focused on core requirements.
- [Twelve Labs Scene Detection (Updated API)](./twelve_labs_scene_detection_issue_108_updated.md) - Implementation using the latest Twelve Labs API structure.

## Related Documents

- [Vidst API Integration Strategy](../vidst_api_integration_strategy.md)
- [Twelve Labs Integration Strategy](../vidst_twelve_labs_integration_strategy.md)
- [Vidst Refactoring Master Plan](../../02_planning/vidst_refactoring_master_plan.md)
