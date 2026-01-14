"""
Factor Analysis - Quick Exploration

A short demo of factor models and how they decompose stock returns into
systematic (market) and idiosyncratic (stock-specific) components.
"""

import marimo as mo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import our finance library
from dumbfi.finance import MarketData, FactorModel


def app(mo):
    mo.md("# Factor Analysis Explorer")

    mo.md("""
    **Factor models** help us understand what drives stock returns. Instead of treating 
    each stock independently, we decompose returns into:
    - **Systematic risk**: Driven by market factors (everyone moves together)
    - **Idiosyncratic risk**: Stock-specific movements (company news, etc.)
    """)

    # Load data
    mo.md("## Step 1: Load Data and Estimate Factor Model")

    market_data = MarketData("data/sample_prices.csv")

    if market_data._prices_df is not None:
        prices_df = market_data.get_prices_dataframe()

        # Use first 3 assets for quick demo
        sample_tickers = list(prices_df.columns)[:3]
        sample_prices = prices_df[sample_tickers].dropna()

        mo.md(f"**Analyzing**: {', '.join(sample_tickers)}")

        # Create factor model
        factor_model = FactorModel("fama_french_5")

        # Generate synthetic factor data (in practice, use real FF data)
        factor_data = factor_model.download_factor_data("2024-01-01", "2024-12-31")

        # Estimate factor loadings
        loadings, residuals = factor_model.estimate_loadings(sample_prices, factor_data)

        mo.md("### Factor Loadings (Betas)")
        mo.md("These show how much each stock responds to each factor:")

        # Display loadings table
        loadings_display = loadings[["Mkt-RF", "SMB", "HML", "RMW", "CMA"]].round(3)
        mo.dataframe(loadings_display)

        mo.md("""
        **Factor Meanings:**
        - **Mkt-RF**: Market excess return (beta > 1 = more volatile than market)
        - **SMB**: Small minus Big (positive = small-cap bias)  
        - **HML**: High minus Low (positive = value stock bias)
        - **RMW**: Robust minus Weak (positive = profitable companies bias)
        - **CMA**: Conservative minus Aggressive (positive = low-investment companies bias)
        """)

    else:
        mo.md("❌ Could not load data")
        return

    # Visualize factor exposures
    mo.md("## Step 2: Factor Exposure Visualization")

    if len(loadings) > 0:
        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        axes = axes.flatten()

        factors = ["Mkt-RF", "SMB", "HML", "RMW", "CMA"]

        for i, factor in enumerate(factors):
            ax = axes[i]
            factor_values = loadings[factor]

            bars = ax.bar(range(len(factor_values)), factor_values.values)
            ax.set_title(f"{factor} Factor Loadings")
            ax.set_xticks(range(len(factor_values)))
            ax.set_xticklabels(factor_values.index, rotation=45)
            ax.axhline(y=0, color="black", linestyle="-", alpha=0.3)
            ax.grid(True, alpha=0.3)

            # Color bars based on positive/negative
            for bar, value in zip(bars, factor_values.values):
                if value > 0:
                    bar.set_color("green")
                else:
                    bar.set_color("red")

        # Hide the extra subplot
        axes[5].set_visible(False)

        plt.tight_layout()
        mo.pyplot(fig)

    # Risk decomposition
    mo.md("## Step 3: Risk Decomposition")

    mo.md("""
    Factor models let us decompose each stock's risk into:
    1. **Systematic risk** from factor exposures
    2. **Idiosyncratic risk** that's stock-specific
    """)

    if len(residuals) > 0:
        # Calculate risk decomposition
        risk_data = []

        for ticker in sample_tickers:
            if ticker in loadings.index and ticker in residuals.index:
                # Systematic risk from factor model (simplified)
                systematic_var = (loadings.loc[ticker, "Mkt-RF"] ** 2) * (
                    factor_data["Mkt-RF"].var() * 252
                )

                # Idiosyncratic risk
                idiosyncratic_var = residuals.loc[ticker] * 252  # Annualized

                total_var = systematic_var + idiosyncratic_var

                risk_data.append(
                    {
                        "Stock": ticker,
                        "Systematic Risk": f"{np.sqrt(systematic_var):.1%}",
                        "Idiosyncratic Risk": f"{np.sqrt(idiosyncratic_var):.1%}",
                        "Total Risk": f"{np.sqrt(total_var):.1%}",
                        "Systematic %": f"{systematic_var / total_var:.1%}",
                    }
                )

        risk_df = pd.DataFrame(risk_data)
        mo.dataframe(risk_df)

        mo.md("""
        **Key Insights:**
        - **Systematic Risk**: Can't be diversified away (market risk)
        - **Idiosyncratic Risk**: Can be reduced through diversification
        - **High systematic %**: Stock moves with the market
        - **High idiosyncratic %**: Stock has company-specific drivers
        """)

    # Simple interpretation
    mo.md("## Step 4: Quick Interpretation Guide")

    mo.md("""
    ### Reading Factor Loadings:
    
    **Market Beta (Mkt-RF):**
    - `> 1.0`: More volatile than market (high beta stock)
    - `< 1.0`: Less volatile than market (defensive stock)
    - `≈ 1.0`: Moves with market average
    
    **Size Factor (SMB):**
    - `Positive`: Behaves like small-cap stocks
    - `Negative`: Behaves like large-cap stocks
    
    **Value Factor (HML):**
    - `Positive`: Value stock characteristics
    - `Negative`: Growth stock characteristics
    
    ### Portfolio Applications:
    
    1. **Diversification**: Combine stocks with different factor exposures
    2. **Risk Management**: Understand where your risk comes from  
    3. **Factor Investing**: Tilt toward factors with higher expected returns
    4. **Hedging**: Use factor exposures to hedge systematic risks
    """)

    mo.md("""
    ### Next Steps:
    
    - Explore **Black-Litterman** model for incorporating market views
    - Study **factor momentum** and **factor mean reversion**
    - Build **factor-based portfolios** targeting specific exposures
    - Learn about **alternative factors** (quality, momentum, low-vol)
    """)


# Run the app
if __name__ == "__main__":
    app(mo)
