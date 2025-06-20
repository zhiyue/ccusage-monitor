# Claude Project Context

This document helps Claude understand the ccusage-monitor project structure and conventions.

## Project Overview

**Name**: ccusage-monitor  
**Type**: Python CLI Tool  
**Purpose**: Real-time monitoring of Claude AI token usage with visual progress bars and predictions

## Key Files

- `ccusage_monitor.py` - Main monitoring script with all core functionality
- `pyproject.toml` - Modern Python packaging configuration  
- `requirements.txt` - Runtime dependencies (only pytz)
- `requirements-dev.txt` - Development dependencies including pytest

## Project Structure

```
ccusage-monitor/
├── ccusage_monitor.py    # Main script
├── tests/               # Test suite
│   ├── test_ccusage_monitor.py
│   └── test_display_functions.py
├── .github/workflows/   # CI/CD
│   ├── publish.yml     # PyPI publishing
│   └── test.yml        # Automated testing
└── docs/               # Documentation
```

## Code Conventions

### Python Style
- Follow PEP 8
- **All Python code MUST pass ruff checks and formatting** - run before committing:
  - Use `ruff check --fix . && ruff format .` to fix issues and format code
  - This ensures consistent style across all Python files
  - Ruff automatically uses settings from `pyproject.toml`:
    - Line length: 120 characters
    - Target Python version: 3.8+
    - Enabled rules: E, F, I, N, UP, B, C4, SIM
    - Quote style: double quotes
    - Indent style: spaces
- **Write code with static typing in mind (Pyright-compliant)**:
  - Add type annotations to ALL function signatures
  - Use type hints for variables when type is not obvious
  - Prefer explicit types over `Any`
  - Use `Protocol` for structural typing
  - Use `TypedDict` for dictionary structures
  - Use `Literal` for string enums
  - Use `Union` or `|` (Python 3.10+) for multiple types
  - Use `Optional[T]` or `T | None` for nullable types
  - Ensure code passes `pyright` with zero errors
- Keep functions focused and testable
- Prefer descriptive variable names
- **Keep Python files under 300 lines** - refactor larger files into modules
  - If a file exceeds 300 lines, split it into logical modules
  - Each module should have a single, clear responsibility

### Testing (TDD Approach)
- **ALWAYS write tests BEFORE writing code** (Test-Driven Development)
- Follow the TDD cycle: Red → Green → Refactor
  1. Write a failing test first
  2. Write minimal code to make the test pass
  3. Refactor while keeping tests green
- Use pytest for all tests
- Maintain >45% coverage (current: 48%)
- Test core functions thoroughly
- Mock external dependencies
- **CRITICAL: Always update tests when modifying code**:
  - If you rename functions, variables, or modules → update test imports and references
  - If you change function signatures → update test calls
  - If you refactor code structure → ensure tests still pass
  - Run `pytest` after ANY code changes to verify nothing is broken
  - Example: When renaming `_cache` to `cache`, update `from cache import _cache` to `from cache import cache` in tests

### Git Workflow
- Write clear commit messages
- Use conventional commits when possible
- **NEVER use `git add .` or `git add -A`** - only add files you modified in the current task
- Always explicitly add each file with `git add <filename>`
- Review changes with `git status` before staging
- Always test before committing
- **ALWAYS run `ruff check --fix . && ruff format .` before committing** to ensure code quality:
  - `ruff check --fix` auto-fixes linting issues (imports, unused variables, etc.)
  - `ruff format` ensures consistent code formatting
  - If ruff reports issues that can't be auto-fixed, manually fix them
- **ALWAYS run `mypy` before committing** to ensure type safety
  - Fix all type errors reported by mypy
  - Add appropriate type hints to functions and variables
  - Only use `# type: ignore` when absolutely necessary with clear explanation
- **ALWAYS run `pyright` before committing** for advanced type checking
  - Pyright provides stricter type checking than mypy
  - Fix all errors and warnings reported by pyright
  - Use type annotations and protocols for better type safety

## Tool Configuration

All development tools are configured in `pyproject.toml`:

