"""
Unit tests for PortfolioHelper functionality.
"""

import pytest
from unittest.mock import Mock, patch
from dumbfi.utils import PortfolioHelper
from dumbfi.finance import Portfolio


class TestPortfolioHelper:
    """Test PortfolioHelper utility functions."""

    def test_get_display_positions_with_positions(self, sample_portfolio):
        """Test getting display positions from portfolio with positions."""
        positions = PortfolioHelper.get_display_positions(sample_portfolio)

        assert isinstance(positions, list)
        assert len(positions) >= 3  # At least AAPL, MSFT, and CASH

        # Check that all positions are tuples with (ticker, value)
        for ticker, value in positions:
            assert isinstance(ticker, str)
            assert isinstance(value, (int, float))

        # Check specific positions exist
        tickers = [pos[0] for pos in positions]
        assert "AAPL" in tickers
        assert "MSFT" in tickers
        assert "CASH" in tickers

    def test_get_display_positions_empty_portfolio(self):
        """Test getting display positions from empty portfolio."""
        portfolio = Portfolio(initial_cash=50000, name="Empty Portfolio")
        positions = PortfolioHelper.get_display_positions(portfolio)

        assert len(positions) == 1  # Only CASH
        assert positions[0][0] == "CASH"
        assert positions[0][1] == 50000  # Initial cash

    def test_get_display_positions_cash_value(self, sample_portfolio):
        """Test that CASH position shows correct remaining cash."""
        positions = PortfolioHelper.get_display_positions(sample_portfolio)

        cash_position = next((pos for pos in positions if pos[0] == "CASH"), None)
        assert cash_position is not None

        # Should match portfolio's cash (after trades)
        expected_cash = sample_portfolio.cash
        assert cash_position[1] == expected_cash

    def test_execute_trade_buy_success(self):
        """Test successful buy trade execution."""
        portfolio = Portfolio(initial_cash=100000, name="Test Portfolio")

        with patch("dumbfi.utils.logger") as mock_logger:
            result = PortfolioHelper.execute_trade(portfolio, "AAPL", 10, 150.0, 0.001)

        assert result is True
        assert "AAPL" in portfolio.positions
        assert portfolio.positions["AAPL"].quantity == 10
        assert portfolio.positions["AAPL"].avg_cost == 150.0

        # Check logging
        mock_logger.info.assert_called_once()
        assert "Bought 10 shares of AAPL" in mock_logger.info.call_args[0][0]

    def test_execute_trade_sell_success(self, sample_portfolio):
        """Test successful sell trade execution."""
        initial_aapl_quantity = sample_portfolio.positions["AAPL"].quantity

        with patch("dumbfi.utils.logger") as mock_logger:
            result = PortfolioHelper.execute_trade(
                sample_portfolio, "AAPL", -5, 155.0, 0.001
            )

        assert result is True
        assert sample_portfolio.positions["AAPL"].quantity == initial_aapl_quantity - 5

        # Check logging
        mock_logger.info.assert_called_once()
        assert "Sold 5 shares of AAPL" in mock_logger.info.call_args[0][0]

    def test_execute_trade_insufficient_funds(self):
        """Test trade execution with insufficient funds."""
        portfolio = Portfolio(initial_cash=1000, name="Low Cash Portfolio")

        with patch("dumbfi.utils.logger") as mock_logger:
            result = PortfolioHelper.execute_trade(
                portfolio,
                "AAPL",
                100,
                150.0,
                0.001,  # Costs $15,015
            )

        assert result is False
        assert len(portfolio.positions) == 0  # No position created

        # Check warning logged
        mock_logger.warning.assert_called_once()
        assert "Trade failed" in mock_logger.warning.call_args[0][0]

    def test_execute_trade_insufficient_shares(self, sample_portfolio):
        """Test trade execution with insufficient shares to sell."""
        with patch("dumbfi.utils.logger") as mock_logger:
            result = PortfolioHelper.execute_trade(
                sample_portfolio,
                "AAPL",
                -50,
                155.0,
                0.001,  # Trying to sell 50, only have 10
            )

        assert result is False

        # Position should remain unchanged
        assert sample_portfolio.positions["AAPL"].quantity == 10

        # Check warning logged
        mock_logger.warning.assert_called_once()
        assert "Trade failed" in mock_logger.warning.call_args[0][0]

    def test_execute_trade_zero_quantity(self, sample_portfolio):
        """Test trade execution with zero quantity."""
        with patch("dumbfi.utils.logger") as mock_logger:
            result = PortfolioHelper.execute_trade(
                sample_portfolio, "AAPL", 0, 150.0, 0.001
            )

        assert result is True  # Zero quantity trade should succeed

        # Check logging (should show 0 shares)
        mock_logger.info.assert_called_once()
        assert "0 shares" in mock_logger.info.call_args[0][0]

    def test_execute_trade_exception_handling(self, sample_portfolio):
        """Test trade execution with exception handling."""
        # Mock portfolio.add_position to raise an exception
        with patch.object(
            sample_portfolio, "add_position", side_effect=Exception("Mock error")
        ):
            with patch("dumbfi.utils.logger") as mock_logger:
                result = PortfolioHelper.execute_trade(
                    sample_portfolio, "AAPL", 10, 150.0, 0.001
                )

        assert result is False

        # Check error logged
        mock_logger.error.assert_called_once()
        assert "Trade execution error" in mock_logger.error.call_args[0][0]

    def test_update_portfolio_displays_value_widget(self, sample_portfolio):
        """Test updating portfolio displays with value widget."""
        # Mock widget manager with a TextBoxWidget
        mock_text_widget = Mock()
        mock_widget_manager = Mock()
        mock_widget_manager.find_widget_by_type.return_value = mock_text_widget

        PortfolioHelper.update_portfolio_displays(sample_portfolio, mock_widget_manager)

        # Check that value widget was updated
        assert mock_text_widget.total_aum == sample_portfolio.get_total_value()

    def test_update_portfolio_displays_holdings_widget(self, sample_portfolio):
        """Test updating portfolio displays with holdings widget."""
        # Mock widget manager with a ScrollableListWidget
        mock_holdings_widget = Mock()
        mock_widget_manager = Mock()
        mock_widget_manager.find_widget_by_type.side_effect = [
            None,
            mock_holdings_widget,
        ]

        PortfolioHelper.update_portfolio_displays(sample_portfolio, mock_widget_manager)

        # Check that holdings widget was updated
        expected_positions = PortfolioHelper.get_display_positions(sample_portfolio)
        assert mock_holdings_widget.positions == expected_positions

    def test_update_portfolio_displays_no_widgets(self, sample_portfolio):
        """Test updating portfolio displays when no widgets found."""
        mock_widget_manager = Mock()
        mock_widget_manager.find_widget_by_type.return_value = None

        # Should not raise exception when no widgets found
        PortfolioHelper.update_portfolio_displays(sample_portfolio, mock_widget_manager)

        # Verify find_widget_by_type was called
        assert mock_widget_manager.find_widget_by_type.called

    def test_update_portfolio_displays_records_snapshot(self, sample_portfolio):
        """Test that updating displays records a performance snapshot."""
        mock_widget_manager = Mock()
        mock_widget_manager.find_widget_by_type.return_value = None

        initial_snapshots = len(sample_portfolio._performance_history)

        PortfolioHelper.update_portfolio_displays(sample_portfolio, mock_widget_manager)

        # Should have recorded one additional snapshot
        assert len(sample_portfolio._performance_history) == initial_snapshots + 1
