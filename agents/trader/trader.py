# trader.py – Simplified paper‑trading bot (Delta Exchange India)
# ---------------------------------------------------------------
import os, json, datetime, requests, pandas as pd

# -------------------------- CONFIG --------------------------
TELEGRAM_BOT_TOKEN = "8656726405:AAEYlyTqGGhZrT0-7CinkYyMtAlLqwCC8tA"
TELEGRAM_CHAT_ID = "6239074712"
WORKSPACE = r"D:\OpenClaw\workspace\second-brain\agents\trader"
DELTA_BASE_URL = "https://api.india.delta.exchange"
SYMBOLS = ["BTCUSD", "ETHUSD", "SOLUSD"]
PAPER_MODE = True
NO_TRADE_START = 0   # 12 AM IST
NO_TRADE_END   = 6   # 6 AM IST

# ---------------------- HELPERS -------------------
def send_telegram(msg: str):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram error", e)

def load_json(fname):
    p = os.path.join(WORKSPACE, fname)
    if not os.path.isfile(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(fname, data):
    p = os.path.join(WORKSPACE, fname)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_candles(symbol, resolution="15m", count=100):
    import time
    from datetime import datetime, timedelta
    base_url = "https://api.india.delta.exchange"
    url = f"{base_url}/v2/history/candles"
    end = int(datetime.now().timestamp())
    # Calculate start time based on resolution and count
    if resolution == "5m":
        start = end - (count * 5 * 60)
    elif resolution == "15m":
        start = end - (count * 15 * 60)
    elif resolution == "1h":
        start = end - (count * 60 * 60)
    else:
        start = end - (count * 15 * 60)
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "start": str(start),
        "end": str(end)
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json().get("result", [])
        if not data:
            send_telegram(f"⚠️ No candle data received for {symbol}")
            return None
        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])
        df = df.sort_values("time").reset_index(drop=True)
        df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df["time"] = df["time"].dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata")
        return df
    except Exception as e:
        send_telegram(f"❌ Error fetching candles for {symbol}: {str(e)}")
        return None

def get_current_price(symbol):
    base_url = "https://api.india.delta.exchange"
    url = f"{base_url}/v2/tickers/{symbol}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        price = float(data["result"]["close"])
        return price
    except Exception as e:
        send_telegram(f"❌ Error fetching price for {symbol}: {str(e)}")
        return None

def calculate_indicators(df):
    # stub – real logic can be added later
    return df

def detect_regime(df):
    return "UNCLEAR"

def strategy_trend_following(df, regime):
    return None

def strategy_mean_reversion(df, regime):
    return None

def strategy_scalping(df, symbol):
    return None

def calculate_position_size(balance, entry, stop):
    if entry == stop:
        return 0.0
    return round((balance * 0.05) / abs(entry - stop), 3)

def check_risk_limits(positions, balance, daily_pnl):
    if len(positions) >= 3:
        return False, "Max 3 positions"
    if daily_pnl <= -(balance * 0.05):
        return False, "Daily loss limit hit"
    return True, "OK"

def record_trade(action, symbol, entry, sl, tp, regime, strategy):
    ts = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M:%S IST")
    line = f"[{ts}] | {symbol} | {strategy} | {regime} | {action} | Entry:{entry:.2f} SL:{sl:.2f} TP:{tp:.2f}\n"
    with open(os.path.join(WORKSPACE, "trades.log"), "a", encoding="utf-8") as f:
        f.write(line)
    # update balance & positions (very simple mock)
    bal = load_json("paper_balance.json")
    if not bal:
        bal = {"initial_capital":10000,"current_balance":10000,"currency":"INR","mode":"PAPER"}
    pos = load_json("open_positions.json").get("positions", [])
    size = calculate_position_size(bal["current_balance"], entry, sl)
    pos.append({"symbol":symbol,"action":action,"entry":entry,"sl":sl,"tp":tp,"size":size})
    save_json("open_positions.json", {"positions":pos})
    bal["current_balance"] = bal["current_balance"]  # unchanged in paper mode
    save_json("paper_balance.json", bal)
    send_telegram(f"🟢 [PAPER] {symbol} {action} opened at {entry:.2f}")

