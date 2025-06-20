#!/usr/bin/env python3
"""Comprehensive unit tests for data_optimized module with static typing."""

import asyncio
import json
import os
import subprocess
import sys
import unittest
from typing import Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccusage_monitor import data_optimized
from ccusage_monitor.cache import cache
from ccusage_monitor.protocols import CcusageBlock, CcusageData


class TestCheckCcusageInstalledOptimized(unittest.TestCase):
    """Test the optimized check_ccusage_installed function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    @patch("shutil.which")
    def test_check_ccusage_installed_caching(self, mock_which: Mock) -> None:
        """Test that ccusage installation check is cached."""
        mock_which.return_value = "/usr/local/bin/ccusage"

        # First call
        result1: bool = data_optimized.check_ccusage_installed()
        self.assertTrue(result1)
        self.assertEqual(mock_which.call_count, 1)

        # Check cache
        cached: Optional[Any] = cache.get("ccusage_installed")
        self.assertTrue(cached)

        # Second call should use cache
        result2: bool = data_optimized.check_ccusage_installed()
        self.assertTrue(result2)
        self.assertEqual(mock_which.call_count, 1)  # Still 1, not called again

    @patch("shutil.which")
    @patch("builtins.print")
    def test_check_ccusage_not_installed_cached(self, mock_print: Mock, mock_which: Mock) -> None:
        """Test that negative result is also cached."""
        mock_which.return_value = None

        # First call
        result1: bool = data_optimized.check_ccusage_installed()
        self.assertFalse(result1)

        # Check cache
        cached: Optional[Any] = cache.get("ccusage_installed")
        self.assertFalse(cached)

        # Clear print mock
        mock_print.reset_mock()

        # Second call should use cache
        result2: bool = data_optimized.check_ccusage_installed()
        self.assertFalse(result2)
        # Error messages should only be printed once
        self.assertEqual(mock_print.call_count, 0)

    @patch("shutil.which")
    def test_check_ccusage_cache_persistence(self, mock_which: Mock) -> None:
        """Test that cache persists across function calls."""
        mock_which.return_value = "/usr/bin/ccusage"

        # Multiple calls
        for _ in range(10):
            result: bool = data_optimized.check_ccusage_installed()
            self.assertTrue(result)

        # which should only be called once
        self.assertEqual(mock_which.call_count, 1)


class TestRunCcusageOptimized(unittest.TestCase):
    """Test the optimized run_ccusage function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    @patch("subprocess.run")
    def test_run_ccusage_caching(self, mock_run: Mock) -> None:
        """Test that ccusage results are cached with TTL."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"blocks": [{"totalTokens": 1000, "isActive": True}]})
        mock_run.return_value = mock_result

        # First call
        result1: Optional[CcusageData] = data_optimized.run_ccusage()
        self.assertIsNotNone(result1)
        self.assertEqual(mock_run.call_count, 1)

        # Check cache
        cached: Optional[Any] = cache.get("ccusage_data", ttl=5)
        self.assertIsNotNone(cached)
        self.assertEqual(cached, result1)

        # Second call within TTL should use cache
        result2: Optional[CcusageData] = data_optimized.run_ccusage()
        self.assertEqual(result1, result2)
        self.assertEqual(mock_run.call_count, 1)  # Still 1

    @patch("subprocess.run")
    def test_run_ccusage_cache_ttl_expiry(self, mock_run: Mock) -> None:
        """Test that cache expires after TTL."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"blocks": [{"totalTokens": 1000}]})
        mock_run.return_value = mock_result

        # Manually set cache with old timestamp
        import time

        old_data: CcusageData = {"blocks": [{"totalTokens": 500}]}
        cache._cache["ccusage_data"] = (old_data, time.time() - 10)  # 10 seconds ago

        # Call should fetch new data (cache expired)
        result: Optional[CcusageData] = data_optimized.run_ccusage()
        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["blocks"][0]["totalTokens"], 1000)
        self.assertEqual(mock_run.call_count, 1)

    @patch("subprocess.run")
    def test_run_ccusage_timeout_handling(self, mock_run: Mock) -> None:
        """Test timeout handling with 10 second limit."""
        mock_run.side_effect = subprocess.TimeoutExpired(["ccusage", "blocks", "--offline", "--json"], timeout=10)

        with patch("builtins.print") as mock_print:
            result: Optional[CcusageData] = data_optimized.run_ccusage()

        self.assertIsNone(result)
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("timed out" in str(call) for call in print_calls))

    @patch("subprocess.run")
    def test_run_ccusage_subprocess_args(self, mock_run: Mock) -> None:
        """Test that subprocess is called with correct arguments."""
        mock_result = MagicMock()
        mock_result.stdout = '{"blocks": []}'
        mock_run.return_value = mock_result

        data_optimized.run_ccusage()

        mock_run.assert_called_once_with(
            ["ccusage", "blocks", "--offline", "--json"], capture_output=True, text=True, check=True, timeout=10
        )

    @patch("subprocess.run")
    def test_run_ccusage_error_not_cached(self, mock_run: Mock) -> None:
        """Test that errors are not cached."""
        # First call fails
        mock_run.side_effect = FileNotFoundError()
        result1: Optional[CcusageData] = data_optimized.run_ccusage()
        self.assertIsNone(result1)

        # Fix the error
        mock_run.side_effect = None
        mock_result = MagicMock()
        mock_result.stdout = '{"blocks": [{"totalTokens": 1000}]}'
        mock_run.return_value = mock_result

        # Second call should work (error wasn't cached)
        result2: Optional[CcusageData] = data_optimized.run_ccusage()
        self.assertIsNotNone(result2)


