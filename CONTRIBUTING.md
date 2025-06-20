# 🤝 Contributing Guide

Welcome to the Claude Code Usage Monitor project! We're excited to have you contribute to making this tool better for everyone.

---

## 🌟 How to Contribute

### 🎯 Types of Contributions

We welcome all kinds of contributions:

- **🐛 Bug Reports**: Found something broken? Let us know!
- **💡 Feature Requests**: Have an idea for improvement?
- **📝 Documentation**: Help improve guides and examples
- **🔧 Code Contributions**: Fix bugs or implement new features
- **🧪 Testing**: Help test on different platforms
- **🎨 UI/UX**: Improve the visual design and user experience
- **📦 Packaging**: Help with distribution

---

## 🚀 Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/ccusage-monitor.git
cd ccusage-monitor
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black isort mypy ruff
```

### 3. Create a Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 4. Make Your Changes

- Follow our coding standards (see below)
- Add tests for new functionality
- Update documentation if needed
- Test your changes thoroughly

### 5. Submit Your Contribution

```bash
# Add and commit your changes
git add .
git commit -m "Add: Brief description of your change"

# Push to your fork
git push origin feature/your-feature-name

# Open a Pull Request on GitHub
```

---

## 📋 Development Guidelines

### 🐍 Python Code Style

We follow **PEP 8** with these specific guidelines:

```python
# Good: Clear variable names
current_token_count = 1500
session_start_time = datetime.now()

# Bad: Unclear abbreviations  
curr_tok_cnt = 1500
sess_st_tm = datetime.now()

# Good: Descriptive function names
def calculate_burn_rate(tokens_used, time_elapsed):
    return tokens_used / time_elapsed

# Good: Clear comments for complex logic
def predict_token_depletion(current_usage, burn_rate):
    """
    Predicts when tokens will be depleted based on current burn rate.
    
    Args:
        current_usage (int): Current token count
        burn_rate (float): Tokens consumed per minute
        
    Returns:
        datetime: Estimated depletion time
    """
    pass
```

### 📁 Current Project Structure

```
ccusage-monitor/
├── ccusage_monitor.py    # Main monitoring script
├── pyproject.toml       # Modern Python packaging
├── requirements.txt     # Python dependencies
├── README.md           # Main documentation
├── CONTRIBUTING.md     # This file
├── ROADMAP.md         # Future development roadmap
├── TROUBLESHOOTING.md  # Common issues and solutions
├── CHANGELOG.md       # Version history
├── tests/             # Test suite
│   └── test_*.py     # Test files
└── doc/              # Documentation assets
    └── sc.png       # Screenshot
```

### 🧪 Testing Guidelines

The project uses pytest for testing. To run tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ccusage_monitor

# Run specific test file
pytest tests/test_ccusage_monitor.py
```

When adding tests:
- Test file naming: `test_*.py`
- Use pytest fixtures for setup
- Test edge cases and error conditions
- Ensure cross-platform compatibility
- Aim for >80% code coverage

### 📝 Commit Message Format

Use clear, descriptive commit messages:

```bash
# Good commit messages
git commit -m "Add: ML-powered token prediction algorithm"
git commit -m "Fix: Handle edge case when no sessions are active"
git commit -m "Update: Improve error handling in ccusage integration"
git commit -m "Docs: Add examples for timezone configuration"

# Prefixes to use:
# Add: New features
# Fix: Bug fixes  
# Update: Improvements to existing features
# Docs: Documentation changes
# Test: Test additions or changes
# Refactor: Code refactoring
# Style: Code style changes
```


## 🎯 Contribution Areas (Priority)

### 🔧 Core Features & Bug Fixes

**Current Needs**:
- Improve error handling
- Add more configuration options
- Optimize performance
- Fix cross-platform issues

**Skills Helpful**:
- Python development
- Terminal/console applications
- Cross-platform compatibility
- Performance optimization

**Getting Started**:
1. Run the monitor on different platforms
2. Identify and fix platform-specific issues
3. Improve error messages and handling
4. Add new configuration options

---

## 🐛 Bug Reports

### 📋 Before Submitting a Bug Report

1. **Check existing issues**: Search GitHub issues for similar problems
2. **Update to latest version**: Ensure you're using the latest code
3. **Test in clean environment**: Try in fresh virtual environment
4. **Gather information**: Collect system details and error messages

### 📝 Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. Configure with '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Ubuntu 20.04, Windows 11, macOS 12]
- Python version: [e.g. 3.9.7]
- ccusage version: [run: ccusage --version]
- Monitor version: [e.g. 0.0.2 or git commit hash]

