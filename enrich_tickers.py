import pandas as pd
import requests

def run_enrichment():
    # 1. Expanded list of NSE sources to cover 1000+ stocks
    sources = [
        "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftymicrocap250list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap100list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv"
    ]
    
    master_map = {}
    headers = {'User-Agent': 'Mozilla/5.0'} # NSE sometimes blocks scripts without headers

    for url in sources:
        try:
            # We use requests to ensure we can pass headers if needed
            response = requests.get(url, headers=headers)
            from io import StringIO
            temp_df = pd.read_csv(StringIO(response.text))
            
            # Identify columns dynamically
            symbol_col = next((c for c in temp_df.columns if 'Symbol' in c), None)
            industry_col = next((c for c in temp_df.columns if 'Industry' in c or 'Sector' in c), None)
            
            if symbol_col and industry_col:
                for _, row in temp_df.iterrows():
                    # Save symbols in UPPERCASE to ensure a perfect match
                    sym = str(row[symbol_col]).strip().upper()
                    ind = str(row[industry_col]).strip()
                    master_map[sym] = ind
        except Exception as e:
            print(f"Skipping source {url}: {e}")
            continue

    # 2. Load your file and force symbols to UPPERCASE
    df = pd.read_csv("tickers.csv")
    
    # Ensure SYMBOL column exists and is uppercase for matching
    df['SYMBOL'] = df['SYMBOL'].astype(str).str.strip().str.upper()
    
    # Apply the mapping
    df['SECTOR'] = df['SYMBOL'].map(master_map).fillna("Other/SmallCap")
    
    # Check if we still have only "Other/SmallCap"
    unique_sectors = df['SECTOR'].unique()
    print(f"Sectors found: {len(unique_sectors)}")
    
    # 3. Save the new version
    df.to_csv("tickers_enriched.csv", index=False)
    print("✅ Successfully updated tickers_enriched.csv")

if __name__ == "__main__":
    run_enrichment()
