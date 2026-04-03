import pandas as pd
import time
from twelvedata import TDClient
import streamlit as st

def download_data():
    # 1. Setup API Client
    key = st.secrets["TWELVE_DATA_KEY"]
    td = TDClient(apikey=key)

    # 2. Load Tickers
    df_tickers = pd.read_csv("tickers.csv")
    # Note: Twelve Data uses "SYMBOL:XNSE" for National Stock Exchange
    symbols = [f"{s}:XNSE" for s in df_tickers['SYMBOL'].dropna().tolist()]
    
    market_data = {}
    count = 0

    st.info(f"Starting download for {len(symbols)} stocks. This will take time due to rate limits...")

    for symbol in symbols:
        try:
            # Fetch Daily Data
            ts = td.time_series(
                symbol=symbol,
                interval="1day",
                outputsize=500 # Approx 2 years of data
            )
            df = ts.as_pandas()

            if not df.empty:
                # Clean column names to match your app logic
                df.columns = [c.capitalize() for c in df.columns]
                market_data[symbol.replace(":XNSE", "")] = df
                count += 1
            
            # --- THE "STABILITY" PAUSE ---
            # Free tier only allows 8 requests per minute. 
            # We wait 8 seconds between stocks to stay safe.
            time.sleep(8) 

            if count >= 800: # Stay under the 800 daily limit
                break

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue

    # 3. Save to Parquet
    if market_data:
        final_df = pd.concat(market_data, axis=1)
        final_df.to_parquet("market_data.parquet")
        st.success("✅ Market Data Updated via Twelve Data")

if __name__ == "__main__":
    download_data()
