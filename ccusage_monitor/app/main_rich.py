"""Main module using Rich for beautiful terminal UI."""

import sys
import time
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import pytz
from rich.live import Live

from ccusage_monitor.core import calculations, data
from ccusage_monitor.protocols import CLIArgs
from ccusage_monitor.ui.rich_display import create_rich_display


def format_time(minutes: float) -> str:
    """Format minutes into human-readable time."""
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def main_with_args(args: CLIArgs):
    """Main monitoring loop with Rich display using provided args."""

    # Check if ccusage is installed
    if not data.check_ccusage_installed():
        print("\n❌ Cannot proceed without ccusage. Exiting.")
        sys.exit(1)

    # Initialize token limit
    if args.plan == "custom_max":
        initial_data = data.run_ccusage()
        if initial_data and "blocks" in initial_data:
            token_limit = data.get_token_limit(args.plan, initial_data["blocks"])
        else:
            token_limit = data.get_token_limit("pro")
    else:
        token_limit = data.get_token_limit(args.plan)

    # Create Rich display
    display = create_rich_display()

    try:
        # Use Rich's Live display for flicker-free updates
        with Live(display.layout, refresh_per_second=1, screen=True):
            while True:
                ccusage_data = data.run_ccusage()
                if not ccusage_data or "blocks" not in ccusage_data:
                    # Update with error message
                    display.update_display(
                        {
                            "token_pct": 0,
                            "time_pct": 0,
                            "tokens_used": 0,
                            "token_limit": token_limit,
                            "time_remaining": "N/A",
                            "stats": {
                                "tokens_used": 0,
                                "token_limit": token_limit,
                                "tokens_left": token_limit,
                                "burn_rate": 0,
                                "predicted_end": "N/A",
                                "reset_time": "N/A",
                                "cost_usd": 0.0,
                            },
                            "warnings": [("Failed to get usage data", "red")],
                            "status_message": "Waiting for data...",
                        }
                    )
                    time.sleep(args.refresh)
                    continue

                # Find active block
                active_block = None
                for block in ccusage_data["blocks"]:
                    if block.get("isActive", False):
                        active_block = block
                        break

                if not active_block:
                    display.update_display(
                        {
                            "token_pct": 0,
                            "time_pct": 0,
                            "tokens_used": 0,
                            "token_limit": token_limit,
                            "time_remaining": "N/A",
                            "stats": {
                                "tokens_used": 0,
                                "token_limit": token_limit,
                                "tokens_left": token_limit,
                                "burn_rate": 0,
                                "predicted_end": "N/A",
                                "reset_time": "N/A",
                                "cost_usd": 0.0,
                            },
                            "warnings": [("No active session found", "yellow")],
                            "status_message": "Waiting for session...",
                        }
                    )
                    time.sleep(args.refresh)
                    continue

                # Extract data
                tokens_used = active_block.get("totalTokens", 0)
                cost_usd = active_block.get("costUSD", 0.0)

                # Auto-switch logic
                if tokens_used > token_limit and args.plan == "pro":
                    new_limit = data.get_token_limit("custom_max", ccusage_data["blocks"])
                    if new_limit > token_limit:
                        token_limit = new_limit

                # Calculate percentages
                token_pct = min(100, (tokens_used / token_limit) * 100) if token_limit > 0 else 0
                tokens_left = token_limit - tokens_used

                # Time calculations
                start_time_str = active_block.get("startTime")
                if start_time_str:
                    start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                    current_time = datetime.now(start_time.tzinfo)
                else:
                    current_time = datetime.now(timezone.utc)

                # Burn rate
                burn_rate = calculations.calculate_hourly_burn_rate(ccusage_data["blocks"], current_time)

                # Reset time
                reset_time = calculations.get_next_reset_time(current_time, args.reset_hour, args.timezone)
                minutes_to_reset = (reset_time - current_time).total_seconds() / 60
                time_pct = max(0, min(100, ((300 - minutes_to_reset) / 300) * 100))

                # Predictions
                if burn_rate > 0 and tokens_left > 0:
                    minutes_to_depletion = tokens_left / burn_rate
                    predicted_end_time = current_time + timedelta(minutes=minutes_to_depletion)
                else:
                    predicted_end_time = reset_time

                # Format times for display
                try:
                    local_tz = pytz.timezone(args.timezone)
                except pytz.exceptions.UnknownTimeZoneError:
                    local_tz = pytz.timezone("Europe/Warsaw")

                predicted_end_str = predicted_end_time.astimezone(local_tz).strftime("%H:%M")
                reset_time_str = reset_time.astimezone(local_tz).strftime("%H:%M")

                # Build warnings
                warnings: List[Tuple[str, str]] = []
                if tokens_used > 7000 and args.plan == "pro" and token_limit > 7000:
                    warnings.append(
                        (f"🔄 Tokens exceeded Pro limit - switched to custom_max ({token_limit:,})", "yellow")
                    )
                if tokens_used > token_limit:
                    warnings.append((f"🚨 TOKENS EXCEEDED MAX LIMIT! ({tokens_used:,} > {token_limit:,})", "red bold"))
                if predicted_end_time < reset_time and burn_rate > 0:
                    warnings.append(("⚠️  Tokens will run out BEFORE reset!", "red"))

                # Update display
                display.update_display(
                    {
                        "token_pct": token_pct,
                        "time_pct": time_pct,
                        "tokens_used": tokens_used,
                        "token_limit": token_limit,
                        "time_remaining": format_time(minutes_to_reset),
                        "stats": {
                            "tokens_used": tokens_used,
                            "token_limit": token_limit,
                            "tokens_left": tokens_left,
                            "burn_rate": burn_rate,
                            "predicted_end": predicted_end_str,
                            "reset_time": reset_time_str,
                            "cost_usd": cost_usd,
                        },
                        "warnings": warnings,
                        "status_message": "Smooth sailing...",
                    }
                )

                time.sleep(args.refresh)

    except KeyboardInterrupt:
        print("\n\n[cyan]Monitoring stopped.[/cyan]")
        sys.exit(0)


def main() -> None:
    """Main entry point when called directly."""
    from ccusage_monitor.core.config import parse_args

    args = parse_args()
    main_with_args(args)


if __name__ == "__main__":
    main()
