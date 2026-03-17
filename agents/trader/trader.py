import requests
import json
import os
import sys
import uuid
import datetime
import time
import pandas as pd
try:
    import telebot
except ImportError:
    telebot = None

# ============================================================
# CONFIG
# ============================================================
TELEGRAM_BOT_TOKEN = "8656726405:AAEYlyTqGGhZrT0-7CinkYyMtAlLqwCC8tA"
TELEGRAM_CHAT_ID = "6239074712"
WORKSPACE = r"D:OpenClawworkspacesecond-brainagents\\trader"
DELTA_BASE_URL = "https://api.india.delta.exchange"
SYMBOLS = ["BTCUSD", "ETHUSD", "SOLUSD"]
PAPER_MODE = True
NO_TRADE_START = 0
NO_TRADE_END = 6
RISK_PERCENT = 0.05
MAX_POSITIONS = 3
DAILY_LOSS_LIMIT = 0.05
TP_PERCENT = 1.043  # +4.3%
SL_PERCENT = 0.983  # -1.7%
SLIPPAGE_BUY = 1.0005
SLIPPAGE_SELL = 0.9995
FEE_RATE = 0.0005
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN) if telebot else None

# ============================================================
# HELPERS
# ============================================================
def send_telegram(message):
    if bot:
        try:
            bot.send_message(TELEGRAM_CHAT_ID, message)
        except Exception as e:
            print(f"Telegram error: {e}")
    else:
        # Fallback: print to console (or you could implement a simple HTTP request)
        print("[Telegram] " + message.encode('ascii', errors='ignore').decode('ascii'))

