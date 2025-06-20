#!/usr/bin/env python3
"""Comprehensive unit tests for optimized display module."""

import os
import sys
import time
import unittest
from io import StringIO
from typing import Optional, List
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccusage_monitor import display_optimized
from ccusage_monitor.cache import cache


class TestOutputBuffer(unittest.TestCase):
    """Test the OutputBuffer class."""

    def setUp(self) -> None:
        """Set up a new buffer for each test."""
        self.buffer: display_optimized.OutputBuffer = display_optimized.OutputBuffer()

    def test_write(self) -> None:
        """Test the write method."""
        self.buffer.write("Hello")
        self.buffer.write(" World")
        self.assertEqual(self.buffer.buffer.getvalue(), "Hello World")

    def test_writeln(self) -> None:
        """Test the writeln method."""
        self.buffer.writeln("Line 1")
        self.buffer.writeln("Line 2")
        self.assertEqual(self.buffer.buffer.getvalue(), "Line 1\nLine 2\n")

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.print")
    def test_flush_with_changes(self, mock_print: Mock, mock_stdout: StringIO) -> None:
        """Test flush when buffer content has changed."""
        self.buffer.writeln("New Content")
        self.buffer.flush()

        # Check that print was called to clear and print
        self.assertTrue(mock_print.called)

        # Check that content was written to stdout
        self.assertIn("New Content", mock_stdout.getvalue())
        self.assertEqual(self.buffer.last_output, "New Content\n")

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.print")
    def test_flush_no_changes(self, mock_print: Mock, mock_stdout: StringIO) -> None:
        """Test flush when buffer content is the same."""
        # Initial flush
        self.buffer.writeln("Initial Content")
        self.buffer.flush()
        mock_print.reset_mock()
        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        # Second flush with same content
        self.buffer.writeln("Initial Content")
        self.buffer.flush()

        # Print should not be called again
        self.assertFalse(mock_print.called)
        self.assertEqual(mock_stdout.getvalue(), "")

    def test_buffer_reset_after_flush(self) -> None:
        """Test that the buffer is cleared after a flush."""
        self.buffer.writeln("Some data")
        self.buffer.flush()
        self.assertEqual(self.buffer.buffer.getvalue(), "")

    def test_last_output_tracking(self) -> None:
        """Test that last_output is correctly updated."""
        self.buffer.writeln("First")
        self.buffer.flush()
        self.assertEqual(self.buffer.last_output, "First\n")

        self.buffer.writeln("Second")
        self.buffer.flush()
        self.assertEqual(self.buffer.last_output, "Second\n")


class TestGlobalBufferFunctions(unittest.TestCase):
    """Test global buffer functions."""

    def setUp(self) -> None:
        """Reset the global buffer before each test."""
        display_optimized._buffer.buffer = StringIO()
        display_optimized._buffer.last_output = ""

    def test_write_to_buffer(self) -> None:
        """Test the global write function."""
        display_optimized.write_to_buffer("A")
        display_optimized.write_to_buffer("B")
        self.assertEqual(display_optimized._buffer.buffer.getvalue(), "AB")

    def test_writeln(self) -> None:
        """Test the global writeln function."""
        display_optimized.writeln("Hello")
        self.assertEqual(display_optimized._buffer.buffer.getvalue(), "Hello\n")

    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.print")
    def test_flush_buffer(self, mock_print: Mock, mock_stdout: StringIO) -> None:
        """Test the global flush function."""
        display_optimized.writeln("Testing flush")
        display_optimized.flush_buffer()

        self.assertTrue(mock_print.called)
        self.assertIn("Testing flush", mock_stdout.getvalue())


