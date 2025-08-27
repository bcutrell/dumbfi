"""
Unit tests for PriceUtils functionality.
"""

import pytest
from unittest.mock import Mock, patch
from dumbfi.utils import PriceUtils


class TestPriceUtils:
    """Test PriceUtils utility functions."""

    def test_calculate_transaction_cost_positive_quantity(self):
        """Test transaction cost calculation with positive quantity."""
        result = PriceUtils.calculate_transaction_cost(100, 150.0, 0.001)
        expected = 100 * 150.0 * 0.001  # 15.0

        assert result == expected

    def test_calculate_transaction_cost_negative_quantity(self):
        """Test transaction cost calculation with negative quantity (sell)."""
        result = PriceUtils.calculate_transaction_cost(-50, 200.0, 0.005)
        expected = 50 * 200.0 * 0.005  # 50.0 (absolute value)

        assert result == expected

    def test_calculate_transaction_cost_zero_quantity(self):
        """Test transaction cost calculation with zero quantity."""
        result = PriceUtils.calculate_transaction_cost(0, 150.0, 0.001)

        assert result == 0.0

    def test_calculate_transaction_cost_zero_fee(self):
        """Test transaction cost calculation with zero fee rate."""
        result = PriceUtils.calculate_transaction_cost(100, 150.0, 0.0)

        assert result == 0.0

    def test_update_prices_from_market_success(self, mock_market_data):
        """Test updating prices from market data successfully."""
        tickers = ["AAPL", "MSFT", "GOOGL"]
        date_str = "2024-01-01"

        result = PriceUtils.update_prices_from_market(
            mock_market_data, date_str, tickers
        )

        assert isinstance(result, dict)
        assert len(result) == 3  # All tickers should have prices
        assert "AAPL" in result
        assert "MSFT" in result
        assert "GOOGL" in result

    def test_update_prices_from_market_missing_prices(self):
        """Test updating prices when some prices are missing."""
        mock_market_data = Mock()
        mock_market_data.get_price.side_effect = [150.0, None, 2800.0]  # MSFT missing

        tickers = ["AAPL", "MSFT", "GOOGL"]
        date_str = "2024-01-01"

        result = PriceUtils.update_prices_from_market(
            mock_market_data, date_str, tickers
        )

        assert len(result) == 2  # Only AAPL and GOOGL
        assert "AAPL" in result
        assert "GOOGL" in result
        assert "MSFT" not in result

    def test_update_prices_from_market_empty_tickers(self, mock_market_data):
        """Test updating prices with empty ticker list."""
        result = PriceUtils.update_prices_from_market(
            mock_market_data, "2024-01-01", []
        )

        assert result == {}

    def test_generate_random_prices_default_base(self, sample_tickers):
        """Test generating random prices with default base price."""
        result = PriceUtils.generate_random_prices(sample_tickers)

        assert len(result) == len(sample_tickers)
        assert all(ticker in result for ticker in sample_tickers)
        assert all(price > 0 for price in result.values())

        # Prices should be around 100.0 (default base) with some variation
        for price in result.values():
            assert 80.0 < price < 120.0  # Within reasonable volatility range

    def test_generate_random_prices_custom_base(self, sample_tickers):
        """Test generating random prices with custom base prices."""
        base_prices = {"AAPL": 150.0, "MSFT": 300.0, "GOOGL": 2800.0}

        result = PriceUtils.generate_random_prices(
            sample_tickers[:3],
            base_prices,
            volatility=0.01,  # Low volatility
        )

        assert len(result) == 3

        # Prices should be close to base prices with low volatility
        for ticker in sample_tickers[:3]:
            base_price = base_prices[ticker]
            actual_price = result[ticker]

            # Should be within 2% of base price (with 1% volatility)
            assert base_price * 0.98 < actual_price < base_price * 1.02

    def test_generate_random_prices_empty_tickers(self):
        """Test generating random prices with empty ticker list."""
        result = PriceUtils.generate_random_prices([])

        assert result == {}

    def test_generate_random_prices_high_volatility(self, sample_tickers):
        """Test generating random prices with high volatility."""
        result = PriceUtils.generate_random_prices(
            sample_tickers[:2],
            volatility=0.5,  # 50% volatility
        )

        assert len(result) == 2

        # With high volatility, prices should vary significantly from base (100.0)
        for price in result.values():
            assert 50.0 < price < 150.0  # Wide range due to high volatility

    @patch("random.uniform")
    def test_generate_random_prices_deterministic(self, mock_random, sample_tickers):
        """Test random price generation with mocked randomness."""
        mock_random.return_value = 0.05  # 5% increase

        base_prices = {"AAPL": 100.0}
        result = PriceUtils.generate_random_prices(
            ["AAPL"], base_prices, volatility=0.1
        )

        expected_price = 100.0 * (1 + 0.05)  # 105.0
        assert result["AAPL"] == expected_price

    def test_generate_random_prices_missing_base_price(self):
        """Test generating random prices when ticker not in base prices."""
        base_prices = {"AAPL": 150.0}  # MSFT not included

        result = PriceUtils.generate_random_prices(["AAPL", "MSFT"], base_prices)

        assert len(result) == 2
        assert "AAPL" in result
        assert "MSFT" in result

        # AAPL should use base price, MSFT should use default (100.0)
        assert 140.0 < result["AAPL"] < 160.0  # Around 150.0 base
        assert 80.0 < result["MSFT"] < 120.0  # Around 100.0 default
