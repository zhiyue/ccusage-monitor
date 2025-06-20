#!/usr/bin/env python3
"""Comprehensive unit tests for display module with static typing."""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccusage_monitor import display


class TestFormatTime(unittest.TestCase):
    """Test the format_time function."""

    def test_format_minutes_only(self) -> None:
        """Test formatting when time is less than an hour."""
        self.assertEqual(display.format_time(0), "0m")
        self.assertEqual(display.format_time(1), "1m")
        self.assertEqual(display.format_time(30), "30m")
        self.assertEqual(display.format_time(59), "59m")
        self.assertEqual(display.format_time(59.99), "59m")

    def test_format_hours_only(self) -> None:
        """Test formatting when time is exactly hours."""
        self.assertEqual(display.format_time(60), "1h")
        self.assertEqual(display.format_time(120), "2h")
        self.assertEqual(display.format_time(180), "3h")
        self.assertEqual(display.format_time(300), "5h")
        self.assertEqual(display.format_time(1440), "24h")

    def test_format_hours_and_minutes(self) -> None:
        """Test formatting when time has both hours and minutes."""
        self.assertEqual(display.format_time(61), "1h 1m")
        self.assertEqual(display.format_time(90), "1h 30m")
        self.assertEqual(display.format_time(125), "2h 5m")
        self.assertEqual(display.format_time(315), "5h 15m")
        self.assertEqual(display.format_time(1500), "25h")  # 0 minutes case returns just hours

    def test_format_negative_time(self) -> None:
        """Test formatting negative time values."""
        self.assertEqual(display.format_time(-30), "-30m")
        # Negative values are handled as is by the function
        self.assertEqual(display.format_time(-90), "-90m")

    def test_format_float_values(self) -> None:
        """Test formatting with float values."""
        self.assertEqual(display.format_time(30.7), "30m")
        self.assertEqual(display.format_time(60.5), "1h")
        self.assertEqual(display.format_time(90.3), "1h 30m")


class TestCreateTokenProgressBar(unittest.TestCase):
    """Test the create_token_progress_bar function."""

    def test_zero_percentage(self) -> None:
        """Test progress bar with 0%."""
        result: str = display.create_token_progress_bar(0, width=10)
        self.assertIn("0.0%", result)
        self.assertIn("░░░░░░░░░░", result)
        self.assertIn("🟢", result)
        self.assertIn("\033[92m", result)  # Green color
        self.assertIn("\033[91m", result)  # Red color

    def test_full_percentage(self) -> None:
        """Test progress bar with 100%."""
        result: str = display.create_token_progress_bar(100, width=10)
        self.assertIn("100.0%", result)
        self.assertIn("██████████", result)
        self.assertIn("🟢", result)

    def test_partial_percentages(self) -> None:
        """Test progress bar with various percentages."""
        # 25%
        result: str = display.create_token_progress_bar(25, width=10)
        self.assertIn("25.0%", result)
        self.assertIn("██", result)
        self.assertIn("░░░░░░░░", result)

        # 50%
        result2: str = display.create_token_progress_bar(50, width=10)
        self.assertIn("50.0%", result2)
        self.assertIn("█████", result2)
        self.assertIn("░░░░░", result2)

        # 75%
        result3: str = display.create_token_progress_bar(75, width=10)
        self.assertIn("75.0%", result3)
        self.assertIn("███████", result3)
        self.assertIn("░░░", result3)

    def test_custom_width(self) -> None:
        """Test progress bar with custom width."""
        result: str = display.create_token_progress_bar(50, width=20)
        self.assertIn("50.0%", result)
        self.assertIn("██████████", result)  # 10 filled blocks
        self.assertIn("░░░░░░░░░░", result)  # 10 empty blocks

    def test_percentage_precision(self) -> None:
        """Test that percentage is formatted with 1 decimal place."""
        result: str = display.create_token_progress_bar(33.33333, width=10)
        self.assertIn("33.3%", result)

    def test_over_100_percentage(self) -> None:
        """Test progress bar with over 100%."""
        result: str = display.create_token_progress_bar(150, width=10)
        self.assertIn("150.0%", result)
        self.assertIn("██████████", result)  # All filled


