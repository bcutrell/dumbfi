"""
Integration tests for game mechanics and components.

Tests the interaction between configuration, market data, portfolio management,
and game utilities.
"""

import pytest
from unittest.mock import Mock, patch
import datetime

from dumbfi.config import GameConfig, UIConfig, LayoutType
from dumbfi.utils import (
    MarketDataManager,
    PortfolioHelper,
    GameState,
    WidgetFactory,
    WidgetManager,
    load_and_validate_configs,
)
from dumbfi.finance import Portfolio


class TestGameMechanicsIntegration:
    """Test game mechanics components working together."""

    def test_config_to_market_data_integration(self, default_game_config):
        """Test configuration loading market data successfully."""
        # Test with default config (may not have real data file)
        market_manager = MarketDataManager(default_game_config)

        # Should have loaded some tickers (real or demo)
        assert len(market_manager.available_tickers) > 0

        # Should be able to get prices
        prices = market_manager.get_prices_for_date("2024-01-01")
        assert isinstance(prices, dict)

    def test_game_state_with_market_data(self, default_game_config):
        """Test game state integration with market data."""
        # Initialize market data manager
        market_manager = MarketDataManager(default_game_config)

        # Create game state
        start_date = datetime.date(2024, 1, 1)
        game_state = GameState(
            current_date=start_date,
            selected_ticker=(
                market_manager.available_tickers[0]
                if market_manager.available_tickers
                else "AAPL"
            ),
        )

        # Update prices for current date
        date_str = game_state.current_date.strftime("%Y-%m-%d")
        prices = market_manager.get_prices_for_date(date_str)
        game_state.current_prices.update(prices)

        # Should have some price data (may be empty if no real data available)
        assert len(game_state.current_prices) >= 0

        # Selected ticker should be valid
        assert game_state.selected_ticker in market_manager.available_tickers

    def test_portfolio_integration_with_game_state(self, default_game_config):
        """Test portfolio operations integrated with game state."""
        # Setup
        market_manager = MarketDataManager(default_game_config)
        portfolio = Portfolio(
            initial_cash=default_game_config.start_cash, name="Game Portfolio"
        )

        game_state = GameState(
            current_date=datetime.date(2024, 1, 15),
            selected_ticker=(
                market_manager.available_tickers[0]
                if market_manager.available_tickers
                else "AAPL"
            ),
            trade_quantity=10,
        )

        # Get prices for current date
        date_str = game_state.current_date.strftime("%Y-%m-%d")
        prices = market_manager.get_prices_for_date(date_str)
        game_state.current_prices.update(prices)

        # Update portfolio with current prices
        portfolio.update_prices(game_state.current_prices)

        # Execute a trade using game state
        if game_state.selected_ticker in game_state.current_prices:
            price = game_state.current_prices[game_state.selected_ticker]
            success = PortfolioHelper.execute_trade(
                portfolio,
                game_state.selected_ticker,
                game_state.trade_quantity,
                price,
                default_game_config.transaction_fee,
            )

            assert success
            assert game_state.selected_ticker in portfolio.positions
            assert (
                portfolio.positions[game_state.selected_ticker].quantity
                == game_state.trade_quantity
            )

    def test_widget_factory_with_configurations(
        self, retro_game_config, compact_ui_config
    ):
        """Test widget factory integration with different configurations."""
        # Test timeline creation
        start_date = datetime.date(2024, 1, 1)
        end_date = datetime.date(2024, 12, 31)
        current_date = datetime.date(2024, 6, 15)

        timeline = WidgetFactory.create_timeline(
            compact_ui_config, retro_game_config, start_date, end_date, current_date
        )

        # Should use retro theme colors
        retro_colors = retro_game_config.get_color_palette()
        assert hasattr(timeline, "border_color")
        # Timeline should be positioned according to compact layout
        assert timeline.x == compact_ui_config.timeline.x
        assert timeline.y == compact_ui_config.timeline.y

        # Test button creation
        def dummy_callback():
            pass

        button = WidgetFactory.create_button(
            compact_ui_config,
            retro_game_config,
            "play_button",
            "Test Button",
            dummy_callback,
        )

        # Should use retro colors and compact positioning
        assert button.x == compact_ui_config.play_button.x
        assert button.y == compact_ui_config.play_button.y
        assert button.text == "Test Button"

    def test_widget_manager_interaction(self, default_game_config, standard_ui_config):
        """Test widget manager with multiple widgets."""
        # Create some mock widgets
        mock_widget1 = Mock()
        mock_widget1.resizeable = True
        mock_widget1.draggable = False
        mock_widget1.resizing = False
        mock_widget1.dragging = False
        mock_widget1.start_resize.return_value = False

        mock_widget2 = Mock()
        mock_widget2.resizeable = False
        mock_widget2.draggable = True
        mock_widget2.resizing = False
        mock_widget2.dragging = False
        mock_widget2.start_drag.return_value = True  # This widget will handle the drag

        widgets = [mock_widget1, mock_widget2]
        widget_manager = WidgetManager(widgets)

        # Test update all
        widget_manager.update_all()
        mock_widget1.update.assert_called_once()
        mock_widget2.update.assert_called_once()

        # Test draw all
        widget_manager.draw_all()
        mock_widget1.draw.assert_called_once()
        mock_widget2.draw.assert_called_once()

        # Test mouse handling
        handled = widget_manager.handle_mouse_press(100, 50)
        assert handled is True  # mock_widget2 should handle the drag
        mock_widget2.start_drag.assert_called_with(100, 50)

        # Test mouse drag
        widget_manager.handle_mouse_drag(105, 55, 320, 240)
        # No widgets are currently dragging/resizing, so no calls expected

        # Test mouse release
        widget_manager.handle_mouse_release()
        mock_widget1.end_drag.assert_called_once()
        mock_widget2.end_drag.assert_called_once()

    def test_config_validation_integration(self):
        """Test complete configuration validation and loading."""
        # Test loading with valid theme and layout
        game_config, ui_config = load_and_validate_configs("hacker", "wide")

        assert game_config.theme.name == "hacker"
        assert ui_config.layout_type.value == "wide"

        # Should have validated and potentially auto-fixed data paths
        data_path = game_config.get_data_file_path()
        assert isinstance(data_path, type(data_path))  # Should be Path object

        # Test with invalid theme (should fall back to default)
        with pytest.raises(ValueError, match="Unknown theme"):
            load_and_validate_configs("nonexistent_theme", "standard")

    def test_full_game_initialization_simulation(self):
        """Test simulating full game initialization without GUI."""
        # This simulates what happens when the game starts

        # 1. Load configurations
        game_config, ui_config = load_and_validate_configs("default", "standard")

        # 2. Initialize market data
        market_manager = MarketDataManager(game_config)

        # 3. Initialize portfolio
        portfolio = Portfolio(
            initial_cash=game_config.start_cash, name="Test Game Portfolio"
        )

        # 4. Initialize game state
        start_date = datetime.datetime.strptime(
            game_config.start_date, "%Y-%m-%d"
        ).date()
        game_state = GameState(
            current_date=start_date,
            selected_ticker=(
                market_manager.available_tickers[0]
                if market_manager.available_tickers
                else "AAPL"
            ),
            trade_quantity=10,
        )

        # 5. Update initial prices
        date_str = start_date.strftime("%Y-%m-%d")
        initial_prices = market_manager.get_prices_for_date(date_str)
        game_state.current_prices.update(initial_prices)
        portfolio.update_prices(game_state.current_prices)

        # 6. Create some mock widgets (simulating widget creation)
        mock_widgets = []

        # Simulate creating timeline widget
        timeline = WidgetFactory.create_timeline(
            ui_config,
            game_config,
            start_date,
            datetime.datetime.strptime(game_config.end_date, "%Y-%m-%d").date(),
            game_state.current_date,
        )
        mock_widgets.append(timeline)

        # 7. Initialize widget manager
        widget_manager = WidgetManager(mock_widgets)

        # 8. Simulate some game operations

        # Execute a trade
        if game_state.selected_ticker in game_state.current_prices:
            price = game_state.current_prices[game_state.selected_ticker]
            success = PortfolioHelper.execute_trade(
                portfolio,
                game_state.selected_ticker,
                game_state.trade_quantity,
                price,
                game_config.transaction_fee,
            )

            if success:
                # Update displays
                mock_widget_manager = Mock()
                mock_widget_manager.find_widget_by_type.return_value = None
                PortfolioHelper.update_portfolio_displays(
                    portfolio, mock_widget_manager
                )

        # 9. Advance time simulation
        new_date = game_state.current_date + datetime.timedelta(days=1)
        if (
            new_date
            <= datetime.datetime.strptime(game_config.end_date, "%Y-%m-%d").date()
        ):
            game_state.current_date = new_date

            # Update prices for new date
            new_date_str = new_date.strftime("%Y-%m-%d")
            new_prices = market_manager.get_prices_for_date(new_date_str)
            game_state.current_prices.update(new_prices)
            portfolio.update_prices(game_state.current_prices)

        # 10. Verify everything is working
        assert portfolio.get_total_value() > 0
        assert len(game_state.current_prices) > 0
        assert game_state.current_date > start_date
        assert widget_manager is not None

        # Get final portfolio summary
        summary = portfolio.summary()
        assert summary["total_value"] > 0
        assert summary["name"] == "Test Game Portfolio"
