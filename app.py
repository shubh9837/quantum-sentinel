import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Quantum-Sentinel Pro", layout="wide", page_icon="🎯")

# --- 1. DATA LOADER ---
@st.cache_data
def load_data():
    try:
        return pd.read_parquet("market_data.parquet")
    except Exception:
        return None

st.title("🎯 Quantum-Sentinel: Institutional Screener")
st.markdown("Analyzing Offline T-1 Data for Maximum Stability & Precision.")

all_data = load_data()

if all_data is None:
    st.error("⚠️ Data file missing. Please ensure 'market_data.parquet' is in your repository.")
else:
    # Get all available tickers
    tickers = list(set([col[0] for col in all_data.columns if isinstance(col, tuple)]))
    tickers.sort()
    st.success(f"✅ Data pipeline active. Analyzing 5-year history for {len(tickers)} stocks.")

    # --- UI NAVIGATION ---
    mode = st.radio("Select Analytical Tool:", ["Market Screener (Bulk)", "Stock Deep Dive (Single)"], horizontal=True)

    # ==========================================
    # TOOL 1: THE BULK MARKET SCREENER
    # ==========================================
    if mode == "Market Screener (Bulk)":
        st.subheader("Automated Multi-Factor Scan")
        st.caption("Filters for stocks trading above 20/50 EMAs with optimal RSI momentum.")
        
        scan_limit = st.slider("Number of Stocks to Scan (from top of list)", 50, len(tickers), 300)
        
        if st.button(f"Run Quantum Scan on {scan_limit} Stocks"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            scan_list = tickers[:scan_limit]
            
            for i, ticker in enumerate(scan_list):
                try:
                    df = all_data[ticker].dropna()
                    if len(df) < 50: continue
                    
                    # 1. Price Action
                    close = float(df['Close'].iloc[-1])
                    ema20 = float(df['Close'].ewm(span=20).mean().iloc[-1])
                    ema50 = float(df['Close'].ewm(span=50).mean().iloc[-1])
                    
                    # 2. RSI Momentum
                    delta = df['Close'].diff()
                    gain = delta.clip(lower=0).rolling(14).mean()
                    loss = -delta.clip(upper=0).rolling(14).mean()
                    rs = gain / loss
                    rsi = float(100 - (100 / (1 + rs.iloc[-1])))
                    
                    # 3. Scoring Engine
                    score = 0
                    if close > ema20: score += 2
                    if ema20 > ema50: score += 2
                    if 45 < rsi < 65: score += 2 # Sweet spot: Trending but not overbought
                    
                    # 4. Risk Management (ATR)
                    if score >= 4:  # Only compile data for strong setups to save time
                        atr = float((df['High'] - df['Low']).rolling(14).mean().iloc[-1])
                        sl = close - (2.5 * atr)
                        tgt = close + (5 * atr)
                        
                        results.append({
                            "Stock": ticker.replace(".NS", ""),
                            "Score": f"{score}/6",
                            "CMP (T-1)": round(close, 2),
                            "RSI": round(rsi, 2),
                            "Stop Loss": round(sl, 2),
                            "Target": round(tgt, 2)
                        })
                except Exception:
                    pass # Skip broken data silently
                
                # Update UI efficiently
                if i % 10 == 0: 
                    progress_bar.progress((i + 1) / scan_limit)
                    status_text.text(f"Scanning: {ticker}...")
            
            progress_bar.empty()
            status_text.empty()
            
            if results:
                res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
                st.subheader("🔥 High-Conviction Setups")
                st.dataframe(res_df, use_container_width=True)
            else:
                st.info("No high-conviction setups found in this batch. Market might be bearish.")

    # ==========================================
    # TOOL 2: SINGLE STOCK DEEP DIVE
    # ==========================================
    elif mode == "Stock Deep Dive (Single)":
        st.subheader("Individual Stock Intelligence")
        selected_stock = st.selectbox("Search Stock Symbol", tickers)
        
        if selected_stock:
            df = all_data[selected_stock].dropna()
            
            # --- Historical Metrics ---
            current_price = df['Close'].iloc[-1]
            high_5yr = df['High'].max()
            drawdown = ((high_5yr - current_price) / high_5yr) * 100
            
            st.markdown("### Technical Overview")
            col1, col2, col3 = st.columns(3)
            col1.metric("T-1 Close Price", f"₹{round(current_price, 2)}")
            col2.metric("5-Year Peak", f"₹{round(high_5yr, 2)}")
            col3.metric("Discount from Peak", f"-{round(drawdown, 2)}%")
            
            st.line_chart(df['Close'].tail(252)) # Last 1 year visual trend
            
            # --- Live Fundamental Fetch ---
            st.markdown("### Fundamental Health Check")
            st.info("Fetches live fundamental data directly from Yahoo Finance to avoid rate limits.")
            if st.button("Fetch Live Fundamentals"):
                with st.spinner(f"Connecting to live data for {selected_stock}..."):
                    try:
                        info = yf.Ticker(selected_stock).info
                        f1, f2, f3 = st.columns(3)
                        
                        pe = info.get("trailingPE", "N/A")
                        roe = info.get("returnOnEquity")
                        debt = info.get("debtToEquity", "N/A")
                        
                        f1.metric("P/E Ratio (Valuation)", round(pe, 2) if isinstance(pe, (int, float)) else pe)
                        f2.metric("ROE (Profitability)", f"{round(roe*100, 2)}%" if roe else "N/A")
                        f3.metric("Debt-to-Equity (Risk)", round(debt, 2) if isinstance(debt, (int, float)) else debt)
                    except Exception:
                        st.error("Failed to retrieve live fundamentals. The stock might be delisted or Yahoo is blocking the request.")
