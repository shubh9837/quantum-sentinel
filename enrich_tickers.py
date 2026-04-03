import pandas as pd
import requests
from io import StringIO

def run_enrichment():
    sources = [
        "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftymicrocap250list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap100list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv"
    ]
    
    master_map = {}
    # Standard headers to prevent being blocked as a bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("--- Starting Sector Enrichment ---")
    for url in sources:
        try:
            print(f"Fetching: {url}")
            # Added timeout=15 to prevent 90-minute hangs
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                temp_df = pd.read_csv(StringIO(response.text))
                
                # Dynamic column detection
                symbol_col = next((c for c in temp_df.columns if 'Symbol' in c), None)
                industry_col = next((c for c in temp_df.columns if 'Industry' in c or 'Sector' in c), None)
                
                if symbol_col and industry_col:
                    for _, row in temp_df.iterrows():
                        sym = str(row[symbol_col]).strip().upper()
                        ind = str(row[industry_col]).strip()
                        master_map[sym] = ind
                    print(f"✅ Loaded {len(temp_df)} stocks from this source.")
            else:
                print(f"⚠️ NSE returned status code: {response.status_code}")

        except Exception as e:
            print(f"❌ Could not reach {url.split('/')[-1]}: {e}")
            continue

    # Load and Match
    try:
        df = pd.read_csv("tickers.csv")
        # Standardize your symbols to uppercase
        df['SYMBOL'] = df['SYMBOL'].astype(str).str.strip().str.upper()
        
        # Map the sectors
        df['SECTOR'] = df['SYMBOL'].map(master_map).fillna("Other/SmallCap")
        
        # Save results
        df.to_csv("tickers_enriched.csv", index=False)
        
        found_count = len(df[df['SECTOR'] != "Other/SmallCap"])
        print(f"--- Summary ---")
        print(f"Total Stocks: {len(df)}")
        print(f"Sectors Identified: {found_count}")
        print("✅ tickers_enriched.csv has been updated.")
    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    run_enrichment()
