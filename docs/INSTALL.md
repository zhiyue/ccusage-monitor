# Installation Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Node.js** for ccusage CLI tool

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
# Install the package
pip install ccusage-monitor

# Install required CLI tool
npm install -g ccusage

# Run the monitor
ccusage-monitor
```

### Method 2: Using uvx (No Installation)

If you have [uv](https://github.com/astral-sh/uv) installed:

```bash
# Run directly without installation
uvx ccusage-monitor
```

### Method 3: Development Installation

For contributors or advanced users:

```bash
# Clone the repository
git clone https://github.com/zhiyue/ccusage-monitor.git
cd ccusage-monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Virtual Environment Setup (Recommended)

Using a virtual environment is strongly recommended to avoid dependency conflicts:

### Why Use Virtual Environment?

- 🛡️ **Isolation**: Keeps system Python clean
- 📦 **Portability**: Easy to replicate environments
- 🔄 **Version Control**: Lock specific dependency versions
- 🧹 **Clean Uninstall**: Simply delete the venv folder

### Creating Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Install ccusage-monitor
pip install ccusage-monitor

# When done, deactivate
deactivate
```

### Installing virtualenv (if needed)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-venv

# Fedora/RHEL/CentOS
sudo dnf install python3-venv

# macOS (usually comes with Python)
# If not available:
brew install python3

# Windows
# Usually comes with Python
# If not, reinstall Python from python.org
```

## Shell Alias Setup

For quick access, add an alias to your shell configuration:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias claude-monitor='ccusage-monitor'

# Or for virtual environment users:
alias claude-monitor='source ~/path/to/venv/bin/activate && ccusage-monitor'
```

## Troubleshooting Installation

### Common Issues

1. **"command not found: ccusage"**
   - Make sure npm is installed
   - Run: `npm install -g ccusage`

2. **"command not found: ccusage-monitor"**
   - Make sure pip installation succeeded
   - Check if it's in PATH: `pip show ccusage-monitor`

3. **Permission errors**
   - Use virtual environment (recommended)
   - Or use `pip install --user ccusage-monitor`

4. **Python version issues**
   - Ensure Python 3.8+ is installed: `python3 --version`
   - Use pyenv or conda to manage Python versions

## Next Steps

After installation, see the [Usage Guide](USAGE.md) to start monitoring your Claude token usage.