class TestRunCcusageAsyncOptimized(unittest.TestCase):
    """Test the async run_ccusage_async function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    async def async_test_run_ccusage_async_basic(self) -> None:
        """Test basic async execution."""
        with patch("asyncio.create_subprocess_exec") as mock_create:
            # Create async mock process
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate.return_value = (json.dumps({"blocks": [{"totalTokens": 1000}]}).encode(), b"")
            mock_create.return_value = mock_proc

            result: Optional[CcusageData] = await data_optimized.run_ccusage_async()

            self.assertIsNotNone(result)
            if result:
                self.assertEqual(len(result["blocks"]), 1)
                self.assertEqual(result["blocks"][0]["totalTokens"], 1000)

    def test_run_ccusage_async_basic(self) -> None:
        """Wrapper to run async test."""
        asyncio.run(self.async_test_run_ccusage_async_basic())

    async def async_test_run_ccusage_async_caching(self) -> None:
        """Test that async version uses cache."""
        # Pre-populate cache
        cached_data: CcusageData = {"blocks": [{"totalTokens": 2000}]}
        cache.set("ccusage_data", cached_data)

        with patch("asyncio.create_subprocess_exec") as mock_create:
            result: Optional[CcusageData] = await data_optimized.run_ccusage_async()

            # Should use cache, not call subprocess
            mock_create.assert_not_called()
            self.assertEqual(result, cached_data)

    def test_run_ccusage_async_caching(self) -> None:
        """Wrapper to run async test."""
        asyncio.run(self.async_test_run_ccusage_async_caching())

    async def async_test_run_ccusage_async_timeout(self) -> None:
        """Test async timeout handling."""
        with patch("asyncio.create_subprocess_exec") as mock_create:
            mock_proc = AsyncMock()
            mock_proc.communicate.side_effect = asyncio.TimeoutError()
            mock_create.return_value = mock_proc

            with patch("builtins.print") as mock_print:
                result: Optional[CcusageData] = await data_optimized.run_ccusage_async()

            self.assertIsNone(result)
            print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("timed out" in str(call) for call in print_calls))

    def test_run_ccusage_async_timeout(self) -> None:
        """Wrapper to run async test."""
        asyncio.run(self.async_test_run_ccusage_async_timeout())

    async def async_test_run_ccusage_async_error(self) -> None:
        """Test async error handling."""
        with patch("asyncio.create_subprocess_exec") as mock_create:
            mock_proc = AsyncMock()
            mock_proc.returncode = 1
            mock_proc.communicate.return_value = (b"", b"Error message")
            mock_create.return_value = mock_proc

            with patch("builtins.print") as mock_print:
                result: Optional[CcusageData] = await data_optimized.run_ccusage_async()

            self.assertIsNone(result)
            print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any("Error running ccusage" in str(call) for call in print_calls))

    def test_run_ccusage_async_error(self) -> None:
        """Wrapper to run async test."""
        asyncio.run(self.async_test_run_ccusage_async_error())


class TestGetTokenLimitOptimized(unittest.TestCase):
    """Test the optimized get_token_limit function."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    def test_fixed_plan_caching(self) -> None:
        """Test that fixed plan limits are cached."""
        # First calls
        pro_limit1: int = data_optimized.get_token_limit("pro")
        max5_limit1: int = data_optimized.get_token_limit("max5")
        max20_limit1: int = data_optimized.get_token_limit("max20")

        # Check cache
        self.assertEqual(cache.get("token_limit_pro"), 7000)
        self.assertEqual(cache.get("token_limit_max5"), 35000)
        self.assertEqual(cache.get("token_limit_max20"), 140000)

        # Subsequent calls should use cache
        pro_limit2: int = data_optimized.get_token_limit("pro")
        max5_limit2: int = data_optimized.get_token_limit("max5")
        max20_limit2: int = data_optimized.get_token_limit("max20")

        self.assertEqual(pro_limit1, pro_limit2)
        self.assertEqual(max5_limit1, max5_limit2)
        self.assertEqual(max20_limit1, max20_limit2)

    def test_custom_max_not_cached(self) -> None:
        """Test that custom_max is calculated dynamically."""
        blocks1: List[CcusageBlock] = [{"isGap": False, "isActive": False, "totalTokens": 10000}]
        blocks2: List[CcusageBlock] = [{"isGap": False, "isActive": False, "totalTokens": 20000}]

        limit1: int = data_optimized.get_token_limit("custom_max", blocks1)
        limit2: int = data_optimized.get_token_limit("custom_max", blocks2)

        self.assertEqual(limit1, 10000)
        self.assertEqual(limit2, 20000)

        # Should not be cached
        self.assertIsNone(cache.get("token_limit_custom_max"))

    def test_custom_max_list_comprehension_optimization(self) -> None:
        """Test optimized list comprehension for custom_max."""
        # Create many blocks
        blocks: List[CcusageBlock] = []
        for i in range(1000):
            blocks.append(
                {
                    "isGap": i % 3 == 0,  # Every 3rd is gap
                    "isActive": i % 5 == 0,  # Every 5th is active
                    "totalTokens": i * 100,
                }
            )

        # Time the calculation
        import time

        start: float = time.time()
        limit: int = data_optimized.get_token_limit("custom_max", blocks)
        elapsed: float = time.time() - start

        # Should be fast even with many blocks
        self.assertLess(elapsed, 0.01)

        # Should return max of valid blocks
        # Valid blocks are those that are not gap and not active
        # Highest valid would be 998 * 100 = 99800
        self.assertEqual(limit, 99800)

    def test_unknown_plan_caching(self) -> None:
        """Test that unknown plans are cached as pro limit."""
        limit: int = data_optimized.get_token_limit("unknown_plan")
        self.assertEqual(limit, 7000)

        # Should be cached
        cached: Optional[Any] = cache.get("token_limit_unknown_plan")
        self.assertEqual(cached, 7000)


