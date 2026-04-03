import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# --- PAGE CONFIG ---
st.set_page_config(page_title="Quantum-Sentinel 10.0", layout="wide", page_icon="🚀")

@st.cache_data
def load_market_data():
    try:
        return pd.read_parquet("market_data.parquet")
    except:
        return None

# --- STYLING & TITLES ---
st.title("🚀 Quantum-Sentinel Pro: Institutional Intelligence")
st.markdown("---")

data = load_market_data()

if data is None:
    st.error("⚠️ Data file not found. Please run the 'Update Stock Data' action in GitHub first.")
    st.stop()

# Extract ticker names from the data
tickers = list(set([col[0] for col in data.columns if isinstance(col, tuple)]))
tickers.sort()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Scan Parameters")
scan_size = st.sidebar.slider("Scan Depth", 50, len(tickers), 200)
min_score = st.sidebar.slider("Min Strategy Score", 1, 10, 6)

tab1, tab2 = st.tabs(["🔥 Multi-Factor Screener", "🔍 Single Stock Deep-Dive"])

# ==========================================
# TAB 1: THE SCREENER (THE "BRAIN")
# ==========================================
with tab1:
    st.subheader("Market-Wide Opportunity Scan")
    
    if st.button("🚀 Start Deep Analysis"):
        results = []
        progress = st.progress(0)
        status = st.empty()
        
        subset = tickers[:scan_size]
        
        for i, t in enumerate(subset):
            try:
                df = data[t].dropna()
                if len(df) < 60: continue
                
                # --- CALCULATIONS ---
                last_close = float(df['Close'].iloc[-1])
                ema20 = float(df['Close'].ewm(span=20).mean().iloc[-1])
                ema50 = float(df['Close'].ewm(span=50).mean().iloc[-1])
                
                # Volume Analysis (Institutional Footprint)
                current_vol = df['Volume'].iloc[-1]
                avg_vol = df['Volume'].tail(20).mean()
                vol_ratio = current_vol / avg_vol
                
                # RSI Momentum
                delta = df['Close'].diff()
                gain = delta.clip(lower=0).rolling(14).mean()
                loss = -delta.clip(upper=0).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                
                # --- SCORING SYSTEM (Out of 10) ---
                score = 0
                if last_close > ema20: score += 2  # Short term trend
                if ema20 > ema50: score += 2      # Medium term trend
                if 45 < rsi < 65: score += 2      # Ideal momentum zone
                if vol_ratio > 1.5: score += 2    # High volume (Conviction)
                if vol_ratio > 3.0: score += 2    # Massive volume (Mega Buy)

                if score >= min_score:
                    # Risk Management
                    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
                    stop_loss = last_close - (2 * atr)
                    target_1 = last_close + (3 * atr)
                    
                    # Holding Period Logic
                    if vol_ratio > 2.5:
                        period = "Short Term (3-10 Days)"
                    elif rsi < 50:
                        period = "Positional (4-8 Weeks)"
                    else:
                        period = "Swing (2-4 Weeks)"

                    results.append({
                        "Ticker": t.replace(".NS", ""),
                        "Score": f"{score}/10",
                        "Price": round(last_close, 2),
                        "Vol Surge": f"{round(vol_ratio, 1)}x",
                        "RSI": int(rsi),
                        "Stop Loss": round(stop_loss, 2),
                        "Target": round(target_1, 2),
                        "Timeframe": period
                    })
            except:
                pass
            
            if i % 5 == 0:
                progress.progress((i + 1) / len(subset))
                status.text(f"Analyzing {t}...")

        progress.empty()
        status.empty()
        
        if results:
            final_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
            st.dataframe(final_df, use_container_width=True)
            st.success(f"Found {len(results)} stocks matching your criteria!")
        else:
            st.warning("No stocks met the criteria. Try lowering the 'Min Strategy Score' in the sidebar.")

# ==========================================
# TAB 2: SINGLE STOCK DEEP DIVE
# ==========================================
with tab2:
    selected = st.selectbox("Select a stock for detailed intelligence:", tickers)
    
    if selected:
        stock_df = data[selected].dropna()
        
        # Performance Metrics
        curr = stock_df['Close'].iloc[-1]
        high_52 = stock_df['High'].tail(252).max()
        dist_from_high = ((high_52 - curr) / high_52) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Price", f"₹{round(curr, 2)}")
        c2.metric("52-Week High", f"₹{round(high_52, 2)}")
        c3.metric("Discount", f"-{round(dist_from_high, 1)}%")
        
        st.line_chart(stock_df['Close'].tail(252))
        
        if st.button("🔍 Get Financial Health (Live)"):
            with st.spinner("Accessing balance sheet..."):
                info = yf.Ticker(selected).info
                f1, f2, f3 = st.columns(3)
                f1.metric("P/E Ratio", info.get("trailingPE", "N/A"))
                f2.metric("Debt-to-Equity", info.get("debtToEquity", "N/A"))
                f3.metric("Profit Margin", f"{round(info.get('profitMargins', 0)*100, 1)}%" if info.get('profitMargins') else "N/A")
