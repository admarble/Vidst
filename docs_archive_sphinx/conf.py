"""Sphinx configuration for Video Understanding AI documentation."""

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock


class Mock(MagicMock):
    """Mock class that returns MagicMock for all attribute access."""

    @classmethod
    def __getattr__(cls, name):
        return MagicMock()


MOCK_MODULES = {
    "numpy": Mock(),
    "numpy.array_api": Mock(),
    "numpy.core": Mock(),
    "numpy.core.multiarray": Mock(),
    "torch": Mock(),
    "cv2": Mock(),
    "PIL": Mock(),
    "sklearn": Mock(),
    "tensorflow": Mock(),
    "src": Mock(),
    "src.storage": Mock(),
    "src.core": Mock(),
    "src.ai": Mock(),
}

sys.modules.update(MOCK_MODULES)

# Add paths to Python path - order matters here
sys.path.insert(0, os.path.abspath("."))  # Add current directory
sys.path.insert(0, os.path.abspath("_ext"))  # Add _ext directory
sys.path.insert(0, os.path.abspath(".."))  # Add parent directory
sys.path.insert(0, os.path.abspath("../src"))  # Add src directory

# Project information
project = "Video Understanding AI"
copyright = f"{datetime.now().year}, Your Organization"
author = "Your Organization"

# LaTeX configuration
latex_documents = []
latex_elements = {}
latex_engine = "pdflatex"  # Required even if we don't use it

# Only build HTML
builders = ["html"]

# The full version, including alpha/beta/rc tags
release = "0.1.0"

# Extensions
extensions = [
    "sphinx.ext.autodoc",  # Automatic API documentation
    "sphinx.ext.napoleon",  # Support for Google-style docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.githubpages",  # GitHub Pages support
    "sphinx_rtd_theme",  # Read The Docs theme
    "sphinx.ext.intersphinx",  # Link to other project's documentation
    "sphinx_autodoc_typehints",  # Better type hints support
    "myst_parser",  # Add support for Markdown
    "sphinx.ext.autosummary",  # Add autosummary support
    "sphinx.ext.coverage",  # Add coverage support
    "sphinx.ext.doctest",  # Add doctest support
    "sphinx.ext.todo",  # Add todo support
    "sphinx.ext.mathjax",  # Add math support
    "sphinx.ext.ifconfig",  # Add conditional content
]

# Warning suppression
suppress_warnings = [
    "app.add_directive",  # Suppress directive registration warnings
    "app.add_node",  # Suppress node registration warnings
    "toc.excluded",  # Suppress warnings about excluded files
    "toc.not_readable",  # Suppress warnings about unreadable files
    "ref.python",  # Suppress Python reference warnings
    "ref.any",  # Suppress any reference warnings
    "ref.doc",  # Suppress document reference warnings
    "autosummary.not_readable",  # Suppress autosummary warnings
    "autosummary.stub",  # Suppress stub warnings
]

# Make Sphinx more strict about references
nitpicky = True
nitpick_ignore = [
    ("py:class", "typing.Any"),
    ("py:class", "typing.Optional"),
    ("py:class", "typing.Union"),
    ("py:class", "typing.List"),
    ("py:class", "typing.Dict"),
    ("py:class", "typing.Tuple"),
    ("py:class", "typing.Callable"),
    ("py:class", "typing.Iterator"),
    ("py:class", "typing.Generator"),
    ("py:class", "typing.TypeVar"),
    ("py:class", "typing.Generic"),
    ("py:class", "pathlib._local.Path"),
    ("py:class", "numpy.float32"),
    ("py:class", "numpy.ndarray"),
    ("py:class", "Dictionary containing"),
    ("py:class", "Optional[str]"),
    ("py:class", "Tuple containing"),
    ("py:class", "Dict[str, Dict[str, Any]]"),
    ("py:class", "Dict[str, Any]"),
    ("py:class", "datetime"),
    ("py:class", "T"),
    ("py:class", "Path"),
    ("py:class", "ABC"),
    ("py:class", "Enum"),
]

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__,__dict__,__module__,__annotations__",
    "show-inheritance": True,
    "inherited-members": True,
    "no-index": True,  # Add this to prevent duplicate object descriptions
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# Add type aliases
napoleon_type_aliases = {
    "array": ":class:`numpy.ndarray`",
    "ndarray": ":class:`numpy.ndarray`",
    "tensor": ":class:`torch.Tensor`",
}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "torch": ("https://pytorch.org/docs/stable/", None),
    "opencv": ("https://docs.opencv.org/4.x/", None),  # Updated OpenCV version
}
intersphinx_disabled_domains = []  # Enable all domains
intersphinx_timeout = 30

