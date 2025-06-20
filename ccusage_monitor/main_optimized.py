"""Optimized main module with performance improvements."""

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, cast

import pytz

from ccusage_monitor import calculations_optimized as calculations
from ccusage_monitor import data_optimized as data
from ccusage_monitor import display_optimized as display
from ccusage_monitor.cache import _cache


def parse_args():
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
        "--refresh",
        type=int,
        default=3,
        help="Refresh interval in seconds (default: 3)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Enable fast mode with aggressive caching",
    )
    return parser.parse_args()


class MonitorState:
    """Track monitor state to avoid redundant calculations."""

    def __init__(self):
        self.last_data_hash = None
        self.last_active_block = None
        self.last_burn_rate = 0
        self.last_reset_time = None
        self.token_limit = 0
        self.timezone = None

    def data_changed(self, data: Dict) -> bool:
        """Check if data actually changed."""
        if not data:
            return False

        # Create a simple hash of relevant data
        active_block = next((b for b in data.get("blocks", []) if b.get("isActive")), None)
        if not active_block:
            return False

        data_hash = (
            active_block.get("totalTokens", 0),
            active_block.get("startTime"),
            len(data.get("blocks", [])),
        )

        changed = data_hash != self.last_data_hash
        if changed:
            self.last_data_hash = data_hash
            self.last_active_block = active_block

        return bool(changed)


def format_display_values(
    tokens_used: int,
    token_limit: int,
    burn_rate: float,
    reset_time: datetime,
    predicted_end_time: datetime,
    timezone_str: str,
) -> Dict[str, Any]:
    """Pre-format all display values with caching."""
    cache_key = f"display_{tokens_used}_{token_limit}_{int(burn_rate)}_{reset_time.hour}"
    cached = _cache.get(cache_key, ttl=10)
    if cached is not None:
        return cast(Dict[str, Any], cached)

    # Calculate derived values
    usage_percentage = (tokens_used / token_limit) * 100 if token_limit > 0 else 0
    tokens_left = token_limit - tokens_used

    # Get timezone for display
    try:
        local_tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        local_tz = pytz.timezone("Europe/Warsaw")

    result = {
        "usage_percentage": usage_percentage,
        "tokens_used_fmt": f"{tokens_used:,}",
        "token_limit_fmt": f"{token_limit:,}",
        "tokens_left_fmt": f"{tokens_left:,}",
        "burn_rate_fmt": f"{burn_rate:.1f}",
        "predicted_end_str": predicted_end_time.astimezone(local_tz).strftime("%H:%M"),
        "reset_time_str": reset_time.astimezone(local_tz).strftime("%H:%M"),
        "velocity_indicator": calculations.get_velocity_indicator(burn_rate),
        "tokens_left": tokens_left,
    }

    _cache.set(cache_key, result)
    return result


