"""Test suite for the new consolidated module structure."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest


class TestCoreConfig:
    """Test the core configuration module."""
    
    def test_parse_args_returns_cliargs_protocol(self):
        """Test that parse_args returns CLIArgs protocol."""
        from ccusage_monitor.core.config import parse_args
        
        with patch('sys.argv', ['ccusage-monitor']):
            args = parse_args()
            
        assert hasattr(args, 'plan')
        assert hasattr(args, 'reset_hour')
        assert hasattr(args, 'timezone')
        assert hasattr(args, 'performance')
        assert hasattr(args, 'rich')
        assert hasattr(args, 'refresh')
    
    def test_default_values(self):
        """Test default configuration values."""
        from ccusage_monitor.core.config import parse_args
        
        with patch('sys.argv', ['ccusage-monitor']):
            args = parse_args()
            
        assert args.plan == "pro"
        assert args.timezone == "Europe/Warsaw"
        assert args.refresh == 3
        assert args.performance is False
        assert args.rich is False


class TestCoreCalculations:
    """Test the consolidated calculations module."""
    
    def test_calculate_hourly_burn_rate_with_empty_blocks(self):
        """Test burn rate calculation with empty blocks."""
        from ccusage_monitor.core.calculations import calculate_hourly_burn_rate
        
        current_time = datetime.now(timezone.utc)
        burn_rate = calculate_hourly_burn_rate([], current_time)
        
        assert burn_rate == 0.0
    
    def test_get_next_reset_time_returns_future_time(self):
        """Test that next reset time is in the future."""
        from ccusage_monitor.core.calculations import get_next_reset_time
        
        current_time = datetime.now(timezone.utc)
        reset_time = get_next_reset_time(current_time, None, "Europe/Warsaw")
        
        assert reset_time > current_time
    
    def test_get_token_limit_for_known_plans(self):
        """Test token limits for different plans."""
        from ccusage_monitor.core.calculations import get_token_limit
        
        assert get_token_limit("pro") == 7000
        assert get_token_limit("max5") == 35000
        assert get_token_limit("max20") == 140000


class TestCoreData:
    """Test the consolidated data module."""
    
    def test_check_ccusage_installed_returns_bool(self):
        """Test ccusage installation check."""
        from ccusage_monitor.core.data import check_ccusage_installed
        
        result = check_ccusage_installed()
        assert isinstance(result, bool)
    
    def test_run_ccusage_returns_dict_or_none(self):
        """Test ccusage execution returns proper type."""
        from ccusage_monitor.core.data import run_ccusage
        
        result = run_ccusage()
        assert result is None or isinstance(result, dict)


class TestUIDisplay:
    """Test the consolidated display module."""
    
    def test_create_token_progress_bar_returns_string(self):
        """Test token progress bar creation."""
        from ccusage_monitor.ui.display import create_token_progress_bar
        
        bar = create_token_progress_bar(50.0)
        assert isinstance(bar, str)
        assert len(bar) > 0
    
    def test_create_time_progress_bar_returns_string(self):
        """Test time progress bar creation."""
        from ccusage_monitor.ui.display import create_time_progress_bar
        
        bar = create_time_progress_bar(150, 300)
        assert isinstance(bar, str)
        assert len(bar) > 0
    
    def test_format_time_returns_readable_string(self):
        """Test time formatting function."""
        from ccusage_monitor.ui.display import format_time
        
        formatted = format_time(125)  # 2h 5m
        assert isinstance(formatted, str)
        assert "2h" in formatted
        assert "5m" in formatted


class TestAppMain:
    """Test the main application logic."""
    
    def test_main_function_can_be_imported(self):
        """Test main function can be imported without errors."""
        try:
            from ccusage_monitor.app.main import main  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Main function import failed: {e}")
    
    def test_parse_args_integration(self):
        """Test argument parsing integration."""
        from ccusage_monitor.core.config import parse_args
        
        with patch('sys.argv', ['ccusage-monitor', '--plan', 'max5', '--performance']):
            args = parse_args()
            
        assert args.plan == 'max5'
        assert args.performance is True


class TestModuleStructure:
    """Test the overall module structure and imports."""
    
    def test_core_modules_importable(self):
        """Test that all core modules can be imported."""
        try:
            import ccusage_monitor.core.cache  # noqa: F401
            import ccusage_monitor.core.calculations  # noqa: F401
            import ccusage_monitor.core.config  # noqa: F401
            import ccusage_monitor.core.data  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Core module import failed: {e}")
    
    def test_ui_modules_importable(self):
        """Test that all UI modules can be imported."""
        try:
            import ccusage_monitor.ui.display  # noqa: F401
            import ccusage_monitor.ui.rich_display  # noqa: F401
        except ImportError as e:
            pytest.fail(f"UI module import failed: {e}")
    
    def test_app_modules_importable(self):
        """Test that app modules can be imported."""
        try:
            import ccusage_monitor.app.main  # noqa: F401
        except ImportError as e:
            pytest.fail(f"App module import failed: {e}")
    
    def test_protocols_importable(self):
        """Test that protocols can be imported."""
        try:
            import ccusage_monitor.protocols  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Protocols import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])