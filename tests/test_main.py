#!/usr/bin/env python3
"""Comprehensive unit tests for main module with static typing."""

import os
import sys
import unittest
from datetime import datetime, timezone
from typing import List
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccusage_monitor.main import main, parse_args
from ccusage_monitor.protocols import CcusageData, CLIArgs


class TestParseArgs(unittest.TestCase):
    """Test the parse_args function."""

    def test_default_arguments(self) -> None:
        """Test parsing with default arguments."""
        with patch("sys.argv", ["ccusage_monitor.py"]):
            args: CLIArgs = parse_args()

            self.assertEqual(args.plan, "pro")
            self.assertIsNone(args.reset_hour)
            self.assertEqual(args.timezone, "Europe/Warsaw")
            self.assertFalse(args.performance)
            self.assertFalse(args.rich)
            self.assertEqual(args.refresh, 3)

    def test_plan_argument(self) -> None:
        """Test parsing plan argument."""
        test_cases: List[str] = ["pro", "max5", "max20", "custom_max"]

        for plan in test_cases:
            with patch("sys.argv", ["ccusage_monitor.py", "--plan", plan]):
                args: CLIArgs = parse_args()
                self.assertEqual(args.plan, plan)

    def test_reset_hour_argument(self) -> None:
        """Test parsing reset hour argument."""
        with patch("sys.argv", ["ccusage_monitor.py", "--reset-hour", "10"]):
            args: CLIArgs = parse_args()
            self.assertEqual(args.reset_hour, 10)

    def test_timezone_argument(self) -> None:
        """Test parsing timezone argument."""
        with patch("sys.argv", ["ccusage_monitor.py", "--timezone", "US/Eastern"]):
            args: CLIArgs = parse_args()
            self.assertEqual(args.timezone, "US/Eastern")

    def test_performance_flag(self) -> None:
        """Test parsing performance flag."""
        with patch("sys.argv", ["ccusage_monitor.py", "--performance"]):
            args: CLIArgs = parse_args()
            self.assertTrue(args.performance)

    def test_rich_flag(self) -> None:
        """Test parsing rich flag."""
        with patch("sys.argv", ["ccusage_monitor.py", "--rich"]):
            args: CLIArgs = parse_args()
            self.assertTrue(args.rich)

    def test_refresh_argument(self) -> None:
        """Test parsing refresh interval."""
        with patch("sys.argv", ["ccusage_monitor.py", "--refresh", "5"]):
            args: CLIArgs = parse_args()
            self.assertEqual(args.refresh, 5)

    def test_multiple_arguments(self) -> None:
        """Test parsing multiple arguments together."""
        with patch(
            "sys.argv",
            [
                "ccusage_monitor.py",
                "--plan",
                "max20",
                "--reset-hour",
                "15",
                "--timezone",
                "Asia/Tokyo",
                "--performance",
                "--refresh",
                "10",
            ],
        ):
            args: CLIArgs = parse_args()

            self.assertEqual(args.plan, "max20")
            self.assertEqual(args.reset_hour, 15)
            self.assertEqual(args.timezone, "Asia/Tokyo")
            self.assertTrue(args.performance)
            self.assertEqual(args.refresh, 10)


