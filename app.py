import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Quantum-Sentinel Offline", layout="wide")

@st.cache_data
def load_big_data():
    return pd.read_parquet("market_data.parquet")

st.title("🏹 Quantum-Sentinel: Institutional 10-Year Engine")

try:
    all_data = load_big_data()
    tickers = all_data.columns.levels[0].tolist()
    
    # Sidebar Search
    search = st.sidebar.selectbox("Select Stock", tickers)
    df = all_data[search].dropna()

    # --- T-1 Analysis ---
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    change = ((current_price - prev_price) / prev_price) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"₹{round(current_price, 2)}", f"{round(change, 2)}%")
    
    # 10-Year High calculation
    ten_yr_high = df['High'].max()
    dist_from_high = ((ten_yr_high - current_price) / ten_yr_high) * 100
    col2.metric("10-Year High", f"₹{round(ten_yr_high, 2)}")
    col3.metric("Dist. from Peak", f"-{round(dist_from_high, 2)}%")

    st.subheader(f"Price History: {search}")
    st.line_chart(df['Close'])

except Exception as e:
    st.error("Data file missing. Please run 'python downloader.py' first.")