def load_json(filename):
    path = os.path.join(WORKSPACE, filename)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    path = os.path.join(WORKSPACE, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def log_trade(line):
    path = os.path.join(WORKSPACE, "trades.log")
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def now_ist():
    utc = datetime.datetime.utcnow()
    ist = utc + datetime.timedelta(hours=5, minutes=30)
    return ist.strftime("%Y-%m-%d %H:%M IST")

def get_usd_to_inr():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        return float(r.json()["rates"]["INR"])
    except:
        return 83.5

# ============================================================
# MARKET DATA
# ============================================================
def get_candles(symbol, resolution="15m", count=200):
    end = int(datetime.datetime.utcnow().timestamp())
    mins = {"5m": 5, "15m": 15, "1h": 60}.get(resolution, 15)
    start = end - (count * mins * 60)
    url = f"{DELTA_BASE_URL}/v2/history/candles"
    params = {"symbol": symbol, "resolution": resolution, "start": str(start), "end": str(end)}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json().get("result", [])
        if not data or len(data) < 60:
            return None
        df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume"])
        df = df.sort_values("time").reset_index(drop=True)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df
    except Exception as e:
        send_telegram(f"Candle fetch error {symbol}: {e}")
        return None

def get_price(symbol):
    try:
        r = requests.get(f"{DELTA_BASE_URL}/v2/tickers/{symbol}", timeout=10)
        return float(r.json()["result"]["close"])
    except:
        return None

# ============================================================
# INDICATORS (optional)
# ============================================================
HAS_TA = False
try:
    import pandas_ta as ta
    HAS_TA = True
except Exception:
    pass

def calculate_indicators(df):
    if not HAS_TA:
        return df
    try:
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.adx(length=14, append=True)
        df.ta.stochrsi(length=14, append=True)
        df.ta.atr(length=14, append=True)
    except Exception:
        pass
    return df

# ============================================================
# REGIME DETECTION
# ============================================================
def detect_regime(df):
    try:
        last = df.iloc[-1]
        adx_col = [c for c in df.columns if c.startswith("ADX_")]
        bb_upper = [c for c in df.columns if "BBU" in c]
        bb_lower = [c for c in df.columns if "BBL" in c]
        vol_mean = df["volume"].tail(20).mean()
        vol_current = last["volume"]
        if adx_col and not pd.isna(last[adx_col[0]]):
            adx = last[adx_col[0]]
            if adx > 25:
                return "TRENDING"
            if adx < 20:
                return "RANGING"
            return "UNCLEAR"
        if bb_upper and bb_lower and not pd.isna(last[bb_upper[0]]):
            bb_width = last[bb_upper[0]] - last[bb_lower[0]]
            bb_avg = (df[bb_upper[0]] - df[bb_lower[0]]).tail(20).mean()
            if bb_width > 3 * bb_avg or vol_current > 2 * vol_mean:
                return "VOLATILE"
        return "UNCLEAR"
    except Exception:
        return "UNDETERMINED"

# ============================================================
# STRATEGIES
# ============================================================
def strategy_trend(df, last):
    try:
        prev = df.iloc[-2]
        macd_col = [c for c in df.columns if c.startswith("MACD_")]
        macds_col = [c for c in df.columns if c.startswith("MACDs_")]
        ema20 = [c for c in df.columns if c == "EMA_20"]
        ema50 = [c for c in df.columns if c == "EMA_50"]
        rsi = [c for c in df.columns if c.startswith("RSI_")]
        if not all([macd_col, macds_col, ema20, ema50, rsi]):
            return None
        vol_avg = df["volume"].tail(10).mean()
        macd_cross_up = prev[macd_col[0]] < prev[macds_col[0]] and last[macd_col[0]] > last[macds_col[0]]
        macd_cross_dn = prev[macd_col[0]] > prev[macds_col[0]] and last[macd_col[0]] < last[macds_col[0]]
        rsi_val = last[rsi[0]]
        if macd_cross_up and 45 <= rsi_val <= 65 and last["close"] > last[ema20[0]] > last[ema50[0]] and last["volume"] > vol_avg * 1.2:
            return "BUY"
        if macd_cross_dn and 35 <= rsi_val <= 55 and last["close"] < last[ema20[0]] < last[ema50[0]]:
            return "SHORT"
    except Exception:
        pass
    return None

def strategy_mean_reversion(df, last):
    try:
        prev = df.iloc[-2]
        bb_upper = [c for c in df.columns if "BBU" in c]
        bb_lower = [c for c in df.columns if "BBL" in c]
        rsi = [c for c in df.columns if c.startswith("RSI_")]
        stochrsi_k = [c for c in df.columns if "STOCHRSIk" in c]
        if not all([bb_upper, bb_lower, rsi, stochrsi_k]):
            return None
        rsi_val = last[rsi[0]]
        prev_k = prev[stochrsi_k[0]]
        curr_k = last[stochrsi_k[0]]
        if last["close"] <= last[bb_lower[0]] and rsi_val < 35 and prev_k < 20 and curr_k > prev_k:
            return "BUY"
        if last["close"] >= last[bb_upper[0]] and rsi_val > 65 and prev_k > 80 and curr_k < prev_k:
            return "SELL"
    except Exception:
        pass
    return None

# ============================================================
# TRADE OPEN
# ============================================================
def open_trade(symbol, direction, price, strategy, regime):
    bal = load_json("paper_balance.json")
    pos_data = load_json("open_positions.json")
    if not isinstance(pos_data.get("positions"), list):
        pos_data["positions"] = []
    current_balance = float(bal.get("current_balance", 10000))
    daily_pnl = float(bal.get("daily_pnl", 0))
    if len(pos_data["positions"]) >= MAX_POSITIONS:
        return
    if daily_pnl <= -(current_balance * DAILY_LOSS_LIMIT):
        send_telegram("Daily loss limit hit. No new trades today.")
        return
    usd_inr = get_usd_to_inr()
    capital_inr = current_balance * RISK_PERCENT
    capital_usd = capital_inr / usd_inr
    if direction.upper() == "BUY":
        actual_entry = price * SLIPPAGE_BUY
        stop_loss = actual_entry * SL_PERCENT
        take_profit = actual_entry * TP_PERCENT
    else:
        actual_entry = price * SLIPPAGE_SELL
        stop_loss = actual_entry * (2 - SL_PERCENT)
        take_profit = actual_entry * (2 - TP_PERCENT)
    quantity = round(capital_usd / actual_entry, 4)
    slippage_cost = abs(actual_entry - price) * quantity * usd_inr
    entry_fee = (actual_entry * quantity) * FEE_RATE * usd_inr
    position = {
        "id": str(uuid.uuid4())[:8],
        "symbol": symbol,
        "direction": direction.upper(),
        "entry_price": round(actual_entry, 4),
        "stop_loss": round(stop_loss, 4),
        "take_profit": round(take_profit, 4),
        "quantity": quantity,
        "strategy": strategy,
        "regime": regime,
        "capital_used_inr": round(capital_inr, 2),
        "slippage_inr": round(slippage_cost, 2),
        "entry_fee_inr": round(entry_fee, 2),
        "opened_at": now_ist()
    }
    bal["current_balance"] = round(current_balance - capital_inr, 4)
    bal["last_updated"] = now_ist()
    pos_data["positions"].append(position)
    pos_data["last_updated"] = now_ist()
    save_json("paper_balance.json", bal)
    save_json("open_positions.json", pos_data)
    log_trade(
        f"[OPENED] [{now_ist()}] | {symbol} | {direction.upper()} | {strategy} | {regime} | "
        f"Entry: ${actual_entry:.2f} | SL: ${stop_loss:.2f} | TP: ${take_profit:.2f} | "
        f"Qty: {quantity} | Capital: Rs{capital_inr:.2f} | Slippage: Rs{slippage_cost:.2f} | Fee: Rs{entry_fee:.2f}"
    )
    send_telegram(
        f"[PAPER] TRADE OPENED Coin: {symbol} Direction: {direction.upper()} Entry: ${actual_entry:.2f} "
        f"SL: ${stop_loss:.2f} TP: ${take_profit:.2f} Strategy: {strategy} Regime: {regime} "
        f"Capital Used: Rs{capital_inr:.2f} Balance: Rs{bal['current_balance']:.2f}"
    )

# ============================================================
# TRADE CLOSE
# ============================================================
def close_trade(position, exit_price, reason):
    usd_inr = get_usd_to_inr()
    entry = float(position["entry_price"])
    qty = float(position["quantity"])
    direction = position["direction"]
    capital_inr = float(position.get("capital_used_inr", 0))
    # Apply slippage on exit
    if direction == "BUY":
        actual_exit = exit_price * SLIPPAGE_SELL
        gross_pnl_usd = (actual_exit - entry) * qty
    else:
        actual_exit = exit_price * SLIPPAGE_BUY
        gross_pnl_usd = (entry - actual_exit) * qty
    gross_pnl_inr = gross_pnl_usd * usd_inr
    # Fees in INR (entry fee stored, exit fee calculated)
    entry_fee_inr = float(position.get("entry_fee_inr", 0))
    exit_fee_inr = (actual_exit * qty) * FEE_RATE * usd_inr
    total_fee_inr = entry_fee_inr + exit_fee_inr
    net_pnl_inr = gross_pnl_inr - total_fee_inr
    # Update balance
    balance = load_json("paper_balance.json")
    new_balance = float(balance.get("current_balance", 10000)) + capital_inr + net_pnl_inr
    daily_pnl = float(balance.get("daily_pnl", 0)) + net_pnl_inr
    balance["current_balance"] = round(new_balance, 4)
    balance["daily_pnl"] = round(daily_pnl, 4)
    balance["last_updated"] = now_ist()
    save_json("paper_balance.json", balance)
    # Remove position
    positions = load_json("open_positions.json")
    positions["positions"] = [p for p in positions.get("positions", []) if p.get("id") != position.get("id")]
    positions["last_updated"] = now_ist()
    save_json("open_positions.json", positions)
    # Log closed trade
    slippage_total = position.get("slippage_inr", 0) + abs(exit_price - actual_exit) * qty * usd_inr
    emoji = "PROFIT" if net_pnl_inr > 0 else "LOSS"
    log_trade(
        f"[CLOSED] [{now_ist()}] | {position['symbol']} | {direction} | {position['strategy']} | "
        f"Entry: ${entry:.2f} | Exit: ${actual_exit:.2f} | "
        f"Gross P&L: Rs{gross_pnl_inr:.2f} | Fee: Rs{total_fee_inr:.2f} | "
        f"Net P&L: Rs{net_pnl_inr:.2f} ({(net_pnl_inr/capital_inr)*100:.2f}%) | Reason: {reason}"
    )
    # Send Telegram notification
    send_telegram(
        f"[PAPER] TRADE CLOSED - {emoji} "
        f"Coin: {position['symbol']} Direction: {direction} "
        f"Entry: ${entry:.2f} -> Exit: ${actual_exit:.2f} "
        f"Gross P&L: Rs{gross_pnl_inr:.2f} Fee: Rs{total_fee_inr:.2f} "
        f"Net P&L: Rs{net_pnl_inr:.2f} Reason: {reason} "
        f"New Balance: Rs{new_balance:.2f}"
    )
    return net_pnl_inr

# ============================================================
# MAIN SCAN
# ============================================================
def run_market_scan():
    print("Running market scan")
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    if NO_TRADE_START <= now.hour < NO_TRADE_END:
        send_telegram("🌙 Night pause – no trading.")
        return
    for sym in SYMBOLS:
        df = get_candles(sym)
        price = get_price(sym)
        if df is None or price is None:
            continue
        df = calculate_indicators(df)
        regime = detect_regime(df)
        if regime in ("VOLATILE", "UNCLEAR"):
            continue
        act = strategy_trend(df, df.iloc[-1]) or strategy_mean_reversion(df, df.iloc[-1])
        if act:
            open_trade(sym, act, price, "Strategy", regime)
    send_telegram("🔍 Market scan completed.")

# ============================================================
# RISK MONITOR
# ============================================================
def run_risk_monitor():
    positions_data = load_json("open_positions.json")
    if not positions_data.get("positions"):
        send_telegram("🔍 No open positions to monitor.")
        return
    for position in positions_data.get("positions", [])[:]:
        current_price = get_price(position["symbol"])
        if current_price is None:
            continue
        direction = position["direction"].upper()
        sl = float(position["stop_loss"])
        tp = float(position["take_profit"])
        if direction == "BUY":
            if current_price <= sl:
                close_trade(position, current_price, "Stop Loss Hit")
            elif current_price >= tp:
                close_trade(position, current_price, "Take Profit Hit")
        else:
            if current_price >= sl:
                close_trade(position, current_price, "Stop Loss Hit")
            elif current_price <= tp:
                close_trade(position, current_price, "Take Profit Hit")
    send_telegram("🔍 Risk monitor completed.")

# ============================================================
# ENTRY POINT
# ============================================================
def self_heal(error_msg, context=""):
    """Auto-fix common issues and notify via Telegram."""
    healed = False
    heal_log = []
    # Fix 1: Corrupted JSON files
    for fname in ["paper_balance.json", "open_positions.json", "memory.json"]:
        path = os.path.join(WORKSPACE, fname)
        try:
            with open(path, "r") as f:
                json.load(f)
        except Exception:
            heal_log.append(f"Rebuilt corrupted {fname}")
            if fname == "paper_balance.json":
                save_json(fname, {
                    "initial_capital": 10000,
                    "current_balance": 10000,
                    "currency": "INR",
                    "mode": "PAPER",
                    "daily_pnl": 0,
                    "last_updated": now_ist()
                })
            elif fname == "open_positions.json":
                save_json(fname, {"positions": [], "last_updated": now_ist()})
            elif fname == "memory.json":
                save_json(fname, {
                    "created": now_ist(),
                    "version": 1,
                    "total_closed_trades": 0,
                    "last_analysis": now_ist()
                })
            healed = True
    # Fix 2: Missing trades.log
    log_path = os.path.join(WORKSPACE, "trades.log")
    if not os.path.exists(log_path):
        open(log_path, "w").close()
        heal_log.append("Recreated missing trades.log")
        healed = True
    # Fix 3: pandas_ta missing
    if "pandas_ta" in error_msg or "No module named" in error_msg:
        os.system("pip install pandas_ta -q")
        heal_log.append("Reinstalled pandas_ta")
        healed = True
    # Fix 4: requests timeout / API unreachable
    if "timeout" in error_msg.lower() or "connectionerror" in error_msg.lower():
        heal_log.append("Network issue detected — will retry next cron cycle")
        healed = True
    # Fix 5: Balance negative or zero
    balance = load_json("paper_balance.json")
    if float(balance.get("current_balance", 10000)) <= 0:
        balance["current_balance"] = 10000
        balance["daily_pnl"] = 0
        balance["last_updated"] = now_ist()
        balance["note"] = "Auto-reset: balance was zero/negative"
        save_json("paper_balance.json", balance)
        heal_log.append("Reset zero/negative balance to Rs10,000")
        healed = True
    status = "HEALED" if healed else "UNRESOLVED"
    send_telegram(
        f"AUTO-HEAL [{status}] Error: {error_msg[:200]} Context: {context} "
        f"Actions taken: " + (" ".join(f"- {h}" for h in heal_log) if heal_log else "- No auto-fix available - Manual review needed")
    )
    error_path = os.path.join(WORKSPACE, "error.log")
    with open(error_path, "a", encoding="utf-8") as f:
        f.write(f"[{now_ist()}] [{status}] {context}: {error_msg}")
        for h in heal_log:
            f.write(f" -> {h}")
        f.write("\n")

# ============================================================
# Placeholder functions for optional commands

def run_daily_report():
    # No daily report implemented yet
    pass

def run_learning_review():
    # No learning review implemented yet
    pass

def run_night_pause():
    # No night pause implemented yet
    pass

def run_morning_resume():
    # No morning resume implemented yet
    pass

def run_weekly_summary():
    # No weekly summary implemented yet
    pass

# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run-market-scan"
    commands = {
        "run-market-scan": run_market_scan,
        "run-risk-monitor": run_risk_monitor,
        "run-daily-report": run_daily_report,
        "run-learning-review": run_learning_review,
        "run-night-pause": run_night_pause,
        "run-morning-resume": run_morning_resume,
        "run-weekly-summary": run_weekly_summary,
    }
    func = commands.get(cmd)
    if func:
        try:
            func()
        except Exception as e:
            self_heal(str(e), context=cmd)
    else:
        print(f"Unknown command: {cmd}")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run-market-scan"
    commands = {
        "run-market-scan": run_market_scan,
        "run-risk-monitor": run_risk_monitor,
        "run-daily-report": run_daily_report,
        "run-learning-review": run_learning_review,
        "run-night-pause": run_night_pause,
        "run-morning-resume": run_morning_resume,
        "run-weekly-summary": run_weekly_summary,
    }
    func = commands.get(cmd)
    if func:
        func()
    else:
        print(f"Unknown command: {cmd}")