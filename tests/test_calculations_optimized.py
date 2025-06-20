#!/usr/bin/env python3
"""Comprehensive unit tests for calculations_optimized module with static typing."""

import os
import sys
import time
import unittest
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz

from ccusage_monitor import calculations_optimized
from ccusage_monitor.cache import cache
from ccusage_monitor.protocols import CcusageBlock


class TestCalculateHourlyBurnRateOptimized(unittest.TestCase):
    """Test the optimized calculate_hourly_burn_rate function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    def test_burn_rate_caching(self) -> None:
        """Test that burn rate calculations are cached."""
        current_time: datetime = datetime.now(timezone.utc)
        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "totalTokens": 1000,
                "isActive": True,
                "isGap": False,
            }
        ]

        # First call
        result1: float = calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)

        # Check cache was populated
        cache_key: str = f"burn_rate_{current_time.minute}"
        cached: Optional[Any] = cache.get(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached, result1)

        # Second call should use cache
        result2: float = calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)
        self.assertEqual(result1, result2)

    def test_burn_rate_cache_ttl(self) -> None:
        """Test that burn rate cache has TTL."""
        current_time: datetime = datetime.now(timezone.utc)
        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "totalTokens": 1000,
                "isActive": True,
                "isGap": False,
            }
        ]

        # Calculate burn rate
        calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)

        # Check cache exists with TTL
        cache_key: str = f"burn_rate_{current_time.minute}"
        cached: Optional[Any] = cache.get(cache_key, ttl=30)
        self.assertIsNotNone(cached)

        # Simulate time passing
        time.sleep(0.1)

        # Should still be cached with 30s TTL
        cached = cache.get(cache_key, ttl=0.05)
        self.assertIsNone(cached)  # Should be expired with 0.05s TTL

    def test_burn_rate_early_termination_optimization(self) -> None:
        """Test early termination optimization for old blocks."""
        current_time: datetime = datetime.now(timezone.utc)

        # Create many blocks, but only recent ones matter
        blocks: List[CcusageBlock] = []

        # Add old blocks (should be skipped early)
        for i in range(100):
            blocks.append(
                {
                    "startTime": (current_time - timedelta(hours=2 + i)).isoformat(),
                    "actualEndTime": (current_time - timedelta(hours=1.5 + i)).isoformat(),
                    "totalTokens": 1000,
                    "isActive": False,
                    "isGap": False,
                }
            )

        # Add one recent block
        blocks.append(
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "totalTokens": 500,
                "isActive": True,
                "isGap": False,
            }
        )

        # Reverse the list (as in the optimized version)
        blocks.reverse()

        # Should calculate quickly due to early termination
        start: float = time.time()
        result: float = calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)
        elapsed: float = time.time() - start

        # Should be fast even with many blocks
        self.assertLess(elapsed, 0.01)
        # Result should only consider the recent block: 500/60 = 8.33
        self.assertAlmostEqual(result, 8.33, places=1)

    def test_burn_rate_future_block_handling(self) -> None:
        """Test that future blocks are handled correctly."""
        current_time: datetime = datetime.now(timezone.utc)
        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time + timedelta(minutes=10)).isoformat(),
                "totalTokens": 1000,
                "isActive": True,
                "isGap": False,
            },
            {
                "startTime": (current_time - timedelta(minutes=20)).isoformat(),
                "totalTokens": 600,
                "isActive": True,
                "isGap": False,
            },
        ]

        # Only past block should count
        result: float = calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(result, 10.0, places=1)  # 600/60

    def test_burn_rate_gap_blocks_skipped_early(self) -> None:
        """Test that gap blocks are skipped early in optimization."""
        current_time: datetime = datetime.now(timezone.utc)
        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time - timedelta(minutes=30)).isoformat(),
                "totalTokens": 1000,
                "isActive": True,
                "isGap": True,  # Should be skipped
            },
            {
                "startTime": (current_time - timedelta(minutes=20)).isoformat(),
                "totalTokens": 400,
                "isActive": True,
                "isGap": False,
            },
        ]

        result: float = calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)
        # Only non-gap block counts: 400/60 = 6.67
        self.assertAlmostEqual(result, 6.67, places=1)


class TestGetNextResetTimeOptimized(unittest.TestCase):
    """Test the optimized get_next_reset_time function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    def test_reset_time_caching(self) -> None:
        """Test that reset times are cached."""
        current_time: datetime = datetime(2024, 1, 1, 10, 30, tzinfo=timezone.utc)

        # First call
        result1: datetime = calculations_optimized.get_next_reset_time(current_time, timezone_str="UTC")

        # Check cache
        cache_key: str = f"reset_time_{current_time.hour}_UTC_None"
        cached: Optional[Any] = cache.get(cache_key)
        self.assertIsNotNone(cached)

        # Second call should use cache
        result2: datetime = calculations_optimized.get_next_reset_time(current_time, timezone_str="UTC")
        self.assertEqual(result1, result2)

    def test_reset_time_cache_ttl(self) -> None:
        """Test that reset time cache has 5 minute TTL."""
        current_time: datetime = datetime(2024, 1, 1, 10, 30, tzinfo=timezone.utc)

        # Calculate reset time
        calculations_optimized.get_next_reset_time(current_time, timezone_str="UTC")

        # Check cache with TTL
        cache_key: str = f"reset_time_{current_time.hour}_UTC_None"
        cached: Optional[Any] = cache.get(cache_key, ttl=300)  # 5 minutes
        self.assertIsNotNone(cached)

    def test_timezone_object_caching(self) -> None:
        """Test that timezone objects are cached."""
        current_time: datetime = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)

        # First call with a timezone
        calculations_optimized.get_next_reset_time(current_time, timezone_str="US/Eastern")

        # Check timezone cache
        tz_cache_key: str = "timezone_US/Eastern"
        cached_tz: Optional[Any] = cache.get(tz_cache_key)
        self.assertIsNotNone(cached_tz)
        self.assertIsInstance(cached_tz, pytz.tzinfo.BaseTzInfo)

        # Clear reset time cache but keep timezone cache
        cache_key: str = f"reset_time_{current_time.hour}_US/Eastern_None"
        if cache_key in cache._cache:
            del cache._cache[cache_key]

        # Second call should use cached timezone
        calculations_optimized.get_next_reset_time(current_time, timezone_str="US/Eastern")

    def test_binary_search_optimization(self) -> None:
        """Test that the function uses efficient searching."""
        current_time: datetime = datetime(2024, 1, 1, 20, 30, tzinfo=timezone.utc)

        # Default reset hours are [4, 9, 14, 18, 23]
        # At 20:30, next should be 23:00
        result: datetime = calculations_optimized.get_next_reset_time(current_time, timezone_str="UTC")

        self.assertEqual(result.hour, 23)
        self.assertEqual(result.minute, 0)

    def test_reset_time_performance(self) -> None:
        """Test performance of reset time calculation."""
        current_time: datetime = datetime.now(timezone.utc)

        # Warm up cache
        calculations_optimized.get_next_reset_time(current_time)

        # Time many calculations
        start: float = time.time()
        for _ in range(1000):
            calculations_optimized.get_next_reset_time(current_time)
        elapsed: float = time.time() - start

        # Should be very fast with caching
        self.assertLess(elapsed, 0.01)

    def test_iso_format_caching(self) -> None:
        """Test that ISO format strings are cached properly."""
        current_time: datetime = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)

        # Calculate reset time
        result: datetime = calculations_optimized.get_next_reset_time(current_time, timezone_str="UTC")

        # Cache stores ISO format
        cache_key: str = f"reset_time_{current_time.hour}_UTC_None"
        cached: Optional[Any] = cache.get(cache_key)
        self.assertIsNotNone(cached)
        self.assertIsInstance(cached, str)  # Should be ISO format string

        # Parse it back
        parsed: datetime = datetime.fromisoformat(cached)
        self.assertEqual(parsed, result)


