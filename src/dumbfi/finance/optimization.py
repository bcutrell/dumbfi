"""
Portfolio optimization utilities using PyPortfolioOpt and custom methods.

Provides interfaces for mean-variance optimization, risk parity, and other approaches.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Any, Tuple
import warnings
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.black_litterman import BlackLittermanModel
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

warnings.filterwarnings("ignore")


class PortfolioOptimizer:
    """
    Portfolio optimization class supporting multiple optimization approaches.
    """

    def __init__(self, prices: pd.DataFrame):
        """
        Initialize optimizer with price data.

        Args:
            prices: DataFrame with date index and ticker columns
        """
        self.prices = prices.dropna()
        self.returns = self.prices.pct_change().dropna()
        self._mu = None
        self._S = None

    def calculate_expected_returns(self, method: str = "mean_historical") -> pd.Series:
        """
        Calculate expected returns using specified method.

        Args:
            method: Method to use ("mean_historical", "capm", "ema")

        Returns:
            Series of expected annual returns
        """
        if method == "mean_historical":
            self._mu = expected_returns.mean_historical_return(self.prices)
        elif method == "capm":
            self._mu = expected_returns.capm_return(self.prices)
        elif method == "ema":
            self._mu = expected_returns.ema_historical_return(self.prices)
        else:
            raise ValueError(f"Unknown expected returns method: {method}")

        return self._mu

    def calculate_covariance_matrix(self, method: str = "sample_cov") -> pd.DataFrame:
        """
        Calculate covariance matrix using specified method.

        Args:
            method: Method to use ("sample_cov", "semicovariance", "exp_cov", "ledoit_wolf")

        Returns:
            Covariance matrix DataFrame
        """
        if method == "sample_cov":
            self._S = risk_models.sample_cov(self.prices, frequency=252)
        elif method == "semicovariance":
            self._S = risk_models.semicovariance(self.prices, frequency=252)
        elif method == "exp_cov":
            self._S = risk_models.exp_cov(self.prices, frequency=252)
        elif method == "ledoit_wolf":
            cs = CovarianceShrinkage(self.prices)
            self._S = cs.ledoit_wolf()
        else:
            raise ValueError(f"Unknown covariance method: {method}")

        return self._S

    def optimize_max_sharpe(
        self, mu: Optional[pd.Series] = None, S: Optional[pd.DataFrame] = None
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Optimize for maximum Sharpe ratio.

        Args:
            mu: Expected returns (uses calculated if None)
            S: Covariance matrix (uses calculated if None)

        Returns:
            Tuple of (weights, performance_metrics)
        """
        if mu is None:
            mu = self._mu or self.calculate_expected_returns()
        if S is None:
            S = self._S or self.calculate_covariance_matrix()

        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe()
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)
        metrics = {
            "expected_return": performance[0],
            "volatility": performance[1],
            "sharpe_ratio": performance[2],
        }

        return cleaned_weights, metrics

    def optimize_min_volatility(
        self, mu: Optional[pd.Series] = None, S: Optional[pd.DataFrame] = None
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Optimize for minimum volatility.

        Args:
            mu: Expected returns (uses calculated if None)
            S: Covariance matrix (uses calculated if None)

        Returns:
            Tuple of (weights, performance_metrics)
        """
        if mu is None:
            mu = self._mu or self.calculate_expected_returns()
        if S is None:
            S = self._S or self.calculate_covariance_matrix()

        ef = EfficientFrontier(mu, S)
        weights = ef.min_volatility()
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)
        metrics = {
            "expected_return": performance[0],
            "volatility": performance[1],
            "sharpe_ratio": performance[2],
        }

        return cleaned_weights, metrics

    def optimize_target_return(
        self,
        target_return: float,
        mu: Optional[pd.Series] = None,
        S: Optional[pd.DataFrame] = None,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Optimize for a target return level.

        Args:
            target_return: Target annual return (e.g., 0.12 for 12%)
            mu: Expected returns (uses calculated if None)
            S: Covariance matrix (uses calculated if None)

        Returns:
            Tuple of (weights, performance_metrics)
        """
        if mu is None:
            mu = self._mu or self.calculate_expected_returns()
        if S is None:
            S = self._S or self.calculate_covariance_matrix()

        ef = EfficientFrontier(mu, S)
        weights = ef.efficient_return(target_return)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)
        metrics = {
            "expected_return": performance[0],
            "volatility": performance[1],
            "sharpe_ratio": performance[2],
        }

        return cleaned_weights, metrics

    def optimize_target_volatility(
        self,
        target_volatility: float,
        mu: Optional[pd.Series] = None,
        S: Optional[pd.DataFrame] = None,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Optimize for a target volatility level.

        Args:
            target_volatility: Target annual volatility (e.g., 0.15 for 15%)
            mu: Expected returns (uses calculated if None)
            S: Covariance matrix (uses calculated if None)

        Returns:
            Tuple of (weights, performance_metrics)
        """
        if mu is None:
            mu = self._mu or self.calculate_expected_returns()
        if S is None:
            S = self._S or self.calculate_covariance_matrix()

        ef = EfficientFrontier(mu, S)
        weights = ef.efficient_risk(target_volatility)
        cleaned_weights = ef.clean_weights()

        performance = ef.portfolio_performance(verbose=False)
        metrics = {
            "expected_return": performance[0],
            "volatility": performance[1],
            "sharpe_ratio": performance[2],
        }

        return cleaned_weights, metrics

    def risk_parity_weights(self) -> Dict[str, float]:
        """
        Calculate risk parity portfolio weights.
        Each asset contributes equally to portfolio risk.

        Returns:
            Dictionary of asset weights
        """
        S = self._S or self.calculate_covariance_matrix()

        # Simple equal risk contribution approximation
        # For exact risk parity, would need iterative solver
        inv_vol = 1 / np.sqrt(np.diag(S))
        weights = inv_vol / inv_vol.sum()

        return dict(zip(S.columns, weights))

    def equal_weight_portfolio(self) -> Dict[str, float]:
        """
        Create equal weight portfolio.

        Returns:
            Dictionary of equal weights
        """
        n_assets = len(self.prices.columns)
        weight = 1.0 / n_assets

        return {ticker: weight for ticker in self.prices.columns}

    def market_cap_weighted_portfolio(
        self, market_caps: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Create market capitalization weighted portfolio.

        Args:
            market_caps: Dictionary of ticker -> market cap

        Returns:
            Dictionary of market cap weights
        """
        # Filter to available tickers
        available_caps = {
            ticker: cap
            for ticker, cap in market_caps.items()
            if ticker in self.prices.columns
        }

        total_cap = sum(available_caps.values())
        weights = {ticker: cap / total_cap for ticker, cap in available_caps.items()}

        # Add zero weights for missing tickers
        for ticker in self.prices.columns:
            if ticker not in weights:
                weights[ticker] = 0.0

        return weights

    def generate_efficient_frontier(self, num_points: int = 100) -> pd.DataFrame:
        """
        Generate points on the efficient frontier.

        Args:
            num_points: Number of points to generate

        Returns:
            DataFrame with return, volatility, and Sharpe ratio columns
        """
        mu = self._mu or self.calculate_expected_returns()
        S = self._S or self.calculate_covariance_matrix()

        # Generate range of target returns
        min_ret = mu.min()
        max_ret = mu.max()
        target_returns = np.linspace(min_ret, max_ret, num_points)

        frontier_data = []

        for target_ret in target_returns:
            try:
                ef = EfficientFrontier(mu, S)
                weights = ef.efficient_return(target_ret)
                performance = ef.portfolio_performance(verbose=False)

                frontier_data.append(
                    {
                        "return": performance[0],
                        "volatility": performance[1],
                        "sharpe_ratio": performance[2],
                    }
                )
            except Exception as e:
                # Skip infeasible points
                continue

        return pd.DataFrame(frontier_data)

    def discrete_allocation(
        self,
        weights: Dict[str, float],
        total_value: float,
        latest_prices: Optional[Dict[str, float]] = None,
    ) -> Dict[str, int]:
        """
        Convert portfolio weights to discrete share allocations.

        Args:
            weights: Dictionary of asset weights
            total_value: Total portfolio value to allocate
            latest_prices: Dictionary of latest prices (fetched if None)

        Returns:
            Dictionary of ticker -> number of shares
        """
        if latest_prices is None:
            latest_prices = get_latest_prices(self.prices)

        # Filter weights to only include assets with prices
        filtered_weights = {
            ticker: weight
            for ticker, weight in weights.items()
            if ticker in latest_prices and weight > 0
        }

        if not filtered_weights:
            return {}

        da = DiscreteAllocation(
            filtered_weights, latest_prices, total_portfolio_value=total_value
        )
        allocation, leftover = da.lp_portfolio()

        return allocation

    def backtest_strategy(
        self, weights: Dict[str, float], rebalance_freq: str = "M"
    ) -> pd.DataFrame:
        """
        Backtest a portfolio strategy with rebalancing.

        Args:
            weights: Target portfolio weights
            rebalance_freq: Rebalancing frequency ("D", "W", "M", "Q")

        Returns:
            DataFrame with portfolio value over time
        """
        # Resample prices to rebalancing frequency
        if rebalance_freq == "D":
            rebal_prices = self.prices
        elif rebalance_freq == "W":
            rebal_prices = self.prices.resample("W").last()
        elif rebalance_freq == "M":
            rebal_prices = self.prices.resample("M").last()
        elif rebalance_freq == "Q":
            rebal_prices = self.prices.resample("Q").last()
        else:
            raise ValueError("rebalance_freq must be 'D', 'W', 'M', or 'Q'")

        # Calculate returns between rebalancing dates
        rebal_returns = rebal_prices.pct_change().dropna()

        # Filter weights to available assets
        available_weights = {
            ticker: weights.get(ticker, 0) for ticker in rebal_returns.columns
        }

        # Convert to numpy array
        weight_array = np.array(
            [available_weights[col] for col in rebal_returns.columns]
        )
        weight_array = weight_array / weight_array.sum()  # Normalize

        # Calculate portfolio returns
        portfolio_returns = (rebal_returns * weight_array).sum(axis=1)

        # Calculate cumulative value
        portfolio_value = (1 + portfolio_returns).cumprod()

        return pd.DataFrame(
            {"portfolio_value": portfolio_value, "portfolio_return": portfolio_returns}
        )

    def compare_strategies(
        self, strategies: Dict[str, Dict[str, float]], rebalance_freq: str = "M"
    ) -> pd.DataFrame:
        """
        Compare multiple portfolio strategies.

        Args:
            strategies: Dictionary of strategy_name -> weights
            rebalance_freq: Rebalancing frequency

        Returns:
            DataFrame with strategy performance comparison
        """
        results = []

        for strategy_name, weights in strategies.items():
            backtest_result = self.backtest_strategy(weights, rebalance_freq)

            # Calculate performance metrics
            returns = backtest_result["portfolio_return"]
            final_value = backtest_result["portfolio_value"].iloc[-1]
            total_return = (final_value - 1) * 100

            annualized_return = (returns.mean() * 252) * 100  # Approximate
            volatility = (returns.std() * np.sqrt(252)) * 100
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0

            # Max drawdown
            cumulative = backtest_result["portfolio_value"]
            peak = cumulative.expanding().max()
            drawdown = (cumulative - peak) / peak
            max_drawdown = drawdown.min() * 100

            results.append(
                {
                    "strategy": strategy_name,
                    "total_return": total_return,
                    "annualized_return": annualized_return,
                    "volatility": volatility,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown,
                    "final_value": final_value,
                }
            )

        return pd.DataFrame(results).set_index("strategy")
