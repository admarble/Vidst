"""Sphinx extension for accessibility features."""


def setup(app):
    """Set up accessibility features."""
    app.add_js_file("js/accessibility.js")
    app.add_css_file("css/custom.css")

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