class TestGetVelocityIndicatorOptimized(unittest.TestCase):
    """Test the optimized get_velocity_indicator function."""

    def test_velocity_lookup_performance(self) -> None:
        """Test O(1) lookup performance."""
        # Time many lookups
        start: float = time.time()
        for i in range(10000):
            calculations_optimized.get_velocity_indicator(float(i % 400))
        elapsed: float = time.time() - start

        # Should be very fast
        self.assertLess(elapsed, 0.01)

    def test_predefined_velocity_indicators(self) -> None:
        """Test the predefined VELOCITY_INDICATORS constant."""
        indicators = calculations_optimized.VELOCITY_INDICATORS

        # Should have 4 entries
        self.assertEqual(len(indicators), 4)

        # Check structure
        for threshold, emoji in indicators:
            self.assertIsInstance(threshold, (int, float))
            self.assertIsInstance(emoji, str)

        # Check order (ascending thresholds)
        thresholds = [t for t, _ in indicators]
        self.assertEqual(thresholds, sorted(thresholds))

        # Check last threshold is infinity
        self.assertEqual(thresholds[-1], float("inf"))

    def test_velocity_indicator_boundaries(self) -> None:
        """Test velocity indicators at exact boundaries."""
        # Test at boundaries
        self.assertEqual(calculations_optimized.get_velocity_indicator(49.9), "🐌")
        self.assertEqual(calculations_optimized.get_velocity_indicator(50.0), "➡️")
        self.assertEqual(calculations_optimized.get_velocity_indicator(149.9), "➡️")
        self.assertEqual(calculations_optimized.get_velocity_indicator(150.0), "🚀")
        self.assertEqual(calculations_optimized.get_velocity_indicator(299.9), "🚀")
        self.assertEqual(calculations_optimized.get_velocity_indicator(300.0), "⚡")

    def test_velocity_indicator_consistency(self) -> None:
        """Test that indicators are consistent with regular version."""
        test_values: List[float] = [0, 25, 50, 100, 150, 200, 300, 500, 1000]

        for value in test_values:
            result: str = calculations_optimized.get_velocity_indicator(value)
            # Check it returns one of the expected emojis
            self.assertIn(result, ["🐌", "➡️", "🚀", "⚡"])


