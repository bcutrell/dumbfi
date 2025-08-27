"""
Download prices from Yahoo Finance for S&P 500 stocks to a single CSV file.

TODO
- Partial rerun: if a ticker is already in the CSV file and the date range is the same, skip it
- Add common (high market cap) ETFs
- Investigate use of funds data
    spy = yf.Ticker('SPY').funds_data
    spy.description
    spy.top_holdings
"""

import os
import time
from typing import List

import pandas as pd
import yfinance as yf
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

# Constants
DEFAULT_OUTPUT_DIR = "data"
STOCK_DATA_FILE = DEFAULT_OUTPUT_DIR + "/prices.csv"
SP500_TICKERS_FILE = DEFAULT_OUTPUT_DIR + "/sp500_tickers.txt"

START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

FORCE_RERUN = False


def get_sp500_tickers(filepath: str) -> List[str]:
    """Get all S&P 500 stock tickers"""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            tickers = [line.strip() for line in f.readlines()]
        print(f"Loaded {len(tickers)} existing S&P 500 tickers from file {filepath}")
        return tickers

    print("Downloading S&P 500 tickers from Wikipedia...")
    sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500_table = pd.read_html(sp500_url)[0]
    tickers = []
    for ticker in sp500_table["Symbol"]:
        cleaned_ticker = ticker.replace(".", "-")
        tickers.append(cleaned_ticker)

    print(f"Found {len(tickers)} S&P 500 tickers from Wikipedia {sp500_url}")
    with open(filepath, "w") as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

    return tickers


def download_prices(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Download prices for the given tickers"""
    print("NOTE: All requests are cached locally to <current_dir>/yfinance.cache")
    df = yf.download(
        tickers,
        group_by="Ticker",
        start=start_date,
        end=end_date,
        session=session,
        auto_adjust=True,
    )
    df = df.stack(level=0).rename_axis(["Date", "Ticker"]).reset_index(level=1)
    return df


def prices_to_csv(df: pd.DataFrame, filepath: str) -> None:
    """Save prices DataFrame to CSV file"""
    # pivot the DataFrame so that each ticker is a column and Date is the index
    df = df.pivot(columns="Ticker", values="Close")
    df.to_csv(filepath, index=True)


def main():
    """Main function to run the stock data download"""
    if not os.path.exists(DEFAULT_OUTPUT_DIR):
        os.makedirs(DEFAULT_OUTPUT_DIR)

    print("Getting S&P 500 stock tickers...")
    tickers = get_sp500_tickers(SP500_TICKERS_FILE)

    if os.path.exists(STOCK_DATA_FILE) and FORCE_RERUN is False:
        print(
            f"NOOP: {STOCK_DATA_FILE} already exists. Set FORCE_RERUN=True to force rerun."
        )
    else:
        print("Downloading stock data...")
        df = download_prices(tickers, start_date=START_DATE, end_date=END_DATE)
        print("Download complete!")

        print("Saving stock data to CSV...")
        prices_to_csv(df, STOCK_DATA_FILE)
        print(f"Saved stock data to {STOCK_DATA_FILE}")

    print("Done!")


if __name__ == "__main__":
    main()
