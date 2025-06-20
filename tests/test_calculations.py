#!/usr/bin/env python3
"""Comprehensive unit tests for calculations module with static typing."""

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from ccusage_monitor import calculations
from ccusage_monitor.protocols import CcusageBlock


class TestCalculateHourlyBurnRate(unittest.TestCase):
    """Test the calculate_hourly_burn_rate function."""

    def test_empty_blocks(self) -> None:
        """Test with empty blocks list."""
        current_time: datetime = datetime.now(timezone.utc)
        self.assertEqual(calculations.calculate_hourly_burn_rate([], current_time), 0.0)

    def test_single_active_block_full_hour(self) -> None:
        """Test with single active block that covers full hour."""
        current_time: datetime = datetime.now(timezone.utc)
        start_time: datetime = current_time - timedelta(hours=1)

        blocks: List[CcusageBlock] = [
            {"startTime": start_time.isoformat(), "totalTokens": 3600, "isActive": True, "isGap": False}
        ]

        # 3600 tokens in 60 minutes = 60 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 60.0, places=1)

    def test_single_active_block_partial_hour(self) -> None:
        """Test with single active block that covers partial hour."""
        current_time: datetime = datetime.now(timezone.utc)
        start_time: datetime = current_time - timedelta(minutes=30)

        blocks: List[CcusageBlock] = [
            {"startTime": start_time.isoformat(), "totalTokens": 1000, "isActive": True, "isGap": False}
        ]

        # 1000 tokens in 30 minutes, projected to 60 minutes = 1000/60 = 16.67 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 16.67, places=1)

    def test_inactive_block_with_actual_end_time(self) -> None:
        """Test with inactive block that has actualEndTime."""
        current_time: datetime = datetime.now(timezone.utc)
        start_time: datetime = current_time - timedelta(minutes=45)
        end_time: datetime = current_time - timedelta(minutes=15)

        blocks: List[CcusageBlock] = [
            {
                "startTime": start_time.isoformat(),
                "actualEndTime": end_time.isoformat(),
                "totalTokens": 1500,
                "isActive": False,
                "isGap": False,
            }
        ]

        # Block duration: 30 minutes (45-15), 1500 tokens
        # All 30 minutes are within the last hour, so: 1500/60 = 25 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 25.0, places=1)

    def test_multiple_blocks(self) -> None:
        """Test with multiple blocks in the last hour."""
        current_time: datetime = datetime.now(timezone.utc)

        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time - timedelta(minutes=50)).isoformat(),
                "actualEndTime": (current_time - timedelta(minutes=40)).isoformat(),
                "totalTokens": 600,
                "isActive": False,
                "isGap": False,
            },
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "totalTokens": 1800,
                "isActive": True,
                "isGap": False,
            },
        ]

        # First block: 600 tokens in 10 minutes
        # Second block: 1800 tokens in 30 minutes
        # Total: (600 + 1800) / 60 = 40 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 40.0, places=1)

    def test_blocks_with_gaps(self) -> None:
        """Test that gap blocks are ignored."""
        current_time: datetime = datetime.now(timezone.utc)

        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "totalTokens": 1000,
                "isActive": True,
                "isGap": True,  # Should be ignored
            },
            {
                "startTime": (current_time - timedelta(minutes=20)).isoformat(),
                "totalTokens": 800,
                "isActive": True,
                "isGap": False,  # Should be counted
            },
        ]

        # Only second block counts: 800 tokens in 20 minutes = 800/60 = 13.33 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 13.33, places=1)

    def test_blocks_outside_hour_window(self) -> None:
        """Test that blocks outside the hour window are excluded."""
        current_time: datetime = datetime.now(timezone.utc)

        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time - timedelta(hours=2)).isoformat(),
                "actualEndTime": (current_time - timedelta(hours=1, minutes=30)).isoformat(),
                "totalTokens": 5000,
                "isActive": False,
                "isGap": False,
            },
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "totalTokens": 900,
                "isActive": True,
                "isGap": False,
            },
        ]

        # First block is completely outside the hour window
        # Only second block counts: 900 tokens in 30 minutes = 900/60 = 15 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 15.0, places=1)

    def test_partial_overlap_with_hour_window(self) -> None:
        """Test block that partially overlaps with the hour window."""
        current_time: datetime = datetime.now(timezone.utc)
        start_time: datetime = current_time - timedelta(hours=1, minutes=30)
        end_time: datetime = current_time - timedelta(minutes=30)

        blocks: List[CcusageBlock] = [
            {
                "startTime": start_time.isoformat(),
                "actualEndTime": end_time.isoformat(),
                "totalTokens": 3000,
                "isActive": False,
                "isGap": False,
            }
        ]

        # Block duration: 60 minutes, but only 30 minutes are in the last hour
        # Tokens in hour window: 3000 * (30/60) = 1500
        # Burn rate: 1500 / 60 = 25 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 25.0, places=1)

    def test_blocks_with_missing_data(self) -> None:
        """Test handling of blocks with missing required fields."""
        current_time: datetime = datetime.now(timezone.utc)

        blocks: List[CcusageBlock] = [
            {
                # Missing startTime - should be skipped
                "totalTokens": 1000,
                "isActive": True,
                "isGap": False,
            },
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                # Missing totalTokens - should use 0
                "isActive": True,
                "isGap": False,
            },
            {
                "startTime": (current_time - timedelta(minutes=20)).isoformat(),
                "totalTokens": 800,
                "isActive": True,
                "isGap": False,
            },
        ]

        # Only last block contributes: 800 tokens in 20 minutes = 800/60 = 13.33 tokens/minute
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 13.33, places=1)

    def test_future_blocks(self) -> None:
        """Test that blocks starting in the future are ignored."""
        current_time: datetime = datetime.now(timezone.utc)

        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time + timedelta(minutes=10)).isoformat(),
                "totalTokens": 1000,
                "isActive": True,
                "isGap": False,
            }
        ]

        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertEqual(burn_rate, 0.0)

    def test_zero_duration_block(self) -> None:
        """Test handling of blocks with zero duration."""
        current_time: datetime = datetime.now(timezone.utc)
        same_time: datetime = current_time - timedelta(minutes=30)

        blocks: List[CcusageBlock] = [
            {
                "startTime": same_time.isoformat(),
                "actualEndTime": same_time.isoformat(),  # Same as start
                "totalTokens": 1000,
                "isActive": False,
                "isGap": False,
            }
        ]

        # Zero duration should result in 0 burn rate
        burn_rate: float = calculations.calculate_hourly_burn_rate(blocks, current_time)
        self.assertEqual(burn_rate, 0.0)


