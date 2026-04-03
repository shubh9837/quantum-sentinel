import pandas as pd
from breeze_connect import BreezeConnect
import os

# --- 1. SETTINGS (Enter your ICICI Keys here) ---
API_KEY = "29#73S4M~375=7163B7343875498Z4v6"
SECRET_KEY = "g14&66601c977Y%(5=!Y05500n2434jZ"
SESSION_TOKEN = "YOUR_SESSION_TOKEN_HERE" # Generated daily via ICICI login

def download_data():
    print("--- Initializing Breeze API ---")
    
    # Initialize Breeze
    breeze = BreezeConnect(api_key=API_KEY)
    breeze.generate_session(api_secret=SECRET_KEY, session_token=SESSION_TOKEN)

    # Load your tickers.csv
    df_tickers = pd.read_csv("tickers.csv")
    symbols = df_tickers['SYMBOL'].dropna().tolist()
    
    market_data = {}

    for symbol in symbols:
        try:
            print(f"Fetching: {symbol}")
            # Fetch last 1000 days of daily data
            res = breeze.get_historical_data_v2(
                interval="1day",
                from_date="2023-01-01T07:00:00.000Z",
                to_date="2026-04-03T07:00:00.000Z",
                stock_code=symbol,
                exchange_code="NSE"
            )
            
            if res['status'] == 200:
                temp_df = pd.DataFrame(res['Success'])
                # Standardize columns to match your app's expectations
                temp_df = temp_df.rename(columns={
                    'close': 'Close', 'open': 'Open', 
                    'high': 'High', 'low': 'Low', 'volume': 'Volume'
                })
                market_data[symbol] = temp_df
                
        except Exception as e:
            print(f"Skipping {symbol}: {e}")

    # Combine and save as Parquet
    final_df = pd.concat(market_data, axis=1)
    final_df.to_parquet("market_data.parquet")
    print("✅ SUCCESS: Data refreshed via Breeze API.")

if __name__ == "__main__":
    download_data()