class TestPrintHeaderOptimized(unittest.TestCase):
    """Test the optimized print_header function."""

    def setUp(self) -> None:
        """Clear cache and buffer before each test."""
        cache.clear()
        display_optimized._buffer.buffer = StringIO()

    def test_print_header_caching(self) -> None:
        """Test that the header is cached."""
        display_optimized.print_header()

        # Check cache
        header_str: str = display_optimized._buffer.buffer.getvalue()
        cached_header = cache.get("header_cached")
        self.assertIsNotNone(cached_header)
        self.assertTrue(cached_header)

    def test_print_header_uses_cache(self) -> None:
        """Test that print_header uses the cache on second call."""
        # First call
        display_optimized.print_header()

        # Manually clear buffer to simulate new run
        display_optimized._buffer.buffer = []

        # Second call
        display_optimized.print_header()
        # If cache is used, buffer will contain same header
        self.assertIn("CLAUDE TOKEN MONITOR", display_optimized._buffer.buffer[0])


class TestCreateTokenProgressBarOptimized(unittest.TestCase):
    """Test the optimized create_token_progress_bar function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    def test_token_progress_bar_caching(self) -> None:
        """Test that token progress bars are cached."""
        percentage: float = 75.5
        width: int = 50

        # First call
        result1: str = display_optimized.create_token_progress_bar(percentage, width)

        # Check cache
        cache_key: str = f"token_bar_{percentage:.1f}_{width}"
        cached: Optional[Any] = cache.get(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached, result1)

        # Second call should return same result
        result2: str = display_optimized.create_token_progress_bar(percentage, width)
        self.assertEqual(result1, result2)

    def test_token_progress_bar_percentage_rounding(self) -> None:
        """Test that percentage is rounded for caching."""
        # These should all use the same cache entry
        result1: str = display_optimized.create_token_progress_bar(50.04, 50)
        result2: str = display_optimized.create_token_progress_bar(50.06, 50)

        # Different enough to have different cache
        result3: str = display_optimized.create_token_progress_bar(50.14, 50)

        # First two should be identical (same cache)
        self.assertEqual(result1, result2)
        # Third might be different
        # (depending on rounding, 50.14 rounds to 50.1)
        self.assertNotEqual(result1, result3)

    def test_token_progress_bar_content(self) -> None:
        """Test progress bar content."""
        result: str = display_optimized.create_token_progress_bar(75.5, width=20)

        # Should contain percentage
        self.assertIn("75.5%", result)
        # Should contain green circle
        self.assertIn("🟢", result)
        # Should contain filled blocks (about 15 out of 20)
        self.assertIn("█" * 15, result)
        # Should contain color codes
        self.assertIn("\033[92m", result)  # Green
        self.assertIn("\033[91m", result)  # Red


class TestCreateTimeProgressBarOptimized(unittest.TestCase):
    """Test the optimized create_time_progress_bar function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    def test_time_progress_bar_caching(self) -> None:
        """Test that time progress bars are cached."""
        elapsed: float = 150.0
        total: float = 300.0
        width: int = 50

        # First call
        result1: str = display_optimized.create_time_progress_bar(elapsed, total, width)

        # Check cache
        cache_key: str = f"time_bar_{round(elapsed)}_{total}_{width}"
        cached: Optional[Any] = cache.get(cache_key)
        self.assertIsNotNone(cached)

        # Second call should use cache
        result2: str = display_optimized.create_time_progress_bar(elapsed, total, width)
        self.assertEqual(result1, result2)

    def test_time_progress_bar_elapsed_rounding(self) -> None:
        """Test that elapsed time is rounded for caching."""
        # These should use same cache (both round to 150)
        result1: str = display_optimized.create_time_progress_bar(149.6, 300, 50)
        result2: str = display_optimized.create_time_progress_bar(150.4, 300, 50)

        self.assertEqual(result1, result2)

    def test_time_progress_bar_content(self) -> None:
        """Test time progress bar content."""
        result: str = display_optimized.create_time_progress_bar(100, 200, width=20)

        # Should contain remaining time (100 minutes)
        self.assertIn("1h 40m", result)
        # Should contain clock emoji
        self.assertIn("⏰", result)
        # Should be 50% filled (10 blocks)
        self.assertIn("█" * 10, result)
        # Should contain color codes
        self.assertIn("\033[94m", result)  # Blue