class TestOptimizationPerformance(unittest.TestCase):
    """Test performance characteristics of optimized functions."""

    def setUp(self) -> None:
        """Clear cache before each test."""
        cache.clear()

    @patch("subprocess.run")
    def test_multiple_run_ccusage_calls(self, mock_run: Mock) -> None:
        """Test performance with multiple ccusage calls."""
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "blocks": [{"totalTokens": 1000}] * 100  # Many blocks
            }
        )
        mock_run.return_value = mock_result

        # Time multiple calls
        import time

        start: float = time.time()

        # First call hits subprocess
        data_optimized.run_ccusage()

        # Next 99 calls should use cache
        for _ in range(99):
            data_optimized.run_ccusage()

        elapsed: float = time.time() - start

        # Should be fast with caching
        self.assertLess(elapsed, 0.1)
        # Subprocess only called once
        self.assertEqual(mock_run.call_count, 1)

    def test_token_limit_performance(self) -> None:
        """Test token limit calculation performance."""
        import time

        # Time many fixed plan lookups
        start: float = time.time()
        for _ in range(10000):
            data_optimized.get_token_limit("pro")
            data_optimized.get_token_limit("max5")
            data_optimized.get_token_limit("max20")
        elapsed: float = time.time() - start

        # Should be extremely fast with caching
        self.assertLess(elapsed, 0.01)


class TestCorrectness(unittest.TestCase):
    """Test that optimized functions match original behavior."""

    def setUp(self) -> None:
        """Clear cache and import original module."""
        cache.clear()
        from ccusage_monitor import data

        self.data = data

    @patch("shutil.which")
    def test_check_ccusage_installed_correctness(self, mock_which: Mock) -> None:
        """Test that optimized version matches original."""
        test_cases = ["/usr/local/bin/ccusage", None, "", "/home/user/.npm/bin/ccusage"]

        for which_result in test_cases:
            mock_which.return_value = which_result

            # Clear cache for fair comparison
            cache.clear()

            original: bool = self.data.check_ccusage_installed()
            optimized: bool = data_optimized.check_ccusage_installed()

            self.assertEqual(original, optimized)

    def test_get_token_limit_correctness(self) -> None:
        """Test that token limits match original."""
        # Test fixed plans
        for plan in ["pro", "max5", "max20", "unknown"]:
            original: int = self.data.get_token_limit(plan)
            optimized: int = data_optimized.get_token_limit(plan)
            self.assertEqual(original, optimized)

        # Test custom_max
        test_blocks: List[List[CcusageBlock]] = [
            [],
            [{"isGap": False, "isActive": False, "totalTokens": 10000}],
            [
                {"isGap": True, "isActive": False, "totalTokens": 20000},
                {"isGap": False, "isActive": True, "totalTokens": 30000},
                {"isGap": False, "isActive": False, "totalTokens": 15000},
            ],
        ]

        for blocks in test_blocks:
            original: int = self.data.get_token_limit("custom_max", blocks)
            optimized: int = data_optimized.get_token_limit("custom_max", blocks)
            self.assertEqual(original, optimized)


if __name__ == "__main__":
    unittest.main()
