"""
Modern Portfolio Theory - Interactive Exploration

This notebook demonstrates the core concepts of Modern Portfolio Theory using
the DumbFi finance library. We'll explore the efficient frontier, risk-return
tradeoffs, and portfolio optimization.
"""

import marimo as mo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

# Import our new finance library
from dumbfi.finance import MarketData, PortfolioOptimizer, Portfolio


def app(mo):
    mo.md("# Modern Portfolio Theory Explorer")

    mo.md("""
    This notebook demonstrates **Modern Portfolio Theory** using real market data.
    We'll build efficient portfolios and explore the risk-return tradeoff that 
    Nobel Prize winner Harry Markowitz discovered.
    """)

    # Load market data
    mo.md("## Step 1: Load Market Data")

    data_file = "data/sample_prices.csv"  # Use our sample data
    market_data = MarketData(data_file)

    if market_data._prices_df is not None:
        prices_df = market_data.get_prices_dataframe()
        mo.md(f"""
        ✅ **Loaded market data successfully!**
        - **Assets**: {len(prices_df.columns)}
        - **Time period**: {prices_df.index[0].strftime("%Y-%m-%d")} to {prices_df.index[-1].strftime("%Y-%m-%d")}
        - **Trading days**: {len(prices_df)}
        """)

        # Show price data preview
        mo.md("### Price Data Preview")
        mo.dataframe(prices_df.head(10))

        # Filter to assets with sufficient data
        valid_tickers = market_data.filter_by_availability(min_data_points=200)
        mo.md(
            f"**Assets with sufficient data**: {len(valid_tickers)} (need 200+ data points)"
        )

        # Take a subset for demonstration (top 10 by data availability)
        selected_tickers = (
            valid_tickers[:10] if len(valid_tickers) >= 10 else valid_tickers
        )
        selected_prices = prices_df[selected_tickers].dropna()

        mo.md(f"**Selected assets for analysis**: {', '.join(selected_tickers)}")

    else:
        mo.md(
            "❌ **Could not load market data.** Please check that `data/sample_prices.csv` exists."
        )
        return

    # Portfolio optimization
    mo.md("## Step 2: Portfolio Optimization")

    if len(selected_tickers) >= 3:
        optimizer = PortfolioOptimizer(selected_prices)

        # Calculate expected returns and covariance
        mu = optimizer.calculate_expected_returns(method="mean_historical")
        S = optimizer.calculate_covariance_matrix(method="sample_cov")

        mo.md("### Expected Returns (Annual)")
        returns_df = pd.DataFrame(
            {
                "Asset": mu.index,
                "Expected Return": [f"{ret:.1%}" for ret in mu.values],
                "Expected Return (Raw)": mu.values,
            }
        ).sort_values("Expected Return (Raw)", ascending=False)
        mo.dataframe(returns_df[["Asset", "Expected Return"]])

        mo.md("### Risk (Volatility)")
        volatilities = np.sqrt(np.diag(S))
        vol_df = pd.DataFrame(
            {
                "Asset": S.index,
                "Volatility": [f"{vol:.1%}" for vol in volatilities],
                "Volatility (Raw)": volatilities,
            }
        ).sort_values("Volatility (Raw)", ascending=False)
        mo.dataframe(vol_df[["Asset", "Volatility"]])

    else:
        mo.md("❌ **Insufficient assets for optimization.** Need at least 3 assets.")
        return

    # Generate efficient frontier
    mo.md("## Step 3: The Efficient Frontier")

    mo.md("""
    The **efficient frontier** shows the best possible risk-return combinations.
    Each point represents a portfolio that gives the highest expected return
    for a given level of risk.
    """)

    try:
        frontier_df = optimizer.generate_efficient_frontier(num_points=50)

        if len(frontier_df) > 0:
            # Plot efficient frontier
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(
                frontier_df["volatility"] * 100,
                frontier_df["return"] * 100,
                c=frontier_df["sharpe_ratio"],
                cmap="viridis",
                alpha=0.7,
            )
            ax.set_xlabel("Risk (Volatility) %")
            ax.set_ylabel("Expected Return %")
            ax.set_title("Efficient Frontier")

            # Add colorbar for Sharpe ratio
            cbar = plt.colorbar(ax.collections[0])
            cbar.set_label("Sharpe Ratio")

            # Add individual asset points
            for i, ticker in enumerate(selected_tickers):
                ret = mu[ticker] * 100
                vol = volatilities[i] * 100
                ax.scatter(vol, ret, marker="x", s=100, c="red", alpha=0.8)
                ax.annotate(
                    ticker,
                    (vol, vol),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                )

            plt.tight_layout()
            mo.pyplot(fig)

        else:
            mo.md("❌ **Could not generate efficient frontier.** Check data quality.")

    except Exception as e:
        mo.md(f"❌ **Error generating efficient frontier**: {str(e)}")

    # Optimize specific portfolios
    mo.md("## Step 4: Optimal Portfolios")

    mo.md("""
    Let's find some optimal portfolios using different objectives:
    """)

    try:
        # Maximum Sharpe ratio portfolio
        max_sharpe_weights, max_sharpe_metrics = optimizer.optimize_max_sharpe(mu, S)

        mo.md("### Maximum Sharpe Ratio Portfolio")
        mo.md("This portfolio provides the best risk-adjusted returns.")

        max_sharpe_df = pd.DataFrame(
            [
                {
                    "Metric": "Expected Return",
                    "Value": f"{max_sharpe_metrics['expected_return']:.1%}",
                },
                {
                    "Metric": "Volatility",
                    "Value": f"{max_sharpe_metrics['volatility']:.1%}",
                },
                {
                    "Metric": "Sharpe Ratio",
                    "Value": f"{max_sharpe_metrics['sharpe_ratio']:.2f}",
                },
            ]
        )
        mo.dataframe(max_sharpe_df)

        # Show portfolio weights
        weights_df = pd.DataFrame(
            [
                {"Asset": asset, "Weight": f"{weight:.1%}"}
                for asset, weight in max_sharpe_weights.items()
                if weight > 0.01  # Only show weights > 1%
            ]
        ).sort_values("Weight", ascending=False)

        mo.md("**Portfolio Weights:**")
        mo.dataframe(weights_df)

        # Minimum volatility portfolio
        min_vol_weights, min_vol_metrics = optimizer.optimize_min_volatility(mu, S)

        mo.md("### Minimum Volatility Portfolio")
        mo.md("This portfolio has the lowest possible risk.")

        min_vol_df = pd.DataFrame(
            [
                {
                    "Metric": "Expected Return",
                    "Value": f"{min_vol_metrics['expected_return']:.1%}",
                },
                {
                    "Metric": "Volatility",
                    "Value": f"{min_vol_metrics['volatility']:.1%}",
                },
                {
                    "Metric": "Sharpe Ratio",
                    "Value": f"{min_vol_metrics['sharpe_ratio']:.2f}",
                },
            ]
        )
        mo.dataframe(min_vol_df)

        min_vol_weights_df = pd.DataFrame(
            [
                {"Asset": asset, "Weight": f"{weight:.1%}"}
                for asset, weight in min_vol_weights.items()
                if weight > 0.01
            ]
        ).sort_values("Weight", ascending=False)

        mo.md("**Portfolio Weights:**")
        mo.dataframe(min_vol_weights_df)

    except Exception as e:
        mo.md(f"❌ **Error optimizing portfolios**: {str(e)}")

    # Compare strategies
    mo.md("## Step 5: Strategy Comparison")

    mo.md("""
    Let's compare different portfolio strategies using backtesting:
    """)

    try:
        # Create strategy comparison
        strategies = {
            "Equal Weight": optimizer.equal_weight_portfolio(),
            "Max Sharpe": max_sharpe_weights,
            "Min Volatility": min_vol_weights,
            "Risk Parity": optimizer.risk_parity_weights(),
        }

        # Backtest strategies
        comparison_df = optimizer.compare_strategies(strategies, rebalance_freq="M")
        comparison_df = comparison_df.round(2)

        mo.md("### Strategy Performance Comparison (Monthly Rebalancing)")
        mo.dataframe(comparison_df)

        # Plot strategy performance
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Return vs Risk scatter
        ax1.scatter(
            comparison_df["volatility"],
            comparison_df["annualized_return"],
            s=100,
            alpha=0.7,
        )
        for strategy in comparison_df.index:
            ax1.annotate(
                strategy,
                (
                    comparison_df.loc[strategy, "volatility"],
                    comparison_df.loc[strategy, "annualized_return"],
                ),
                xytext=(5, 5),
                textcoords="offset points",
            )
        ax1.set_xlabel("Volatility %")
        ax1.set_ylabel("Annualized Return %")
        ax1.set_title("Risk vs Return by Strategy")
        ax1.grid(True, alpha=0.3)

        # Sharpe ratio comparison
        ax2.bar(comparison_df.index, comparison_df["sharpe_ratio"])
        ax2.set_ylabel("Sharpe Ratio")
        ax2.set_title("Sharpe Ratio by Strategy")
        ax2.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        mo.pyplot(fig)

    except Exception as e:
        mo.md(f"❌ **Error comparing strategies**: {str(e)}")

    # Key insights
    mo.md("## Key Insights from Modern Portfolio Theory")

    mo.md("""
    ### What We Learned:
    
    1. **Diversification Benefits**: Combining assets can reduce risk without sacrificing return
    2. **Efficient Frontier**: Shows optimal risk-return combinations
    3. **Sharpe Ratio**: Measures risk-adjusted returns (higher is better)
    4. **No Free Lunch**: Higher returns generally require accepting higher risk
    5. **Optimization Matters**: Strategic portfolio construction can improve outcomes
    
    ### Real-World Considerations:
    
    - **Transaction Costs**: Frequent rebalancing has costs
    - **Estimation Risk**: Historical data may not predict future returns
    - **Market Changes**: Correlations and volatilities change over time  
    - **Behavioral Factors**: Investors don't always act rationally
    
    ### Next Steps:
    
    - Explore **factor models** to understand sources of return
    - Study **Black-Litterman** model for incorporating views
    - Learn about **risk parity** and alternative weighting schemes
    - Investigate **regime changes** and dynamic allocation
    """)


# Run the app
if __name__ == "__main__":
    app(mo)
