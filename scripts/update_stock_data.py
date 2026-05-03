import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# 你想抽嘅股票，可以之後加多幾隻
TICKERS = ["TSLA", "NVDA", "GOOG", "SOXL"]

DATA_DIR = "data"
YEARS = 5

os.makedirs(DATA_DIR, exist_ok=True)

def download_stock_data(ticker):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * YEARS)

    print(f"Downloading {ticker} data from {start_date.date()} to {end_date.date()}")

    df = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        print(f"No data found for {ticker}")
        return

    df = df.reset_index()

    # 防止 yfinance 有時出 multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = df[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]

    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df["Ticker"] = ticker
    df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output_path = os.path.join(DATA_DIR, f"{ticker}_daily.csv")
    df.to_csv(output_path, index=False)

    print(f"Saved {ticker} data to {output_path}")
    print(f"Rows: {len(df)}")

def main():
    for ticker in TICKERS:
        download_stock_data(ticker)

if __name__ == "__main__":
    main()
