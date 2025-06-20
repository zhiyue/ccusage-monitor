"""Comprehensive tests for ccusage_monitor.core.config module."""

from unittest.mock import patch

import pytest

from ccusage_monitor.core.config import (
    CYAN,
    DEFAULT_TIMEZONE,
    GRAY,
    GREEN,
    RED,
    RESET,
    SESSION_DURATION,
    TOKEN_LIMITS,
    WHITE,
    YELLOW,
    parse_args,
)


class TestConstants:
    """Test module constants."""

    def test_color_constants_are_strings(self):
        """Test that all color constants are strings."""
        colors = [CYAN, RED, YELLOW, WHITE, GRAY, GREEN, RESET]
        for color in colors:
            assert isinstance(color, str)
            assert len(color) > 0

    def test_token_limits_structure(self):
        """Test token limits dictionary structure."""
        assert isinstance(TOKEN_LIMITS, dict)
        assert "pro" in TOKEN_LIMITS
        assert "max5" in TOKEN_LIMITS
        assert "max20" in TOKEN_LIMITS

        assert TOKEN_LIMITS["pro"] == 7000
        assert TOKEN_LIMITS["max5"] == 35000
        assert TOKEN_LIMITS["max20"] == 140000

    def test_default_timezone_is_string(self):
        """Test default timezone constant."""
        assert isinstance(DEFAULT_TIMEZONE, str)
        assert DEFAULT_TIMEZONE == "Europe/Warsaw"

    def test_session_duration_is_integer(self):
        """Test session duration constant."""
        assert isinstance(SESSION_DURATION, int)
        assert SESSION_DURATION == 300


class TestParseArgs:
    """Test command line argument parsing."""

    def test_parse_args_with_defaults(self):
        """Test parsing with default arguments."""
        with patch("sys.argv", ["ccusage-monitor"]):
            args = parse_args()

        assert args.plan == "pro"
        assert args.timezone == "Europe/Warsaw"
        assert args.refresh == 3
        assert args.performance is False
        assert args.rich is False
        assert args.reset_hour is None

    def test_parse_args_with_all_options(self):
        """Test parsing with all command line options."""
        with patch(
            "sys.argv",
            [
                "ccusage-monitor",
                "--plan",
                "max5",
                "--reset-hour",
                "12",
                "--timezone",
                "US/Eastern",
                "--performance",
                "--rich",
                "--refresh",
                "5",
            ],
        ):
            args = parse_args()

        assert args.plan == "max5"
        assert args.reset_hour == 12
        assert args.timezone == "US/Eastern"
        assert args.performance is True
        assert args.rich is True
        assert args.refresh == 5

    def test_parse_args_plan_choices(self):
        """Test that plan argument accepts only valid choices."""
        valid_plans = ["pro", "max5", "max20", "custom_max"]

        for plan in valid_plans:
            with patch("sys.argv", ["ccusage-monitor", "--plan", plan]):
                args = parse_args()
                assert args.plan == plan

    def test_parse_args_invalid_plan_raises_error(self):
        """Test that invalid plan raises SystemExit."""
        with patch("sys.argv", ["ccusage-monitor", "--plan", "invalid"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_reset_hour_range(self):
        """Test reset hour argument accepts valid range."""
        # Test valid hours
        for hour in [0, 12, 23]:
            with patch("sys.argv", ["ccusage-monitor", "--reset-hour", str(hour)]):
                args = parse_args()
                assert args.reset_hour == hour

    def test_parse_args_refresh_interval(self):
        """Test refresh interval argument."""
        with patch("sys.argv", ["ccusage-monitor", "--refresh", "10"]):
            args = parse_args()
            assert args.refresh == 10

    def test_parse_args_returns_cliargs_protocol(self):
        """Test that parse_args returns object with CLIArgs protocol."""
        with patch("sys.argv", ["ccusage-monitor"]):
            args = parse_args()

        # Check that all required attributes exist
        assert hasattr(args, "plan")
        assert hasattr(args, "reset_hour")
        assert hasattr(args, "timezone")
        assert hasattr(args, "performance")
        assert hasattr(args, "rich")
        assert hasattr(args, "refresh")

    def test_parse_args_help_text_exists(self):
        """Test that help text is available."""
        with patch("sys.argv", ["ccusage-monitor", "--help"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_timezone_examples(self):
        """Test various timezone formats."""
        timezones = ["UTC", "US/Eastern", "Asia/Tokyo", "Europe/London"]

        for tz in timezones:
            with patch("sys.argv", ["ccusage-monitor", "--timezone", tz]):
                args = parse_args()
                assert args.timezone == tz


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