class TestGetNextResetTime(unittest.TestCase):
    """Test the get_next_reset_time function."""

    def test_default_reset_hours_morning(self) -> None:
        """Test with default reset hours in the morning."""
        # Test at 3:00 AM UTC
        current_time: datetime = datetime(2024, 1, 1, 3, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="UTC")

        # Next reset should be 4:00 AM UTC
        self.assertEqual(next_reset.hour, 4)
        self.assertEqual(next_reset.minute, 0)
        self.assertEqual(next_reset.day, 1)

    def test_default_reset_hours_afternoon(self) -> None:
        """Test with default reset hours in the afternoon."""
        # Test at 15:30 PM UTC
        current_time: datetime = datetime(2024, 1, 1, 15, 30, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="UTC")

        # Next reset should be 18:00 (6 PM) UTC
        self.assertEqual(next_reset.hour, 18)
        self.assertEqual(next_reset.minute, 0)

    def test_default_reset_hours_evening(self) -> None:
        """Test with default reset hours in the evening."""
        # Test at 20:00 PM UTC
        current_time: datetime = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="UTC")

        # Next reset should be 23:00 (11 PM) UTC
        self.assertEqual(next_reset.hour, 23)
        self.assertEqual(next_reset.minute, 0)

    def test_reset_next_day(self) -> None:
        """Test when next reset is the following day."""
        # Test at 23:30 PM UTC
        current_time: datetime = datetime(2024, 1, 1, 23, 30, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="UTC")

        # Next reset should be 4:00 AM next day
        self.assertEqual(next_reset.hour, 4)
        self.assertEqual(next_reset.minute, 0)
        self.assertEqual(next_reset.day, 2)

    def test_custom_reset_hour(self) -> None:
        """Test with custom reset hour."""
        # Test at 10:00 AM UTC with custom reset at 15:00
        current_time: datetime = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, custom_reset_hour=15, timezone_str="UTC")

        # Next reset should be 15:00 (3 PM) UTC
        self.assertEqual(next_reset.hour, 15)
        self.assertEqual(next_reset.minute, 0)

    def test_custom_reset_hour_next_day(self) -> None:
        """Test custom reset hour when it requires next day."""
        # Test at 16:00 PM UTC with custom reset at 10:00
        current_time: datetime = datetime(2024, 1, 1, 16, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, custom_reset_hour=10, timezone_str="UTC")

        # Next reset should be 10:00 AM next day
        self.assertEqual(next_reset.hour, 10)
        self.assertEqual(next_reset.minute, 0)
        self.assertEqual(next_reset.day, 2)

    def test_different_timezone(self) -> None:
        """Test with different timezone (Europe/Warsaw)."""
        # Test at 10:00 AM UTC (11:00 AM in Warsaw)
        current_time: datetime = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="Europe/Warsaw")

        # In Warsaw time, it's 11:00 AM, so next reset is 14:00 (2 PM) Warsaw time
        # Which is 13:00 UTC
        self.assertEqual(next_reset.hour, 13)
        self.assertEqual(next_reset.minute, 0)

    def test_asia_timezone(self) -> None:
        """Test with Asian timezone."""
        # Test at 10:00 AM UTC
        current_time: datetime = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="Asia/Tokyo")

        # In Tokyo, it's 7:00 PM, so next reset is 23:00 (11 PM) Tokyo time
        # Which is 14:00 UTC
        self.assertEqual(next_reset.hour, 14)
        self.assertEqual(next_reset.minute, 0)

    def test_invalid_timezone_fallback(self) -> None:
        """Test fallback when invalid timezone is provided."""
        current_time: datetime = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="Invalid/Timezone")

        # Should fall back to Europe/Warsaw
        # In Warsaw, it's 11:00 AM, so next reset is 14:00 (2 PM) Warsaw time
        self.assertEqual(next_reset.hour, 13)  # 13:00 UTC
        self.assertEqual(next_reset.minute, 0)

    def test_exact_reset_time(self) -> None:
        """Test when current time is exactly at a reset hour."""
        # Test at exactly 14:00 UTC
        current_time: datetime = datetime(2024, 1, 1, 14, 0, tzinfo=timezone.utc)
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="UTC")

        # Should return the same time
        self.assertEqual(next_reset.hour, 14)
        self.assertEqual(next_reset.minute, 0)
        self.assertEqual(next_reset.day, 1)

    def test_naive_datetime_handling(self) -> None:
        """Test handling of naive datetime (no timezone)."""
        # Create naive datetime
        current_time: datetime = datetime(2024, 1, 1, 10, 0)  # No timezone
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="UTC")

        # Should handle gracefully
        self.assertIsNotNone(next_reset)
        self.assertIsNotNone(next_reset.tzinfo)

    def test_dst_transition(self) -> None:
        """Test behavior during DST transition."""
        # Test during DST transition in US/Eastern
        # March 10, 2024, 2:00 AM -> 3:00 AM (spring forward)
        current_time: datetime = datetime(2024, 3, 10, 6, 30, tzinfo=timezone.utc)  # 1:30 AM EST
        next_reset: datetime = calculations.get_next_reset_time(current_time, timezone_str="US/Eastern")

        # Should handle DST transition correctly
        self.assertIsNotNone(next_reset)