def main():
    """Optimized main monitoring loop."""
    args = parse_args()

    # Check if ccusage is installed
    if not data.check_ccusage_installed():
        print("\n❌ Cannot proceed without ccusage. Exiting.")
        sys.exit(1)

    # Initialize state tracker
    state = MonitorState()
    state.timezone = args.timezone

    # Pre-calculate static values
    cyan = "\033[96m"
    red = "\033[91m"
    yellow = "\033[93m"
    white = "\033[97m"
    gray = "\033[90m"
    reset = "\033[0m"

    # Initial token limit setup
    if args.plan == "custom_max":
        initial_data = data.run_ccusage()
        if initial_data and "blocks" in initial_data:
            state.token_limit = data.get_token_limit(args.plan, initial_data["blocks"])
        else:
            state.token_limit = data.get_token_limit("pro")
    else:
        state.token_limit = data.get_token_limit(args.plan)

    try:
        # Initial screen setup
        display.clear_screen()
        display.hide_cursor()

        # Main loop
        loop_count = 0
        while True:
            loop_count += 1

            # Get data (cached for 5 seconds)
            ccusage_data = data.run_ccusage()
            if not ccusage_data or "blocks" not in ccusage_data:
                print("Failed to get usage data")
                time.sleep(args.refresh)
                continue

            # Check if data actually changed
            if not state.data_changed(ccusage_data) and not args.fast:
                # Skip update if nothing changed
                time.sleep(args.refresh)
                continue

            active_block = state.last_active_block
            if not active_block:
                print("No active session found")
                time.sleep(args.refresh)
                continue

            # Extract data
            tokens_used = active_block.get("totalTokens", 0)

            # Auto-switch logic (only check when needed)
            if tokens_used > state.token_limit and args.plan == "pro":
                new_limit = data.get_token_limit("custom_max", ccusage_data["blocks"])
                if new_limit > state.token_limit:
                    state.token_limit = new_limit

            # Time calculations (cached)
            start_time_str = active_block.get("startTime")
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                current_time = datetime.now(start_time.tzinfo)
            else:
                current_time = datetime.now(timezone.utc)

            # Calculate burn rate (cached for 30 seconds)
            burn_rate = calculations.calculate_hourly_burn_rate(ccusage_data["blocks"], current_time)

            # Reset time (cached for 5 minutes)
            reset_time = calculations.get_next_reset_time(current_time, args.reset_hour, args.timezone)
            minutes_to_reset = (reset_time - current_time).total_seconds() / 60

            # Predicted end time
            if burn_rate > 0 and tokens_used < state.token_limit:
                minutes_to_depletion = (state.token_limit - tokens_used) / burn_rate
                predicted_end_time = current_time + timedelta(minutes=minutes_to_depletion)
            else:
                predicted_end_time = reset_time

            # Format all values at once
            values = format_display_values(
                tokens_used,
                state.token_limit,
                burn_rate,
                reset_time,
                predicted_end_time,
                args.timezone,
            )

            # Build display using buffer
            display.print_header()

            # Token usage
            display._buffer.writeln(
                f"📊 {white}Token Usage:{reset}    {display.create_token_progress_bar(values['usage_percentage'])}"
            )
            display._buffer.writeln()

            # Time to reset
            time_since_reset = max(0, 300 - minutes_to_reset)
            display._buffer.writeln(
                f"⏳ {white}Time to Reset:{reset}  {display.create_time_progress_bar(time_since_reset, 300)}"
            )
            display._buffer.writeln()

            # Stats
            display._buffer.writeln(
                f"🎯 {white}Tokens:{reset}         "
                f"{white}{values['tokens_used_fmt']}{reset} / "
                f"{gray}~{values['token_limit_fmt']}{reset} "
                f"({cyan}{values['tokens_left_fmt']} left{reset})"
            )
            display._buffer.writeln(
                f"🔥 {white}Burn Rate:{reset}      {yellow}{values['burn_rate_fmt']}{reset} {gray}tokens/min{reset}"
            )
            display._buffer.writeln()

            # Predictions
            display._buffer.writeln(f"🏁 {white}Predicted End:{reset} {values['predicted_end_str']}")
            display._buffer.writeln(f"🔄 {white}Token Reset:{reset}   {values['reset_time_str']}")
            display._buffer.writeln()

            # Notifications (only when needed)
            if tokens_used > 7000 and args.plan == "pro" and state.token_limit > 7000:
                display._buffer.writeln(
                    f"🔄 {yellow}Tokens exceeded Pro limit - switched to custom_max ({state.token_limit:,}){reset}"
                )
                display._buffer.writeln()

            if tokens_used > state.token_limit:
                display._buffer.writeln(
                    f"🚨 {red}TOKENS EXCEEDED MAX LIMIT! "
                    f"({values['tokens_used_fmt']} > {values['token_limit_fmt']}){reset}"
                )
                display._buffer.writeln()

            if predicted_end_time < reset_time:
                display._buffer.writeln(f"⚠️  {red}Tokens will run out BEFORE reset!{reset}")
                display._buffer.writeln()

            # Status line
            current_time_str = datetime.now().strftime("%H:%M:%S")
            display._buffer.writeln(
                f"⏰ {gray}{current_time_str}{reset} 📝 {cyan}Smooth sailing...{reset} | {gray}Ctrl+C to exit{reset} 🟨"
            )

            # Flush buffer (only updates if changed)
            display._buffer.flush()

            time.sleep(args.refresh)

    except KeyboardInterrupt:
        display.show_cursor()
        print(f"\n\n{cyan}Monitoring stopped.{reset}")
        display.clear_screen()
        sys.exit(0)
    except Exception:
        display.show_cursor()
        raise


if __name__ == "__main__":
    main()
