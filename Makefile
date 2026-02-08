.PHONY: help install install-dev test lint format type-check docs clean build upload publish

help:
	@echo "Available commands:"
	@echo "  install      Install package"
	@echo "  install-dev  Install package with dev dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  type-check   Run type checking"
	@echo "  docs         Build documentation"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload       Upload to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	flake8 adaptive_executor tests
	mypy adaptive_executor

format:
	black adaptive_executor tests
	isort adaptive_executor tests

type-check:
	mypy adaptive_executor

docs:
	cd docs && make html

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf docs/_build/

build: clean
	python -m build

upload: build
	python -m twine upload dist/*
