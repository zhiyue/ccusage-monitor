#!/usr/bin/env python3
"""
Unit tests for ccusage_monitor.py
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ccusage_monitor


class TestFormatTime(unittest.TestCase):
    """Test the format_time function."""
    
    def test_format_minutes_only(self):
        """Test formatting when time is less than an hour."""
        self.assertEqual(ccusage_monitor.format_time(30), "30m")
        self.assertEqual(ccusage_monitor.format_time(59), "59m")
        self.assertEqual(ccusage_monitor.format_time(0), "0m")
    
    def test_format_hours_only(self):
        """Test formatting when time is exactly hours."""
        self.assertEqual(ccusage_monitor.format_time(60), "1h")
        self.assertEqual(ccusage_monitor.format_time(120), "2h")
        self.assertEqual(ccusage_monitor.format_time(300), "5h")
    
    def test_format_hours_and_minutes(self):
        """Test formatting when time has both hours and minutes."""
        self.assertEqual(ccusage_monitor.format_time(90), "1h 30m")
        self.assertEqual(ccusage_monitor.format_time(125), "2h 5m")
        self.assertEqual(ccusage_monitor.format_time(315), "5h 15m")


class TestProgressBars(unittest.TestCase):
    """Test progress bar creation functions."""
    
    def test_token_progress_bar_empty(self):
        """Test token progress bar with 0%."""
        result = ccusage_monitor.create_token_progress_bar(0, width=10)
        self.assertIn("0.0%", result)
        self.assertIn("░░░░░░░░░░", result)  # All empty
    
    def test_token_progress_bar_full(self):
        """Test token progress bar with 100%."""
        result = ccusage_monitor.create_token_progress_bar(100, width=10)
        self.assertIn("100.0%", result)
        self.assertIn("██████████", result)  # All filled
    
    def test_token_progress_bar_partial(self):
        """Test token progress bar with 50%."""
        result = ccusage_monitor.create_token_progress_bar(50, width=10)
        self.assertIn("50.0%", result)
        self.assertIn("█████", result)  # Half filled
    
    def test_time_progress_bar(self):
        """Test time progress bar."""
        result = ccusage_monitor.create_time_progress_bar(150, 300, width=10)
        self.assertIn("2h 30m", result)  # Remaining time
        # 50% progress = 5 filled blocks
        self.assertIn("█████", result)


class TestVelocityIndicator(unittest.TestCase):
    """Test the get_velocity_indicator function."""
    
    def test_slow_velocity(self):
        """Test slow burn rate indicator."""
        self.assertEqual(ccusage_monitor.get_velocity_indicator(25), '🐌')
        self.assertEqual(ccusage_monitor.get_velocity_indicator(0), '🐌')
    
    def test_normal_velocity(self):
        """Test normal burn rate indicator."""
        self.assertEqual(ccusage_monitor.get_velocity_indicator(75), '➡️')
        self.assertEqual(ccusage_monitor.get_velocity_indicator(100), '➡️')
    
    def test_fast_velocity(self):
        """Test fast burn rate indicator."""
        self.assertEqual(ccusage_monitor.get_velocity_indicator(200), '🚀')
        self.assertEqual(ccusage_monitor.get_velocity_indicator(250), '🚀')
    
    def test_very_fast_velocity(self):
        """Test very fast burn rate indicator."""
        self.assertEqual(ccusage_monitor.get_velocity_indicator(350), '⚡')
        self.assertEqual(ccusage_monitor.get_velocity_indicator(500), '⚡')


class TestBurnRateCalculation(unittest.TestCase):
    """Test the calculate_hourly_burn_rate function."""
    
    def test_no_blocks(self):
        """Test burn rate with no blocks."""
        current_time = datetime.now(timezone.utc)
        self.assertEqual(ccusage_monitor.calculate_hourly_burn_rate([], current_time), 0)
    
    def test_single_active_block(self):
        """Test burn rate with single active block."""
        current_time = datetime.now(timezone.utc)
        start_time = current_time - timedelta(minutes=30)
        
        blocks = [{
            'startTime': start_time.isoformat(),
            'totalTokens': 1000,
            'isActive': True,
            'isGap': False
        }]
        
        # The function returns tokens per minute for the last hour
        # With 1000 tokens in 30 minutes, that's 1000 tokens / 60 minutes = 16.67 tokens/minute
        burn_rate = ccusage_monitor.calculate_hourly_burn_rate(blocks, current_time)
        self.assertAlmostEqual(burn_rate, 16.67, places=1)
    
    def test_skip_gap_blocks(self):
        """Test that gap blocks are skipped."""
        current_time = datetime.now(timezone.utc)
        start_time = current_time - timedelta(minutes=30)
        
        blocks = [{
            'startTime': start_time.isoformat(),
            'totalTokens': 1000,
            'isActive': True,
            'isGap': True  # This should be skipped
        }]
        
        burn_rate = ccusage_monitor.calculate_hourly_burn_rate(blocks, current_time)
        self.assertEqual(burn_rate, 0)


class TestNextResetTime(unittest.TestCase):
    """Test the get_next_reset_time function."""
    
    def test_default_reset_hours(self):
        """Test with default 5-hour intervals."""
        # Test at 10:30 AM UTC (11:30 AM in Europe/Warsaw)
        current_time = datetime(2024, 1, 1, 10, 30, tzinfo=timezone.utc)
        next_reset = ccusage_monitor.get_next_reset_time(current_time, timezone_str='UTC')
        
        # Should be 14:00 (2 PM) UTC
        self.assertEqual(next_reset.hour, 14)
        self.assertEqual(next_reset.minute, 0)
    
    def test_custom_reset_hour(self):
        """Test with custom reset hour."""
        # Test at 10:30 AM UTC with custom reset at 15:00
        current_time = datetime(2024, 1, 1, 10, 30, tzinfo=timezone.utc)
        next_reset = ccusage_monitor.get_next_reset_time(current_time, custom_reset_hour=15, timezone_str='UTC')
        
        # Should be 15:00 (3 PM) UTC
        self.assertEqual(next_reset.hour, 15)
        self.assertEqual(next_reset.minute, 0)
    
    def test_next_day_reset(self):
        """Test when next reset is tomorrow."""
        # Test at 23:30 PM UTC
        current_time = datetime(2024, 1, 1, 23, 30, tzinfo=timezone.utc)
        next_reset = ccusage_monitor.get_next_reset_time(current_time, timezone_str='UTC')
        
        # Should be 04:00 (4 AM) next day UTC
        self.assertEqual(next_reset.hour, 4)
        self.assertEqual(next_reset.minute, 0)
        self.assertEqual(next_reset.day, 2)


class TestTokenLimit(unittest.TestCase):
    """Test the get_token_limit function."""
    
    def test_pro_limit(self):
        """Test Pro plan limit."""
        self.assertEqual(ccusage_monitor.get_token_limit('pro'), 7000)
    
    def test_max5_limit(self):
        """Test Max5 plan limit."""
        self.assertEqual(ccusage_monitor.get_token_limit('max5'), 35000)
    
    def test_max20_limit(self):
        """Test Max20 plan limit."""
        self.assertEqual(ccusage_monitor.get_token_limit('max20'), 140000)
    
    def test_custom_max_no_blocks(self):
        """Test custom_max with no blocks."""
        self.assertEqual(ccusage_monitor.get_token_limit('custom_max', None), 7000)
        self.assertEqual(ccusage_monitor.get_token_limit('custom_max', []), 7000)
    
    def test_custom_max_with_blocks(self):
        """Test custom_max with blocks."""
        blocks = [
            {'isGap': False, 'isActive': False, 'totalTokens': 10000},
            {'isGap': False, 'isActive': False, 'totalTokens': 25000},
            {'isGap': False, 'isActive': True, 'totalTokens': 5000},  # Active, should be ignored
            {'isGap': True, 'isActive': False, 'totalTokens': 50000},  # Gap, should be ignored
        ]
        self.assertEqual(ccusage_monitor.get_token_limit('custom_max', blocks), 25000)


class TestCheckCcusageInstalled(unittest.TestCase):
    """Test the check_ccusage_installed function."""
    
    @patch('shutil.which')
    def test_ccusage_installed(self, mock_which):
        """Test when ccusage is installed."""
        mock_which.return_value = '/usr/local/bin/ccusage'
        self.assertTrue(ccusage_monitor.check_ccusage_installed())
    
    @patch('shutil.which')
    @patch('builtins.print')
    def test_ccusage_not_installed(self, mock_print, mock_which):
        """Test when ccusage is not installed."""
        mock_which.return_value = None
        self.assertFalse(ccusage_monitor.check_ccusage_installed())
        # Check that error message was printed
        mock_print.assert_any_call("❌ 'ccusage' command not found!")


class TestRunCcusage(unittest.TestCase):
    """Test the run_ccusage function."""
    
    @patch('subprocess.run')
    def test_successful_run(self, mock_run):
        """Test successful ccusage execution."""
        mock_result = MagicMock()
        mock_result.stdout = '{"blocks": [{"totalTokens": 1000}]}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = ccusage_monitor.run_ccusage()
        self.assertIsNotNone(result)
        self.assertIn('blocks', result)
        self.assertEqual(result['blocks'][0]['totalTokens'], 1000)
    
    @patch('subprocess.run')
    def test_command_not_found(self, mock_run):
        """Test when ccusage command is not found."""
        mock_run.side_effect = FileNotFoundError()
        result = ccusage_monitor.run_ccusage()
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_json_decode_error(self, mock_run):
        """Test when ccusage returns invalid JSON."""
        mock_result = MagicMock()
        mock_result.stdout = 'invalid json'
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = ccusage_monitor.run_ccusage()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()