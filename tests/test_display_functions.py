#!/usr/bin/env python3
"""
Additional unit tests for display functions in ccusage_monitor.py
"""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ccusage_monitor


class TestPrintHeader(unittest.TestCase):
    """Test the print_header function."""
    
    @patch('builtins.print')
    def test_print_header(self, mock_print):
        """Test that header is printed correctly."""
        ccusage_monitor.print_header()
        
        # Check that print was called multiple times
        self.assertGreater(mock_print.call_count, 0)
        
        # Check that the title is printed
        calls = [str(call) for call in mock_print.call_args_list]
        title_found = any('CLAUDE TOKEN MONITOR' in str(call) for call in calls)
        self.assertTrue(title_found)


class TestParseArgs(unittest.TestCase):
    """Test the parse_args function."""
    
    def test_default_args(self):
        """Test parsing with default arguments."""
        with patch('sys.argv', ['ccusage_monitor.py']):
            args = ccusage_monitor.parse_args()
            self.assertEqual(args.plan, 'pro')
            self.assertIsNone(args.reset_hour)
            self.assertEqual(args.timezone, 'Europe/Warsaw')
    
    def test_custom_args(self):
        """Test parsing with custom arguments."""
        with patch('sys.argv', ['ccusage_monitor.py', '--plan', 'max5', '--reset-hour', '10', '--timezone', 'UTC']):
            args = ccusage_monitor.parse_args()
            self.assertEqual(args.plan, 'max5')
            self.assertEqual(args.reset_hour, 10)
            self.assertEqual(args.timezone, 'UTC')


class TestMainFunction(unittest.TestCase):
    """Test the main function."""
    
    @patch('ccusage_monitor.check_ccusage_installed')
    @patch('builtins.print')
    def test_main_no_ccusage(self, mock_print, mock_check):
        """Test main function when ccusage is not installed."""
        mock_check.return_value = False
        
        with self.assertRaises(SystemExit) as cm:
            with patch('sys.argv', ['ccusage_monitor.py']):
                ccusage_monitor.main()
        
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_any_call("\n❌ Cannot proceed without ccusage. Exiting.")
    
    @patch('ccusage_monitor.check_ccusage_installed')
    @patch('ccusage_monitor.run_ccusage')
    @patch('os.system')
    @patch('builtins.print')
    @patch('time.sleep')
    def test_main_no_active_session(self, mock_sleep, mock_print, mock_system, mock_run, mock_check):
        """Test main function when no active session is found."""
        mock_check.return_value = True
        mock_run.return_value = {'blocks': [{'isActive': False}]}  # No active blocks
        
        # Make sleep raise KeyboardInterrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with self.assertRaises(KeyboardInterrupt):
            with patch('sys.argv', ['ccusage_monitor.py']):
                ccusage_monitor.main()
        
        # Check that "No active session found" was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        no_session_found = any('No active session found' in str(call) for call in print_calls)
        self.assertTrue(no_session_found)


if __name__ == '__main__':
    unittest.main()