class TestMainFunction(unittest.TestCase):
    """Test the main function."""

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_no_ccusage_installed(self, mock_exit: Mock, mock_print: Mock, mock_check: Mock) -> None:
        """Test main exits when ccusage is not installed."""
        mock_check.return_value = False

        with patch("sys.argv", ["ccusage_monitor.py"]):
            main()

        # Should print error and exit
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Cannot proceed without ccusage" in str(call) for call in print_calls))
        mock_exit.assert_called_once_with(1)

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("ccusage_monitor.data.run_ccusage")
    @patch("ccusage_monitor.display.clear_screen")
    @patch("ccusage_monitor.display.hide_cursor")
    @patch("ccusage_monitor.display.show_cursor")
    @patch("builtins.print")
    @patch("time.sleep")
    @patch("sys.exit")
    def test_main_no_data(
        self,
        mock_exit: Mock,
        mock_sleep: Mock,
        mock_print: Mock,
        mock_show_cursor: Mock,
        mock_hide_cursor: Mock,
        mock_clear_screen: Mock,
        mock_run: Mock,
        mock_check: Mock,
    ) -> None:
        """Test main handles missing data gracefully."""
        mock_check.return_value = True
        mock_run.return_value = None  # No data

        # Make sleep raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["ccusage_monitor.py"]):
            main()

        # Should print error message
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Failed to get usage data" in str(call) for call in print_calls))
        mock_exit.assert_called_once_with(0)

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("ccusage_monitor.data.run_ccusage")
    @patch("ccusage_monitor.display.clear_screen")
    @patch("ccusage_monitor.display.hide_cursor")
    @patch("ccusage_monitor.display.show_cursor")
    @patch("builtins.print")
    @patch("time.sleep")
    @patch("sys.exit")
    def test_main_no_active_session(
        self,
        mock_exit: Mock,
        mock_sleep: Mock,
        mock_print: Mock,
        mock_show_cursor: Mock,
        mock_hide_cursor: Mock,
        mock_clear_screen: Mock,
        mock_run: Mock,
        mock_check: Mock,
    ) -> None:
        """Test main handles no active session."""
        mock_check.return_value = True
        mock_run.return_value = {"blocks": [{"isActive": False, "totalTokens": 1000}]}

        # Make sleep raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["ccusage_monitor.py"]):
            main()

        # Should print no active session message
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("No active session found" in str(call) for call in print_calls))

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("ccusage_monitor.data.run_ccusage")
    @patch("ccusage_monitor.data.get_token_limit")
    @patch("ccusage_monitor.calculations.calculate_hourly_burn_rate")
    @patch("ccusage_monitor.calculations.get_next_reset_time")
    @patch("ccusage_monitor.display.clear_screen")
    @patch("ccusage_monitor.display.hide_cursor")
    @patch("ccusage_monitor.display.show_cursor")
    @patch("builtins.print")
    @patch("time.sleep")
    @patch("sys.exit")
    def test_main_normal_operation(
        self,
        mock_exit: Mock,
        mock_sleep: Mock,
        mock_print: Mock,
        mock_show_cursor: Mock,
        mock_hide_cursor: Mock,
        mock_clear_screen: Mock,
        mock_reset_time: Mock,
        mock_burn_rate: Mock,
        mock_token_limit: Mock,
        mock_run: Mock,
        mock_check: Mock,
    ) -> None:
        """Test main function normal operation."""
        # Setup mocks
        mock_check.return_value = True
        current_time: datetime = datetime.now(timezone.utc)
        mock_run.return_value = {
            "blocks": [{"isActive": True, "totalTokens": 5000, "startTime": current_time.isoformat()}]
        }
        mock_token_limit.return_value = 7000
        mock_burn_rate.return_value = 100.0
        mock_reset_time.return_value = current_time

        # Make sleep raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["ccusage_monitor.py"]):
            main()

        # Verify display functions were called
        mock_clear_screen.assert_called()
        mock_hide_cursor.assert_called()
        mock_show_cursor.assert_called()

        # Verify calculations were performed
        mock_burn_rate.assert_called()
        mock_reset_time.assert_called()

        # Should exit cleanly
        mock_exit.assert_called_once_with(0)

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("ccusage_monitor.main_rich.main_with_args")
    def test_main_rich_mode(self, mock_rich_main: Mock, mock_check: Mock) -> None:
        """Test main function with --rich flag."""
        mock_check.return_value = True

        with patch("sys.argv", ["ccusage_monitor.py", "--rich"]):
            main()

        # Should call rich main instead
        mock_rich_main.assert_called_once()
        args = mock_rich_main.call_args[0][0]
        self.assertTrue(args.rich)

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_rich_import_error(self, mock_exit: Mock, mock_print: Mock, mock_check: Mock) -> None:
        """Test main handles Rich import error."""
        mock_check.return_value = True

        with patch("sys.argv", ["ccusage_monitor.py", "--rich"]):
            # Mock import error
            with patch("ccusage_monitor.main.main_rich", side_effect=ImportError()):
                main()

        # Should print error message
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Rich library not installed" in str(call) for call in print_calls))
        mock_exit.assert_called_once_with(1)


