import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import time
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Strategy Battle Royale", layout="wide")
LOG_FILE = "master_trading_battle.json"
INITIAL_CAPITAL_USD = 500.0  # Bhai yahan apna per-team budget set kar lo ($)

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .profit-card { border: 1px solid #4ade80; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_live_forex():
    """Fetches real-time USD to INR conversion rate"""
    try:
        # Public API for current exchange rates
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['rates']['INR']
    except Exception:
        return 83.50  # Fallback rate agar internet slow ho

def get_coindcx_price(pair="BTCINR"):
    try:
        url = "https://public.coindcx.com/market_data/current_prices"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data.get(pair, "N/A")
    except Exception:
        return "Conn Error"

def load_data():
    if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
        return pd.DataFrame()
    data = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data)
    name_map = {
        'Scalper': 'Team_A', 'Scalping': 'Team_A', 'Team_A': 'Team_A',
        'Trend': 'Team_B', 'TrendFollowing': 'Team_B', 'Team_B': 'Team_B',
        'MeanReversion': 'Team_C', 'Reversion': 'Team_C', 'Team_C': 'Team_C'
    }
    if 'team' in df.columns:
        df['team'] = df['team'].replace(name_map)
    if 'cumulative_pnl' in df.columns:
        df['cumulative_pnl'] = pd.to_numeric(df['cumulative_pnl'], errors='coerce').fillna(0.0)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.sort_values('timestamp')
    return df

# --- UI LAYOUT ---
st.title("⚔️ AI Trading Strategy: Battle Royale")

# Sidebar: Live Market Widget
usd_to_inr = get_live_forex()
st.sidebar.header("📡 Live Market Feed")
st.sidebar.write(f"💵 **1 USD = ₹{usd_to_inr:.2f}**")
st.sidebar.caption("Daily exchange rate applied")

btc_p = get_coindcx_price("BTCINR")
eth_p = get_coindcx_price("ETHINR")
st.sidebar.metric("BTC/INR", f"₹{btc_p}")
st.sidebar.metric("ETH/INR", f"₹{eth_p}")

# Data Load
df = load_data()

# --- LIFETIME CASH PROFIT SECTION ---
st.write("### 💰 Cash Profit Summary (Lifetime)")
if not df.empty:
    p_col1, p_col2, p_col3 = st.columns(3)
    teams = {"Team_A": "🚀 Scalper", "Team_B": "📈 Trend", "Team_C": "📉 Reversion"}
    p_cols = [p_col1, p_col2, p_col3]
    
    for i, (t_id, t_name) in enumerate(teams.items()):
        t_df = df[df['team'] == t_id]
        if not t_df.empty:
            pnl_pct = t_df.iloc[-1]['cumulative_pnl']
            # Dollar and INR Calculation
            cash_usd = (pnl_pct / 100) * INITIAL_CAPITAL_USD
            cash_inr = cash_usd * usd_to_inr
            
            with p_cols[i]:
                color = "#4ade80" if cash_usd >= 0 else "#f87171"
                st.markdown(f"""
                <div style="border: 1px solid {color}; padding: 15px; border-radius: 10px; text-align: center;">
                    <h4 style="margin:0;">{t_name}</h4>
                    <h2 style="color:{color}; margin: 5px 0;">₹{cash_inr:,.2f}</h2>
                    <p style="margin:0; opacity: 0.8;">${cash_usd:,.2f} USD</p>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("Waiting for data to calculate profits...")

st.markdown("---")

# --- AI STRATEGY ADVISOR LOGIC ---
st.sidebar.markdown("---")
st.sidebar.header("🤖 AI Strategy Advisor")

if not df.empty:
    latest_pnls = df.groupby('team')['cumulative_pnl'].last()
    best_team = latest_pnls.idxmax()
    
    advice = ""
    if best_team == 'Team_A':
        advice = "🚀 **Scalping Mode:** Market is volatile. Quick 1m-5m entries are printing cash."
    elif best_team == 'Team_B':
        advice = "📈 **Trend Mode:** Strong momentum detected. Ride the trend for maximum USD gain."
    elif best_team == 'Team_C':
        advice = "📉 **Reversion Mode:** Range-bound market. Buy support, sell resistance."
    
    st.sidebar.success(f"**Recommended Strategy:**\n\n{advice}")

placeholder = st.empty()

while True:
    df = load_data()
    with placeholder.container():
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            team_meta = {"Team_A": ("🚀 Scalper", m1), "Team_B": ("📈 Trend", m2), "Team_C": ("📉 Reversion", m3)}
            
            for t_id, (t_label, t_col) in team_meta.items():
                t_df = df[df['team'] == t_id]
                if not t_df.empty:
                    latest = t_df.iloc[-1]
                    val = latest['cumulative_pnl']
                    t_col.metric(t_label, f"{val:.2f}%", f"Status: {latest.get('status', 'IDLE')}", delta_color="normal" if val >= 0 else "inverse")
                else:
                    t_col.metric(t_label, "0.00%", "Waiting...")

            st.write("### 📊 Live Performance Battle")
            fig = px.line(df, x='timestamp', y='cumulative_pnl', color='team', markers=True, template="plotly_dark",
                          color_discrete_map={"Team_A": "#FFD700", "Team_B": "#00CCFF", "Team_C": "#00FF7F"})
            
            y_min, y_max = df['cumulative_pnl'].min() - 2, df['cumulative_pnl'].max() + 2
            fig.update_layout(hovermode="x unified", yaxis=dict(range=[y_min, y_max]))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Awaiting standardized data from OpenClaw...")

    time.sleep(5)
    st.rerun()