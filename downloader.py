import yfinance as yf
import pandas as pd

def download_data():
    try:
        # Load your tickers from the file you uploaded
        df_tickers = pd.read_csv("tickers.csv")
        symbols = [str(s).strip() + ".NS" for s in df_tickers.iloc[:, 0].tolist()]
        
        print(f"Starting download for {len(symbols)} stocks...")
        
        # Download 10 years of data
        data = yf.download(symbols, period="10y", interval="1d", group_by='ticker', threads=True)
        
        # Save the file that app.py is looking for
        data.to_parquet("market_data.parquet")
        print("Success! market_data.parquet created.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_data()