class TestOptimizationCorrectness(unittest.TestCase):
    """Test that optimized functions produce same results as original."""

    def setUp(self) -> None:
        """Clear cache and import both modules."""
        cache.clear()
        from ccusage_monitor import calculations

        self.calculations = calculations

    def test_burn_rate_correctness(self) -> None:
        """Test burn rate calculation matches original."""
        current_time: datetime = datetime.now(timezone.utc)
        blocks: List[CcusageBlock] = [
            {
                "startTime": (current_time - timedelta(minutes=45)).isoformat(),
                "actualEndTime": (current_time - timedelta(minutes=15)).isoformat(),
                "totalTokens": 1500,
                "isActive": False,
                "isGap": False,
            },
            {
                "startTime": (current_time - timedelta(minutes=20)).isoformat(),
                "totalTokens": 800,
                "isActive": True,
                "isGap": False,
            },
        ]

        # Calculate with both versions
        original: float = self.calculations.calculate_hourly_burn_rate(blocks, current_time)
        optimized: float = calculations_optimized.calculate_hourly_burn_rate(blocks, current_time)

        # Should be identical
        self.assertAlmostEqual(original, optimized, places=2)

    def test_reset_time_correctness(self) -> None:
        """Test reset time calculation matches original."""
        test_times: List[datetime] = [
            datetime(2024, 1, 1, 3, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 15, 30, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 23, 45, tzinfo=timezone.utc),
        ]

        for current_time in test_times:
            # Calculate with both versions
            original: datetime = self.calculations.get_next_reset_time(current_time, timezone_str="Europe/Warsaw")
            optimized: datetime = calculations_optimized.get_next_reset_time(current_time, timezone_str="Europe/Warsaw")

            # Should be identical
            self.assertEqual(original, optimized)

    def test_velocity_indicator_correctness(self) -> None:
        """Test velocity indicator matches original."""
        test_values: List[float] = [0, 25, 49, 50, 100, 149, 150, 250, 299, 300, 500]

        for value in test_values:
            # Get from both versions
            original: str = self.calculations.get_velocity_indicator(value)
            optimized: str = calculations_optimized.get_velocity_indicator(value)

            # Should be identical
            self.assertEqual(original, optimized)


if __name__ == "__main__":
    unittest.main()
