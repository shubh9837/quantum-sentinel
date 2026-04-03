import pandas as pd
import yfinance as yf
import time

def download_data():
    # Load enriched tickers
    df_tickers = pd.read_csv("tickers_enriched.csv")
    symbols = [f"{s}.NS" for s in df_tickers['SYMBOL'].tolist()]
    
    # Also add the Nifty 50 Index for comparison
    symbols.append("^NSEI") 
    
    print(f"Downloading data for {len(symbols)} symbols...")
    # Use 2-year history for relative strength calculations
    data = yf.download(symbols, period="2y", interval="1d", group_by='ticker', threads=True)
    
    data.to_parquet("market_data.parquet")
    print("✅ market_data.parquet updated.")

if __name__ == "__main__":
    download_data()
