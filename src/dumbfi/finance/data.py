"""
Market data utilities wrapping the Rust backend and providing higher-level interfaces.

Handles price data loading, caching, and common data operations.
"""

import pandas as pd
from typing import List, Optional, Dict, Any
from pathlib import Path
import yfinance as yf
from datetime import datetime, date, timedelta

from dumbfi.market_data import PyMarket


class MarketData:
    """
    High-level interface for market data operations.
    Wraps the Rust PyMarket backend with convenience methods.
    """

    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize MarketData with optional data file.

        Args:
            data_file: Path to CSV file with price data
        """
        self._market = PyMarket()
        self._prices_df = None
        self._data_file = data_file

        if data_file and Path(data_file).exists():
            self.load_prices(data_file)

    def load_prices(self, csv_path: str) -> None:
        """
        Load price data from CSV file into Rust backend.

        Args:
            csv_path: Path to CSV file with Date as first column, tickers as other columns
        """
        self._market.read_prices(csv_path)
        self._data_file = csv_path

        # Also load into pandas for convenience methods
        self._prices_df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        print(
            f"Loaded price data for {len(self._prices_df.columns)} assets over {len(self._prices_df)} days"
        )

    def get_price(self, date: str, ticker: str) -> Optional[float]:
        """
        Get price for specific date and ticker.

        Args:
            date: Date in YYYY-MM-DD format
            ticker: Stock ticker symbol

        Returns:
            Price or None if not found
        """
        return self._market.get_price(date, ticker)

    def get_prices_dataframe(self) -> pd.DataFrame:
        """Get full prices DataFrame."""
        if self._prices_df is None:
            raise ValueError("No price data loaded. Call load_prices() first.")
        return self._prices_df.copy()

    def get_returns(self, period: str = "daily") -> pd.DataFrame:
        """
        Calculate returns from price data.

        Args:
            period: Return period ("daily", "weekly", "monthly")

        Returns:
            DataFrame of returns
        """
        if self._prices_df is None:
            raise ValueError("No price data loaded. Call load_prices() first.")

        if period == "daily":
            return self._prices_df.pct_change().dropna()
        elif period == "weekly":
            weekly_prices = self._prices_df.resample("W").last()
            return weekly_prices.pct_change().dropna()
        elif period == "monthly":
            monthly_prices = self._prices_df.resample("M").last()
            return monthly_prices.pct_change().dropna()
        else:
            raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    def get_available_dates(self) -> List[str]:
        """Get all available dates in the dataset."""
        return self._market.get_all_dates()

    def get_available_tickers(self, date: Optional[str] = None) -> List[str]:
        """
        Get available tickers, optionally for a specific date.

        Args:
            date: Specific date in YYYY-MM-DD format (optional)

        Returns:
            List of ticker symbols
        """
        if date:
            return self._market.get_tickers_for_date(date)
        elif self._prices_df is not None:
            return list(self._prices_df.columns)
        else:
            # Get tickers from first available date
            dates = self.get_available_dates()
            if dates:
                return self._market.get_tickers_for_date(dates[0])
            return []

    def get_price_range(self, ticker: str, start_date: str, end_date: str) -> pd.Series:
        """
        Get price series for a ticker over a date range.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Series of prices indexed by date
        """
        if self._prices_df is None:
            raise ValueError("No price data loaded. Call load_prices() first.")

        if ticker not in self._prices_df.columns:
            raise ValueError(f"Ticker {ticker} not found in data")

        mask = (self._prices_df.index >= start_date) & (
            self._prices_df.index <= end_date
        )
        return self._prices_df.loc[mask, ticker].dropna()

    def get_latest_prices(
        self, tickers: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Get latest available prices for tickers.

        Args:
            tickers: List of ticker symbols (uses all if None)

        Returns:
            Dictionary of ticker -> latest price
        """
        if self._prices_df is None:
            raise ValueError("No price data loaded. Call load_prices() first.")

        if tickers is None:
            tickers = list(self._prices_df.columns)

        latest_date = self._prices_df.index[-1].strftime("%Y-%m-%d")

        prices = {}
        for ticker in tickers:
            price = self.get_price(latest_date, ticker)
            if price is not None:
                prices[ticker] = price

        return prices

    def calculate_basic_stats(self, ticker: str, days: int = 252) -> Dict[str, float]:
        """
        Calculate basic statistics for a ticker.

        Args:
            ticker: Stock ticker symbol
            days: Number of recent days to analyze

        Returns:
            Dictionary with statistics
        """
        if self._prices_df is None:
            raise ValueError("No price data loaded. Call load_prices() first.")

        if ticker not in self._prices_df.columns:
            raise ValueError(f"Ticker {ticker} not found in data")

        prices = self._prices_df[ticker].dropna().tail(days)
        returns = prices.pct_change().dropna()

        return {
            "current_price": prices.iloc[-1],
            "min_price": prices.min(),
            "max_price": prices.max(),
            "avg_price": prices.mean(),
            "volatility": returns.std() * (252**0.5),  # Annualized
            "avg_return": returns.mean() * 252,  # Annualized
            "total_return": (prices.iloc[-1] / prices.iloc[0]) - 1,
            "days_analyzed": len(prices),
        }

    def filter_by_availability(self, min_data_points: int = 100) -> List[str]:
        """
        Filter tickers by data availability.

        Args:
            min_data_points: Minimum number of non-null price points required

        Returns:
            List of tickers that meet the criteria
        """
        if self._prices_df is None:
            raise ValueError("No price data loaded. Call load_prices() first.")

        valid_tickers = []
        for ticker in self._prices_df.columns:
            non_null_count = self._prices_df[ticker].notna().sum()
            if non_null_count >= min_data_points:
                valid_tickers.append(ticker)

        return valid_tickers


