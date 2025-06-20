#!/usr/bin/env python3
"""Comprehensive unit tests for data module with static typing."""

import json
import os
import subprocess
import sys
import unittest
from typing import Any, Dict, List, Optional, cast
from unittest.mock import MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccusage_monitor import data
from ccusage_monitor.protocols import CcusageBlock, CcusageData


class TestCheckCcusageInstalled(unittest.TestCase):
    """Test the check_ccusage_installed function."""

    @patch("shutil.which")
    def test_ccusage_installed(self, mock_which: Mock) -> None:
        """Test when ccusage is installed."""
        mock_which.return_value = "/usr/local/bin/ccusage"
        result: bool = data.check_ccusage_installed()
        self.assertTrue(result)
        mock_which.assert_called_once_with("ccusage")

    @patch("shutil.which")
    @patch("builtins.print")
    def test_ccusage_not_installed(self, mock_print: Mock, mock_which: Mock) -> None:
        """Test when ccusage is not installed."""
        mock_which.return_value = None
        result: bool = data.check_ccusage_installed()
        self.assertFalse(result)

        # Check that error messages were printed
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("'ccusage' command not found!" in str(call) for call in print_calls))
        self.assertTrue(any("npm install -g ccusage" in str(call) for call in print_calls))

    @patch("shutil.which")
    def test_ccusage_different_path(self, mock_which: Mock) -> None:
        """Test when ccusage is installed in different location."""
        mock_which.return_value = "/home/user/.npm/bin/ccusage"
        result: bool = data.check_ccusage_installed()
        self.assertTrue(result)

    @patch("shutil.which")
    def test_ccusage_empty_path(self, mock_which: Mock) -> None:
        """Test when which returns empty string."""
        mock_which.return_value = ""
        result: bool = data.check_ccusage_installed()
        self.assertFalse(result)


