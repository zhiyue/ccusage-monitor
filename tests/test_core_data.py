"""Comprehensive tests for ccusage_monitor.core.data module."""

import asyncio
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ccusage_monitor.core.data import (
    check_ccusage_installed,
    get_token_limit,
    run_ccusage,
    run_ccusage_async,
)


class TestCheckCcusageInstalled:
    """Test the check_ccusage_installed function."""

    @patch("shutil.which")
    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    def test_ccusage_found_first_time(self, mock_set, mock_get, mock_which):
        """Test when ccusage is found for the first time."""
        mock_get.return_value = None  # Not cached
        mock_which.return_value = "/usr/local/bin/ccusage"

        result = check_ccusage_installed()

        assert result is True
        mock_which.assert_called_once_with("ccusage")
        mock_set.assert_called_once_with("ccusage_installed", True)

    @patch("shutil.which")
    @patch("ccusage_monitor.core.cache.cache.get")
    def test_ccusage_found_cached(self, mock_get, mock_which):
        """Test when ccusage status is cached."""
        mock_get.return_value = True  # Cached as found

        result = check_ccusage_installed()

        assert result is True
        mock_which.assert_not_called()  # Should not check again

    @patch("shutil.which")
    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    @patch("builtins.print")
    def test_ccusage_not_found(self, mock_print, mock_set, mock_get, mock_which):
        """Test when ccusage is not found."""
        mock_get.return_value = None  # Not cached
        mock_which.return_value = None  # Not found

        result = check_ccusage_installed()

        assert result is False
        mock_set.assert_called_once_with("ccusage_installed", False)
        # Should print installation instructions
        assert mock_print.call_count > 0

    @patch("ccusage_monitor.core.cache.cache.get")
    def test_ccusage_cached_not_found(self, mock_get):
        """Test when ccusage is cached as not found."""
        mock_get.return_value = False  # Cached as not found

        result = check_ccusage_installed()

        assert result is False


class TestRunCcusage:
    """Test the run_ccusage function."""

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    @patch("subprocess.run")
    def test_successful_ccusage_run(self, mock_run, mock_set, mock_get):
        """Test successful ccusage execution."""
        mock_get.return_value = None  # Not cached

        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.stdout = '{"blocks": [{"totalTokens": 100}]}'
        mock_run.return_value = mock_result

        result = run_ccusage()

        assert result is not None
        assert "blocks" in result
        assert result["blocks"][0]["totalTokens"] == 100

        mock_run.assert_called_once_with(
            ["ccusage", "blocks", "--offline", "--json"], capture_output=True, text=True, check=True, timeout=10
        )
        mock_set.assert_called_once()

    @patch("ccusage_monitor.core.cache.cache.get")
    def test_cached_ccusage_data(self, mock_get):
        """Test returning cached ccusage data."""
        cached_data = {"blocks": [{"totalTokens": 200}]}
        mock_get.return_value = cached_data

        result = run_ccusage()

        assert result == cached_data

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("subprocess.run")
    @patch("builtins.print")
    def test_ccusage_timeout(self, mock_print, mock_run, mock_get):
        """Test ccusage command timeout."""
        mock_get.return_value = None
        mock_run.side_effect = subprocess.TimeoutExpired(["ccusage"], 10)

        result = run_ccusage()

        assert result is None
        mock_print.assert_called_with("❌ ccusage command timed out")

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("subprocess.run")
    @patch("builtins.print")
    def test_ccusage_not_found_error(self, mock_print, mock_run, mock_get):
        """Test ccusage command not found."""
        mock_get.return_value = None
        mock_run.side_effect = FileNotFoundError()

        result = run_ccusage()

        assert result is None
        mock_print.assert_called_with("❌ ccusage command not found. Please install it with: npm install -g ccusage")

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("subprocess.run")
    @patch("builtins.print")
    def test_ccusage_process_error(self, mock_print, mock_run, mock_get):
        """Test ccusage process error."""
        mock_get.return_value = None
        error = subprocess.CalledProcessError(1, ["ccusage"])
        error.stderr = "Auth error"
        mock_run.side_effect = error

        result = run_ccusage()

        assert result is None
        # Should print error and solutions
        assert mock_print.call_count >= 2

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("subprocess.run")
    @patch("builtins.print")
    def test_ccusage_json_decode_error(self, mock_print, mock_run, mock_get):
        """Test JSON decode error from ccusage output."""
        mock_get.return_value = None

        mock_result = MagicMock()
        mock_result.stdout = "invalid json"
        mock_run.return_value = mock_result

        result = run_ccusage()

        assert result is None
        mock_print.assert_called()


