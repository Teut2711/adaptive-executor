import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Adaptive Executor'
copyright = '2024, Teut2711'
author = 'Teut2711'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_baseurl = 'https://Teut2711.github.io/adaptive-executor/'

html_meta_tags = {
    'description': 'Adaptive Executor - Python thread pool executor with dynamic scaling policies based on time, CPU, and memory usage',
    'keywords': 'python, threading, concurrency, executor, adaptive, scaling, thread pool, scheduler, performance',
    'author': 'Teut2711',
    'viewport': 'width=device-width, initial-scale=1.0',
    'og:title': 'Adaptive Executor - Dynamic Thread Pool Scaling',
    'og:description': 'Python library for adaptive thread pool execution with intelligent scaling based on system resources and time-based policies',
    'og:url': 'https://Teut2711.github.io/adaptive-executor',
    'og:type': 'website',
    'og:site_name': 'Adaptive Executor',
    'twitter:card': 'summary_large_image',
    'twitter:title': 'Adaptive Executor - Dynamic Thread Pool Scaling',
    'twitter:description': 'Python library for adaptive thread pool execution with intelligent scaling',
    'robots': 'index, follow',
    'googlebot': 'index, follow',
}

html_context = {
    'meta_tags': html_meta_tags,
    'display_github': True,
    'github_user': 'Teut2711',
    'github_repo': 'adaptive-executor',
    'github_version': 'main',
}

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
