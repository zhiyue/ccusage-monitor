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

Real-time terminal monitoring tool for Claude AI token usage. Track consumption, burn rate, and predict when tokens will run out.

![Claude Token Monitor Screenshot](docs/sc.png)

## ✨ Features

- 🔄 **Real-time monitoring** - Updates every 3 seconds
- 📊 **Visual progress bars** - Token and time usage at a glance
- 🔮 **Smart predictions** - Know when tokens will deplete
- 🤖 **Auto-detection** - Automatically detects your token limits
- 📋 **Multiple plans** - Supports Pro, Max5, Max20
- ⚠️ **Smart warnings** - Alerts before token depletion
- 🎨 **Rich UI mode** - Beautiful, flicker-free terminal interface (NEW!)

## 🚀 Quick Start

```bash
# Install from PyPI
pip install ccusage-monitor

# Install ccusage CLI tool (required)
npm install -g ccusage

# Run the monitor
ccusage-monitor
```

Or use without installation:
```bash
uvx ccusage-monitor
```

## 📖 Basic Usage

```bash
# Default (Pro plan)
ccusage-monitor

# Specify plan
ccusage-monitor --plan max5
ccusage-monitor --plan max20
ccusage-monitor --plan custom_max  # Auto-detect

# Custom timezone
ccusage-monitor --timezone US/Eastern

# Custom reset hour
ccusage-monitor --reset-hour 9

# Beautiful Rich UI mode (recommended!)
ccusage-monitor --rich
```

## 📚 Documentation

- [Installation Guide](docs/INSTALL.md) - Detailed installation instructions
- [Usage Guide](docs/USAGE.md) - Complete usage documentation
- [Configuration](docs/CONFIG.md) - All configuration options
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Changelog](CHANGELOG.md) - Version history

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

Built upon [ccusage](https://github.com/ryoppippi/ccusage) by [@ryoppippi](https://github.com/ryoppippi).

---

<div align="center">

⭐ **Star this repo if you find it useful!** ⭐

[Report Bug](https://github.com/zhiyue/ccusage-monitor/issues) • [Request Feature](https://github.com/zhiyue/ccusage-monitor/issues)

</div>