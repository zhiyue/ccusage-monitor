"""Comprehensive tests for ccusage_monitor.core.calculations module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from ccusage_monitor.core.calculations import (
    VELOCITY_INDICATORS,
    calculate_hourly_burn_rate,
    get_next_reset_time,
    get_token_limit,
    get_velocity_indicator,
)


class TestCalculateHourlyBurnRate:
    """Test the calculate_hourly_burn_rate function."""

    def test_empty_blocks_returns_zero(self):
        """Test that empty blocks list returns 0 burn rate."""
        current_time = datetime.now(timezone.utc)
        burn_rate = calculate_hourly_burn_rate([], current_time)
        assert burn_rate == 0.0

    def test_no_active_blocks_returns_zero(self):
        """Test that blocks without active sessions return 0."""
        current_time = datetime.now(timezone.utc)
        blocks = [{"isGap": True, "totalTokens": 100}, {"isActive": False, "totalTokens": 200, "startTime": None}]
        burn_rate = calculate_hourly_burn_rate(blocks, current_time)
        assert burn_rate == 0.0

    def test_single_active_block_calculation(self):
        """Test burn rate calculation with single active block."""
        current_time = datetime.now(timezone.utc)
        start_time = current_time - timedelta(minutes=30)  # 30 minutes ago

        blocks = [
            {
                "isActive": True,
                "totalTokens": 600,  # 600 tokens in 30 minutes = 20 tokens/min
                "startTime": start_time.isoformat(),
                "isGap": False,
            }
        ]

        burn_rate = calculate_hourly_burn_rate(blocks, current_time)
        assert burn_rate == 20.0  # 600 tokens / 30 minutes

    def test_multiple_blocks_in_last_hour(self):
        """Test burn rate with multiple blocks within last hour."""
        current_time = datetime.now(timezone.utc)

        blocks = [
            {
                "isActive": False,
                "totalTokens": 300,
                "startTime": (current_time - timedelta(minutes=45)).isoformat(),
                "actualEndTime": (current_time - timedelta(minutes=30)).isoformat(),
                "isGap": False,
            },
            {
                "isActive": True,
                "totalTokens": 600,
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "isGap": False,
            },
        ]

        burn_rate = calculate_hourly_burn_rate(blocks, current_time)
        # First block: 300 tokens in 15 minutes (within hour) = 20 tokens/min
        # Second block: 600 tokens in 30 minutes = 20 tokens/min
        # Total: 40 tokens/min
        assert burn_rate == 40.0

    def test_blocks_outside_hour_window_ignored(self):
        """Test that blocks outside 1-hour window are ignored."""
        current_time = datetime.now(timezone.utc)
        old_time = current_time - timedelta(hours=2)

        blocks = [
            {
                "isActive": False,
                "totalTokens": 1000,
                "startTime": old_time.isoformat(),
                "actualEndTime": (old_time + timedelta(minutes=30)).isoformat(),
                "isGap": False,
            },
            {
                "isActive": True,
                "totalTokens": 300,
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "isGap": False,
            },
        ]

        burn_rate = calculate_hourly_burn_rate(blocks, current_time)
        # Only the recent block should count: 300 tokens / 30 minutes = 10
        assert burn_rate == 10.0

    def test_gap_blocks_ignored(self):
        """Test that gap blocks are ignored in calculation."""
        current_time = datetime.now(timezone.utc)

        blocks = [
            {"isGap": True, "totalTokens": 1000, "startTime": (current_time - timedelta(minutes=30)).isoformat()},
            {
                "isActive": True,
                "totalTokens": 300,
                "startTime": (current_time - timedelta(minutes=15)).isoformat(),
                "isGap": False,
            },
        ]

        burn_rate = calculate_hourly_burn_rate(blocks, current_time)
        # Only non-gap block: 300 tokens / 15 minutes = 20
        assert burn_rate == 20.0

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    def test_caching_mechanism(self, mock_set, mock_get):
        """Test that results are cached properly."""
        current_time = datetime.now(timezone.utc)
        mock_get.return_value = 15.5  # Cached value

        blocks = [
            {
                "isActive": True,
                "totalTokens": 300,
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "isGap": False,
            }
        ]

        burn_rate = calculate_hourly_burn_rate(blocks, current_time)

        # Should return cached value
        assert burn_rate == 15.5
        mock_get.assert_called_once()
        mock_set.assert_not_called()


class TestGetNextResetTime:
    """Test the get_next_reset_time function."""

    def test_next_reset_time_is_future(self):
        """Test that next reset time is always in the future."""
        current_time = datetime.now(timezone.utc)
        reset_time = get_next_reset_time(current_time)
        assert reset_time > current_time

    def test_custom_reset_hour(self):
        """Test reset time with custom hour."""
        # Test at 10 AM, with custom reset at 2 PM
        current_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        reset_time = get_next_reset_time(current_time, custom_reset_hour=14)

        # Should be same day at 2 PM
        assert reset_time.hour == 14
        assert reset_time.date() == current_time.date()

    def test_default_reset_hours(self):
        """Test default reset hours (4, 9, 14, 18, 23)."""
        # Test at 10 AM - next reset should be 2 PM (14:00)
        current_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        reset_time = get_next_reset_time(current_time)
        assert reset_time.hour == 14

    def test_reset_next_day_when_past_last_hour(self):
        """Test reset time goes to next day when past last reset hour."""
        # Test at 11 PM (past last reset at 23:00)
        current_time = datetime(2024, 1, 1, 23, 30, 0, tzinfo=timezone.utc)
        reset_time = get_next_reset_time(current_time)

        # Should be next day at 4 AM
        assert reset_time.hour == 4
        assert reset_time.date() == current_time.date() + timedelta(days=1)

    def test_timezone_conversion(self):
        """Test timezone handling."""
        # Test with timezone-aware current time
        current_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        reset_time = get_next_reset_time(current_time, timezone_str="US/Eastern")

        # Should handle timezone conversion properly
        assert reset_time.tzinfo is not None

    def test_invalid_timezone_fallback(self):
        """Test fallback to Europe/Warsaw for invalid timezone."""
        current_time = datetime.now(timezone.utc)
        reset_time = get_next_reset_time(current_time, timezone_str="Invalid/Timezone")

        # Should not raise error and return valid time
        assert reset_time > current_time

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    def test_caching_mechanism(self, mock_set, mock_get):
        """Test that reset times are cached."""
        current_time = datetime.now(timezone.utc)
        cached_time = (current_time + timedelta(hours=1)).isoformat()
        mock_get.return_value = cached_time

        reset_time = get_next_reset_time(current_time)

        mock_get.assert_called()
        assert reset_time.isoformat() == cached_time


class TestGetTokenLimit:
    """Test the get_token_limit function."""

    def test_known_plan_limits(self):
        """Test token limits for known plans."""
        assert get_token_limit("pro") == 7000
        assert get_token_limit("max5") == 35000
        assert get_token_limit("max20") == 140000

    def test_unknown_plan_defaults_to_pro(self):
        """Test that unknown plan defaults to pro limit."""
        assert get_token_limit("unknown_plan") == 7000

    def test_custom_max_with_blocks(self):
        """Test custom_max plan with block analysis."""
        blocks = [
            {"totalTokens": 8000, "isGap": False, "isActive": False},
            {"totalTokens": 12000, "isGap": False, "isActive": False},
            {"totalTokens": 50000, "isGap": False, "isActive": False},  # Highest
        ]

        limit = get_token_limit("custom_max", blocks)
        assert limit == 140000  # Should return max20 limit for 50k usage

    def test_custom_max_with_low_usage(self):
        """Test custom_max with low token usage."""
        blocks = [
            {"totalTokens": 5000, "isGap": False, "isActive": False},
            {"totalTokens": 6000, "isGap": False, "isActive": False},
        ]

        limit = get_token_limit("custom_max", blocks)
        assert limit == 7000  # Should return pro limit

    def test_custom_max_with_medium_usage(self):
        """Test custom_max with medium token usage."""
        blocks = [
            {"totalTokens": 15000, "isGap": False, "isActive": False},
            {"totalTokens": 20000, "isGap": False, "isActive": False},
        ]

        limit = get_token_limit("custom_max", blocks)
        assert limit == 35000  # Should return max5 limit

    def test_custom_max_ignores_gaps_and_active(self):
        """Test that custom_max ignores gap and active blocks."""
        blocks = [
            {"totalTokens": 50000, "isGap": True, "isActive": False},  # Gap - ignored
            {"totalTokens": 60000, "isGap": False, "isActive": True},  # Active - ignored
            {"totalTokens": 15000, "isGap": False, "isActive": False},  # Valid
        ]

        limit = get_token_limit("custom_max", blocks)
        assert limit == 35000  # Based on 15k, not 50k or 60k

    def test_custom_max_no_blocks(self):
        """Test custom_max with no blocks defaults to pro."""
        limit = get_token_limit("custom_max", [])
        assert limit == 7000

        limit = get_token_limit("custom_max", None)
        assert limit == 7000


class TestGetVelocityIndicator:
    """Test the get_velocity_indicator function."""

    def test_velocity_indicators_constant(self):
        """Test that velocity indicators constant is properly defined."""
        assert isinstance(VELOCITY_INDICATORS, list)
        assert len(VELOCITY_INDICATORS) == 4

        # Check structure
        for threshold, indicator in VELOCITY_INDICATORS:
            assert isinstance(threshold, (int, float))
            assert isinstance(indicator, str)

    def test_slow_velocity(self):
        """Test slow velocity indicator."""
        assert get_velocity_indicator(0) == "🐌"
        assert get_velocity_indicator(25) == "🐌"
        assert get_velocity_indicator(49.9) == "🐌"

    def test_normal_velocity(self):
        """Test normal velocity indicator."""
        assert get_velocity_indicator(50) == "➡️"
        assert get_velocity_indicator(100) == "➡️"
        assert get_velocity_indicator(149.9) == "➡️"

    def test_fast_velocity(self):
        """Test fast velocity indicator."""
        assert get_velocity_indicator(150) == "🚀"
        assert get_velocity_indicator(200) == "🚀"
        assert get_velocity_indicator(299.9) == "🚀"

    def test_very_fast_velocity(self):
        """Test very fast velocity indicator."""
        assert get_velocity_indicator(300) == "⚡"
        assert get_velocity_indicator(500) == "⚡"
        assert get_velocity_indicator(1000) == "⚡"

    def test_edge_cases(self):
        """Test edge cases and boundary values."""
        # Exact boundary values
        assert get_velocity_indicator(50.0) == "➡️"
        assert get_velocity_indicator(150.0) == "🚀"
        assert get_velocity_indicator(300.0) == "⚡"

        # Negative values (should still work)
        assert get_velocity_indicator(-10) == "🐌"

        # Very large values
        assert get_velocity_indicator(999999) == "⚡"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
