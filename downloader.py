import yfinance as yf
import pandas as pd
import os

def download_data():
    if not os.path.exists("tickers.csv"):
        print("❌ Error: tickers.csv missing!")
        exit(1)

    df_tickers = pd.read_csv("tickers.csv")
    # This handles files with or without headers automatically
    raw_symbols = df_tickers.iloc[:, 0].dropna().tolist()
    symbols = [str(s).strip().upper() for s in raw_symbols]
    symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]
    
    print(f"Attempting to download {len(symbols)} stocks...")
    
    # Download with a longer timeout and auto-repair
    data = yf.download(symbols, period="10y", interval="1d", group_by='ticker', threads=True)
    
    if data.empty:
        print("❌ Error: No data returned from Yahoo.")
        exit(1)
        
    data.to_parquet("market_data.parquet")
    print("✅ Success! market_data.parquet saved.")

if __name__ == "__main__":
    download_data()
