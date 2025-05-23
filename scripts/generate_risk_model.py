"""
Generate risk model from stock price data using PyPortfolioOpt.

This script reads price data from a CSV file and generates:
- Expected returns using CAPM
- Risk model (covariance matrix) using sample covariance
- Saves the risk model components to files for use in Rust backend

Expected Returns Models
Current: Simple CAPM
    - Mean-historical returns
    - Black-Litterman model
    - Factor-based expected returns
    - James-Stein estimator

Risk Model Options
Current: Sample Covariance
    - Ledoit-Wolf shrinkage (used as fallback)
    - Empirical covariance with different frequencies
    - Factor models (Fama-French 3 or 5 factor)
    - Exponentially weighted covariance
"""

import pandas as pd
import numpy as np
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier
import json
import os
from typing import Dict, Any

# Configuration
PRICES_FILE = "sample_prices.csv"
OUTPUT_DIR = "data/risk_model"
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"


def load_price_data(filepath: str) -> pd.DataFrame:
    """Load price data from CSV file."""
    print(f"Loading price data from {filepath}...")
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    df = df.dropna(axis=1, how='all')
    df = df.dropna()
    print(f"Loaded data for {len(df.columns)} assets over {len(df)} trading days")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    return df


def calculate_expected_returns(prices: pd.DataFrame) -> pd.Series:
    """Calculate expected returns using CAPM model."""
    print("Calculating expected returns using CAPM...")
    mu = expected_returns.capm_return(prices)
    print(f"Expected annual returns calculated for {len(mu)} assets")
    print("Top 3 expected returns:")
    print(mu.sort_values(ascending=False).head(3))
    return mu


def calculate_risk_model(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate risk model (covariance matrix)."""
    print("Calculating risk model (covariance matrix)...")
    S = risk_models.sample_cov(prices, frequency=252)
    print(f"Covariance matrix calculated: {S.shape[0]}x{S.shape[1]}")

    # Check if matrix is positive semi-definite (all eigenvalues are >= 0)
    eigenvals = np.linalg.eigvals(S)
    min_eigenval = np.min(eigenvals)
    print(f"Minimum eigenvalue: {min_eigenval:.6f}")

    if min_eigenval < -1e-8:
        print("Warning: Covariance matrix is not positive semi-definite")
        print("Applying Ledoit-Wolf shrinkage...")
        S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()

    return S


def test_portfolio_optimization(mu: pd.Series, S: pd.DataFrame) -> None:
    """Test portfolio optimization to validate risk model."""
    print("\nTesting portfolio optimization...")
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()

    print("Max Sharpe portfolio weights:")
    for ticker, weight in cleaned_weights.items():
        if weight > 0.01:  # Only show weights > 1%
            print(f"  {ticker}: {weight:.3f}")

    # Get portfolio performance
    performance = ef.portfolio_performance(verbose=False)
    print(f"\nPortfolio Performance:")
    print(f"  Expected Return: {performance[0]:.3f}")
    print(f"  Volatility: {performance[1]:.3f}")
    print(f"  Sharpe Ratio: {performance[2]:.3f}")


def save_risk_model(mu: pd.Series, S: pd.DataFrame, output_dir: str):
    """Save risk model components to files."""
    print(f"\nSaving risk model to {output_dir}...")
    os.makedirs(output_dir, exist_ok=True)

    # Save expected returns as JSON
    expected_returns_dict = mu.to_dict()
    with open(os.path.join(output_dir, "expected_returns.json"), "w") as f:
        json.dump(expected_returns_dict, f, indent=2)

    # Save covariance matrix as CSV
    S.to_csv(os.path.join(output_dir, "covariance_matrix.csv"))

    # Save asset list
    assets = list(mu.index)
    with open(os.path.join(output_dir, "assets.json"), "w") as f:
        json.dump(assets, f, indent=2)

    # Save metadata
    metadata = {
        "num_assets": len(assets),
        "date_range": {
            "start": START_DATE,
            "end": END_DATE
        },
        "risk_free_rate": 0.02,  # Assumed 2% risk-free rate
        "frequency": 252,  # Trading days per year
        "model_type": "sample_covariance"
    }

    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("Risk model saved successfully!")
    print(f"Files created:")
    print(f"  - expected_returns.json ({len(expected_returns_dict)} assets)")
    print(f"  - covariance_matrix.csv ({S.shape[0]}x{S.shape[1]})")
    print(f"  - assets.json")
    print(f"  - metadata.json")


def main():
    """Main function to generate risk model."""
    print("=== Risk Model Generation ===\n")

    # Load price data
    try:
        prices = load_price_data(PRICES_FILE)
    except FileNotFoundError:
        print(f"Error: Could not find {PRICES_FILE}")
        print("Please ensure the price data file exists.")
        return
    except Exception as e:
        print(f"Error loading price data: {e}")
        return

    # Calculate expected returns
    try:
        mu = calculate_expected_returns(prices)
    except Exception as e:
        print(f"Error calculating expected returns: {e}")
        return

    # Calculate risk model
    try:
        S = calculate_risk_model(prices)
    except Exception as e:
        print(f"Error calculating risk model: {e}")
        return

    # Test the risk model
    try:
        test_portfolio_optimization(mu, S)
        print("✓ Risk model validation successful")
    except Exception as e:
        print(f"✗ Risk model validation failed: {e}")
        return

    # Save risk model
    try:
        save_risk_model(mu, S, OUTPUT_DIR)
        print("\n✓ Risk model generation completed successfully!")
    except Exception as e:
        print(f"Error saving risk model: {e}")
        return


if __name__ == "__main__":
    main()
