import os
import sys
import re

sys.path.insert(0, os.path.abspath("../src"))

def get_version():
    # 1. Try getting version from installed package metadata
    try:
        from importlib.metadata import version
        return version("adaptive-executor")
    except Exception:
        pass

    # 2. Fallback to manual parsing of pyproject.toml
    try:
        import re
        with open(os.path.abspath("../pyproject.toml"), "r", encoding="utf-8") as f:
            content = f.read()
            project_section = re.search(r"\[project\](.*?)(?=\n\[|$)", content, re.DOTALL)
            if project_section:
                version_match = re.search(r'version\s*=\s*"(.*?)"', project_section.group(1))
                if version_match:
                    return version_match.group(1)
    except Exception:
        pass
    return "0.1.0"

project = "Adaptive Executor"
copyright = "2024, Teut2711"
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
    "github_version": "master/",
    "conf_py_path": "/docs/",
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