class TestCustomMaxPlan(unittest.TestCase):
    """Test custom_max plan handling."""

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("ccusage_monitor.data.run_ccusage")
    @patch("ccusage_monitor.data.get_token_limit")
    @patch("ccusage_monitor.display.clear_screen")
    @patch("ccusage_monitor.display.hide_cursor")
    @patch("ccusage_monitor.display.show_cursor")
    @patch("time.sleep")
    @patch("sys.exit")
    def test_custom_max_initialization(
        self,
        mock_exit: Mock,
        mock_sleep: Mock,
        mock_show_cursor: Mock,
        mock_hide_cursor: Mock,
        mock_clear_screen: Mock,
        mock_token_limit: Mock,
        mock_run: Mock,
        mock_check: Mock,
    ) -> None:
        """Test custom_max plan initialization."""
        mock_check.return_value = True

        # Setup initial data for custom_max
        initial_data: CcusageData = {
            "blocks": [{"isActive": False, "totalTokens": 35000}, {"isActive": True, "totalTokens": 5000}]
        }
        mock_run.return_value = initial_data

        # First call returns custom limit, then regular calls
        mock_token_limit.side_effect = [35000, 35000]

        # Make sleep raise KeyboardInterrupt
        mock_sleep.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["ccusage_monitor.py", "--plan", "custom_max"]):
            main()

        # Should call get_token_limit with blocks
        calls = mock_token_limit.call_args_list
        self.assertEqual(calls[0][0][0], "custom_max")
        self.assertEqual(calls[0][0][1], initial_data["blocks"])


class TestAutoSwitchToCustomMax(unittest.TestCase):
    """Test automatic switching to custom_max when pro limit exceeded."""

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("ccusage_monitor.data.run_ccusage")
    @patch("ccusage_monitor.data.get_token_limit")
    @patch("ccusage_monitor.calculations.calculate_hourly_burn_rate")
    @patch("ccusage_monitor.calculations.get_next_reset_time")
    @patch("ccusage_monitor.display.clear_screen")
    @patch("ccusage_monitor.display.hide_cursor")
    @patch("ccusage_monitor.display.show_cursor")
    @patch("builtins.print")
    @patch("time.sleep")
    @patch("sys.exit")
    def test_auto_switch_to_custom_max(
        self,
        mock_exit: Mock,
        mock_sleep: Mock,
        mock_print: Mock,
        mock_show_cursor: Mock,
        mock_hide_cursor: Mock,
        mock_clear_screen: Mock,
        mock_reset_time: Mock,
        mock_burn_rate: Mock,
        mock_token_limit: Mock,
        mock_run: Mock,
        mock_check: Mock,
    ) -> None:
        """Test auto-switching to custom_max when tokens exceed pro limit."""
        mock_check.return_value = True
        current_time: datetime = datetime.now(timezone.utc)

        # Tokens exceed pro limit
        mock_run.return_value = {
            "blocks": [
                {
                    "isActive": True,
                    "totalTokens": 8000,  # > 7000
                    "startTime": current_time.isoformat(),
                }
            ]
        }

        # First returns pro limit, then custom_max limit
        mock_token_limit.side_effect = [7000, 35000]
        mock_burn_rate.return_value = 100.0
        mock_reset_time.return_value = current_time

        # Make sleep raise KeyboardInterrupt
        mock_sleep.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["ccusage_monitor.py", "--plan", "pro"]):
            main()

        # Should have called get_token_limit twice
        self.assertEqual(mock_token_limit.call_count, 2)

        # Should show switch notification
        output: str = "".join(str(call) for call in mock_print.call_args_list)
        self.assertIn("custom_max", output)


class TestOptimizedModuleLoading(unittest.TestCase):
    """Test loading of optimized modules."""

    @patch("ccusage_monitor.data.check_ccusage_installed")
    @patch("ccusage_monitor.data.run_ccusage")
    @patch("builtins.print")
    @patch("time.sleep")
    @patch("sys.exit")
    def test_performance_indicator(
        self, mock_exit: Mock, mock_sleep: Mock, mock_print: Mock, mock_run: Mock, mock_check: Mock
    ) -> None:
        """Test performance indicator when optimized modules are loaded."""
        mock_check.return_value = True
        current_time: datetime = datetime.now(timezone.utc)
        mock_run.return_value = {
            "blocks": [{"isActive": True, "totalTokens": 5000, "startTime": current_time.isoformat()}]
        }

        # Make sleep raise KeyboardInterrupt
        mock_sleep.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["ccusage_monitor.py", "--performance"]):
            # Check if OPTIMIZED flag affects output
            from ccusage_monitor import main as main_module

            if hasattr(main_module, "OPTIMIZED") and main_module.OPTIMIZED:
                main()

                # Should show optimized indicator
                output: str = "".join(str(call) for call in mock_print.call_args_list)
                self.assertIn("⚡ OPTIMIZED", output)


if __name__ == "__main__":
    unittest.main()
