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

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
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
    
    # --- STRONGER AUTO-MAPPER ---
    name_map = {
        'Scalper': 'Team_A', 'Scalping': 'Team_A', 'Team_A': 'Team_A', 'team_a': 'Team_A',
        'Trend': 'Team_B', 'TrendFollowing': 'Team_B', 'Team_B': 'Team_B', 'team_b': 'Team_B',
        'MeanReversion': 'Team_C', 'Reversion': 'Team_C', 'Team_C': 'Team_C', 'team_c': 'Team_C'
    }
    if 'team' in df.columns:
        df['team'] = df['team'].replace(name_map)
    
    if 'cumulative_pnl' in df.columns:
        df['cumulative_pnl'] = pd.to_numeric(df['cumulative_pnl'], errors='coerce').fillna(0.0)
    
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values('timestamp')
    return df

# --- UI LAYOUT ---
st.title("⚔️ AI Trading Strategy: Battle Royale")

# Sidebar: Live Market Widget
st.sidebar.header("📡 Live Market Feed (CoinDCX)")
btc_p = get_coindcx_price("BTCINR")
eth_p = get_coindcx_price("ETHINR")
st.sidebar.metric("BTC/INR", f"₹{btc_p}")
st.sidebar.metric("ETH/INR", f"₹{eth_p}")

# Leaderboard Logic
df_check = load_data()
if not df_check.empty:
    latest_scores = df_check.groupby('team')['cumulative_pnl'].last().reset_index()
    if not latest_scores.empty:
        winner_row = latest_scores.loc[latest_scores['cumulative_pnl'].idxmax()]
        st.sidebar.success(f"🏆 Leading: {winner_row['team']} ({winner_row['cumulative_pnl']:.2f}%)")

placeholder = st.empty()

# --- MAIN LOOP ---
while True:
    df = load_data()
    with placeholder.container():
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            team_meta = {
                "Team_A": ("🚀 Scalper", m1),
                "Team_B": ("📈 Trend", m2),
                "Team_C": ("📉 Reversion", m3)
            }
            
            for t_id, (t_label, t_col) in team_meta.items():
                t_df = df[df['team'] == t_id]
                if not t_df.empty:
                    latest = t_df.iloc[-1]
                    val = latest['cumulative_pnl']
                    status = latest.get('status', 'IDLE')
                    t_col.metric(t_label, f"{val:.2f}%", f"Status: {status}", 
                                 delta_color="normal" if val >= 0 else "inverse")
                else:
                    t_col.metric(t_label, "0.00%", "Status: Waiting...")

            # --- GRAPH WITH AUTO-SCALE FIX ---
            st.write("### 📊 Live Performance Battle")
            
            # 'markers=True' ensures that even single dots are visible
            fig = px.line(df, x='timestamp', y='cumulative_pnl', color='team',
                          markers=True, template="plotly_dark",
                          color_discrete_map={"Team_A": "#FFD700", "Team_B": "#00CCFF", "Team_C": "#00FF7F"})
            
            # --- FIXED SCALE LOGIC ---
            # Hum minimum range -5 se start karenge taaki 0% wali teams gayab na hon
            y_min = min(df['cumulative_pnl'].min() - 2, -5) 
            y_max = max(df['cumulative_pnl'].max() + 2, 5)
            
            fig.update_layout(
                hovermode="x unified",
                yaxis=dict(range=[y_min, y_max], autorange=False), # Forced Range
                xaxis_title="Timeline",
                yaxis_title="Profit/Loss (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📝 View Live Trade Audit Logs"):
                st.dataframe(df.tail(20).sort_values('timestamp', ascending=False), use_container_width=True)
        else:
            st.warning("Awaiting data... OpenClaw must write to `master_trading_battle.json` in JSONL format.")

    time.sleep(5)
    st.rerun()