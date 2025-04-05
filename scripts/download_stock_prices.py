import pandas as pd
import yfinance as yf
import os
from datetime import datetime
import time
from typing import Dict, List, Optional

DEFAULT_OUTPUT_DIR = "data"
STOCK_DATA_FILE = "prices.csv"
SP500_TICKERS_FILE = "sp500_tickers.txt"


def get_sp500_tickers() -> List[str]:
    """
    Get all S&P 500 stock tickers
    """
    sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500_table = pd.read_html(sp500_url)[0]

    tickers = []
    for ticker in sp500_table["Symbol"]:
        cleaned_ticker = ticker.replace(".", "-")
        tickers.append(cleaned_ticker)
        print(f"Added ticker: {cleaned_ticker}")

    with open(SP500_TICKERS_FILE, "w") as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

    return tickers


def download_stock_data(
    tickers: List[str], output_dir: str = DEFAULT_OUTPUT_DIR
) -> pd.DataFrame:
    """
    Download stock data for the given tickers and save to a single CSV file
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_date = "2024-01-01"
    current_date = datetime.now()
    if current_date.year < 2024:
        end_date = "2024-12-31"
    elif current_date.year > 2024:
        end_date = "2024-12-31"
    else:
        end_date = current_date.strftime("%Y-%m-%d")

    stock_data = pd.DataFrame()
    output_file = os.path.join(output_dir, STOCK_DATA_FILE)
    if os.path.exists(output_file):
        stock_data = pd.read_csv(output_file)
        print("Loaded existing stock data")

    for ticker in tickers:
        if not stock_data.empty and ticker in stock_data.columns:
            print(f"Using cached data for {ticker}")
            continue

        max_retries = 3
        retry_delay = 5 # seconds

        for attempt in range(max_retries):
            try:
                data = yf.download(ticker, start=start_date, end=end_date)
                data["ticker"] = ticker
                data = data.reset_index()
                data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")
                data = data.rename(
                    columns={
                        "Date": "date",
                        "Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close",
                        "Adj Close": "adj_close",
                        "Volume": "volume",
                    }
                )
                stock_data = pd.concat([stock_data, data], ignore_index=True)
                print(f"Downloaded data for {ticker}")

                stock_data.to_csv(output_file, index=False)
                break
            except Exception as e:
                if "Rate limited" in str(e) and attempt < max_retries - 1:
                    print(
                        f"Rate limited for {ticker}, waiting {retry_delay} seconds before retry {attempt + 1}/{max_retries}"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Error downloading data for {ticker}: {e}")
                    break

    return stock_data


def main():
    """
    Main function to run the stock data download
    """
    print("Getting S&P 500 stock tickers...")
    tickers = get_sp500_tickers()

    print(f"Found {len(tickers)} S&P 500 tickers")

    print("Downloading stock data...")
    download_stock_data(tickers)

    print("Download complete!")


if __name__ == "__main__":
    main()
