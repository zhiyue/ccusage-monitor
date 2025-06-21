# 🎯 Claude Code Usage Monitor

[![PyPI version](https://img.shields.io/pypi/v/ccusage-monitor?color=blue)](https://pypi.org/project/ccusage-monitor/)
[![Python Version](https://img.shields.io/pypi/pyversions/ccusage-monitor)](https://pypi.org/project/ccusage-monitor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/zhiyue/ccusage-monitor/actions/workflows/test.yml/badge.svg)](https://github.com/zhiyue/ccusage-monitor/actions/workflows/test.yml)
[![Test PyPI](https://github.com/zhiyue/ccusage-monitor/actions/workflows/publish-test.yml/badge.svg)](https://github.com/zhiyue/ccusage-monitor/actions/workflows/publish-test.yml)
[![Release](https://github.com/zhiyue/ccusage-monitor/actions/workflows/publish-release.yml/badge.svg)](https://github.com/zhiyue/ccusage-monitor/actions/workflows/publish-release.yml)
[![codecov](https://codecov.io/gh/zhiyue/ccusage-monitor/branch/main/graph/badge.svg)](https://codecov.io/gh/zhiyue/ccusage-monitor)
[![Downloads](https://img.shields.io/badge/downloads-0%2Fmonth-orange)](https://pypi.org/project/ccusage-monitor/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![GitHub stars](https://img.shields.io/github/stars/zhiyue/ccusage-monitor?style=social)](https://github.com/zhiyue/ccusage-monitor/stargazers)

**Real-time terminal monitoring tool for Claude AI token usage.** Track consumption, burn rate, and predict when tokens will run out with a beautiful, flicker-free interface.

![Claude Token Monitor Screenshot](docs/sc.png)

## ✨ Features

- 🎨 **Beautiful Rich UI** - Professional terminal interface with zero flicker *(NEW!)*
- 🔄 **Real-time monitoring** - Updates every 3 seconds with live progress bars
- 📊 **Visual progress bars** - Token and time usage at a glance
- 🔮 **Smart predictions** - AI-powered burn rate analysis and depletion forecasts
- 🤖 **Auto-detection** - Automatically detects your Claude token limits
- 📋 **Multiple plans** - Full support for Pro, Max5, Max20, and custom limits
- ⚠️ **Smart warnings** - Proactive alerts before token depletion
- 🚀 **High performance** - Optimized calculations with intelligent caching
- 🌍 **Timezone support** - Custom timezones and reset hours
- 🖥️ **Cross-platform** - Works on Linux, macOS, and Windows

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js and npm (for ccusage dependency)

### Installation

**Option 1: Install with pip (recommended)**
```bash
# Install the monitor
pip install ccusage-monitor

# Install required ccusage CLI tool
npm install -g ccusage

# Run with beautiful Rich UI
ccusage-monitor --rich
```

**Option 2: Run without installation**
```bash
# Using uvx (no installation needed)
uvx ccusage-monitor --rich

# Still need ccusage CLI
npm install -g ccusage
```

### First Run
```bash
# Start with recommended Rich UI mode
ccusage-monitor --rich

# Or use standard mode
ccusage-monitor
```

## 📖 Usage Examples

### Basic Usage
```bash
# Default monitoring (Pro plan)
ccusage-monitor --rich

# Monitor specific plans
ccusage-monitor --rich --plan max5     # Max 5 plan
ccusage-monitor --rich --plan max20    # Max 20 plan
ccusage-monitor --rich --plan custom_max  # Auto-detect limits
```

### Advanced Configuration
```bash
# Custom timezone and reset time
ccusage-monitor --rich --timezone US/Eastern --reset-hour 9

# Multiple options combined
ccusage-monitor --rich --plan max20 --timezone Asia/Shanghai --reset-hour 8

# Standard mode (without Rich UI)
ccusage-monitor --plan pro --timezone UTC
```

### UI Modes Comparison

**Rich UI Mode (--rich)** ✨ *Recommended*
- Professional panels with borders
- Smooth, flicker-free animations  
- Better color scheme and typography
- Optimized performance

**Standard Mode** 
- Basic ANSI terminal output
- Faster startup, lower memory usage
- Compatible with all terminals

## 🎨 Interface Preview 

### Rich UI Mode
```
╔══════════════════════════════════════════════════════════╗
║         ✦ ✧ ✦ ✧ CLAUDE TOKEN MONITOR ✦ ✧ ✦ ✧          ║
╚══════════════════════════════════════════════════════════╝

╭──────────────────────────────────────────────────────────╮
│ 📊 Token Usage:  ████████████░░░░░░░░░░░░░░░░░░░░  23.5% │
│                                                          │
│ ⏳ Time to Reset: ██████████░░░░░░░░░░░░░░░░░░░░░  3h 55m│
╰──────────────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────╮
│ 🎯 Tokens:       1,645 / ~7,000 (5,355 left)            │
│ 🔥 Burn Rate:    2.4 tokens/min                          │
│                                                          │
│ 🏁 Predicted End: 07:42                                  │
│ 🔄 Token Reset:   23:00                                  │
╰──────────────────────────────────────────────────────────╯
```

## ⚡ Performance

ccusage-monitor is highly optimized for performance:

- **Intelligent caching** - Repeated calculations are cached for speed
- **Optimized algorithms** - Up to 3x faster than naive implementations  
- **Low memory footprint** - Minimal resource usage
- **Benchmark included** - Run `python benchmark_performance.py` to test

Performance highlights:
- ~1000 token calculations per second
- <50MB memory usage
- Smart caching provides 10x+ speedup for repeated queries

## 🔧 Configuration

### Supported Plans
- `pro` - Claude Pro (default)
- `max5` - Claude Max 5 messages  
- `max20` - Claude Max 20 messages
- `custom_max` - Auto-detect your plan limits

### Environment Variables
```bash
export CCUSAGE_PLAN=max20
export CCUSAGE_TIMEZONE=US/Pacific
export CCUSAGE_RESET_HOUR=6
```

### Configuration File
See [docs/CONFIG.md](docs/CONFIG.md) for advanced configuration options.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/INSTALL.md) | Detailed installation instructions |
| [Usage Guide](docs/USAGE.md) | Complete usage documentation |
| [Rich UI Guide](docs/RICH_UI.md) | Rich UI mode features and screenshots |
| [Configuration](docs/CONFIG.md) | All configuration options |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions |
| [Contributing](CONTRIBUTING.md) | Development and contribution guide |
| [Changelog](CHANGELOG.md) | Version history and updates |
| [Performance](PERFORMANCE_OPTIMIZATIONS.md) | Performance optimizations details |

## 🛠️ Development

### Project Structure
```
ccusage_monitor/
├── app/          # Application logic
├── core/         # Core calculations and data processing  
├── ui/           # User interface components
├── main.py       # Entry point
└── protocols.py  # Type definitions
```

### Running Tests
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
make test
# or
pytest --cov=ccusage_monitor

# Run benchmarks
python benchmark_performance.py
```

### Code Quality
```bash
make format     # Format code with black/isort
make lint       # Run ruff linting  
make type-check # Run mypy type checking
make pre-commit # Run all pre-commit hooks
```

## 🤝 Contributing

Contributions are welcome! This project uses modern Python development practices:

- **Type hints** with mypy
- **Code formatting** with black and isort  
- **Linting** with ruff
- **Testing** with pytest
- **CI/CD** with GitHub Actions

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🐛 Troubleshooting

**Common Issues:**

- **"ccusage command not found"** → Install with `npm install -g ccusage`
- **Permission errors** → Use `sudo npm install -g ccusage` on Unix systems
- **Token not updating** → Check if you're logged into Claude and have recent usage
- **Display issues** → Try `--rich` mode for better terminal compatibility

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [open an issue](https://github.com/zhiyue/ccusage-monitor/issues).

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built upon [ccusage](https://github.com/ryoppippi/ccusage) by [@ryoppippi](https://github.com/ryoppippi)
- Rich terminal UI powered by [Rich](https://github.com/Textualize/rich)
- Performance optimizations and caching improvements
- Community contributions and feedback

## 🚀 What's Next?

Upcoming features in development:
- 📊 Historical usage charts and analytics
- 📋 Multi-session monitoring with tabbed interface  
- 🎯 Clickable UI elements and interactive mode
- 📈 Advanced prediction models with machine learning
- 🎨 Custom themes and color schemes
- 📱 Web dashboard for remote monitoring

---

<div align="center">

⭐ **Star this repo if you find it useful!** ⭐

[📖 Documentation](docs/) • [🐛 Report Bug](https://github.com/zhiyue/ccusage-monitor/issues) • [💡 Request Feature](https://github.com/zhiyue/ccusage-monitor/issues) • [💬 Discussions](https://github.com/zhiyue/ccusage-monitor/discussions)

</div>