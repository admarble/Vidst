# Archived RST Documentation

This directory contains the original RST (ReStructuredText) files that were used in the Sphinx documentation system before the migration to MkDocs.

## Migration Decision

As part of Issue #109 (Documentation Consolidation), we decided to migrate from Sphinx to MkDocs for the following reasons:

1. **Simplicity**: Markdown is easier to write and maintain than ReStructuredText
2. **Modern Interface**: Material theme provides a responsive, professional look
3. **Appropriate for POC**: MkDocs provides sufficient functionality without excess complexity
4. **Reduced Maintenance Burden**: Single documentation system is easier to maintain

## Archived Files

The following files have been converted to Markdown and are now available in the MkDocs documentation:

- `issues-and-resolutions.rst` -> `docs/troubleshooting/common-issues.md`
- `setup.rst` -> `docs/getting_started/setup.md`
- `api.rst` -> `docs/api/index.md`
- `guides/video-processing.rst` -> `docs/guides/video-processing.md`

## Auto-generated API Documentation

The auto-generated API documentation in the `_autosummary` directory has not been migrated, as it was deemed too detailed for the POC. Instead, we've created a high-level API reference that provides an overview of the main modules and classes.

## Future Considerations

If more detailed API documentation is needed in the future, we can:

1. Use MkDocs plugins like `mkdocstrings` to generate API documentation from docstrings
2. Create more detailed manual API documentation for key classes and functions
3. Consider migrating back to Sphinx if the documentation needs become more complex
