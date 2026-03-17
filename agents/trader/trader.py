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

def get_candles(symbol, resolution="15m", count=200):
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
        # Validation: need at least 60 candles
        if len(df) < 60:
            send_telegram(f"⚠️ {symbol}: Only {len(df)} candles received — need minimum 60. Skipping.")
            return None
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

def get_usd_to_inr_rate():
    """Fetch live USD->INR rate, fallback to 83.5"""
    try:
        resp = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        data = resp.json()
        return float(data["rates"].get("INR", 83.5))
    except Exception:
        return 83.5

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

import uuid

def record_trade(action, symbol, entry, sl, tp, regime, strategy, slippage_cost=0.0, fee=0.0, gross_pnl=0.0, net_pnl=0.0, capital_used_inr=0.0, quantity=None):
    # action is direction e.g., "BUY" or "SELL"
    ts = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M:%S IST")
    # Log with detailed fields for open trade
    line = (f"[{ts}] | {symbol} | {strategy} | {regime} | {action} | Entry:{entry:.2f} "
            f"SL:{sl:.2f} TP:{tp:.2f} Slippage:{slippage_cost:.2f} Fee:{fee:.2f} "
            f"GrossP&L:{gross_pnl:.2f} NetP&L:{net_pnl:.2f}\n")
    with open(os.path.join(WORKSPACE, "trades.log"), "a", encoding="utf-8") as f:
        f.write(line)
    # Update open positions list with needed fields
    bal = load_json("paper_balance.json")
    if not bal:
        bal = {"initial_capital":10000,"current_balance":10000,"currency":"INR","mode":"PAPER"}
    pos_data = load_json("open_positions.json")
    if not pos_data:
        pos_data = {"positions": []}
    positions = pos_data.get("positions", [])
    # Calculate quantity (size) – using same logic as before
    if quantity is None:
        quantity = calculate_position_size(bal["current_balance"], entry, sl)
    # Generate unique id for the position
    pos_id = str(uuid.uuid4())
    positions.append({
        "id": pos_id,
        "symbol": symbol,
        "direction": action,
        "actual_entry": entry,
        "stop_loss": sl,
        "take_profit": tp,
        "quantity": quantity,
        "strategy": strategy,
        "regime": regime,
        "slippage_cost": slippage_cost,
        "fee": fee,
        "gross_pnl": gross_pnl,
        "net_pnl": net_pnl
    })
    save_json("open_positions.json", {"positions": positions})
    # paper balance unchanged on opening
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
        df = get_candles(sym, resolution="15m", count=200)
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
        # Initialize regime placeholder for possible London breakout
        regime = None
        # --- London session breakout check (12:30‑14:30 IST) ---
        now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
        if (now_ist.hour == 12 and now_ist.minute >= 30) or (now_ist.hour > 12 and now_ist.hour < 14) or (now_ist.hour == 14 and now_ist.minute <= 30):
            # Determine Asia session range (6:00‑12:00 IST)
            asia_start = now_ist.replace(hour=6, minute=0, second=0, microsecond=0)
            asia_end = now_ist.replace(hour=12, minute=0, second=0, microsecond=0)
            asia_df = df[(df["time"] >= asia_start) & (df["time"] <= asia_end)]
            if not asia_df.empty:
                asia_high = asia_df["high"].max()
                asia_low = asia_df["low"].min()
                latest_volume = df["volume"].iloc[-1]
                avg_volume = df["volume"].mean()
                if price > asia_high and latest_volume > avg_volume:
                    regime = "LONDON_BREAKOUT"
                    act = "BUY"
                elif price < asia_low and latest_volume > avg_volume:
                    regime = "LONDON_BREAKOUT"
                    act = "SHORT"
                else:
                    act = None
                if regime == "LONDON_BREAKOUT":
                    current_regimes[sym] = regime
                    # Log breakout regime
                    ts = now_ist.strftime("%Y-%m-%d %H:%M IST")
                    with open(os.path.join(WORKSPACE, "trades.log"), "a", encoding="utf-8") as f:
                        f.write(f"[{ts}] | SCAN | {regime} regime | {sym}: ₹{price:.2f} | Breakout signal: {act}\n")
                # If breakout detected, skip normal regime logic and continue to trade handling below
                if act:
                    # Continue to trade execution using breakout signal
                    # Use same SL/TP logic as normal but with breakout regime
                    sl = price * 0.983  # -1.7%
                    tp = price * 1.043  # +4.3%
                    ok, reason = check_risk_limits(positions, bal, daily_pnl)
                    if ok:
                        # Allocate capital: 5% of INR balance
                        bal_json = load_json("paper_balance.json")
                        capital_used_inr = bal_json["current_balance"] * 0.05
                        bal_json["current_balance"] -= capital_used_inr
                        save_json("paper_balance.json", bal_json)
                        usd_rate = get_usd_to_inr_rate()
                        capital_used_usd = capital_used_inr / usd_rate
                        qty = round(capital_used_usd / price, 4)
                        record_trade(act, sym, price, sl, tp, regime, "LondonBreakout",
                                     slippage_cost=0.0, fee=0.0, gross_pnl=0.0, net_pnl=0.0,
                                     capital_used_inr=capital_used_inr, quantity=qty)
                    continue
        # Normal regime detection
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
        # Adjusted SL/TP and slippage buffer
        # SL -1.7%, TP +4.3%
        sl = price * 0.983
        tp = price * 1.043
        # Determine slippage based on order side
        if isinstance(act, str) and act.upper().startswith("BUY"):
            actual_entry = price * 1.0005  # BUY buffer
        else:
            actual_entry = price * 0.9995  # SELL/SHORT buffer
        slippage_cost = abs(actual_entry - price)
        ok, reason = check_risk_limits(positions, bal, daily_pnl)
        if not ok:
            send_telegram(f"⚠️ Risk limit: {reason}, skipping {sym}")
            continue
        # fee and P&L will be calculated on close; placeholders for now
        record_trade(act, sym, actual_entry, sl, tp, regime, "DummyStrategy", slippage_cost=slippage_cost, fee=0.0, gross_pnl=0.0, net_pnl=0.0)
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

