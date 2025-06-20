"""Display module for terminal UI functions."""

from typing import Union


def print_header() -> None:
    """Print the stylized header with sparkles."""
    cyan = "\033[96m"
    blue = "\033[94m"
    reset = "\033[0m"

    # Sparkle pattern
    sparkles = f"{cyan}✦ ✧ ✦ ✧ {reset}"

    print(f"{sparkles}{cyan}CLAUDE TOKEN MONITOR{reset} {sparkles}")
    print(f"{blue}{'=' * 60}{reset}")
    print()


def create_token_progress_bar(percentage: float, width: int = 50) -> str:
    """Create a token usage progress bar with bracket style."""
    filled = int(width * percentage / 100)

    # Create the bar with green fill and red empty space
    green_bar = "█" * filled
    red_bar = "░" * (width - filled)

    # Color codes
    green = "\033[92m"  # Bright green
    red = "\033[91m"  # Bright red
    reset = "\033[0m"

    return f"🟢 [{green}{green_bar}{red}{red_bar}{reset}] {percentage:.1f}%"


def create_time_progress_bar(
    elapsed_minutes: Union[int, float], total_minutes: Union[int, float], width: int = 50
) -> str:
    """Create a time progress bar showing time until reset."""
    percentage = 0 if total_minutes <= 0 else min(100, (elapsed_minutes / total_minutes) * 100)

    filled = int(width * percentage / 100)

    # Create the bar with blue fill and red empty space
    blue_bar = "█" * filled
    red_bar = "░" * (width - filled)

    # Color codes
    blue = "\033[94m"  # Bright blue
    red = "\033[91m"  # Bright red
    reset = "\033[0m"

    remaining_time = format_time(max(0, total_minutes - elapsed_minutes))
    return f"⏰ [{blue}{blue_bar}{red}{red_bar}{reset}] {remaining_time}"


def format_time(minutes: Union[int, float]) -> str:
    """Format minutes into human-readable time (e.g., '3h 45m')."""
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def clear_screen() -> None:
    """Clear the terminal screen."""
    # Use ANSI escape codes for better compatibility
    print("\033[2J\033[3J\033[H", end="", flush=True)


def hide_cursor() -> None:
    """Hide the terminal cursor."""
    print("\033[?25l", end="", flush=True)


def show_cursor() -> None:
    """Show the terminal cursor."""
    print("\033[?25h", end="", flush=True)


def move_cursor_to_top() -> None:
    """Move cursor to top of screen."""
    print("\033[H", end="", flush=True)


def clear_below_cursor() -> None:
    """Clear any remaining lines below cursor."""
    print("\033[J", end="", flush=True)


def writeln(text: str = "") -> None:
    """Print text with newline - compatibility with optimized version."""
    print(text)


def flush_buffer() -> None:
    """Flush output - compatibility with optimized version (no-op)."""
    pass
