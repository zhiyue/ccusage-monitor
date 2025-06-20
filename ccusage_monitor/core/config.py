"""Configuration and CLI argument parsing for ccusage monitor."""

import argparse

from ccusage_monitor.protocols import CLIArgs


def parse_args() -> CLIArgs:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Claude Token Monitor - Real-time token usage monitoring")
    parser.add_argument(
        "--plan",
        type=str,
        default="pro",
        choices=["pro", "max5", "max20", "custom_max"],
        help='Claude plan type (default: pro). Use "custom_max" to auto-detect from highest previous block',
    )
    parser.add_argument("--reset-hour", type=int, help="Change the reset hour (0-23) for daily limits")
    parser.add_argument(
        "--timezone",
        type=str,
        default="Europe/Warsaw",
        help="Timezone for reset times (default: Europe/Warsaw). Examples: US/Eastern, Asia/Tokyo, UTC",
    )
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Show performance mode indicator",
    )
    parser.add_argument(
        "--rich",
        action="store_true",
        help="Use Rich library for beautiful terminal UI (experimental)",
    )
    parser.add_argument(
        "--refresh",
        type=int,
        default=3,
        help="Refresh interval in seconds (default: 3, for rich mode)",
    )
    args = parser.parse_args()

    # Create a CLIArgs instance with the parsed values
    cli_args = CLIArgs()
    cli_args.plan = args.plan
    cli_args.reset_hour = args.reset_hour
    cli_args.timezone = args.timezone
    cli_args.performance = args.performance
    cli_args.rich = args.rich
    cli_args.refresh = args.refresh

    return cli_args


# Color constants
CYAN = "\033[96m"
RED = "\033[91m"
YELLOW = "\033[93m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GREEN = "\033[92m"
RESET = "\033[0m"

# Token limits
TOKEN_LIMITS = {
    "pro": 7000,
    "max5": 35000,
    "max20": 140000,
}

# Default timezone
DEFAULT_TIMEZONE = "Europe/Warsaw"

# Session duration in minutes
SESSION_DURATION = 300  # 5 hours