class TestGetVelocityIndicator(unittest.TestCase):
    """Test the get_velocity_indicator function."""

    def test_slow_velocity(self) -> None:
        """Test slow burn rate (< 50 tokens/min)."""
        self.assertEqual(calculations.get_velocity_indicator(0), "🐌")
        self.assertEqual(calculations.get_velocity_indicator(1), "🐌")
        self.assertEqual(calculations.get_velocity_indicator(25), "🐌")
        self.assertEqual(calculations.get_velocity_indicator(49), "🐌")
        self.assertEqual(calculations.get_velocity_indicator(49.9), "🐌")

    def test_normal_velocity(self) -> None:
        """Test normal burn rate (50-150 tokens/min)."""
        self.assertEqual(calculations.get_velocity_indicator(50), "➡️")
        self.assertEqual(calculations.get_velocity_indicator(75), "➡️")
        self.assertEqual(calculations.get_velocity_indicator(100), "➡️")
        self.assertEqual(calculations.get_velocity_indicator(149), "➡️")
        self.assertEqual(calculations.get_velocity_indicator(149.9), "➡️")

    def test_fast_velocity(self) -> None:
        """Test fast burn rate (150-300 tokens/min)."""
        self.assertEqual(calculations.get_velocity_indicator(150), "🚀")
        self.assertEqual(calculations.get_velocity_indicator(200), "🚀")
        self.assertEqual(calculations.get_velocity_indicator(250), "🚀")
        self.assertEqual(calculations.get_velocity_indicator(299), "🚀")
        self.assertEqual(calculations.get_velocity_indicator(299.9), "🚀")

    def test_very_fast_velocity(self) -> None:
        """Test very fast burn rate (>= 300 tokens/min)."""
        self.assertEqual(calculations.get_velocity_indicator(300), "⚡")
        self.assertEqual(calculations.get_velocity_indicator(400), "⚡")
        self.assertEqual(calculations.get_velocity_indicator(500), "⚡")
        self.assertEqual(calculations.get_velocity_indicator(1000), "⚡")
        self.assertEqual(calculations.get_velocity_indicator(10000), "⚡")

    def test_negative_velocity(self) -> None:
        """Test negative burn rate."""
        # Should still work, probably returns slow indicator
        self.assertEqual(calculations.get_velocity_indicator(-10), "🐌")
        self.assertEqual(calculations.get_velocity_indicator(-100), "🐌")

    def test_float_velocity(self) -> None:
        """Test float burn rate values."""
        self.assertEqual(calculations.get_velocity_indicator(49.5), "🐌")
        self.assertEqual(calculations.get_velocity_indicator(50.0), "➡️")
        self.assertEqual(calculations.get_velocity_indicator(150.0), "🚀")
        self.assertEqual(calculations.get_velocity_indicator(300.0), "⚡")


if __name__ == "__main__":
    unittest.main()
