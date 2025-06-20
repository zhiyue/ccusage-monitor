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
- **All Python code MUST pass ruff checks** - run `ruff check` before committing
  - Use `ruff check --fix` to auto-fix issues when safe
  - Configure ruff settings in pyproject.toml
- Use type hints where beneficial
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

### Git Workflow
- Write clear commit messages
- Use conventional commits when possible
- **NEVER use `git add .` or `git add -A`** - only add files you modified in the current task
- Always explicitly add each file with `git add <filename>`
- Review changes with `git status` before staging
- Always test before committing

## Dependencies

### Runtime
- Python 3.8+
- pytz (timezone handling)
- ccusage (Node.js CLI - external dependency)

### Development
- pytest & pytest-cov (testing)
- ruff (linting and code quality - primary tool)
- black (code formatting)
- mypy (type checking)
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

### Linting with Ruff
```bash
# Check all Python files
ruff check .

# Auto-fix safe issues
ruff check --fix .

# Check specific file
ruff check ccusage_monitor.py

# Show all available rules
ruff rule --all
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