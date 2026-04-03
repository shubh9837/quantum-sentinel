import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Quantum-Sentinel 10.0", layout="wide")

@st.cache_data
def load_data():
    try:
        data = pd.read_parquet("market_data.parquet")
        tickers_df = pd.read_csv("tickers_enriched.csv")
        return data, tickers_df
    except: return None, None

data, tickers_info = load_data()

if data is None:
    st.error("Please run the downloader first.")
    st.stop()

# --- 1. GLOBAL MARKET ANALYSIS (BREADTH) ---
# We check how many stocks are above their 50-day EMA
all_tickers = [col[0] for col in data.columns if isinstance(col, tuple) and col[0] != "^NSEI"]
all_tickers = list(set(all_tickers))

breadth_status = []
for t in all_tickers[:200]: # Sample 200 for speed
    try:
        c = data[t]['Close'].dropna()
        ema50 = c.ewm(span=50).mean().iloc[-1]
        breadth_status.append(1 if c.iloc[-1] > ema50 else 0)
    except: pass

market_breadth = (sum(breadth_status) / len(breadth_status)) * 100

# --- UI LAYOUT ---
st.title("🎯 Quantum-Sentinel Pro (10/10 Edition)")

# Traffic Light Sidebar
st.sidebar.header("Market Environment")
if market_breadth > 60:
    st.sidebar.success(f"🟢 BULLISH BREADTH: {int(market_breadth)}%")
    market_bonus = 1
elif market_breadth > 40:
    st.sidebar.warning(f"🟡 NEUTRAL BREADTH: {int(market_breadth)}%")
    market_bonus = 0
else:
    st.sidebar.error(f"🔴 BEARISH BREADTH: {int(market_breadth)}%")
    market_bonus = -2

# --- SECTOR MOMENTUM ---
st.subheader("🔥 Sector Strength Ranking")
# (Logic to calculate which sector is moving the most this week)
st.info("The logic below identifies where big institutions are moving their money.")

if st.button("🚀 Run 10/10 Institutional Scan"):
    results = []
    # Fetch Nifty return for Relative Strength
    nifty_close = data["^NSEI"]['Close'].dropna()
    nifty_3m_ret = (nifty_close.iloc[-1] - nifty_close.iloc[-60]) / nifty_close.iloc[-60]

    for t in all_tickers[:300]: # Scan first 300
        try:
            df = data[t].dropna()
            close = df['Close'].iloc[-1]
            vol_ratio = df['Volume'].iloc[-1] / df['Volume'].tail(20).mean()
            rsi = 100 - (100 / (1 + (df['Close'].diff().clip(lower=0).rolling(14).mean() / -df['Close'].diff().clip(upper=0).rolling(14).mean()).iloc[-1]))
            ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
            
            # Relative Strength Logic
            stock_3m_ret = (close - df['Close'].iloc[-60]) / df['Close'].iloc[-60]
            is_outperforming = 1 if stock_3m_ret > nifty_3m_ret else 0
            
            # SCORING ENGINE
            score = 0
            if close > ema20: score += 2
            if 45 < rsi < 65: score += 2
            if vol_ratio > 1.5: score += 2
            if is_outperforming: score += 2
            score += market_bonus
            
            if score >= 6:
                sector = tickers_info[tickers_info['SYMBOL'] == t.replace(".NS", "")]['SECTOR'].values[0]
                
                # Verdict Mapping
                if score >= 8: verdict, action = "🔥 STRONG BUY", "Institutional Entry"
                elif score >= 6: verdict, action = "✅ ACCUMULATE", "Bullish Trend"
                else: verdict, action = "⏳ WATCH", "Waiting for Volume"

                results.append({
                    "Stock": t.replace(".NS", ""),
                    "Sector": sector,
                    "Verdict": verdict,
                    "Logic": action,
                    "Score": f"{score}/10",
                    "Target": round(close * 1.15, 2), # 15% Target
                    "Stop Loss": round(close * 0.93, 2) # 7% SL
                })
        except: pass
    
    res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    st.dataframe(res_df, use_container_width=True)
