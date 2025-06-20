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
- Use type hints where beneficial
- Keep functions focused and testable
- Prefer descriptive variable names

### Testing
- Use pytest for all tests
- Maintain >45% coverage (current: 48%)
- Test core functions thoroughly
- Mock external dependencies

### Git Workflow
- Write clear commit messages
- Use conventional commits when possible
- Don't use `git add .` - add specific files
- Always test before committing

## Dependencies

### Runtime
- Python 3.8+
- pytz (timezone handling)
- ccusage (Node.js CLI - external dependency)

### Development
- pytest & pytest-cov (testing)
- black, flake8, mypy (code quality)
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

## Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ccusage_monitor

# Run specific test file
pytest tests/test_ccusage_monitor.py -v
```

## Common Tasks

### Adding New Features
1. Write tests first (TDD approach)
2. Implement feature in ccusage_monitor.py
3. Update documentation if needed
4. Run tests to ensure nothing breaks

### Fixing Bugs
1. Reproduce the issue
2. Write a test that fails
3. Fix the bug
4. Ensure test passes

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

## Future Improvements

See ROADMAP.md for planned features. Current implementation is intentionally simple and focused on core functionality.