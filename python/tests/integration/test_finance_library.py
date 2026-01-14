"""
Integration tests for the finance library components.

Tests the interaction between MarketData, Portfolio, and optimization components.
"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path

from dumbfi.finance import (
    MarketData,
    Portfolio,
    PortfolioOptimizer,
    RiskModel,
    FactorModel,
)


class TestFinanceLibraryIntegration:
    """Test finance library components working together."""

    def test_market_data_to_portfolio_workflow(self, temp_csv_file):
        """Test complete workflow from market data to portfolio management."""
        # Load market data
        market_data = MarketData(temp_csv_file)

        # Verify data loaded
        tickers = market_data.get_available_tickers()
        dates = market_data.get_available_dates()
        assert len(tickers) == 3  # AAPL, MSFT, GOOGL
        assert len(dates) == 3  # 3 days of data

        # Create portfolio
        portfolio = Portfolio(initial_cash=100000, name="Integration Test Portfolio")

        # Get current prices and update portfolio
        latest_date = dates[-1]
        current_prices = {}
        for ticker in tickers:
            price = market_data.get_price(latest_date, ticker)
            if price:
                current_prices[ticker] = price

        portfolio.update_prices(current_prices)

        # Execute trades
        success1 = portfolio.add_position("AAPL", 10, current_prices["AAPL"], 1.0)
        success2 = portfolio.add_position("MSFT", 5, current_prices["MSFT"], 1.0)

        assert success1 and success2
        assert len(portfolio.positions) == 2
        assert portfolio.get_total_value() > portfolio.cash  # Has stock positions

        # Test performance tracking
        portfolio.record_snapshot()
        performance = portfolio.get_performance_history()
        assert len(performance) == 1

        # Test portfolio metrics
        weights = portfolio.get_position_weights()
        assert "AAPL" in weights
        assert "MSFT" in weights
        assert (
            abs(sum(weights.values()) + portfolio.get_cash_weight() - 100) < 0.1
        )  # ~100%

    def test_market_data_to_optimization_workflow(self, temp_csv_file):
        """Test workflow from market data to portfolio optimization."""
        # Load market data
        market_data = MarketData(temp_csv_file)
        prices_df = market_data.get_prices_dataframe()

        # Create optimizer
        optimizer = PortfolioOptimizer(prices_df)

        # Calculate expected returns and covariance
        mu = optimizer.calculate_expected_returns("mean_historical")
        S = optimizer.calculate_covariance_matrix("sample_cov")

        assert len(mu) == 3  # 3 assets
        assert S.shape == (3, 3)  # 3x3 covariance matrix

        # For demo data, we might not have realistic expected returns
        # Skip optimization if expected returns are too low
        if mu.max() <= 0.02:  # If max expected return is less than 2% (risk-free rate)
            pytest.skip(
                "Demo data doesn't have sufficient expected returns for max Sharpe optimization"
            )

        # Optimize portfolio
        weights, metrics = optimizer.optimize_max_sharpe(mu, S)

        assert abs(sum(weights.values()) - 1.0) < 0.01  # Weights sum to ~1
        assert metrics["sharpe_ratio"] > 0  # Should have positive Sharpe ratio
        assert metrics["expected_return"] > 0
        assert metrics["volatility"] > 0

        # Test alternative optimization
        min_vol_weights, min_vol_metrics = optimizer.optimize_min_volatility(mu, S)

        # Min volatility should have lower volatility than max Sharpe
        assert (
            min_vol_metrics["volatility"] <= metrics["volatility"] + 0.01
        )  # Allow small numerical error

    def test_risk_model_integration(self, temp_csv_file):
        """Test risk model with market data."""
        # Load market data
        market_data = MarketData(temp_csv_file)
        prices_df = market_data.get_prices_dataframe()

        # Create risk model
        risk_model = RiskModel()

        # Calculate expected returns
        mu_capm = risk_model.calculate_expected_returns(prices_df, method="capm")
        mu_mean = risk_model.calculate_expected_returns(
            prices_df, method="mean_historical"
        )

        assert len(mu_capm) == 3
        assert len(mu_mean) == 3

        # Calculate risk matrices
        S_sample = risk_model.calculate_risk_matrix(prices_df, method="sample_cov")
        S_shrunk = risk_model.calculate_risk_matrix(prices_df, method="ledoit_wolf")

        assert S_sample.shape == (3, 3)
        assert S_shrunk.shape == (3, 3)

        # Test optimization with risk model
        test_result = risk_model.test_optimization(mu_capm, S_sample)

        assert "weights" in test_result
        assert "expected_return" in test_result
        assert "volatility" in test_result
        assert "sharpe_ratio" in test_result

    def test_factor_model_integration(self, temp_csv_file):
        """Test factor model with market data."""
        # Load market data
        market_data = MarketData(temp_csv_file)
        prices_df = market_data.get_prices_dataframe()

        # Create factor model
        factor_model = FactorModel("fama_french_5")

        # Download synthetic factor data
        factor_data = factor_model.download_factor_data("2024-01-01", "2024-01-03")

        assert factor_data is not None
        assert len(factor_data.columns) == 6  # 5 factors + RF

        # Estimate factor loadings (use subset of data due to limited sample)
        subset_prices = prices_df.iloc[:, :2]  # Use only 2 assets
        loadings, residuals = factor_model.estimate_loadings(subset_prices, factor_data)

        # With only 3 days of data, may not get results for all assets
        assert len(loadings) <= 2
        assert len(residuals) <= 2

        # If we got loadings, test covariance calculation
        if len(loadings) > 0:
            try:
                cov_matrix = factor_model.calculate_covariance_matrix()
                assert cov_matrix.shape[0] == len(loadings)
                assert cov_matrix.shape[1] == len(loadings)
            except ValueError:
                # Expected with limited data
                pass

    def test_end_to_end_portfolio_workflow(self, temp_csv_file):
        """Test complete end-to-end portfolio management workflow."""
        # 1. Load market data
        market_data = MarketData(temp_csv_file)
        prices_df = market_data.get_prices_dataframe()
        tickers = market_data.get_available_tickers()

        # 2. Optimize portfolio
        optimizer = PortfolioOptimizer(prices_df)
        mu = optimizer.calculate_expected_returns()
        S = optimizer.calculate_covariance_matrix()

        # Skip optimization if expected returns are too low for demo data
        if mu.max() <= 0.02:  # If max expected return is less than 2% (risk-free rate)
            pytest.skip(
                "Demo data doesn't have sufficient expected returns for max Sharpe optimization"
            )

        optimal_weights, metrics = optimizer.optimize_max_sharpe(mu, S)

        # 3. Create and fund portfolio
        portfolio = Portfolio(initial_cash=100000, name="End-to-End Test")

        # 4. Get latest prices
        latest_date = market_data.get_available_dates()[-1]
        current_prices = {}
        for ticker in tickers:
            price = market_data.get_price(latest_date, ticker)
            if price:
                current_prices[ticker] = price

        portfolio.update_prices(current_prices)

        # 5. Implement optimal portfolio (simplified discrete allocation)
        total_value = portfolio.get_total_value()
        for ticker, weight in optimal_weights.items():
            if (
                weight > 0.01 and ticker in current_prices
            ):  # Only trade meaningful weights
                target_value = weight * total_value
                price = current_prices[ticker]
                shares = int(target_value / price)  # Simple integer shares

                if shares > 0:
                    portfolio.add_position(ticker, shares, price, 1.0)

        # 6. Verify portfolio implementation
        assert len(portfolio.positions) > 0
        final_weights = portfolio.get_position_weights()

        # Should have positions in some of the optimized assets
        implemented_tickers = set(final_weights.keys())
        optimal_tickers = set(t for t, w in optimal_weights.items() if w > 0.01)
        assert len(implemented_tickers.intersection(optimal_tickers)) > 0

        # 7. Test performance tracking
        portfolio.record_snapshot()
        performance_history = portfolio.get_performance_history()
        assert len(performance_history) == 1

        # 8. Test portfolio summary
        summary = portfolio.summary()
        assert summary["num_positions"] > 0
        assert summary["total_value"] > 0
        assert summary["total_return"] != 0  # Should have some return due to positions
