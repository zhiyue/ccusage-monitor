.PHONY: help install dev test lint format clean build publish

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    Install the package in production mode"
	@echo "  make dev        Install in development mode with dev dependencies"
	@echo "  make test       Run tests with pytest"
	@echo "  make lint       Run linting checks"
	@echo "  make format     Format code with black and isort"
	@echo "  make clean      Clean build artifacts"
	@echo "  make build      Build distribution packages"
	@echo "  make publish    Publish to PyPI (requires credentials)"

# Install production dependencies
install:
	pip install -e .

# Install development dependencies
dev:
	pip install -e .
	pip install pytest pytest-cov black isort mypy ruff

# Run tests
test:
	pytest -v --cov=ccusage_monitor --cov-report=term-missing

# Run linting
lint:
	@echo "Running ruff..."
	ruff check ccusage_monitor.py
	@echo "Running mypy..."
	mypy ccusage_monitor.py --ignore-missing-imports
	@echo "Checking black formatting..."
	black --check ccusage_monitor.py
	@echo "Checking import order..."
	isort --check-only ccusage_monitor.py

# Format code
format:
	black ccusage_monitor.py
	isort ccusage_monitor.py

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Build distribution packages
build: clean
	uv build

# Publish to PyPI
publish: build
	@echo "Publishing to PyPI..."
	@echo "Make sure UV_PUBLISH_USERNAME and UV_PUBLISH_PASSWORD are set"
	uv publish

# Quick test and lint
check: test lint

# Development workflow - format, test, and lint
ready: format test lint
	@echo "Code is ready for commit!"