"""
script to get prices and save them to a csv file

in the format
symbol         RANDNX1     RANDNX2
2021-01-01  101.042956  100.920462
2021-01-02  100.987327  100.956455
"""

import yfinance as yf
import pandas as pd


def get_historical_prices(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)
    prices_df = data["Close"]
    return prices_df


def main():
    # Define the tickers and date range
    tickers = ["AAPL", "MSFT"]
    start_date = "2021-01-01"
    end_date = "2023-12-31"

    prices_df = get_historical_prices(tickers, start_date, end_date)
    prices_df.to_csv("prices.csv")
    print("Prices saved to prices.csv")


if __name__ == "__main__":
    main()