class TestRunCcusageAsync:
    """Test the run_ccusage_async function."""

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    @patch("asyncio.create_subprocess_exec")
    @patch("asyncio.wait_for")
    def test_successful_async_ccusage_run(self, mock_wait_for, mock_create_subprocess, mock_set, mock_get):
        """Test successful async ccusage execution."""
        mock_get.return_value = None  # Not cached

        # Mock subprocess
        mock_proc = AsyncMock()
        mock_proc.returncode = 0
        mock_create_subprocess.return_value = mock_proc

        # Mock communication result
        stdout = b'{"blocks": [{"totalTokens": 150}]}'
        stderr = b""
        mock_wait_for.return_value = (stdout, stderr)

        async def run_test():
            result = await run_ccusage_async()
            return result

        result = asyncio.run(run_test())

        assert result is not None
        assert "blocks" in result
        assert result["blocks"][0]["totalTokens"] == 150
        mock_set.assert_called_once()

    @patch("ccusage_monitor.core.cache.cache.get")
    def test_cached_async_ccusage_data(self, mock_get):
        """Test returning cached data in async version."""
        cached_data = {"blocks": [{"totalTokens": 300}]}
        mock_get.return_value = cached_data

        async def run_test():
            result = await run_ccusage_async()
            return result

        result = asyncio.run(run_test())
        assert result == cached_data

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("asyncio.create_subprocess_exec")
    @patch("asyncio.wait_for")
    @patch("builtins.print")
    def test_async_ccusage_timeout(self, mock_print, mock_wait_for, mock_create_subprocess, mock_get):
        """Test async ccusage timeout."""
        mock_get.return_value = None
        mock_create_subprocess.return_value = AsyncMock()
        mock_wait_for.side_effect = asyncio.TimeoutError()

        async def run_test():
            result = await run_ccusage_async()
            return result

        result = asyncio.run(run_test())

        assert result is None
        mock_print.assert_called_with("❌ ccusage command timed out")

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("asyncio.create_subprocess_exec")
    @patch("builtins.print")
    def test_async_ccusage_general_error(self, mock_print, mock_create_subprocess, mock_get):
        """Test async ccusage general error."""
        mock_get.return_value = None
        mock_create_subprocess.side_effect = Exception("Something went wrong")

        async def run_test():
            result = await run_ccusage_async()
            return result

        result = asyncio.run(run_test())

        assert result is None
        mock_print.assert_called()


class TestGetTokenLimit:
    """Test the get_token_limit function."""

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    def test_get_token_limit_known_plans(self, mock_set, mock_get):
        """Test token limits for known plans."""
        mock_get.return_value = None  # Not cached

        assert get_token_limit("pro") == 7000
        assert get_token_limit("max5") == 35000
        assert get_token_limit("max20") == 140000

        # Should cache the results
        assert mock_set.call_count == 3

    @patch("ccusage_monitor.core.cache.cache.get")
    def test_get_token_limit_cached(self, mock_get):
        """Test cached token limits."""
        mock_get.return_value = 7000

        result = get_token_limit("pro")
        assert result == 7000

    @patch("ccusage_monitor.core.cache.cache.get")
    @patch("ccusage_monitor.core.cache.cache.set")
    def test_get_token_limit_unknown_plan(self, mock_set, mock_get):
        """Test unknown plan defaults to pro limit."""
        mock_get.return_value = None

        result = get_token_limit("unknown_plan")
        assert result == 7000

    def test_get_token_limit_custom_max_with_blocks(self):
        """Test custom_max plan with block analysis."""
        blocks = [
            {"totalTokens": 8000, "isGap": False, "isActive": False},
            {"totalTokens": 12000, "isGap": False, "isActive": False},
            {"totalTokens": 50000, "isGap": False, "isActive": False},  # Highest
        ]

        limit = get_token_limit("custom_max", blocks)
        assert limit == 50000  # Should return the highest usage found

    def test_get_token_limit_custom_max_with_gaps_and_active(self):
        """Test custom_max ignores gap and active blocks."""
        blocks = [
            {"totalTokens": 50000, "isGap": True, "isActive": False},  # Gap - ignored
            {"totalTokens": 60000, "isGap": False, "isActive": True},  # Active - ignored
            {"totalTokens": 15000, "isGap": False, "isActive": False},  # Valid
        ]

        limit = get_token_limit("custom_max", blocks)
        assert limit == 15000  # Based on 15k, not 50k or 60k

    def test_get_token_limit_custom_max_no_blocks(self):
        """Test custom_max with no blocks defaults to pro."""
        assert get_token_limit("custom_max", []) == 7000
        assert get_token_limit("custom_max", None) == 7000

    def test_get_token_limit_custom_max_no_valid_blocks(self):
        """Test custom_max with no valid blocks."""
        blocks = [
            {"totalTokens": 1000, "isGap": True, "isActive": False},
            {"totalTokens": 2000, "isGap": False, "isActive": True},
        ]

        limit = get_token_limit("custom_max", blocks)
        assert limit == 7000  # Should default to pro when no valid blocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
