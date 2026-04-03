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

# Extract ticker names
tickers = list(set([col[0] for col in data.columns if isinstance(col, tuple)]))
tickers.sort()

# --- SIDEBAR ---
st.sidebar.header("Scan Parameters")
scan_size = st.sidebar.slider("Scan Depth", 50, len(tickers), 200)
min_score = st.sidebar.slider("Min Strategy Score", 1, 10, 6)

tab1, tab2 = st.tabs(["🔥 Multi-Factor Screener", "🔍 Single Stock Deep-Dive"])

# ==========================================
# TAB 1: THE SCREENER
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
                
                last_close = float(df['Close'].iloc[-1])
                ema20 = float(df['Close'].ewm(span=20).mean().iloc[-1])
                ema50 = float(df['Close'].ewm(span=50).mean().iloc[-1])
                
                current_vol = df['Volume'].iloc[-1]
                avg_vol = df['Volume'].tail(20).mean()
                vol_ratio = current_vol / avg_vol
                
                delta = df['Close'].diff()
                gain = delta.clip(lower=0).rolling(14).mean()
                loss = -delta.clip(upper=0).rolling(14).mean()
                rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
                
                score = 0
                if last_close > ema20: score += 2
                if ema20 > ema50: score += 2
                if 45 < rsi < 65: score += 2
                if vol_ratio > 1.5: score += 2
                if vol_ratio > 3.0: score += 2

                if score >= min_score:
                    atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
                    stop_loss = last_close - (2 * atr)
                    target_1 = last_close + (3 * atr)
                    
                    if vol_ratio > 2.5: period = "Short Term (3-10 Days)"
                    elif rsi < 50: period = "Positional (4-8 Weeks)"
                    else: period = "Swing (2-4 Weeks)"

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
            
            if i % 10 == 0:
                progress.progress((i + 1) / len(subset))
                status.text(f"Analyzing {t}...")

        progress.empty()
        status.empty()
        
        if results:
            final_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("No stocks met the criteria.")

# ==========================================
# TAB 2: SINGLE STOCK DEEP DIVE
# ==========================================
with tab2:
    selected = st.selectbox("Select a stock:", tickers)
    
    if selected:
        stock_df = data[selected].dropna()
        curr = stock_df['Close'].iloc[-1]
        high_52 = stock_df['High'].tail(252).max()
        dist_from_high = ((high_52 - curr) / high_52) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Price", f"₹{round(curr, 2)}")
        c2.metric("52-Week High", f"₹{round(high_52, 2)}")
        c3.metric("Discount", f"-{round(dist_from_high, 1)}%")
        
        st.line_chart(stock_df['Close'].tail(252))
        
        st.markdown("### Fundamental Health")
        
        # --- SAFE FUNDAMENTAL FETCH ---
        if st.button("🔍 Fetch Live Fundamentals"):
            with st.spinner("Requesting data from Yahoo Finance..."):
                try:
                    # Create a ticker object and attempt to get info
                    ticker_obj = yf.Ticker(selected)
                    info = ticker_obj.info
                    
                    if not info or 'trailingPE' not in info:
                        st.warning("Data not available for this specific symbol.")
                    else:
                        f1, f2, f3 = st.columns(3)
                        f1.metric("P/E Ratio", info.get("trailingPE", "N/A"))
                        f2.metric("Debt-to-Equity", info.get("debtToEquity", "N/A"))
                        f3.metric("Profit Margin", f"{round(info.get('profitMargins', 0)*100, 1)}%" if info.get('profitMargins') else "N/A")
                
                except Exception as e:
                    # If blocked by Yahoo, show this helpful message instead of crashing
                    st.error("🚨 **Yahoo Finance is currently busy.**")
                    st.info("Cloud servers (Streamlit) often get 'Rate Limited' by Yahoo. To see the fundamentals for this stock immediately, click the button below:")
                    
                    # Create a direct link to Yahoo Finance for that stock
                    clean_ticker = selected.replace(".NS", "")
                    yahoo_url = f"https://finance.yahoo.com/quote/{selected}"
                    st.link_button(f"View {clean_ticker} Fundamentals on Yahoo Finance ↗️", yahoo_url)
