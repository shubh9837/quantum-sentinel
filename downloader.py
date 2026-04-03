import pandas as pd
import yfinance as yf

def download_data():
    # Load enriched tickers
    df_tickers = pd.read_csv("tickers_enriched.csv")
    symbols = [f"{s}.NS" for s in df_tickers['SYMBOL'].tolist()]
    
    # CRITICAL: Explicitly add the Nifty 50 Index
    nifty_symbol = "^NSEI"
    if nifty_symbol not in symbols:
        symbols.append(nifty_symbol)
    
    print(f"Downloading data for {len(symbols)} symbols...")
    
    # Download 2 years of data for Relative Strength calculations
    # auto_adjust=True ensures we handle stock splits correctly
    data = yf.download(symbols, period="2y", interval="1d", group_by='ticker', auto_adjust=True)
    
    # Save as Parquet
    data.to_parquet("market_data.parquet")
    print("✅ market_data.parquet updated with Nifty Index.")

if __name__ == "__main__":
    download_data()
