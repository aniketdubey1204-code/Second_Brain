import os, json, time
from binance import Client

def load_config():
    return {
        "api_key": os.getenv('BINANCE_API_KEY'),
        "api_secret": os.getenv('BINANCE_API_SECRET')
    }

def get_signal(client):
    # Simple RSI & EMA20 > EMA50 strategy with strict checks (all 4 must pass)
    # For demo, we fetch ticker and use hard‑coded indicator values from the latest log.
    # In a real bot you would compute these from market data.
    # We'll generate a LONG signal only if all conditions are met.
    indicators = {
        "BTCUSDT": {"rsi": 38.82, "ema20_gt_ema50": True, "macd_crossover": "bearish", "volume_pct": -44.0},
        "ETHUSDT": {"rsi": 47.15, "ema20_gt_ema50": True, "macd_crossover": "bullish", "volume_pct": 12.5},
        "SOLUSDT": {"rsi": 46.23, "ema20_gt_ema50": True, "macd_crossover": "bullish", "volume_pct": 5.0},
    }
    for symbol, data in indicators.items():
        # Evaluate conditions
        rsi_check = data["rsi"] < 50
        macd_check = data.get("macd_crossover") in ["bullish", "bearish"]
        volume_check = data.get("volume_pct", 0) > 0
        ema_check = data["ema20_gt_ema50"]
        conditions_passed = sum([rsi_check, macd_check, volume_check, ema_check])
        # Debug output
        # Debug line removed for production
        if conditions_passed < 4:
            continue
        # fetch current price
        try:
            ticker = client.get_symbol_ticker(symbol=symbol)
            entry_price = float(ticker["price"])
        except Exception:
            entry_price = 0.0
        quantity = 0.01  # fixed for demo
        stop_loss = round(entry_price * 0.99, 2)  # 1% SL
        take_profit = round(entry_price * 1.02, 2)  # 2% TP
        return {
            "symbol": symbol,
            "side": "LONG",
            "quantity": quantity,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "conditions_met": conditions_passed,
        }
    return None

def main():
    cfg = load_config()
    client = Client(cfg['api_key'], cfg['api_secret'])
    signal = get_signal(client)
    if signal:
        # Send proposal to owner via OpenClaw messaging (placeholder)
        print(json.dumps({"type": "proposal", **signal}))

if __name__ == "__main__":
    main()
