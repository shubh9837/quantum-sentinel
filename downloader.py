import yfinance as yf
import pandas as pd
import os

def download_data():
    print("--- Starting Robust Data Update ---")
    
    if not os.path.exists("tickers.csv"):
        print("❌ ERROR: tickers.csv missing! Please upload it to GitHub.")
        exit(1)

    try:
        # 1. Read your exact tickers.csv file
        df_tickers = pd.read_csv("tickers.csv")
        # Ensure we read the 'SYMBOL' column
        col_name = 'SYMBOL' if 'SYMBOL' in df_tickers.columns else df_tickers.columns[0]
        raw_symbols = df_tickers[col_name].dropna().tolist()
        
        # 2. Add .NS for Yahoo Finance compatibility
        symbols = [str(s).strip().upper() for s in raw_symbols]
        symbols = [s if s.endswith(".NS") else f"{s}.NS" for s in symbols]
        
        print(f"Loaded {len(symbols)} symbols. Preparing download...")
        
        # 3. Download 5 Years of Data (Prevents GitHub Memory Crash)
        # threads=True makes it fast, group_by='ticker' organizes it easily for our app
        data = yf.download(symbols, period="5y", interval="1d", group_by='ticker', threads=True)
        
        if data.empty:
            print("❌ ERROR: Yahoo returned NO data. Blocked by Yahoo.")
            exit(1)
            
        # 4. Save as highly compressed Parquet format
        data.to_parquet("market_data.parquet")
        print("✅ SUCCESS: market_data.parquet successfully created and saved!")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        exit(1)

if __name__ == "__main__":
    download_data()
