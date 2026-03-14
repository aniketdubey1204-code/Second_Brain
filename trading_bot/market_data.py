"""Market data module.
Provides functions to fetch real‑time price and OHLCV candles from supported APIs.
Currently implements:
- CoinGecko (free, no API key)
- Binance public REST (no auth for market data)
"""
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict

# Simple rate‑limit decorator
def rate_limited(min_interval: float):
    def decorator(func):
        last_call = [0.0]
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result
        return wrapper
    return decorator

# ---------- CoinGecko ----------
@rate_limited(1.2)  # ~50 calls/minute limit
def coingecko_price(symbol: str) -> float:
    # Symbol format: BTCUSDT -> btc
    id_map = {
        "BTCUSDT": "bitcoin",
        "ETHUSDT": "ethereum",
        "SOLUSDT": "solana",
        "MATICUSDT": "matic-network",
    }
    cg_id = id_map.get(symbol.upper())
    if not cg_id:
        raise ValueError(f"Unsupported symbol for CoinGecko: {symbol}")
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return float(data[cg_id]["usd"])

# ---------- Binance ----------
BINANCE_BASE = "https://api.binance.com"

@rate_limited(0.5)
def binance_ohlcv(symbol: str, interval: str = "1m", limit: int = 300) -> pd.DataFrame:
    """Fetch OHLCV candles from Binance public endpoint.
    Returns a DataFrame with columns: ['timestamp','open','high','low','close','volume']
    """
    endpoint = f"/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit,
    }
    resp = requests.get(BINANCE_BASE + endpoint, params=params, timeout=10)
    resp.raise_for_status()
    raw = resp.json()
    df = pd.DataFrame(raw, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    # Convert timestamps
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    # Cast numeric columns
    for col in ["open","high","low","close","volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["timestamp","open","high","low","close","volume"]]

def get_price(symbol: str) -> float:
    """Unified price getter – tries CoinGecko first, falls back to Binance."""
    try:
        return coingecko_price(symbol)
    except Exception:
        # Binance ticker endpoint (latest price)
        url = f"{BINANCE_BASE}/api/v3/ticker/price"
        resp = requests.get(url, params={"symbol": symbol.upper()}, timeout=10)
        resp.raise_for_status()
        return float(resp.json()["price"])

def get_ohlcv(symbol: str, timeframe: str = "1m", limit: int = 300) -> pd.DataFrame:
    """Unified OHLCV getter – currently implemented via Binance public API."""
    interval_map = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
    }
    interval = interval_map.get(timeframe)
    if not interval:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    return binance_ohlcv(symbol, interval=interval, limit=limit)
