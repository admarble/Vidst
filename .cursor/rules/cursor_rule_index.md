# Vidst POC Rules Index

This index provides quick access to both the simplified rules for junior developers and the original, more detailed rules. Junior developers should start with the simplified rules to maintain focus on POC scope and avoid unnecessary complexity.

## Simplified Rules for Junior Developers

These simplified rules provide focused guidance for POC implementation without unnecessary complexity:

1. [POC Scope Guidelines](./poc_scope_guidelines.md) - Essential guidelines to stay within POC scope
2. [Simplified API Integration](./simplified_api_integration.md) - Basic API integration patterns for the POC
3. [Simplified Component Structure](./simplified_component_structure.md) - Straightforward component design
4. [Simplified Testing Approach](./simplified_testing_approach.md) - Testing focused on core requirements
5. [Simplified Video Understanding](./simplified_video_understanding.md) - Core video understanding implementation for POC

## Original Detailed Rules

These rules contain more detailed guidance and patterns, which may be useful as reference but can introduce unnecessary complexity for the POC:

1. [API Integration Rules](./api_integration_rules.md) - Detailed API integration patterns
2. [Component Base Patterns](./component_base_patterns.md) - Advanced component architecture
3. [Component Factory Patterns](./component_factory_patterns.md) - Factory design patterns
4. [General Refactor Rules](./general_refactor_rules.md) - General refactoring guidelines
5. [Documentation Rules](./documentation_rules.md) - Documentation standards
6. [Testing Strategy](./testing_strategy.md) - Comprehensive testing approach
7. [Video Understanding](./video_understanding.md) - Advanced video understanding implementation (⚠️ beyond POC scope)

## Recommendation for Junior Developers

1. Start with the **Simplified Rules** which provide essential guidance while maintaining focus on POC requirements
2. Reference the **Original Rules** only when needed for specific advanced scenarios
3. Always check the [Minimum Viable Component Definitions](/Users/tony/Documents/Vidst/refactor/02_planning/vidst_minimum_viable_components.md) document to ensure implementations stay within POC scope
4. When in doubt, opt for the simpler approach that meets the minimum requirements rather than a more complex architecture

## Quick Reference Guide

| Task | Junior Developer Approach | Reference Rule |
|------|---------------------------|----------------|
| Adding new API integration | Use simple API client with basic error handling | [Simplified API Integration](./simplified_api_integration.md) |
| Creating new component | Follow basic component pattern with direct methods | [Simplified Component Structure](./simplified_component_structure.md) |
| Testing functionality | Focus on integration tests and meeting accuracy requirements | [Simplified Testing Approach](./simplified_testing_approach.md) |
| Checking feature scope | Verify against minimum viable definitions | [POC Scope Guidelines](./poc_scope_guidelines.md) |
| Implementing video understanding | Use simple patterns focused on core functionality | [Simplified Video Understanding](./simplified_video_understanding.md) |
