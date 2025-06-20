# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.4] - 2025-06-20

### Fixed
- GitHub Actions workflows now handle existing packages gracefully
- Added --check-url to uv publish to detect conflicts before upload
- Improved error handling in publish workflows
- Fixed workflow badges in README

### Changed
- Split publish workflow into separate test and release workflows
- Enhanced package hash checking with better error messages

## [0.0.3] - 2025-06-20

### Added
- GitHub Actions workflow for automated PyPI publishing
- Support for installation via pip and uvx
- Comprehensive test suite with pytest
- Development dependencies in pyproject.toml
- This CHANGELOG file
- Makefile for development tasks
- Pre-commit configuration
- EditorConfig for code style consistency
- Detailed documentation in docs/ directory

### Changed
- Updated Python requirement from 3.6+ to 3.8+
- Simplified README to be more concise
- Moved detailed documentation to separate files
- Enhanced CONTRIBUTING guide with modern Python practices
- Updated project URLs to new GitHub repository
- Moved screenshot from doc/ to docs/

### Fixed
- Various documentation inconsistencies
- GitHub Actions workflow version conflicts

## [0.0.2] - 2025-06-20

### Added
- First release to PyPI
- Automatic package building and distribution

### Changed
- Project renamed to `ccusage-monitor` for PyPI
- Updated all documentation to reflect new package name

## [0.0.1] - 2025-06-20

### Added
- Initial release with core functionality
- Real-time token usage monitoring
- Beautiful terminal UI with progress bars
- Smart burn rate predictions
- Auto-detection of token limits
- Support for Pro, Max5, and Max20 plans
- Customizable reset times and timezones
- Cross-platform support (Linux, macOS, Windows)

### Contributors
- Initial implementation by Maciek (maciek@roboblog.eu)
- PyPI packaging and improvements by zhiyue (cszhiyue@gmail.com)

[Unreleased]: https://github.com/zhiyue/ccusage-monitor/compare/v0.0.4...HEAD
[0.0.4]: https://github.com/zhiyue/ccusage-monitor/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/zhiyue/ccusage-monitor/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/zhiyue/ccusage-monitor/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/zhiyue/ccusage-monitor/releases/tag/v0.0.1