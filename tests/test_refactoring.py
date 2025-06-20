#!/usr/bin/env python3
"""
Tests for refactored modules - TDD approach for refactoring ccusage_monitor.py
"""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDisplayModule(unittest.TestCase):
    """Test the display module functions."""

    def test_display_module_exists(self):
        """Test that display module can be imported."""
        try:
            from ccusage_monitor import display

            self.assertTrue(hasattr(display, "print_header"))
            self.assertTrue(hasattr(display, "create_token_progress_bar"))
            self.assertTrue(hasattr(display, "create_time_progress_bar"))
            self.assertTrue(hasattr(display, "format_time"))
        except ImportError:
            self.fail("display module should exist")


class TestDataModule(unittest.TestCase):
    """Test the data module functions."""

    def test_data_module_exists(self):
        """Test that data module can be imported."""
        try:
            from ccusage_monitor import data

            self.assertTrue(hasattr(data, "run_ccusage"))
            self.assertTrue(hasattr(data, "check_ccusage_installed"))
            self.assertTrue(hasattr(data, "get_token_limit"))
        except ImportError:
            self.fail("data module should exist")


class TestCalculationsModule(unittest.TestCase):
    """Test the calculations module functions."""

    def test_calculations_module_exists(self):
        """Test that calculations module can be imported."""
        try:
            from ccusage_monitor import calculations

            self.assertTrue(hasattr(calculations, "calculate_hourly_burn_rate"))
            self.assertTrue(hasattr(calculations, "get_next_reset_time"))
            self.assertTrue(hasattr(calculations, "get_velocity_indicator"))
        except ImportError:
            self.fail("calculations module should exist")


class TestMainModule(unittest.TestCase):
    """Test that main module is simplified after refactoring."""

    def test_main_module_size(self):
        """Test that main module is under 300 lines."""
        main_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ccusage_monitor.py")
        if os.path.exists(main_file):
            with open(main_file) as f:
                lines = f.readlines()
                self.assertLess(len(lines), 300, "Main module should be under 300 lines after refactoring")


if __name__ == "__main__":
    unittest.main()
