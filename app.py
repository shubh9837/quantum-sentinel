import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Quantum-Sentinel Pro", layout="wide")

# --- 1. LOAD LOCAL DATA ---
@st.cache_data
def load_data():
    try:
        return pd.read_parquet("market_data.parquet")
    except Exception:
        return None

st.title("🏹 Quantum-Sentinel: Institutional Screener")
st.markdown("Analyzing Offline T-1 Data for Maximum Stability.")

all_data = load_data()

if all_data is None:
    st.error("⚠️ Data file missing. Please go to GitHub Actions and run 'Update Stock Data' first.")
else:
    # Identify available tickers securely
    tickers = list(set([col[0] for col in all_data.columns if isinstance(col, tuple)]))
    st.success(f"✅ Securely loaded 5-year historical data for {len(tickers)} stocks.")

    mode = st.radio("Select Tool:", ["Deep Market Screener", "Single Stock Analyzer"], horizontal=True)

    # --- MODE 1: THE BULK SCREENER ---
    if mode == "Deep Market Screener":
        st.subheader("Automated Technical Scan")
        st.write("Finds stocks trading above their 20/50 Averages with healthy RSI momentum.")
        
        scan_limit = st.slider("Stocks to Scan (Scanning 2000+ may slow your browser)", 50, len(tickers), 300)
        
        if st.button("Run Quantum Scan"):
            results = []
            progress = st.progress(0)
            
            scan_list = tickers[:scan_limit]
            
            for i, ticker in enumerate(scan_list):
                try:
                    df = all_data[ticker].dropna()
                    if len(df) < 50: continue
                    
                    close = float(df['Close'].iloc[-1])
                    ema20 = float(df['Close'].ewm(span=20).mean().iloc[-1])
                    ema50 = float(df['Close'].ewm(span=50).mean().iloc[-1])
                    
                    # RSI Calc
                    delta = df['Close'].diff()
                    gain = delta.clip(lower=0).rolling(14).mean()
                    loss = -delta.clip(upper=0).rolling(14).mean()
                    rsi = float(100 - (100 / (1 + (gain / loss).iloc[-1])))
                    
                    score = 0
                    if close > ema20: score += 2
                    if ema20 > ema50: score += 2
                    if 45 < rsi < 65: score += 2
                    
                    if score >= 4:  # Only show strong setups
                        atr = float((df['High'] - df['Low']).rolling(14).mean().iloc[-1])
                        sl = close - (2.5 * atr)
                        tgt = close + (5 * atr)
                        
                        results.append({
                            "Stock": ticker.replace(".NS", ""),
                            "Score": f"{score}/6",
                            "Price": round(close, 2),
                            "RSI Momentum": round(rsi, 2),
                            "Stop Loss": round(sl, 2),
                            "Target": round(tgt, 2)
                        })
                except:
                    pass
                
                # Update progress bar every 10 stocks to save UI rendering time
                if i % 10 == 0: progress.progress((i + 1) / scan_limit)
            
            progress.empty()
            if results:
                res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
                st.dataframe(res_df, use_container_width=True)
            else:
                st.info("No high-conviction setups found in this batch.")

    # --- MODE 2: SINGLE STOCK DEEP DIVE ---
    else:
        st.subheader("Individual Stock deep dive")
        selected_stock = st.selectbox("Select Stock", sorted(tickers))
        
        if selected_stock:
            df = all_data[selected_stock].dropna()
            
            current_price = df['Close'].iloc[-1]
            high_5yr = df['High'].max()
            drawdown = ((high_5yr - current_price) / high_5yr) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("T-1 Close Price", f"₹{round(current_price, 2)}")
            col2.metric("5-Year Peak", f"₹{round(high_5yr, 2)}")
            col3.metric("Discount from Peak", f"-{round(drawdown, 2)}%")
            
            st.line_chart(df['Close'].tail(250)) # Show last 1 year of daily charts
            
            # Fetch Live Fundamentals on Button Click (prevents rate limits!)
            if st.button("Fetch Live Fundamentals (P/E & Debt)"):
                with st.spinner("Connecting to live markets..."):
                    info = yf.Ticker(selected_stock).info
                    f1, f2, f3 = st.columns(3)
                    f1.metric("P/E Ratio", info.get("trailingPE", "N/A"))
                    f2.metric("Return on Equity (ROE)", f"{round(info.get('returnOnEquity', 0)*100, 2)}%" if info.get('returnOnEquity') else "N/A")
                    f3.metric("Debt-to-Equity", info.get("debtToEquity", "N/A"))
