"""
Pure Python replacement for the Rust PyMarket functionality.

Provides the same API as PyMarket but implemented in Python using pandas and dictionaries.
"""

import csv
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path


class PyMarket:
    """
    Pure Python replacement for the Rust PyMarket class.

    Provides identical functionality but without Rust dependencies.
    Uses pandas DataFrame for efficient data operations.
    """

    def __init__(self):
        """Initialize empty market data store."""
        self.prices: Dict[str, Dict[str, float]] = {}
        self._prices_df: Optional[pd.DataFrame] = None

    def read_prices(self, csv_path: str) -> None:
        """
        Load price data from CSV file.

        Args:
            csv_path: Path to CSV file with Date as first column, tickers as other columns

        Raises:
            IOError: If file cannot be read or has invalid format
        """
        try:
            # Load CSV into pandas DataFrame
            df = pd.read_csv(csv_path, index_col=0)
            self._prices_df = df

            # Convert to nested dictionary format for compatibility with Rust version
            self.prices = {}

            for date_str in df.index:
                # Ensure date is string format
                if hasattr(date_str, 'strftime'):
                    date_key = date_str.strftime('%Y-%m-%d')
                else:
                    date_key = str(date_str)

                day_prices = {}
                for ticker in df.columns:
                    price_value = df.loc[date_str, ticker]
                    # Only add non-null values
                    if pd.notna(price_value):
                        day_prices[ticker] = float(price_value)

                if day_prices:  # Only add dates with valid prices
                    self.prices[date_key] = day_prices

        except FileNotFoundError:
            raise IOError(f"Failed to read CSV file '{csv_path}': File not found")
        except pd.errors.EmptyDataError:
            raise IOError(f"Failed to read CSV file '{csv_path}': File is empty")
        except Exception as e:
            raise IOError(f"Failed to read CSV file '{csv_path}': {str(e)}")

    def get_price(self, date: str, ticker: str) -> Optional[float]:
        """
        Get price for specific date and ticker.

        Args:
            date: Date in YYYY-MM-DD format
            ticker: Stock ticker symbol

        Returns:
            Price or None if not found
        """
        day_prices = self.prices.get(date)
        if day_prices is None:
            return None
        return day_prices.get(ticker)

    def get_all_dates(self) -> List[str]:
        """
        Get all available dates in the dataset.

        Returns:
            Sorted list of date strings in YYYY-MM-DD format
        """
        dates = list(self.prices.keys())
        dates.sort()
        return dates

    def get_tickers_for_date(self, date: str) -> List[str]:
        """
        Get available tickers for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Sorted list of ticker symbols available for that date
        """
        day_prices = self.prices.get(date)
        if day_prices is None:
            return []

        tickers = list(day_prices.keys())
        tickers.sort()
        return tickers

    def get_prices_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Get the loaded prices as a pandas DataFrame.

        Returns:
            DataFrame with dates as index and tickers as columns, or None if no data loaded
        """
        return self._prices_df.copy() if self._prices_df is not None else None