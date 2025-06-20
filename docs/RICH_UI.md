# Rich UI Mode

ccusage-monitor now supports an enhanced UI mode using the [Rich](https://github.com/Textualize/rich) library.

## Features

### 🎨 Beautiful Terminal UI
- Professional panels and borders
- Smooth progress bar animations
- Consistent styling and colors
- Better layout management

### 🚀 Performance
- **Zero flicker** - Uses Rich's Live display for smooth updates
- Optimized rendering - Only redraws changed elements
- Lower CPU usage compared to manual screen clearing

### 💻 Cross-Platform
- Works identically on Windows, macOS, and Linux
- Automatic terminal capability detection
- Graceful fallback for limited terminals

## Usage

```bash
# Use Rich UI mode
ccusage-monitor --rich

# With other options
ccusage-monitor --rich --plan max20 --timezone Asia/Shanghai
```

## Comparison

### Standard Mode
- Uses ANSI escape codes
- Manual screen positioning
- Basic progress bars
- May flicker on some terminals

### Rich Mode
- Professional UI framework
- Automatic layout management
- Animated progress bars
- Flicker-free updates

## Installation

Rich is now included as a dependency. If you need to install it manually:

```bash
pip install rich
```

## Future Enhancements

With Rich, we can easily add:
- 📊 Real-time charts and graphs
- 📋 Tabbed views for multiple sessions
- 🎯 Click-able UI elements
- 📈 Historical data visualization
- 🎨 Custom themes and colors

## Screenshots

### Rich Mode
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

⏰ 01:05:18 📝 Smooth sailing... | Ctrl+C to exit 🟨
```

### Standard Mode
```
✦ ✧ ✦ ✧ CLAUDE TOKEN MONITOR ✦ ✧ ✦ ✧
============================================================

📊 Token Usage:    🟢 [████████████░░░░░░░░░░░░░░░░░░░░░░░░░] 23.5%

⏳ Time to Reset:  ⏰ [██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░] 3h 55m

🎯 Tokens:         1,645 / ~7,000 (5,355 left)
🔥 Burn Rate:      2.4 tokens/min

🏁 Predicted End: 07:42
🔄 Token Reset:   23:00

⏰ 01:05:18 📝 Smooth sailing... | Ctrl+C to exit 🟨
```