class TestRunCcusage(unittest.TestCase):
    """Test the run_ccusage function."""

    @patch("subprocess.run")
    def test_successful_run_simple(self, mock_run: Mock) -> None:
        """Test successful ccusage execution with simple data."""
        mock_result: MagicMock = MagicMock()
        mock_result.stdout = json.dumps(
            {"blocks": [{"totalTokens": 1000, "isActive": True, "startTime": "2024-01-01T10:00:00Z"}]}
        )
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result: Optional[CcusageData] = data.run_ccusage()

        self.assertIsNotNone(result)
        assert result is not None
        self.assertIn("blocks", result)
        self.assertEqual(len(result["blocks"]), 1)
        self.assertEqual(result["blocks"][0].get("totalTokens"), 1000)

        # Verify subprocess was called correctly
        mock_run.assert_called_once_with(
            ["ccusage", "blocks", "--offline", "--json"], capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    def test_successful_run_multiple_blocks(self, mock_run: Mock) -> None:
        """Test successful ccusage execution with multiple blocks."""
        mock_result: MagicMock = MagicMock()
        mock_result.stdout = json.dumps(
            {
                "blocks": [
                    {
                        "totalTokens": 1000,
                        "isActive": False,
                        "startTime": "2024-01-01T09:00:00Z",
                        "actualEndTime": "2024-01-01T10:00:00Z",
                    },
                    {"totalTokens": 2000, "isActive": True, "startTime": "2024-01-01T10:00:00Z"},
                ]
            }
        )
        mock_run.return_value = mock_result

        result: Optional[CcusageData] = data.run_ccusage()

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(len(result["blocks"]), 2)
        self.assertEqual(result["blocks"][0].get("totalTokens"), 1000)
        self.assertEqual(result["blocks"][1].get("totalTokens"), 2000)
        self.assertTrue(result["blocks"][1].get("isActive"))

    @patch("subprocess.run")
    def test_file_not_found_error(self, mock_run: Mock) -> None:
        """Test when ccusage command is not found."""
        mock_run.side_effect = FileNotFoundError("ccusage not found")

        with patch("builtins.print") as mock_print:
            result: Optional[CcusageData] = data.run_ccusage()

        self.assertIsNone(result)
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("ccusage command not found" in str(call) for call in print_calls))
        self.assertTrue(any("npm install -g ccusage" in str(call) for call in print_calls))

    @patch("subprocess.run")
    def test_subprocess_error(self, mock_run: Mock) -> None:
        """Test when ccusage returns non-zero exit code."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["ccusage", "blocks", "--offline", "--json"], stderr="Authentication required"
        )

        with patch("builtins.print") as mock_print:
            result: Optional[CcusageData] = data.run_ccusage()

        self.assertIsNone(result)
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Error running ccusage" in str(call) for call in print_calls))
        self.assertTrue(any("Authentication required" in str(call) for call in print_calls))
        self.assertTrue(any("ccusage login" in str(call) for call in print_calls))

    @patch("subprocess.run")
    def test_invalid_json_response(self, mock_run: Mock) -> None:
        """Test when ccusage returns invalid JSON."""
        mock_result: MagicMock = MagicMock()
        mock_result.stdout = "This is not valid JSON"
        mock_run.return_value = mock_result

        with patch("builtins.print") as mock_print:
            result: Optional[CcusageData] = data.run_ccusage()

        self.assertIsNone(result)
        print_calls: List[str] = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Error parsing JSON" in str(call) for call in print_calls))

    @patch("subprocess.run")
    def test_empty_json_response(self, mock_run: Mock) -> None:
        """Test when ccusage returns empty JSON."""
        mock_result: MagicMock = MagicMock()
        mock_result.stdout = "{}"
        mock_run.return_value = mock_result

        result: Optional[CcusageData] = data.run_ccusage()

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result, {})

    @patch("subprocess.run")
    def test_json_with_extra_fields(self, mock_run: Mock) -> None:
        """Test JSON response with extra fields."""
        mock_result: MagicMock = MagicMock()
        mock_result.stdout = json.dumps(
            {"blocks": [{"totalTokens": 1000}], "extra_field": "should be preserved", "metadata": {"version": "1.0"}}
        )
        mock_run.return_value = mock_result

        result: Optional[CcusageData] = data.run_ccusage()

        self.assertIsNotNone(result)
        assert result is not None
        self.assertIn("blocks", result)
        self.assertIn("extra_field", result)
        self.assertIn("metadata", result)

    @patch("subprocess.run")
    def test_subprocess_timeout(self, mock_run: Mock) -> None:
        """Test handling of subprocess timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["ccusage", "blocks", "--offline", "--json"], timeout=30)

        # The current implementation doesn't handle TimeoutExpired specifically,
        # so it would raise. This tests current behavior.
        with self.assertRaises(subprocess.TimeoutExpired):
            data.run_ccusage()


