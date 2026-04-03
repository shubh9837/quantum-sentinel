import pandas as pd

def run_enrichment():
    # Official NSE Links for different market caps
    sources = [
        "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftymicrocap250list.csv",
        "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap100list.csv"
    ]
    
    master_map = {}
    for url in sources:
        try:
            temp_df = pd.read_csv(url)
            # Standardize column names (NSE uses Industry or Sector)
            industry_col = 'Industry' if 'Industry' in temp_df.columns else 'Sector'
            for _, row in temp_df.iterrows():
                master_map[row['Symbol']] = row[industry_col]
        except: continue

    # Load your existing tickers
    df = pd.read_csv("tickers.csv")
    df['SECTOR'] = df['SYMBOL'].map(master_map).fillna("Other/SmallCap")
    
    # Save the new version
    df.to_csv("tickers_enriched.csv", index=False)
    print("✅ Created tickers_enriched.csv with sectors.")

if __name__ == "__main__":
    run_enrichment()
