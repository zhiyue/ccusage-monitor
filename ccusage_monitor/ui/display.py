"""Consolidated display module with optimized terminal UI functions."""

import sys
from io import StringIO
from typing import Union, cast

from ccusage_monitor.core.cache import cache


class OptimizedOutputBuffer:
    """Enhanced buffer for optimized terminal output with differential rendering."""

    def __init__(self) -> None:
        self.buffer: StringIO = StringIO()
        self.last_output: str = ""
        self.last_lines: list[str] = []
        self._write_count = 0
        self._flush_count = 0

    def write(self, text: str) -> None:
        """Add text to buffer."""
        self.buffer.write(text)
        self._write_count += 1

    def writeln(self, text: str = "") -> None:
        """Add text with newline to buffer."""
        self.buffer.write(text + "\n")
        self._write_count += 1

    def flush(self) -> None:
        """Flush buffer to stdout with differential rendering."""
        current_output = self.buffer.getvalue()

        # Only update screen if content actually changed
        if current_output != self.last_output:
            current_lines = current_output.split('\n')

            # Use differential rendering for better performance
            if self.last_lines and len(current_lines) == len(self.last_lines):
                self._differential_update(current_lines)
            else:
                self._full_update(current_output)

            self.last_output = current_output
            self.last_lines = current_lines[:]

        self._flush_count += 1
        # Reset buffer
        self.buffer = StringIO()

    def _differential_update(self, current_lines: list[str]) -> None:
        """Update only changed lines."""
        changes_made = False

        for i, (old_line, new_line) in enumerate(zip(self.last_lines, current_lines)):
            if old_line != new_line:
                if not changes_made:
                    # Move cursor to home position only once
                    sys.stdout.write("\033[H")
                    changes_made = True

                # Move to specific line and update
                sys.stdout.write(f"\033[{i+1};1H")  # Move to line i+1, column 1
                sys.stdout.write("\033[K")  # Clear line
                sys.stdout.write(new_line)

        if changes_made:
            sys.stdout.flush()

    def _full_update(self, output: str) -> None:
        """Full screen update for major changes."""
        # Move cursor to top
        sys.stdout.write("\033[H")
        # Write all at once
        sys.stdout.write(output)
        # Clear remaining lines
        sys.stdout.write("\033[J")
        sys.stdout.flush()

    def get_stats(self) -> dict[str, int]:
        """Get buffer statistics."""
        return {
            "writes": self._write_count,
            "flushes": self._flush_count,
            "buffer_size": len(self.last_output)
        }


# Global buffer instance
_buffer = OptimizedOutputBuffer()


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
    """Create optimized token progress bar with enhanced caching and pre-computed segments."""
    # Round percentage to reduce cache entries (0.5% precision)
    rounded_pct = round(percentage * 2) / 2
    cache_key = f"token_bar_{rounded_pct}_{width}"

    cached = cache.get(cache_key, ttl=300)  # Cache for 5 minutes
    if cached is not None:
        return cast(str, cached)

    # Pre-compute common segments for better performance
    filled = int(width * rounded_pct / 100)

    # Use more efficient string building
    if filled == 0:
        bar_content = "░" * width
        color_code = "\033[91m"  # Red
    elif filled == width:
        bar_content = "█" * width
        color_code = "\033[92m"  # Green
    else:
        # Mixed bar - use list join for better performance
        segments = ["█"] * filled + ["░"] * (width - filled)
        bar_content = "".join(segments)
        color_code = "\033[92m" if rounded_pct < 80 else "\033[93m" if rounded_pct < 95 else "\033[91m"

    # Build result with minimal string operations
    result = f"🟢 [{color_code}{bar_content}\033[0m] {rounded_pct:.1f}%"
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