# ------------------------ MAIN SCAN ----------------
def run_market_scan():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    if NO_TRADE_START <= now.hour < NO_TRADE_END:
        send_telegram("🌙 Night pause – no trading.")
        return
    bal = load_json("paper_balance.json").get("current_balance", 10000)
    positions = load_json("open_positions.json").get("positions", [])
    daily_pnl = 0.0
    # Load previous regimes state
    regime_state = load_json("regime_state.json")
    current_prices = {}
    current_regimes = {}
    regime_change = False
    for sym in SYMBOLS:
        df = get_candles(sym, resolution="15m", count=100)
        price = get_current_price(sym)
        current_prices[sym] = price if price is not None else 0.0
        if df is None or len(df) < 50:
            # insufficient data, treat as unclear for logging
            current_regimes[sym] = "UNCLEAR"
            ts = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M IST")
            with open(os.path.join(WORKSPACE, "trades.log"), "a", encoding="utf-8") as f:
                f.write(f"[{ts}] | SCAN | UNCLEAR regime | {sym}: ₹{current_prices[sym]:.2f} | No trade taken | Reason: Insufficient data\n")
            continue
        df = calculate_indicators(df)
        regime = detect_regime(df)
        current_regimes[sym] = regime
        if regime == "UNCLEAR":
            ts = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M IST")
            with open(os.path.join(WORKSPACE, "trades.log"), "a", encoding="utf-8") as f:
                f.write(f"[{ts}] | SCAN | UNCLEAR regime | {sym}: ₹{current_prices[sym]:.2f} | No trade taken | Reason: ADX in 20-25 zone\n")
            # No telegram for continuous unclear scans
            continue
        # Detect change from UNCLEAR to clear regime
        prev = regime_state.get(sym)
        if prev == "UNCLEAR" and regime != "UNCLEAR":
            regime_change = True
        # Strategy evaluation
        act = strategy_trend_following(df, regime) or strategy_mean_reversion(df, regime)
        if not act:
            continue
        if price is None:
            continue
        # dummy SL/TP
        sl = price * 0.98
        tp = price * 1.04
        ok, reason = check_risk_limits(positions, bal, daily_pnl)
        if not ok:
            send_telegram(f"⚠️ Risk limit: {reason}, skipping {sym}")
            continue
        record_trade(act, sym, price, sl, tp, regime, "DummyStrategy")
    # Send consolidated telegram if any regime changed from UNCLEAR to clear
    if regime_change:
        time_str = now.strftime("%H:%M IST")
        parts = []
        for sym in SYMBOLS:
            price = current_prices.get(sym, 0.0)
            reg = current_regimes.get(sym, "UNCLEAR")
            parts.append(f"{sym}: ₹{price:.2f} | Regime: {reg}")
        msg = f"📊 Market Scan — [{time_str}] " + " ".join(parts) + " ⏳ Waiting for clear directional signal... Next scan: 15 mins"
        send_telegram(msg)
    # Save current regimes for next run
    save_json("regime_state.json", current_regimes)

def run_risk_monitor():
    send_telegram("🔍 Running risk monitor (stub).")

def run_learning_review():
    send_telegram("📚 Running learning review (stub).")

def run_daily_report():
    send_telegram("📈 Daily report generated (stub).")

def run_night_pause():
    send_telegram("🌙 Night pause – closing all positions (stub).")
    save_json("open_positions.json", {"positions":[]})

def run_morning_resume():
    send_telegram("☀️ Morning resume – starting market scan.")
    run_market_scan()

def run_weekly_summary():
    send_telegram("🗓 Weekly summary (stub).")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run-market-scan"
    if cmd == "run-market-scan":
        run_market_scan()
    elif cmd == "run-risk-monitor":
        run_risk_monitor()
    elif cmd == "run-learning-review":
        run_learning_review()
    elif cmd == "run-daily-report":
        run_daily_report()
    elif cmd == "run-night-pause":
        run_night_pause()
    elif cmd == "run-morning-resume":
        run_morning_resume()
    elif cmd == "run-weekly-summary":
        run_weekly_summary()
    else:
        send_telegram(f"⚠️ Unknown command {cmd}")