# Autosummary settings
AUTOSUMMARY_GENERATE = True
AUTOSUMMARY_IMPORTED_MEMBERS = False
AUTOSUMMARY_GENERATE_OVERWRITE = True
ADD_MODULE_NAMES = False

# Mock ALL modules
autodoc_mock_imports = [
    "numpy",
    "numpy.array_api",
    "numpy.core",
    "numpy.core.multiarray",
    "torch",
    "cv2",
    "PIL",
    "sklearn",
    "tensorflow",
    "src",
    "src.storage",
    "src.core",
    "src.ai",
    "src.storage.cache",
    "src.storage.vector",
    "src.storage.metadata",
    "src.core.config",
    "src.core.processing",
    "src.ai.models",
]

# Suppress ALL warnings
suppress_warnings.extend(
    [
        "autosummary",
        "app.add_directive",
        "app.add_node",
        "toc.excluded",
        "toc.not_readable",
        "ref.python",
        "ref.any",
        "ref.doc",
        "ref.ref",
        "ref.numref",
        "ref.keyword",
        "ref.citation",
        "ref.footnote",
        "ref.doc",
        "ref.python",
        "misc.highlighting_failure",
        "toc.circular",
        "toc.secnum",
        "epub.unknown_project_files",
        "epub.duplicated_toc_entry",
        "autosummary.not_readable",
        "autosummary.stub",
    ]
)

# Exclude patterns
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**/.ipynb_checkpoints",
    "**/__pycache__",
    "**/._*",
]

# Extend exclude patterns
exclude_patterns.extend(
    [
        "_autosummary",
        "_build",
        "Thumbs.db",
        ".DS_Store",
        "**/.ipynb_checkpoints",
        "**/__pycache__",
        "**/._*",
        "_autosummary/src.*",
    ]
)

# Source suffix
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# MyST-Parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "tasklist",
]

# Templates and static paths
templates_path = ["_templates"]
html_static_path = ["_static"]

# HTML theme settings
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "both",
    "style_external_links": True,
    "style_nav_header_background": "#2980B9",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
}

# CSS/JS files
html_css_files = [
    "css/custom.css",
]

html_js_files = [
    "js/accessibility.js",
]

# Meta tags
html_meta = {
    "charset": "utf-8",
    "viewport": "width=device-width, initial-scale=1.0",
    "description": "Video Understanding AI Documentation",
    "author": author,
    "keywords": "video understanding, AI, documentation, machine learning",
    "robots": "index, follow",
}

# HTML settings
html_additional_pages = {}
html_secnumber_suffix = ". "
html_title_template = "%(title)s"
html_use_index = True
html_domain_indices = True
html_copy_source = False
html_show_sourcelink = False

# Code highlighting
pygments_style = "sphinx"
highlight_language = "python3"
highlight_options = {"default_lang": "python3", "guess_lang": False}

# Accessibility
html_show_sphinx = False

# Custom context
html_context = {
    "display_github": False,
    "show_sphinx": False,
    "show_source": False,
    "theme_display_version": False,
}

# Search settings
html_search_language = "en"
html_search_scorer = "_static/scorer.js"


def setup(app):
    """Set up Sphinx application."""
    app.add_js_file("js/accessibility.js")
    app.add_css_file("css/custom.css")

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
