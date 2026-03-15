import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("../src"))

def get_version():
    """
    Retrieves the version from installed metadata or pyproject.toml.
    Ensures the docs don't crash if the package isn't installed in CI.
    """
    # 1. Try metadata (works if 'pip install .' was run in CI)
    try:
        from importlib.metadata import PackageNotFoundError, version
        return version("adaptive-executor")
    except (ImportError, PackageNotFoundError):
        pass

    # 2. Fallback: Parse pyproject.toml directly
    try:
        # Locate pyproject.toml relative to this conf.py file
        # (Assuming: /repo/docs/conf.py -> /repo/pyproject.toml)
        pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Look for version = "x.y.z" inside the [project] section
                match = re.search(
                    r'\[project\].*?version\s*=\s*"(.*?)"',
                    content,
                    re.DOTALL,
                )
                if match:
                    return match.group(1)
    except Exception as e:
        # If we get here, something is fundamentally wrong with the file path
        print(f"Warning: Could not parse pyproject.toml: {e}")
        
    return "0.0.0-dev" # Distinctive fallback so you know it's failing

project = "Adaptive Executor"
copyright = "2026, Teut2711"
author = "Teut2711"
release = get_version()
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_theme_options = {
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "blob",
}

html_baseurl = os.environ.get("PAGES_URL", "")

html_copy_source = False
html_show_sourcelink = False
html_show_sphinx = False

html_meta_tags = {
    "description": (
        "Adaptive Executor - Python thread pool executor with dynamic "
        "scaling policies based on time, CPU, and memory usage"
    ),
    "keywords": (
        "threading, concurrency, executor, adaptive, scaling, "
        "scheduler, thread, pool, executor"
    ),
    "author": "Teut2711",
    "viewport": "width=device-width, initial-scale=1.0",
    "og:title": "Adaptive Executor - Dynamic Thread Pool Scaling",
    "og:description": (
        "Python library for adaptive thread pool execution with "
        "intelligent scaling based on system resources and time-based policies"
    ),
    "og:url": "https://Teut2711.github.io/adaptive-executor",
    "og:type": "website",
    "og:site_name": "Adaptive Executor",
    "twitter:card": "summary_large_image",
    "twitter:title": "Adaptive Executor - Dynamic Thread Pool Scaling",
    "twitter:description": (
        "Python library for adaptive thread pool execution with intelligent scaling"
    ),
    "robots": "index, follow",
    "googlebot": "index, follow",
}

html_context = {
    "meta_tags": html_meta_tags,
    "display_github": True,
    "github_user": "Teut2711",
    "github_repo": "adaptive-executor",
    "github_version": "master/",      # Added trailing slash
    "conf_py_path": "docs/",          # Standard path
}

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