def close_trade(position, exit_price, reason):
    # Compute actual exit with slippage buffer
    direction = position["direction"]  # BUY or SELL/SHORT
    entry_price = float(position["actual_entry"])
    quantity = float(position["quantity"])
    # Slippage on exit
    if direction.upper() == "BUY":
        actual_exit = exit_price * 0.9995  # sell slightly lower
    else:
        actual_exit = exit_price * 1.0005  # cover slightly higher
    # Gross P&L in USD
    if direction.upper() == "BUY":
        gross_pnl_usd = (actual_exit - entry_price) * quantity
    else:
        gross_pnl_usd = (entry_price - actual_exit) * quantity
    # Fees in USD
    trade_value_usd = entry_price * quantity
    entry_fee_usd = trade_value_usd * 0.0005
    exit_fee_usd = (actual_exit * quantity) * 0.0005
    total_fee_usd = entry_fee_usd + exit_fee_usd
    net_pnl_usd = gross_pnl_usd - total_fee_usd
    # Convert to INR
    usd_to_inr = get_usd_to_inr_rate()
    net_pnl_inr = net_pnl_usd * usd_to_inr
    # Capital used (return it) and update balance
    capital_used = float(position.get("capital_used_inr", 0.0))
    balance = load_json("paper_balance.json")
    balance["current_balance"] = balance.get("current_balance", 0) + capital_used + net_pnl_inr
    balance["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")
    save_json("paper_balance.json", balance)
    # Log closed trade
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")
    slippage_total = position.get("slippage_cost", 0.0) + abs(exit_price - actual_exit) * quantity
    log_line = (f"[CLOSED] [{ts}] | {position['symbol']} | {position['strategy']} | {position['regime']} | "
                f"Entry: ₹{entry_price:.2f} | Exit: ₹{actual_exit:.2f} | "
                f"Slippage: ₹{slippage_total:.2f} | Fee: ₹{total_fee_usd * usd_to_inr:.2f} | "
                f"Gross P&L: ₹{gross_pnl_usd * usd_to_inr:.2f} | Net P&L: ₹{net_pnl_inr:.2f} ({(net_pnl_usd / (entry_price * quantity))*100:.2f}%) | "
                f"Reason: {reason}")
    with open(os.path.join(WORKSPACE, "trades.log"), "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    # Remove from open positions
    pos_data = load_json("open_positions.json")
    if pos_data:
        positions = pos_data.get("positions", [])
        positions = [p for p in positions if p.get("id") != position.get("id")]
        pos_data["positions"] = positions
        pos_data["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")
        save_json("

def run_risk_monitor():
    # Iterate open positions and close if SL/TP hit
    positions_data = load_json("open_positions.json")
    if not positions_data:
        send_telegram("🔍 No open positions to monitor.")
        return
    positions = positions_data.get("positions", [])
    for position in positions[:]:  # copy to allow removal
        current_price = get_current_price(position["symbol"])
        if current_price is None:
            continue
        direction = position["direction"].upper()
        stop_loss = float(position["stop_loss"])
        take_profit = float(position["take_profit"])
        if direction == "BUY":
            if current_price <= stop_loss:
                close_trade(position, current_price, "Stop Loss Hit")
            elif current_price >= take_profit:
                close_trade(position, current_price, "Take Profit Hit")
        else:  # SHORT or SELL
            if current_price >= stop_loss:
                close_trade(position, current_price, "Stop Loss Hit")
            elif current_price <= take_profit:
                close_trade(position, current_price, "Take Profit Hit")
    send_telegram("🔍 Risk monitor completed.")

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
