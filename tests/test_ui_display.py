"""Comprehensive tests for ccusage_monitor.ui.display module."""

from io import StringIO
from unittest.mock import patch

import pytest

from ccusage_monitor.ui.display import (
    OutputBuffer,
    _buffer,
    clear_screen,
    create_time_progress_bar,
    create_token_progress_bar,
    flush_buffer,
    format_time,
    hide_cursor,
    print_header,
    show_cursor,
    writeln,
)


class TestOutputBuffer:
    """Test the OutputBuffer class."""

    def test_buffer_initialization(self):
        """Test buffer initializes correctly."""
        buffer = OutputBuffer()
        assert buffer.buffer.getvalue() == ""
        assert buffer.last_output == ""

    def test_buffer_write(self):
        """Test writing to buffer."""
        buffer = OutputBuffer()
        buffer.write("test text")
        assert buffer.buffer.getvalue() == "test text"

    def test_buffer_writeln(self):
        """Test writing line to buffer."""
        buffer = OutputBuffer()
        buffer.writeln("test line")
        assert buffer.buffer.getvalue() == "test line\n"

    @patch("sys.stdout.write")
    @patch("builtins.print")
    def test_buffer_flush_new_content(self, mock_print, mock_write):
        """Test flushing buffer with new content."""
        buffer = OutputBuffer()
        buffer.write("new content")

        buffer.flush()

        mock_write.assert_called_once_with("new content")
        assert buffer.last_output == "new content"
        assert buffer.buffer.getvalue() == ""  # Buffer should be reset

    @patch("sys.stdout.write")
    @patch("builtins.print")
    def test_buffer_flush_same_content(self, mock_print, mock_write):
        """Test flushing buffer with same content doesn't update."""
        buffer = OutputBuffer()
        buffer.write("same content")
        buffer.flush()

        # Write same content again
        buffer.write("same content")
        buffer.flush()

        # Should only write once
        mock_write.assert_called_once()


class TestProgressBars:
    """Test progress bar creation functions."""

    def test_create_token_progress_bar_zero_percent(self):
        """Test token progress bar at 0%."""
        bar = create_token_progress_bar(0.0)
        assert isinstance(bar, str)
        assert "0.0%" in bar
        assert "🟢" in bar

    def test_create_token_progress_bar_fifty_percent(self):
        """Test token progress bar at 50%."""
        bar = create_token_progress_bar(50.0)
        assert isinstance(bar, str)
        assert "50.0%" in bar
        assert "🟢" in bar

    def test_create_token_progress_bar_hundred_percent(self):
        """Test token progress bar at 100%."""
        bar = create_token_progress_bar(100.0)
        assert isinstance(bar, str)
        assert "100.0%" in bar
        assert "🟢" in bar

    def test_create_token_progress_bar_custom_width(self):
        """Test token progress bar with custom width."""
        bar = create_token_progress_bar(50.0, width=20)
        assert isinstance(bar, str)
        assert "50.0%" in bar

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    def test_create_token_progress_bar_caching(self, mock_set, mock_get):
        """Test that progress bars are cached."""
        mock_get.return_value = None  # Not cached

        bar1 = create_token_progress_bar(25.0)
        bar2 = create_token_progress_bar(25.0)  # Same value

        assert bar1 == bar2
        mock_set.assert_called()  # Should cache the result

    def test_create_time_progress_bar_zero_elapsed(self):
        """Test time progress bar with zero elapsed time."""
        bar = create_time_progress_bar(0, 300)
        assert isinstance(bar, str)
        assert "⏰" in bar
        assert "5h" in bar  # 300 minutes = 5 hours remaining

    def test_create_time_progress_bar_half_elapsed(self):
        """Test time progress bar with half elapsed time."""
        bar = create_time_progress_bar(150, 300)
        assert isinstance(bar, str)
        assert "⏰" in bar
        assert "2h 30m" in bar  # 150 minutes remaining

    def test_create_time_progress_bar_fully_elapsed(self):
        """Test time progress bar with full elapsed time."""
        bar = create_time_progress_bar(300, 300)
        assert isinstance(bar, str)
        assert "⏰" in bar
        assert "0m" in bar  # No time remaining

    def test_create_time_progress_bar_over_elapsed(self):
        """Test time progress bar with over-elapsed time."""
        bar = create_time_progress_bar(400, 300)
        assert isinstance(bar, str)
        assert "⏰" in bar
        assert "0m" in bar  # Can't go below 0

    def test_create_time_progress_bar_zero_total(self):
        """Test time progress bar with zero total time."""
        bar = create_time_progress_bar(100, 0)
        assert isinstance(bar, str)
        assert "⏰" in bar


class TestFormatTime:
    """Test the format_time function."""

    def test_format_time_minutes_only(self):
        """Test formatting time with minutes only."""
        assert format_time(30) == "30m"
        assert format_time(59) == "59m"

    def test_format_time_hours_only(self):
        """Test formatting time with exact hours."""
        assert format_time(60) == "1h"
        assert format_time(120) == "2h"
        assert format_time(180) == "3h"

    def test_format_time_hours_and_minutes(self):
        """Test formatting time with hours and minutes."""
        assert format_time(65) == "1h 5m"
        assert format_time(125) == "2h 5m"
        assert format_time(185) == "3h 5m"

    def test_format_time_zero(self):
        """Test formatting zero time."""
        assert format_time(0) == "0m"

    def test_format_time_fractional(self):
        """Test formatting fractional minutes."""
        assert format_time(30.7) == "31m"  # Should round
        assert format_time(59.2) == "59m"

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    def test_format_time_caching(self, mock_set, mock_get):
        """Test that formatted times are cached."""
        mock_get.return_value = None  # Not cached

        result = format_time(125)
        assert result == "2h 5m"
        mock_set.assert_called()


class TestDisplayFunctions:
    """Test display utility functions."""

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.ui.display.write_to_buffer")
    def test_print_header_caching(self, mock_write, mock_get):
        """Test header printing with caching."""
        mock_get.return_value = None  # Not cached

        print_header()

        mock_write.assert_called_once()

    @patch("ccusage_monitor.ui.display._buffer.writeln")
    def test_writeln_function(self, mock_writeln):
        """Test writeln function."""
        writeln("test message")
        mock_writeln.assert_called_once_with("test message")

    @patch("ccusage_monitor.ui.display._buffer.flush")
    def test_flush_buffer_function(self, mock_flush):
        """Test flush_buffer function."""
        flush_buffer()
        mock_flush.assert_called_once()

    @patch("builtins.print")
    def test_clear_screen(self, mock_print):
        """Test clear_screen function."""
        clear_screen()
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_hide_cursor(self, mock_print):
        """Test hide_cursor function."""
        hide_cursor()
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_show_cursor(self, mock_print):
        """Test show_cursor function."""
        show_cursor()
        mock_print.assert_called_once()


class TestGlobalBuffer:
    """Test the global buffer instance."""

    def test_global_buffer_exists(self):
        """Test that global buffer exists."""
        assert _buffer is not None
        assert isinstance(_buffer, OutputBuffer)

    def test_global_buffer_operations(self):
        """Test operations on global buffer."""
        # Clear any existing content
        _buffer.buffer = StringIO()
        _buffer.last_output = ""

        writeln("test global buffer")
        assert _buffer.buffer.getvalue() == "test global buffer\n"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
