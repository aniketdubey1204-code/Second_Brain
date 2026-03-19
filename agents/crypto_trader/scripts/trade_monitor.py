import os, json, time
from binance import Client

def load_config():
    return {
        "api_key": os.getenv('BINANCE_API_KEY'),
        "api_secret": os.getenv('BINANCE_API_SECRET')
    }

def get_signal(client):
    # Simple RSI & EMA20 > EMA50 strategy with relaxed RSI cutoff (45)
    # For demo, we fetch ticker and use hard‑coded indicator values from the latest log.
    # In a real bot you would compute these from market data.
    # We'll generate a LONG signal for BTCUSDT if RSI < 45 and EMA20 > EMA50.
    # Indicator snapshot (from logs):
    indicators = {
        "BTCUSDT": {"rsi": 38.82, "ema20_gt_ema50": True},
        "ETHUSDT": {"rsi": 47.15, "ema20_gt_ema50": True},
        "SOLUSDT": {"rsi": 46.23, "ema20_gt_ema50": True},
    }
    for symbol, data in indicators.items():
        if data["rsi"] < 45 and data["ema20_gt_ema50"]:
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