class TestFormatTimeOptimized(unittest.TestCase):
    """Test the optimized format_time function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    def test_format_time_caching(self) -> None:
        """Test that formatted times are cached."""
        minutes: float = 125.0

        # First call
        result1: str = display_optimized.format_time(minutes)

        # Check cache
        cache_key: str = f"time_format_{round(minutes)}"
        cached: Optional[Any] = cache.get(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached, result1)

        # Second call should use cache
        result2: str = display_optimized.format_time(minutes)
        self.assertEqual(result1, result2)

    def test_format__time_rounding(self) -> None:
        """Test that minutes are rounded for caching."""
        # These should use same cache (both round to 90)
        result1: str = display_optimized.format_time(89.6)
        result2: str = display_optimized.format_time(90.4)

        self.assertEqual(result1, result2)
        self.assertEqual(result1, "1h 30m")

    def test_format_time_various_values(self) -> None:
        """Test format_time with various values."""
        self.assertEqual(display_optimized.format_time(30), "30m")
        self.assertEqual(display_optimized.format_time(60), "1h")
        self.assertEqual(display_optimized.format_time(90), "1h 30m")
        self.assertEqual(display_optimized.format_time(125), "2h 5m")


class TestTerminalControlFunctionsOptimized(unittest.TestCase):
    """Test optimized terminal control functions."""

    @patch("builtins.print")
    def test_clear_screen(self, mock_print: Mock) -> None:
        """Test clear_screen function."""
        display_optimized.clear_screen()

        mock_print.assert_called_once_with("\033[2J\033[3J\033[H", end="", flush=True)

    @patch("builtins.print")
    def test_hide_cursor(self, mock_print: Mock) -> None:
        """Test hide_cursor function."""
        display_optimized.hide_cursor()

        mock_print.assert_called_once_with("\033[?25l", end="", flush=True)

    @patch("builtins.print")
    def test_show_cursor(self, mock_print: Mock) -> None:
        """Test show_cursor function."""
        display_optimized.show_cursor()

        mock_print.assert_called_once_with("\033[?25h", end="", flush=True)

    def test_move_cursor_to_top(self) -> None:
        """Test move_cursor_to_top (no-op in optimized version)."""
        # Should not raise any errors
        display_optimized.move_cursor_to_top()

    def test_clear_below_cursor(self) -> None:
        """Test clear_below_cursor (no-op in optimized version)."""
        # Should not raise any errors
        display_optimized.clear_below_cursor()


class TestCacheIntegration(unittest.TestCase):
    """Test cache integration with display functions."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    def test_multiple_cached_calls_performance(self) -> None:
        """Test that cached calls are fast."""
        # Warm up cache
        for i in range(100):
            display_optimized.create_token_progress_bar(i, 50)
            display_optimized.create_time_progress_bar(i * 3, 300, 50)
            display_optimized.format_time(i * 2)

        # Time cached calls
        start_time: float = time.time()
        for _ in range(1000):
            display_optimized.create_token_progress_bar(50, 50)
            display_optimized.create_time_progress_bar(150, 300, 50)
            display_optimized.format_time(90)
        elapsed: float = time.time() - start_time

        # Should be very fast (< 0.1 seconds for 1000 iterations)
        self.assertLess(elapsed, 0.1)

    def test_cache_memory_usage(self) -> None:
        """Test that cache doesn't grow unbounded."""
        # Create many different cache entries
        for i in range(1000):
            display_optimized.create_token_progress_bar(i / 10.0, 50)

        # Cache should have reasonable number of entries
        # (due to rounding, should be around 100 entries)
        cache_size: int = len(cache._cache)
        self.assertLess(cache_size, 200)


if __name__ == "__main__":
    unittest.main()
