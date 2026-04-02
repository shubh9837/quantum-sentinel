import yfinance as yf
import pandas as pd
import os

def download_data():
    print("--- Starting Data Update Process ---")
    
    # 1. Check if tickers.csv exists
    if not os.path.exists("tickers.csv"):
        print("❌ ERROR: tickers.csv not found in the repository!")
        return

    try:
        # 2. Load Tickers
        df_tickers = pd.read_csv("tickers.csv")
        symbols = [str(s).strip().upper() for s in df_tickers.iloc[:, 0].tolist()]
        # Add .NS if missing
        symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]
        
        print(f"Found {len(symbols)} symbols. First 5: {symbols[:5]}")
        
        # 3. Download
        print("Downloading from Yahoo Finance...")
        data = yf.download(symbols, period="10y", interval="1d", group_by='ticker', threads=True)
        
        if data.empty:
            print("❌ ERROR: Yahoo returned NO data. Check your ticker symbols!")
            return

        # 4. Save
        data.to_parquet("market_data.parquet")
        print("✅ SUCCESS: market_data.parquet created and saved.")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    download_data()
