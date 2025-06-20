# Configuration Guide

## Overview

Claude Code Usage Monitor can be configured through command-line arguments. There are no configuration files - all settings are passed as arguments when running the monitor.

## Command Line Arguments

### --plan

Select your Claude subscription plan or auto-detection mode.

**Options:**
- `pro` (default) - Pro plan with ~7,000 tokens per session
- `max5` - Max5 plan with ~35,000 tokens per session
- `max20` - Max20 plan with ~140,000 tokens per session
- `custom_max` - Auto-detect maximum tokens from previous sessions

**Examples:**
```bash
ccusage-monitor --plan pro
ccusage-monitor --plan max5
ccusage-monitor --plan custom_max
```

**Auto-Detection:**
When using `custom_max`, the monitor will:
1. Scan all previous Claude sessions
2. Find the highest token count achieved
3. Use that as the maximum limit
4. Update if a higher limit is discovered

### --timezone

Set the timezone for displaying times and calculating reset schedules.

**Default:** `Europe/Warsaw`

**Format:** Any valid timezone from the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

**Common Examples:**
```bash
# Americas
ccusage-monitor --timezone US/Eastern
ccusage-monitor --timezone US/Central
ccusage-monitor --timezone US/Mountain
ccusage-monitor --timezone US/Pacific
ccusage-monitor --timezone America/New_York
ccusage-monitor --timezone America/Los_Angeles

# Europe
ccusage-monitor --timezone Europe/London
ccusage-monitor --timezone Europe/Paris
ccusage-monitor --timezone Europe/Berlin
ccusage-monitor --timezone Europe/Warsaw

# Asia/Pacific
ccusage-monitor --timezone Asia/Tokyo
ccusage-monitor --timezone Asia/Shanghai
ccusage-monitor --timezone Australia/Sydney

# Other
ccusage-monitor --timezone UTC
```

### --reset-hour

Set the reference hour for session reset calculations.

**Default:** `4` (4:00 AM)

**Range:** 0-23 (24-hour format)

**Examples:**
```bash
ccusage-monitor --reset-hour 0    # Midnight
ccusage-monitor --reset-hour 9    # 9:00 AM
ccusage-monitor --reset-hour 14   # 2:00 PM
ccusage-monitor --reset-hour 22   # 10:00 PM
```

**Note:** This sets reference times for planning. Actual token refresh happens exactly 5 hours after your first message in each session.

## Environment Variables

### CLAUDE_CONFIG_DIR

Override the default Claude configuration directory location.

**Default:** `~/.config/claude`

**Usage:**
```bash
CLAUDE_CONFIG_DIR=/custom/path ccusage-monitor
```

This is useful when:
- Claude Code uses a non-standard config location
- Running in containerized environments
- Multiple Claude installations

## Plan Details

### Token Limits by Plan

| Plan | Token Limit | Best For | Notes |
|------|-------------|----------|-------|
| `pro` | ~7,000 | Light usage, learning | Default option |
| `max5` | ~35,000 | Regular development | 5x Pro limits |
| `max20` | ~140,000 | Heavy usage, large projects | 20x Pro limits |
| `custom_max` | Variable | Unknown/changing limits | Auto-detects |

### Choosing the Right Plan

**Use `pro` when:**
- Just starting with Claude Code
- Light coding tasks
- Testing and learning

**Use `max5` when:**
- Regular daily development
- Medium-sized projects
- Known Max5 subscription

**Use `max20` when:**
- Heavy development work
- Large refactoring tasks
- Known Max20 subscription

**Use `custom_max` when:**
- Unsure of your limits
- Limits seem to vary
- Want automatic adjustment

## Session Mechanics

### Understanding 5-Hour Sessions

Claude Code operates on a 5-hour rolling window system:

```
Timeline Example:
09:00 - Send first message (Session A starts, 7000 tokens)
10:30 - Send message (Session B starts, 7000 tokens) 
14:00 - Session A expires (tokens refresh)
15:30 - Session B expires (tokens refresh)
```

### Reference Reset Times

Based on your `--reset-hour` setting, reference times are calculated:

```
--reset-hour 4 (default):
Reference times: 04:00, 09:00, 14:00, 19:00, 00:00

--reset-hour 9:
Reference times: 09:00, 14:00, 19:00, 00:00, 05:00
```

These help you plan when to start new sessions for optimal token usage.

## Configuration Examples

### Example 1: US Developer, Pro Plan

```bash
ccusage-monitor --timezone US/Eastern --reset-hour 9
```

- Uses Eastern Time
- Reference resets at 9 AM (work start)
- Pro plan limits

### Example 2: European Heavy User

```bash
ccusage-monitor --plan max20 --timezone Europe/Berlin --reset-hour 8
```

- Max20 plan for heavy usage
- Berlin timezone
- Morning reset alignment

### Example 3: Auto-Detecting Night Owl

```bash
ccusage-monitor --plan custom_max --reset-hour 0
```

- Auto-detect token limits
- Midnight reset reference
- Default timezone

### Example 4: Global Remote Worker

```bash
ccusage-monitor --timezone UTC --plan max5
```

- UTC for global coordination
- Max5 plan
- Default reset hour

## Performance Settings

The monitor has fixed performance settings:

- **Refresh Rate**: 3 seconds
- **History Analysis**: Last 60 minutes
- **Display Width**: Adapts to terminal
- **Color Output**: Automatic detection

These are optimized for real-time monitoring without excessive system load.

## Troubleshooting Configuration

### Wrong Timezone

**Symptom**: Reset times don't match expectations

**Solution**: 
```bash
# List available timezones
python3 -c "import pytz; print('\n'.join(pytz.all_timezones))" | grep -i your_region

# Use exact timezone name
ccusage-monitor --timezone America/New_York  # Not "EST"
```

### Plan Detection Issues

**Symptom**: Auto-detection shows wrong limits

**Solution**:
1. Use `custom_max` for a few sessions
2. Let it learn your actual limits
3. Or specify plan explicitly

### Session Not Found

**Symptom**: "No active session found"

**Solution**:
```bash
# Check config directory
CLAUDE_CONFIG_DIR=~/.config/claude ccusage-monitor

# Or try default location
ccusage-monitor
```

## Best Practices

1. **Set Your Timezone**: Always use your local timezone for accurate planning
2. **Choose Appropriate Plan**: Start with default, upgrade if needed
3. **Align Reset Hours**: Match your work schedule
4. **Monitor Regularly**: Keep it running during active development
5. **Use Auto-Detection**: When unsure about limits

## Future Configuration

Planned configuration enhancements:
- Configuration file support
- Refresh rate customization
- Custom warning thresholds
- Display preferences
- Notification settings

See [ROADMAP.md](../ROADMAP.md) for details.