class DataDownloader:
    """
    Utility class for downloading fresh market data.
    """

    @staticmethod
    def download_sp500_tickers() -> List[str]:
        """
        Download current S&P 500 tickers from Wikipedia.

        Returns:
            List of S&P 500 ticker symbols
        """
        print("Downloading S&P 500 tickers from Wikipedia...")
        sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp500_table = pd.read_html(sp500_url)[0]

        tickers = []
        for ticker in sp500_table["Symbol"]:
            cleaned_ticker = ticker.replace(".", "-")
            tickers.append(cleaned_ticker)

        print(f"Found {len(tickers)} S&P 500 tickers")
        return tickers

    @staticmethod
    def download_prices(
        tickers: List[str], start_date: str, end_date: str, cache_session: bool = True
    ) -> pd.DataFrame:
        """
        Download price data using yfinance.

        Args:
            tickers: List of ticker symbols
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            cache_session: Whether to use caching for requests

        Returns:
            DataFrame with Date index and tickers as columns
        """
        print(
            f"Downloading prices for {len(tickers)} tickers from {start_date} to {end_date}..."
        )

        if cache_session:
            # Use cached session to avoid hitting rate limits
            from requests import Session
            from requests_cache import CacheMixin, SQLiteCache
            from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
            from pyrate_limiter import Duration, RequestRate, Limiter

            class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
                pass

            session = CachedLimiterSession(
                limiter=Limiter(
                    RequestRate(2, Duration.SECOND * 5)
                ),  # max 2 requests per 5 seconds
                bucket_class=MemoryQueueBucket,
                backend=SQLiteCache("yfinance.cache"),
            )
        else:
            session = None

        # Download data
        df = yf.download(
            tickers,
            group_by="Ticker",
            start=start_date,
            end=end_date,
            session=session,
            auto_adjust=True,
        )

        # Restructure data
        if len(tickers) == 1:
            # Single ticker case
            df = df[["Close"]].rename(columns={"Close": tickers[0]})
        else:
            # Multiple tickers case
            df = df.stack(level=0).rename_axis(["Date", "Ticker"]).reset_index(level=1)
            df = df.pivot(columns="Ticker", values="Close")

        return df

    @staticmethod
    def save_to_csv(df: pd.DataFrame, filepath: str) -> None:
        """Save DataFrame to CSV file."""
        df.to_csv(filepath, index=True)
        print(f"Saved data to {filepath}")

    @classmethod
    def update_sp500_data(
        cls, filepath: str, start_date: str, end_date: str, force_rerun: bool = False
    ) -> None:
        """
        Update S&P 500 data file.

        Args:
            filepath: Path to save CSV file
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            force_rerun: Whether to redownload if file exists
        """
        if Path(filepath).exists() and not force_rerun:
            print(
                f"Data file {filepath} already exists. Use force_rerun=True to update."
            )
            return

        tickers = cls.download_sp500_tickers()
        df = cls.download_prices(tickers, start_date, end_date)
        cls.save_to_csv(df, filepath)
