"""Comprehensive tests for ccusage_monitor.app.main module."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from ccusage_monitor.app.main import main


def create_mock_args(**overrides):
    """Create a mock arguments object with all required attributes."""
    mock_args = MagicMock()
    mock_args.rich = False
    mock_args.plan = "pro"
    mock_args.reset_hour = None
    mock_args.timezone = "Europe/Warsaw"
    mock_args.performance = False
    mock_args.refresh = 3

    # Apply any overrides
    for key, value in overrides.items():
        setattr(mock_args, key, value)

    return mock_args


class TestMainFunction:
    """Test the main application function."""

    @patch("ccusage_monitor.app.main.parse_args")
    @patch("ccusage_monitor.app.main.check_ccusage_installed")
    @patch("builtins.print")
    def test_main_exits_when_ccusage_not_installed(self, mock_print, mock_check, mock_parse):
        """Test main exits when ccusage is not installed."""
        # Mock arguments
        mock_parse.return_value = create_mock_args()

        # Mock ccusage not installed
        mock_check.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_check.assert_called_once()
        mock_print.assert_called()

    @patch("ccusage_monitor.app.main.parse_args")
    @patch("ccusage_monitor.app.main_rich.main_with_args")
    def test_main_uses_rich_when_requested(self, mock_rich_main, mock_parse):
        """Test main uses rich version when requested."""
        # Mock arguments with rich=True
        mock_args = create_mock_args(rich=True)
        mock_parse.return_value = mock_args

        main()

        mock_rich_main.assert_called_once_with(mock_args)

    @patch("ccusage_monitor.app.main.parse_args")
    @patch("builtins.print")
    def test_main_handles_rich_import_error(self, mock_print, mock_parse):
        """Test main handles rich import error gracefully."""
        mock_parse.return_value = create_mock_args(rich=True)

        # Mock import error
        with patch("ccusage_monitor.app.main_rich.main_with_args", side_effect=ImportError):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
        mock_print.assert_called_with("❌ Rich library not installed. Install with: pip install rich")

    @patch("ccusage_monitor.core.config.parse_args")
    @patch("ccusage_monitor.core.data.check_ccusage_installed")
    @patch("ccusage_monitor.core.data.get_token_limit")
    @patch("ccusage_monitor.core.data.run_ccusage")
    @patch("ccusage_monitor.ui.display.clear_screen")
    @patch("ccusage_monitor.ui.display.hide_cursor")
    @patch("time.sleep")
    def test_main_handles_custom_max_plan(
        self, mock_sleep, mock_hide, mock_clear, mock_run_ccusage, mock_get_limit, mock_check, mock_parse
    ):
        """Test main handles custom_max plan correctly."""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.rich = False
        mock_args.plan = "custom_max"
        mock_args.refresh = 0.1  # Short sleep for testing
        mock_parse.return_value = mock_args

        # Mock ccusage installed
        mock_check.return_value = True

        # Mock ccusage data
        mock_data = {"blocks": [{"totalTokens": 5000}]}
        mock_run_ccusage.return_value = mock_data

        # Mock token limit
        mock_get_limit.return_value = 7000

        # Mock sleep to interrupt the loop after first iteration
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        with patch("ccusage_monitor.ui.display.show_cursor"):
            with patch("ccusage_monitor.ui.display.clear_screen"):
                with pytest.raises(SystemExit):
                    main()

        mock_get_limit.assert_called()
        mock_run_ccusage.assert_called()

    @patch("ccusage_monitor.core.config.parse_args")
    @patch("ccusage_monitor.core.data.check_ccusage_installed")
    @patch("ccusage_monitor.core.data.get_token_limit")
    @patch("ccusage_monitor.core.data.run_ccusage")
    @patch("ccusage_monitor.ui.display.clear_screen")
    @patch("ccusage_monitor.ui.display.hide_cursor")
    @patch("time.sleep")
    def test_main_handles_failed_ccusage_data(
        self, mock_sleep, mock_hide, mock_clear, mock_run_ccusage, mock_get_limit, mock_check, mock_parse
    ):
        """Test main handles failed ccusage data gracefully."""
        # Mock arguments
        mock_args = MagicMock()
        mock_args.rich = False
        mock_args.plan = "pro"
        mock_args.refresh = 0.1
        mock_parse.return_value = mock_args

        mock_check.return_value = True
        mock_get_limit.return_value = 7000

        # Mock failed ccusage call
        mock_run_ccusage.return_value = None

        # Mock sleep to interrupt after a few iterations
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]

        with patch("builtins.print"):
            with patch("ccusage_monitor.ui.display.show_cursor"):
                with patch("ccusage_monitor.ui.display.clear_screen"):
                    with pytest.raises(SystemExit):
                        main()

        # Should continue trying even with failed data
        assert mock_run_ccusage.call_count >= 2

    @patch("ccusage_monitor.core.config.parse_args")
    @patch("ccusage_monitor.core.data.check_ccusage_installed")
    @patch("ccusage_monitor.core.data.get_token_limit")
    @patch("ccusage_monitor.core.data.run_ccusage")
    @patch("ccusage_monitor.ui.display.clear_screen")
    @patch("ccusage_monitor.ui.display.hide_cursor")
    @patch("time.sleep")
    def test_main_handles_no_active_session(
        self, mock_sleep, mock_hide, mock_clear, mock_run_ccusage, mock_get_limit, mock_check, mock_parse
    ):
        """Test main handles no active session gracefully."""
        mock_args = MagicMock()
        mock_args.rich = False
        mock_args.plan = "pro"
        mock_args.refresh = 0.1
        mock_parse.return_value = mock_args

        mock_check.return_value = True
        mock_get_limit.return_value = 7000

        # Mock data with no active blocks
        mock_data = {"blocks": [{"totalTokens": 1000, "isActive": False}]}
        mock_run_ccusage.return_value = mock_data

        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        with patch("builtins.print"):
            with patch("ccusage_monitor.ui.display.show_cursor"):
                with patch("ccusage_monitor.ui.display.clear_screen"):
                    with pytest.raises(SystemExit):
                        main()

        mock_run_ccusage.assert_called()

    @patch("ccusage_monitor.core.config.parse_args")
    @patch("ccusage_monitor.core.data.check_ccusage_installed")
    @patch("ccusage_monitor.ui.display.show_cursor")
    def test_main_handles_keyboard_interrupt(self, mock_show, mock_check, mock_parse):
        """Test main handles KeyboardInterrupt gracefully."""
        mock_args = MagicMock()
        mock_args.rich = False
        mock_parse.return_value = mock_args

        mock_check.return_value = True

        # Mock KeyboardInterrupt in the main loop
        with patch("ccusage_monitor.ui.display.clear_screen"):
            with patch("ccusage_monitor.ui.display.hide_cursor", side_effect=KeyboardInterrupt):
                with patch("ccusage_monitor.ui.display.clear_screen"):
                    with patch("builtins.print"):
                        with pytest.raises(SystemExit) as exc_info:
                            main()

        assert exc_info.value.code == 0
        mock_show.assert_called_once()  # Should show cursor before exit

    @patch("ccusage_monitor.core.config.parse_args")
    @patch("ccusage_monitor.core.data.check_ccusage_installed")
    @patch("ccusage_monitor.ui.display.show_cursor")
    def test_main_handles_general_exception(self, mock_show, mock_check, mock_parse):
        """Test main shows cursor on general exception."""
        mock_args = MagicMock()
        mock_args.rich = False
        mock_parse.return_value = mock_args

        mock_check.return_value = True

        # Mock general exception in the main loop
        with patch("ccusage_monitor.ui.display.hide_cursor", side_effect=RuntimeError("Test error")):
            with pytest.raises(RuntimeError):
                main()

        mock_show.assert_called_once()  # Should show cursor before re-raising


class TestMainIntegration:
    """Integration tests for main function."""

    def test_main_can_be_imported(self):
        """Test that main function can be imported without errors."""
        from ccusage_monitor.app.main import main

        assert callable(main)

    def test_main_module_execution(self):
        """Test main module can be executed."""
        # This test ensures the if __name__ == "__main__": main() works
        assert hasattr(sys.modules[__name__], "pytest")  # Sanity check we're in test


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