class TestCreateTimeProgressBar(unittest.TestCase):
    """Test the create_time_progress_bar function."""

    def test_zero_progress(self) -> None:
        """Test time progress bar with no time elapsed."""
        result: str = display.create_time_progress_bar(0, 300, width=10)
        self.assertIn("5h", result)  # 300 minutes remaining
        self.assertIn("░░░░░░░░░░", result)
        self.assertIn("⏰", result)
        self.assertIn("\033[94m", result)  # Blue color

    def test_full_progress(self) -> None:
        """Test time progress bar with all time elapsed."""
        result: str = display.create_time_progress_bar(300, 300, width=10)
        self.assertIn("0m", result)  # 0 minutes remaining
        self.assertIn("██████████", result)
        self.assertIn("⏰", result)

    def test_partial_progress(self) -> None:
        """Test time progress bar with partial progress."""
        result: str = display.create_time_progress_bar(150, 300, width=10)
        self.assertIn("2h 30m", result)  # 150 minutes remaining
        self.assertIn("█████", result)  # 50% filled
        self.assertIn("░░░░░", result)

    def test_zero_total_minutes(self) -> None:
        """Test handling of zero total minutes."""
        result: str = display.create_time_progress_bar(100, 0, width=10)
        self.assertIn("0m", result)
        self.assertIn("░░░░░░░░░░", result)  # No progress

    def test_negative_total_minutes(self) -> None:
        """Test handling of negative total minutes."""
        result: str = display.create_time_progress_bar(100, -300, width=10)
        self.assertIn("0m", result)
        self.assertIn("░░░░░░░░░░", result)  # No progress

    def test_elapsed_exceeds_total(self) -> None:
        """Test when elapsed time exceeds total time."""
        result: str = display.create_time_progress_bar(400, 300, width=10)
        self.assertIn("0m", result)  # No negative time
        self.assertIn("██████████", result)  # 100% filled

    def test_custom_width(self) -> None:
        """Test time progress bar with custom width."""
        result: str = display.create_time_progress_bar(100, 200, width=20)
        self.assertIn("1h 40m", result)  # 100 minutes remaining
        self.assertIn("██████████", result)  # 10 filled blocks (50%)

    def test_float_values(self) -> None:
        """Test time progress bar with float values."""
        result: str = display.create_time_progress_bar(150.5, 300.0, width=10)
        # Should handle floats properly
        self.assertIn("h", result)
        self.assertIn("m", result)


class TestPrintHeader(unittest.TestCase):
    """Test the print_header function."""

    @patch("builtins.print")
    def test_print_header_output(self, mock_print: Mock) -> None:
        """Test that header is printed with correct content."""
        display.print_header()

        # Verify print was called
        self.assertTrue(mock_print.called)

        # Get all printed content
        printed_content: str = ""
        for call in mock_print.call_args_list:
            if call[0]:  # If there are positional arguments
                printed_content += str(call[0][0])
            else:  # Empty print() call
                printed_content += "\n"

        # Check for expected content
        self.assertIn("CLAUDE TOKEN MONITOR", printed_content)
        self.assertIn("✦ ✧ ✦ ✧", printed_content)
        self.assertIn("=" * 60, printed_content)
        self.assertIn("\033[96m", printed_content)  # Cyan color
        self.assertIn("\033[94m", printed_content)  # Blue color
        self.assertIn("\033[0m", printed_content)  # Reset color

    @patch("builtins.print")
    def test_print_header_call_count(self, mock_print: Mock) -> None:
        """Test that header prints the expected number of lines."""
        display.print_header()

        # Should print: sparkles + title, separator line, empty line
        self.assertEqual(mock_print.call_count, 3)


class TestTerminalControlFunctions(unittest.TestCase):
    """Test terminal control functions."""

    @patch("builtins.print")
    def test_clear_screen(self, mock_print: Mock) -> None:
        """Test clear_screen function."""
        display.clear_screen()
        mock_print.assert_called_once_with("\033[2J\033[3J\033[H", end="", flush=True)

    @patch("builtins.print")
    def test_hide_cursor(self, mock_print: Mock) -> None:
        """Test hide_cursor function."""
        display.hide_cursor()
        mock_print.assert_called_once_with("\033[?25l", end="", flush=True)

    @patch("builtins.print")
    def test_show_cursor(self, mock_print: Mock) -> None:
        """Test show_cursor function."""
        display.show_cursor()
        mock_print.assert_called_once_with("\033[?25h", end="", flush=True)

    @patch("builtins.print")
    def test_move_cursor_to_top(self, mock_print: Mock) -> None:
        """Test move_cursor_to_top function."""
        display.move_cursor_to_top()
        mock_print.assert_called_once_with("\033[H", end="", flush=True)

    @patch("builtins.print")
    def test_clear_below_cursor(self, mock_print: Mock) -> None:
        """Test clear_below_cursor function."""
        display.clear_below_cursor()
        mock_print.assert_called_once_with("\033[J", end="", flush=True)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_progress_bar_negative_percentage(self) -> None:
        """Test progress bar with negative percentage."""
        result: str = display.create_token_progress_bar(-10, width=10)
        self.assertIn("-10.0%", result)
        self.assertIn("░░░░░░░░░░", result)  # All empty

    def test_progress_bar_zero_width(self) -> None:
        """Test progress bar with zero width."""
        result: str = display.create_token_progress_bar(50, width=0)
        self.assertIn("50.0%", result)
        self.assertNotIn("█", result)
        self.assertNotIn("░", result)

    def test_progress_bar_negative_width(self) -> None:
        """Test progress bar with negative width."""
        result: str = display.create_token_progress_bar(50, width=-10)
        self.assertIn("50.0%", result)
        # Should handle gracefully, no blocks

    def test_time_progress_bar_edge_cases(self) -> None:
        """Test time progress bar edge cases."""
        # Very large values
        result: str = display.create_time_progress_bar(1000000, 2000000, width=10)
        self.assertIn("h", result)

        # Negative elapsed time
        result2: str = display.create_time_progress_bar(-100, 300, width=10)
        # Should handle gracefully
        self.assertIn("░░░░░░░░░░", result2)


if __name__ == "__main__":
    unittest.main()
