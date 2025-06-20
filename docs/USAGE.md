# Usage Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Command Line Options](#command-line-options)
- [Understanding the Display](#understanding-the-display)
- [Usage Scenarios](#usage-scenarios)
- [Advanced Usage](#advanced-usage)
- [Tips and Best Practices](#tips-and-best-practices)

## Getting Started

### Basic Usage

Simply run the monitor with default settings:

```bash
ccusage-monitor
```

This will:
- Start monitoring with Pro plan limits (~7,000 tokens)
- Use Europe/Warsaw timezone
- Update every 3 seconds
- Auto-detect higher limits if exceeded

### Exit the Monitor

Press `Ctrl+C` to gracefully exit the monitor.

## Command Line Options

### Plan Selection

Choose your Claude subscription plan:

```bash
# Pro plan (default, ~7,000 tokens)
ccusage-monitor --plan pro

# Max5 plan (~35,000 tokens)
ccusage-monitor --plan max5

# Max20 plan (~140,000 tokens)
ccusage-monitor --plan max20

# Auto-detect from previous sessions
ccusage-monitor --plan custom_max
```

### Timezone Configuration

Set your local timezone for accurate reset times:

```bash
# US timezones
ccusage-monitor --timezone US/Eastern
ccusage-monitor --timezone US/Pacific

# European timezones
ccusage-monitor --timezone Europe/London
ccusage-monitor --timezone Europe/Berlin

# Asian timezones
ccusage-monitor --timezone Asia/Tokyo
ccusage-monitor --timezone Asia/Shanghai

# UTC
ccusage-monitor --timezone UTC
```

### Reset Hour

Customize when your reference reset times occur:

```bash
# Reset at 9 AM
ccusage-monitor --reset-hour 9

# Reset at midnight
ccusage-monitor --reset-hour 0

# Reset at 10 PM
ccusage-monitor --reset-hour 22
```

### Combined Options

You can combine multiple options:

```bash
ccusage-monitor --plan max5 --timezone US/Pacific --reset-hour 8
```

## Understanding the Display

### Display Components

```
🎯 Claude Code Usage Monitor

📊 Current Usage:
Active Sessions: 3
Current Session: #abc123... (started 2h 15m ago)
Token Usage: 12,450 / 35,000 (35.6%)
[████████████░░░░░░░░░░░░░░░░] 35.6%

⏱️ Time Progress:
Time Until Reset: 2h 45m
Session Progress: 2h 15m / 5h (45.0%)
[█████████████░░░░░░░░░░░░░░░] 45.0%

🔥 Burn Rate:
Current Rate: 92.2 tokens/min (5.5K/hour)
Status: ⚠️ Tokens will deplete before reset!
Predicted Depletion: in 3h 45m (11:45 PM)

[Auto-refreshing every 3 seconds...]
```

### Status Indicators

- ✅ **Green**: Normal usage, tokens will last
- ⚠️ **Yellow**: Warning, high burn rate
- 🚨 **Red**: Critical, tokens depleting soon

### Progress Bars

- **Token Bar**: Shows current token usage vs limit
- **Time Bar**: Shows time elapsed in current session

## Usage Scenarios

### Morning Developer

Start work at 9 AM with aligned reset times:

```bash
ccusage-monitor --reset-hour 9 --timezone US/Eastern
```

Benefits:
- Fresh tokens at work start
- Better daily planning
- Predictable session windows

### Night Owl Coder

Working late with midnight resets:

```bash
ccusage-monitor --reset-hour 0 --plan max20
```

Strategy:
- Plan heavy work before midnight
- Use new tokens after reset
- Monitor burn rate during peak hours

### Heavy User (Unknown Limits)

Let auto-detection find your limits:

```bash
ccusage-monitor --plan custom_max
```

The monitor will:
- Scan previous sessions
- Find highest token usage
- Automatically adjust limits

### International/Remote Work

Working across timezones:

```bash
# Working from Europe for US team
ccusage-monitor --timezone America/New_York

# Coordinating globally
ccusage-monitor --timezone UTC
```

## Advanced Usage

### Understanding Claude Sessions

Claude Code uses a **5-hour rolling session window**:

1. **Session Start**: First message to Claude
2. **Duration**: Exactly 5 hours
3. **Token Limits**: Apply per session
4. **Multiple Sessions**: Can overlap
5. **Reset**: New tokens after 5 hours

Example timeline:
```
10:30 AM - Start Session A (7,000 tokens)
12:15 PM - Start Session B (7,000 tokens)
03:30 PM - Session A expires, tokens refresh
05:15 PM - Session B expires, tokens refresh
```

### Burn Rate Analysis

The monitor analyzes token consumption:

1. **Data Collection**: Last hour of usage
2. **Pattern Analysis**: Consumption trends
3. **Velocity Tracking**: Tokens per minute
4. **Prediction**: When tokens deplete

### Auto-Detection Features

When using default Pro plan:

1. Monitor detects >7,000 token usage
2. Scans session history
3. Switches to custom_max
4. Shows notification
5. Continues with new limit

## Tips and Best Practices

### Optimize Token Usage

1. **Start Early**: Begin monitoring when starting work
2. **Watch Velocity**: Monitor burn rate changes
3. **Plan Around Resets**: Schedule heavy work after resets

### Terminal Setup

- Use terminal width ≥80 characters
- Enable color support
- Consider dedicated monitoring window

### Workflow Integration

Run in background with tmux/screen:

```bash
# Start in tmux
tmux new-session -d -s claude-monitor 'ccusage-monitor'

# Check anytime
tmux attach -t claude-monitor
```

### Strategic Planning

1. **Morning**: Check overnight usage
2. **Midday**: Adjust work based on burn rate
3. **Evening**: Plan for next session

### Common Patterns

**High burn rate causes:**
- Large file processing
- Complex refactoring
- Extensive code generation
- Multiple file edits

**Optimization strategies:**
- Break large tasks into chunks
- Use sessions efficiently
- Plan heavy work post-reset
- Monitor velocity changes

## Troubleshooting

See [Troubleshooting Guide](../TROUBLESHOOTING.md) for common issues.

## Next Steps

- Read [Configuration Guide](CONFIG.md) for detailed options
- Check [Contributing Guide](../CONTRIBUTING.md) to help improve the tool
- Report issues on [GitHub](https://github.com/zhiyue/ccusage-monitor/issues)