### Ruff Configuration
- **Line length**: 120 characters (longer than Black's 88 for better readability)
- **Target Python**: 3.8+ (ensures compatibility)
- **Lint rules**:
  - E: pycodestyle errors
  - F: pyflakes (undefined names, imports)
  - I: isort (import sorting)
  - N: pep8-naming (naming conventions)
  - UP: pyupgrade (Python version-specific updates)
  - B: flake8-bugbear (bug detection)
  - C4: flake8-comprehensions (list/dict comprehension)
  - SIM: flake8-simplify (code simplification)
- **Format settings**:
  - Double quotes for strings
  - Space indentation
  - Auto line endings (LF on Unix, CRLF on Windows)

### MyPy Configuration
- **Python version**: 3.8
- **Strict mode**: warn on Any returns, unused configs
- **Import handling**: ignore missing imports for external packages

### Pyright Configuration
- **Type checking mode**: strict
- **Python version**: 3.8+
- **Key features**:
  - Better type inference than mypy
  - Support for type guards and narrowing
  - Advanced protocol checking
  - Better IDE integration
- **Usage**: `pyright` or `pyright ccusage_monitor/`

### Other Tools
- **Black**: Line length 88 (not actively used, ruff format is preferred)
- **isort**: Black-compatible profile (handled by ruff)
- **pytest**: Verbose output, short tracebacks
- **coverage**: 98% precision, show missing lines

## Dependencies

### Virtual Environment Setup
- **ALWAYS activate virtual environment before pip install**:
  ```bash
  pyenv activate cc  # or your virtual environment name
  ```
- Never install packages globally
- This ensures clean, isolated development environment

### Runtime
- Python 3.8+
- pytz (timezone handling)
- ccusage (Node.js CLI - external dependency)

### Development
- pytest & pytest-cov (testing)
- ruff (linting and code quality - primary tool)
- black (code formatting)
- mypy (type checking)
- types-pytz (type stubs for pytz)
- GitHub Actions (CI/CD)

## Key Functions

### Core Monitoring
- `run_ccusage()` - Execute ccusage CLI and parse JSON
- `calculate_hourly_burn_rate()` - Calculate token consumption rate
- `get_next_reset_time()` - Determine when tokens reset
- `get_token_limit()` - Get limit based on plan type

### Display Functions
- `create_token_progress_bar()` - Visual token usage bar
- `create_time_progress_bar()` - Time remaining bar
- `format_time()` - Human-readable time formatting
- `print_header()` - Styled terminal header

## Quality Check Commands

### Linting and Formatting with Ruff
```bash
# Complete code quality check (recommended)
# Ruff automatically finds and uses pyproject.toml in the project root
ruff check --fix . && ruff format .

# Explicitly specify config file (optional, same result)
ruff check --config pyproject.toml --fix . && ruff format --config pyproject.toml .

# Individual commands:
# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .

# Check specific file
ruff check ccusage_monitor.py
ruff format ccusage_monitor.py

# Show current configuration (merged from pyproject.toml)
ruff check --show-settings

# Show all available rules
ruff rule --all
```

### Type Checking with MyPy
```bash
# Check all Python files
mypy .

# Check specific module
mypy ccusage_monitor/

# Show error codes
mypy --show-error-codes .

# Strict mode
mypy --strict ccusage_monitor/
```

### Type Checking with Pyright
```bash
# Check all Python files
pyright

# Check specific module
pyright ccusage_monitor/

# Check specific file
pyright ccusage_monitor/main.py

# Watch mode (re-check on file changes)
pyright --watch

# Generate type stubs
pyright --createstub ccusage_monitor
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ccusage_monitor

# Run specific test file
pytest tests/test_ccusage_monitor.py -v
```

### Code Formatting
```bash
# Format with black
black .

# Check formatting without changing
black --check .
```

## Pre-Commit Checklist

Before committing any code changes:

1. **Run ruff to check and format code**:
   ```bash
   # Complete code quality check (lint + format)
   ruff check --fix . && ruff format .
   ```

2. **Run mypy for type checking**:
   ```bash
   # Check all Python files
   mypy .
   
   # Check specific module
   mypy ccusage_monitor/
   ```
   - Fix any type errors reported by mypy
   - Add type hints where needed
   - Use `# type: ignore` only when absolutely necessary with explanation

3. **Run pyright for advanced type checking**:
   ```bash
   # Check all Python files
   pyright
   ```
   - Fix all errors and warnings
   - Ensure proper use of protocols and type annotations
   - Pyright is stricter than mypy and catches more issues

4. **Run tests to ensure nothing is broken**:
   ```bash
   pytest
   ```

5. **Check test coverage** (optional but recommended):
   ```bash
   pytest --cov=ccusage_monitor
   ```

6. **Stage only the files you modified**:
   ```bash
   git add <specific-file>
   # Never use git add . or git add -A
   ```

7. **Review your changes**:
   ```bash
   git status
   git diff --cached
   ```

8. **Commit with a clear message**:
   ```bash
   git commit -m "type: description"
   ```

## Common Tasks

### Adding New Features (TDD Required)
1. **Write failing tests FIRST** - define expected behavior
2. Run tests to confirm they fail (Red phase)
3. Implement minimal code in ccusage_monitor.py to pass tests (Green phase)
4. Refactor code while keeping tests green
5. Update documentation if needed
6. Run all tests to ensure nothing breaks

### Fixing Bugs (TDD Required)
1. Reproduce the issue
2. **Write a test that fails** due to the bug
3. Run test to confirm it fails (Red phase)
4. Fix the bug with minimal changes (Green phase)
5. Refactor if needed
6. Ensure all tests pass

### Updating Dependencies
1. Update requirements.txt or requirements-dev.txt
2. Test thoroughly
3. Update pyproject.toml if needed

## Important Notes

- The main loop runs indefinitely - use Ctrl+C to exit gracefully
- Terminal width should be 80+ characters for proper display
- Default timezone is Europe/Warsaw
- Token limits: Pro (7k), Max5 (35k), Max20 (140k)
- Sessions last exactly 5 hours
- **NOTE**: ccusage_monitor.py currently has 442 lines and needs refactoring to comply with the 300-line rule

## Future Improvements

See ROADMAP.md for planned features. Current implementation is intentionally simple and focused on core functionality.