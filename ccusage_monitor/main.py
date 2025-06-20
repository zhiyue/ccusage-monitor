"""Main module for Claude Code Usage Monitor."""

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone

import pytz

# Use optimized modules if available, fallback to original
try:
    from ccusage_monitor import calculations_optimized as calculations
    from ccusage_monitor import data_optimized as data
    from ccusage_monitor import display_optimized as display

    OPTIMIZED = True
except ImportError:
    from ccusage_monitor import (
        calculations,  # type: ignore[no-redef]
        data,  # type: ignore[no-redef]
        display,  # type: ignore[no-redef]
    )

    OPTIMIZED = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Claude Token Monitor - Real-time token usage monitoring"
    )
    parser.add_argument(
        "--plan",
        type=str,
        default="pro",
        choices=["pro", "max5", "max20", "custom_max"],
        help='Claude plan type (default: pro). Use "custom_max" to auto-detect from highest previous block',
    )
    parser.add_argument(
        "--reset-hour", type=int, help="Change the reset hour (0-23) for daily limits"
    )
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
    return parser.parse_args()


def main():
    """Main monitoring loop."""
    args = parse_args()

    # Check if ccusage is installed
    if not data.check_ccusage_installed():
        print("\n❌ Cannot proceed without ccusage. Exiting.")
        sys.exit(1)

    # For 'custom_max' plan, we need to get data first to determine the limit
    if args.plan == "custom_max":
        initial_data = data.run_ccusage()
        if initial_data and "blocks" in initial_data:
            token_limit = data.get_token_limit(args.plan, initial_data["blocks"])
        else:
            token_limit = data.get_token_limit("pro")  # Fallback to pro
    else:
        token_limit = data.get_token_limit(args.plan)

    try:
        # Initial screen clear and hide cursor
        display.clear_screen()
        display.hide_cursor()

        while True:
            # Move cursor to top without clearing
            display.move_cursor_to_top()

            ccusage_data = data.run_ccusage()
            if not ccusage_data or "blocks" not in ccusage_data:
                print("Failed to get usage data")
                continue

            # Find the active block
            active_block = None
            for block in ccusage_data["blocks"]:
                if block.get("isActive", False):
                    active_block = block
                    break

            if not active_block:
                print("No active session found")
                continue

            # Extract data from active block
            tokens_used = active_block.get("totalTokens", 0)

            # Check if tokens exceed limit and switch to custom_max if needed
            if tokens_used > token_limit and args.plan == "pro":
                # Auto-switch to custom_max when pro limit is exceeded
                new_limit = data.get_token_limit("custom_max", ccusage_data["blocks"])
                if new_limit > token_limit:
                    token_limit = new_limit

            usage_percentage = (
                (tokens_used / token_limit) * 100 if token_limit > 0 else 0
            )
            tokens_left = token_limit - tokens_used

            # Time calculations
            start_time_str = active_block.get("startTime")
            if start_time_str:
                start_time = datetime.fromisoformat(
                    start_time_str.replace("Z", "+00:00")
                )
                current_time = datetime.now(start_time.tzinfo)
            else:
                current_time = datetime.now(timezone.utc)

            # Calculate burn rate from ALL sessions in the last hour
            burn_rate = calculations.calculate_hourly_burn_rate(
                ccusage_data["blocks"], current_time
            )

            # Reset time calculation - use fixed schedule or custom hour with timezone
            reset_time = calculations.get_next_reset_time(
                current_time, args.reset_hour, args.timezone
            )

            # Calculate time to reset
            time_to_reset = reset_time - current_time
            minutes_to_reset = time_to_reset.total_seconds() / 60

            # Predicted end calculation - when tokens will run out based on burn rate
            if burn_rate > 0 and tokens_left > 0:
                minutes_to_depletion = tokens_left / burn_rate
                predicted_end_time = current_time + timedelta(
                    minutes=minutes_to_depletion
                )
            else:
                # If no burn rate or tokens already depleted, use reset time
                predicted_end_time = reset_time

            # Color codes
            cyan = "\033[96m"
            red = "\033[91m"
            yellow = "\033[93m"
            white = "\033[97m"
            gray = "\033[90m"
            green = "\033[92m"
            reset = "\033[0m"

            # Display header
            display.print_header()

            # Token Usage section
            print(
                f"📊 {white}Token Usage:{reset}    {display.create_token_progress_bar(usage_percentage)}"
            )
            print()

            # Time to Reset section - calculate progress based on time since last reset
            # Estimate time since last reset (max 5 hours = 300 minutes)
            time_since_reset = max(0, 300 - minutes_to_reset)
            print(
                f"⏳ {white}Time to Reset:{reset}  {display.create_time_progress_bar(time_since_reset, 300)}"
            )
            print()

            # Detailed stats
            print(
                f"🎯 {white}Tokens:{reset}         {white}{tokens_used:,}{reset} / {gray}~{token_limit:,}{reset} ({cyan}{tokens_left:,} left{reset})"
            )
            print(
                f"🔥 {white}Burn Rate:{reset}      {yellow}{burn_rate:.1f}{reset} {gray}tokens/min{reset}"
            )
            print()

            # Predictions - convert to configured timezone for display
            try:
                local_tz = pytz.timezone(args.timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                local_tz = pytz.timezone("Europe/Warsaw")
            predicted_end_local = predicted_end_time.astimezone(local_tz)
            reset_time_local = reset_time.astimezone(local_tz)

            predicted_end_str = predicted_end_local.strftime("%H:%M")
            reset_time_str = reset_time_local.strftime("%H:%M")
            print(f"🏁 {white}Predicted End:{reset} {predicted_end_str}")
            print(f"🔄 {white}Token Reset:{reset}   {reset_time_str}")
            print()

            # Show notification if we switched to custom_max
            show_switch_notification = False
            if tokens_used > 7000 and args.plan == "pro" and token_limit > 7000:
                show_switch_notification = True

            # Notification when tokens exceed max limit
            show_exceed_notification = tokens_used > token_limit

            # Show notifications
            if show_switch_notification:
                print(
                    f"🔄 {yellow}Tokens exceeded Pro limit - switched to custom_max ({token_limit:,}){reset}"
                )
                print()

            if show_exceed_notification:
                print(
                    f"🚨 {red}TOKENS EXCEEDED MAX LIMIT! ({tokens_used:,} > {token_limit:,}){reset}"
                )
                print()

            # Warning if tokens will run out before reset
            if predicted_end_time < reset_time:
                print(f"⚠️  {red}Tokens will run out BEFORE reset!{reset}")
                print()

            # Status line
            current_time_str = datetime.now().strftime("%H:%M:%S")
            perf_indicator = (
                f" | {green}⚡ OPTIMIZED{reset}"
                if OPTIMIZED and args.performance
                else ""
            )
            print(
                f"⏰ {gray}{current_time_str}{reset} 📝 {cyan}Smooth sailing...{reset}{perf_indicator} | {gray}Ctrl+C to exit{reset} 🟨"
            )

            # Clear any remaining lines below to prevent artifacts
            display.clear_below_cursor()

            # Flush buffer if using optimized display
            if OPTIMIZED and hasattr(display, "_buffer"):
                display._buffer.flush()

            time.sleep(3)

    except KeyboardInterrupt:
        # Show cursor before exiting
        display.show_cursor()
        print(f"\n\n{cyan}Monitoring stopped.{reset}")
        # Clear the terminal
        display.clear_screen()
        sys.exit(0)
    except Exception:
        # Show cursor on any error
        display.show_cursor()
        raise


if __name__ == "__main__":
    main()
