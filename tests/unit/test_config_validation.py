"""
Unit tests for ConfigValidator functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
from dumbfi.utils import ConfigValidator
from dumbfi.config import GameConfig, UIConfig, LayoutType


class TestConfigValidator:
    """Test ConfigValidator utility functions."""

    def test_validate_and_fix_config_valid_configs(
        self, default_game_config, standard_ui_config
    ):
        """Test validation with valid configurations."""
        config_warnings, layout_warnings = ConfigValidator.validate_and_fix_config(
            default_game_config, standard_ui_config
        )

        assert isinstance(config_warnings, list)
        assert isinstance(layout_warnings, list)
        # Valid configs should have minimal warnings
        assert len(config_warnings) <= 1  # Might warn about missing data file
        assert len(layout_warnings) == 0

    def test_validate_and_fix_config_invalid_game_config(self, standard_ui_config):
        """Test validation with invalid game configuration."""
        # Create invalid game config
        invalid_config = GameConfig()
        invalid_config.screen_width = -100  # Invalid
        invalid_config.screen_height = 0  # Invalid
        invalid_config.screen_fps = -5  # Invalid
        invalid_config.start_cash = -1000  # Invalid
        invalid_config.transaction_fee = 2.0  # Invalid (> 1)

        config_warnings, layout_warnings = ConfigValidator.validate_and_fix_config(
            invalid_config, standard_ui_config
        )

        assert len(config_warnings) >= 4  # Should have multiple warnings
        assert any(
            "Screen dimensions must be positive" in warning
            for warning in config_warnings
        )
        assert any("FPS must be positive" in warning for warning in config_warnings)
        assert any(
            "Starting cash must be positive" in warning for warning in config_warnings
        )
        assert any(
            "Transaction fee must be between 0 and 1" in warning
            for warning in config_warnings
        )

    def test_validate_and_fix_config_invalid_ui_config(self, default_game_config):
        """Test validation with invalid UI configuration."""
        # Create invalid UI config
        invalid_ui_config = UIConfig.from_layout_type(LayoutType.STANDARD)

        # Make timeline extend beyond screen
        invalid_ui_config.timeline.width = 500  # Screen is only 320 wide
        invalid_ui_config.timeline.height = -10  # Negative height

        config_warnings, layout_warnings = ConfigValidator.validate_and_fix_config(
            default_game_config, invalid_ui_config
        )

        assert len(layout_warnings) >= 2
        assert any(
            "timeline extends beyond right edge" in warning
            for warning in layout_warnings
        )
        assert any(
            "timeline has invalid dimensions" in warning for warning in layout_warnings
        )

    def test_validate_and_fix_config_logging(
        self, default_game_config, standard_ui_config
    ):
        """Test that validation logs warnings properly."""
        # Create config with one warning
        config_with_warning = GameConfig()
        config_with_warning.market_data_file = "nonexistent_file.csv"

        with patch("dumbfi.utils.logger") as mock_logger:
            ConfigValidator.validate_and_fix_config(
                config_with_warning, standard_ui_config
            )

        # Should have logged warnings
        assert mock_logger.warning.called

        # Check that warnings were logged with correct prefixes
        warning_calls = mock_logger.warning.call_args_list
        config_warnings = [
            call for call in warning_calls if call[0][0].startswith("Config:")
        ]
        assert len(config_warnings) >= 1

    def test_auto_fix_data_path_file_exists(self, default_game_config):
        """Test auto-fix when data file already exists."""
        original_path = default_game_config.market_data_file

        with patch.object(Path, "exists", return_value=True):
            fixed_config = ConfigValidator.auto_fix_data_path(default_game_config)

        # Should not change path if file exists
        assert fixed_config.market_data_file == original_path

    def test_auto_fix_data_path_no_alternatives(self, default_game_config):
        """Test auto-fix when no alternative files exist."""
        with patch.object(Path, "exists", return_value=False):
            fixed_config = ConfigValidator.auto_fix_data_path(default_game_config)

        # Should keep original path if no alternatives found
        assert fixed_config.market_data_file == default_game_config.market_data_file

    def test_auto_fix_data_path_functional(self, default_game_config):
        """Test auto-fix functionality without complex mocking."""
        # This tests the function works without crashing
        fixed_config = ConfigValidator.auto_fix_data_path(default_game_config)

        # Should return a valid config
        assert isinstance(fixed_config, type(default_game_config))
        assert hasattr(fixed_config, "market_data_file")
        assert isinstance(fixed_config.market_data_file, str)

    def test_auto_fix_data_path_preserves_other_config(self, default_game_config):
        """Test that auto-fix only changes data path, not other config."""
        original_theme = default_game_config.theme.name
        original_cash = default_game_config.start_cash
        original_fee = default_game_config.transaction_fee

        with patch.object(Path, "exists", return_value=False):
            fixed_config = ConfigValidator.auto_fix_data_path(default_game_config)

        # Other config should be unchanged
        assert fixed_config.theme.name == original_theme
        assert fixed_config.start_cash == original_cash
        assert fixed_config.transaction_fee == original_fee
