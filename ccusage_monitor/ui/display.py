"""Consolidated display module with optimized terminal UI functions."""

import sys
from io import StringIO
from typing import Union, cast

from ccusage_monitor.core.cache import cache


class OutputBuffer:
    """Buffer for optimized terminal output."""

    def __init__(self) -> None:
        self.buffer: StringIO = StringIO()
        self.last_output: str = ""

    def write(self, text: str) -> None:
        """Add text to buffer."""
        self.buffer.write(text)

    def writeln(self, text: str = "") -> None:
        """Add text with newline to buffer."""
        self.buffer.write(text + "\n")

    def flush(self) -> None:
        """Flush buffer to stdout only if content changed."""
        current_output = self.buffer.getvalue()

        # Only update screen if content actually changed
        if current_output != self.last_output:
            # Move cursor to top
            print("\033[H", end="", flush=False)
            # Write all at once
            sys.stdout.write(current_output)
            # Clear remaining lines
            print("\033[J", end="", flush=True)
            self.last_output = current_output

        # Reset buffer
        self.buffer = StringIO()


# Global buffer instance
_buffer = OutputBuffer()


def write_to_buffer(text: str) -> None:
    """Public interface to write to buffer."""
    _buffer.write(text)


def writeln(text: str = "") -> None:
    """Public interface to writeln."""
    _buffer.writeln(text)


def flush_buffer() -> None:
    """Public interface to flush buffer."""
    _buffer.flush()


def print_header() -> None:
    """Print header with caching."""
    # Header doesn't change, so cache it
    cached = cache.get("header_output")
    if cached is None:
        cyan = "\033[96m"
        blue = "\033[94m"
        reset = "\033[0m"
        sparkles = f"{cyan}✦ ✧ ✦ ✧ {reset}"

        header_str = f"{sparkles}{cyan}CLAUDE TOKEN MONITOR{reset} {sparkles}\n{blue}{'=' * 60}{reset}\n\n"
        cache.set("header_output", header_str)
        cached = header_str

    write_to_buffer(cast(str, cached))


def create_token_progress_bar(percentage: float, width: int = 50) -> str:
    """Create token progress bar with caching for common values."""
    # Round percentage to reduce cache entries
    rounded_pct = round(percentage, 1)
    cache_key = f"token_bar_{rounded_pct}_{width}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cast(str, cached)

    filled = int(width * percentage / 100)
    green_bar = "█" * filled
    red_bar = "░" * (width - filled)

    # Use pre-defined color codes
    result = f"🟢 [\033[92m{green_bar}\033[91m{red_bar}\033[0m] {percentage:.1f}%"
    cache.set(cache_key, result)
    return result


def create_time_progress_bar(
    elapsed_minutes: Union[int, float], total_minutes: Union[int, float], width: int = 50
) -> str:
    """Create time progress bar with caching."""
    percentage = 0 if total_minutes <= 0 else min(100, (elapsed_minutes / total_minutes) * 100)

    # Round values for better caching
    rounded_elapsed = round(elapsed_minutes)
    cache_key = f"time_bar_{rounded_elapsed}_{total_minutes}_{width}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cast(str, cached)

    filled = int(width * percentage / 100)
    blue_bar = "█" * filled
    red_bar = "░" * (width - filled)

    remaining_time = format_time(max(0, total_minutes - elapsed_minutes))
    result = f"⏰ [\033[94m{blue_bar}\033[91m{red_bar}\033[0m] {remaining_time}"
    cache.set(cache_key, result)
    return result


def format_time(minutes: Union[int, float]) -> str:
    """Format time with caching."""
    # Round to nearest minute for better caching
    rounded_minutes = round(minutes)

    cached = cache.get(f"time_format_{rounded_minutes}")
    if cached is not None:
        return cast(str, cached)

    if rounded_minutes < 60:
        result = f"{rounded_minutes}m"
    else:
        hours = rounded_minutes // 60
        mins = rounded_minutes % 60
        result = f"{hours}h" if mins == 0 else f"{hours}h {mins}m"

    cache.set(f"time_format_{rounded_minutes}", result)
    return result


def clear_screen() -> None:
    """Clear the terminal screen."""
    # Use ANSI escape codes for better compatibility
    print("\033[2J\033[3J\033[H", end="", flush=True)


def hide_cursor() -> None:
    """Hide cursor."""
    print("\033[?25l", end="", flush=True)


def show_cursor() -> None:
    """Show cursor."""
    print("\033[?25h", end="", flush=True)


def move_cursor_to_top() -> None:
    """Move cursor to top (handled by buffer now)."""
    pass  # Buffer handles this


def clear_below_cursor() -> None:
    """Clear below cursor (handled by buffer now)."""
    pass  # Buffer handles this