**Error Output**
```
Paste full error messages here
```

**Additional Context**
Add any other context about the problem here.
```

---

## 💡 Feature Requests

### 🎯 Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How do you envision this feature working?

**Alternative Solutions**
Any alternative approaches you've considered.

**Use Cases**
Specific scenarios where this feature would be helpful.

**Implementation Ideas**
Any ideas about how this could be implemented (optional).
```

### 🔍 Feature Evaluation Criteria

We evaluate features based on:

1. **User Value**: How many users would benefit?
2. **Complexity**: Implementation effort required
3. **Maintenance**: Long-term maintenance burden
4. **Compatibility**: Impact on existing functionality
5. **Performance**: Effect on monitor performance
6. **Dependencies**: Additional dependencies required

---

## 🧪 Testing Contributions

### 🔧 Testing

*Note: Test infrastructure is not yet implemented. Help us set it up!*

Future testing goals:
- Set up pytest framework
- Add unit tests for core functions
- Test cross-platform compatibility
- Add CI/CD integration

### 🌍 Platform Testing

Help us test on different platforms:

- **Linux**: Ubuntu, Fedora, Arch, Debian
- **macOS**: Intel and Apple Silicon Macs
- **Windows**: Windows 10/11, different Python installations
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12

---

## 📝 Documentation Contributions

### 📚 Documentation Areas

- **README improvements**: Make getting started easier
- **Code comments**: Explain complex algorithms
- **Usage examples**: Real-world scenarios
- **API documentation**: Function and class documentation
- **Troubleshooting guides**: Common problems and solutions

### ✍️ Writing Guidelines

- **Be clear and concise**: Avoid jargon when possible
- **Use examples**: Show don't just tell
- **Consider all users**: From beginners to advanced
- **Keep it updated**: Ensure examples work with current code
- **Use consistent formatting**: Follow existing style

---

## 📊 Data Collection for Improvement

### 🔍 Help Us Improve Token Limit Detection

We're collecting **anonymized data** about token limits to improve auto-detection:

**What to share in [GitHub Issues](https://github.com/zhiyue/ccusage-monitor/issues)**:
- Your subscription type (Pro, Teams, Enterprise)
- Maximum tokens reached (custom_max value)
- When the limit was exceeded
- Usage patterns you've noticed

**Privacy**: Only share what you're comfortable with. No personal information needed.

### 📈 Usage Pattern Research

Help us understand usage patterns:
- Peak usage times
- Session duration preferences  
- Token consumption patterns
- Feature usage statistics

This helps prioritize development and improve user experience.


## 🏆 Recognition

### 📸 Contributor Spotlight

Outstanding contributors will be featured:
- **README acknowledgments**: Credit for major contributions
- **CHANGELOG mentions**: Recognition in version history
- **AUTHORS file**: Permanent record of contributors

### 🎖️ Contribution Levels

- **🌟 First Contribution**: Welcome to the community!
- **🔧 Regular Contributor**: Multiple merged PRs
- **🚀 Core Contributor**: Significant feature development
- **👑 Maintainer**: Ongoing project stewardship


## ❓ Getting Help

### 💬 Where to Ask Questions

1. **GitHub Issues**: For bug reports and feature requests
2. **GitHub Discussions**: For general questions and ideas
3. **Email**: [cszhiyue@gmail.com](mailto:cszhiyue@gmail.com) for direct contact
4. **Code Review**: Ask questions in PR comments

### 📚 Resources

- **[ROADMAP.md](ROADMAP.md)**: Future development plans
- **[README.md](README.md)**: Installation, usage, and features
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Common issues

---

## 📜 Code of Conduct

### 🤝 Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome contributors of all backgrounds
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember everyone is learning
- **Be professional**: Keep interactions focused on the project

### 🚫 Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Spam or off-topic discussions
- Sharing private information without permission

### 📞 Reporting Issues

If you experience unacceptable behavior, contact: [cszhiyue@gmail.com](mailto:cszhiyue@gmail.com)

---

## 🎉 Thank You!

Thank you for considering contributing to Claude Code Usage Monitor! Every contribution, no matter how small, helps make this tool better for the entire community.

**Ready to get started?** 

1. 🍴 Fork the repository
2. 💻 Set up your development environment  
3. 🔍 Look at open issues for ideas
4. 🚀 Start coding!

We can't wait to see what you'll contribute! 🚀
