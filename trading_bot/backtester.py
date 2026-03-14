"""Backtester module.
Runs a supplied strategy engine against historical OHLCV data and returns
performance metrics.
"""
import pandas as pd
from typing import Callable, Dict, List

class Backtester:
    def __init__(self, strategy_fn: Callable, initial_balance: float = 10000.0):
        self.strategy_fn = strategy_fn
        self.initial_balance = initial_balance
        self.results: List[Dict] = []

    def run(self, ohlcv: pd.DataFrame):
        """Iterate over OHLCV rows, feed them to the strategy, and simulate trades.
        The strategy function receives a row dict with price/indicators and should
        return either None or a trade dict with keys: symbol, side, size, entry_price,
        stop_loss, take_profit, reason.
        """
        balance = self.initial_balance
        positions = []
        for idx, row in ohlcv.iterrows():
            # Let strategy decide based on row
            trade = self.strategy_fn(row)
            if trade:
                # Simple simulation: assume immediate fill at entry_price
                pnl = 0.0
                # No exit logic here – this is a skeleton; real implementation would
                # handle exit conditions over subsequent rows.
                balance += pnl
                self.results.append({**trade, 'pnl': pnl, 'balance': balance, 'timestamp': row['timestamp']})
        return self.results