class TestGetTokenLimit(unittest.TestCase):
    """Test the get_token_limit function."""

    def test_pro_plan_limit(self) -> None:
        """Test Pro plan token limit."""
        self.assertEqual(data.get_token_limit("pro"), 7000)

    def test_max5_plan_limit(self) -> None:
        """Test Max5 plan token limit."""
        self.assertEqual(data.get_token_limit("max5"), 35000)

    def test_max20_plan_limit(self) -> None:
        """Test Max20 plan token limit."""
        self.assertEqual(data.get_token_limit("max20"), 140000)

    def test_unknown_plan_defaults_to_pro(self) -> None:
        """Test unknown plan defaults to Pro limit."""
        self.assertEqual(data.get_token_limit("unknown_plan"), 7000)
        self.assertEqual(data.get_token_limit(""), 7000)
        self.assertEqual(data.get_token_limit("MAX20"), 7000)  # Case sensitive

    def test_custom_max_with_no_blocks(self) -> None:
        """Test custom_max plan with no blocks."""
        self.assertEqual(data.get_token_limit("custom_max", None), 7000)
        self.assertEqual(data.get_token_limit("custom_max", []), 7000)

    def test_custom_max_with_single_block(self) -> None:
        """Test custom_max with single valid block."""
        blocks: List[CcusageBlock] = [{"isGap": False, "isActive": False, "totalTokens": 25000}]
        self.assertEqual(data.get_token_limit("custom_max", blocks), 25000)

    def test_custom_max_with_multiple_blocks(self) -> None:
        """Test custom_max returns highest token count."""
        blocks: List[CcusageBlock] = [
            {"isGap": False, "isActive": False, "totalTokens": 10000},
            {"isGap": False, "isActive": False, "totalTokens": 30000},
            {"isGap": False, "isActive": False, "totalTokens": 20000},
        ]
        self.assertEqual(data.get_token_limit("custom_max", blocks), 30000)

    def test_custom_max_ignores_active_blocks(self) -> None:
        """Test custom_max ignores active blocks."""
        blocks: List[CcusageBlock] = [
            {"isGap": False, "isActive": True, "totalTokens": 50000},
            {"isGap": False, "isActive": False, "totalTokens": 30000},
        ]
        self.assertEqual(data.get_token_limit("custom_max", blocks), 30000)

    def test_custom_max_ignores_gap_blocks(self) -> None:
        """Test custom_max ignores gap blocks."""
        blocks: List[CcusageBlock] = [
            {"isGap": True, "isActive": False, "totalTokens": 50000},
            {"isGap": False, "isActive": False, "totalTokens": 30000},
        ]
        self.assertEqual(data.get_token_limit("custom_max", blocks), 30000)

    def test_custom_max_with_all_invalid_blocks(self) -> None:
        """Test custom_max when all blocks are invalid."""
        blocks: List[CcusageBlock] = [
            {"isGap": True, "isActive": False, "totalTokens": 50000},
            {"isGap": False, "isActive": True, "totalTokens": 30000},
        ]
        self.assertEqual(data.get_token_limit("custom_max", blocks), 7000)

    def test_custom_max_with_missing_fields(self) -> None:
        """Test custom_max with missing token fields."""
        blocks_missing_tokens: List[Dict[str, Any]] = [{"isGap": False, "isActive": False}]
        self.assertEqual(data.get_token_limit("custom_max", cast(List[CcusageBlock], blocks_missing_tokens)), 7000)

    def test_custom_max_with_zero_tokens(self) -> None:
        """Test custom_max with zero tokens."""
        blocks: List[CcusageBlock] = [{"isGap": False, "isActive": False, "totalTokens": 0}]
        # When highest token count is 0 or less, defaults to pro limit (7000)
        self.assertEqual(data.get_token_limit("custom_max", blocks), 7000)

    def test_custom_max_with_negative_tokens(self) -> None:
        """Test custom_max with negative tokens."""
        blocks: List[CcusageBlock] = [{"isGap": False, "isActive": False, "totalTokens": -100}]
        self.assertEqual(data.get_token_limit("custom_max", blocks), 7000)  # Should default

    def test_plan_parameter_type(self) -> None:
        """Test that get_token_limit handles non-string plan types."""
        # Test non-string plan types, should default to pro
        self.assertEqual(data.get_token_limit(None), 7000)  # type: ignore[arg-type]
        self.assertEqual(data.get_token_limit(123), 7000)  # type: ignore[arg-type]


class TestIntegration(unittest.TestCase):
    """Test full integration between functions."""

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_full_workflow(self, mock_which: Mock, mock_run: Mock) -> None:
        """Test a full workflow from checking install to getting limits."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/ccusage"
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({"blocks": [{"totalTokens": 12345}]})
        mock_run.return_value = mock_result

        # Run checks
        self.assertTrue(data.check_ccusage_installed())
        initial_data = data.run_ccusage()
        self.assertIsNotNone(initial_data)
        assert initial_data is not None

        # Get limit
        limit = data.get_token_limit("custom_max", initial_data["blocks"])
        self.assertEqual(limit, 12345)


if __name__ == "__main__":
    unittest.main()
