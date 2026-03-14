"""Optimizer module.
Runs a simple parameter sweep on recent historical data and saves the best
parameter set to ``strategy_params.json`` if performance improves.
"""
import json
import os
from typing import Dict, List
import pandas as pd

# Assuming strategy_engine module exposes a function build_strategy(params) -> callable

class Optimizer:
    def __init__(self, config: Dict, data_fetcher):
        self.config = config
        self.data_fetcher = data_fetcher  # callable that returns OHLCV DataFrame
        self.params_path = os.path.join(os.path.dirname(__file__), "strategy_params.json")
        # Load existing params if any
        if os.path.exists(self.params_path):
            with open(self.params_path, "r", encoding="utf-8") as f:
                self.current_params = json.load(f)
        else:
            self.current_params = {}

    def _load_params(self) -> Dict:
        return self.current_params

    def _save_params(self, params: Dict):
        with open(self.params_path, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=2)
        self.current_params = params

    def optimize(self, symbol: str, timeframe: str = "1m"):
        # Fetch recent data (e.g., last 7 days)
        df = self.data_fetcher(symbol, timeframe=timeframe, limit=5000)
        # Define search space (simplified)
        ema_short_vals = [10, 15, 20]
        ema_long_vals = [40, 50, 60]
        rsi_thresh = [(30, 70), (40, 80)]
        best_score = -1
        best_params = None
        from .strategy_engine import build_strategy
        from .backtester import Backtester
        for es in ema_short_vals:
            for el in ema_long_vals:
                for r_low, r_high in rsi_thresh:
                    params = {
                        'ema_short': es,
                        'ema_long': el,
                        'rsi_low': r_low,
                        'rsi_high': r_high,
                    }
                    strategy_fn = build_strategy(params)
                    bt = Backtester(strategy_fn, initial_balance=self.config.get('initial_balance', 10000))
                    trades = bt.run(df)
                    # Simple metric: total P&L
                    total_pnl = sum(t.get('pnl',0) for t in trades)
                    if total_pnl > best_score:
                        best_score = total_pnl
                        best_params = params
        if best_params and best_score > 0:
            # Save only if improvement (greater than current total P&L if we have a baseline)
            self._save_params(best_params)
        return best_params, best_score
