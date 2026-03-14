"""Main trading agent.
Coordinates market data fetching, indicator computation, regime detection,
strategy evaluation, risk checks, execution and logging.
"""
import yaml
import time
from datetime import datetime
from pathlib import Path

from .market_data import get_price, get_ohlcv
from .indicators import calculate_indicators
from .regime_detector import detect_regime
from .risk_manager import RiskManager
from .portfolio_manager import PortfolioManager
from .execution_engine import ExecutionEngine
from .trade_logger import log_trade
from .strategy_engine import build_strategy

CONFIG_PATH = Path(__file__).parent / "config.yaml"

class TradingAgent:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.risk_manager = RiskManager(self.config)
        self.portfolio = PortfolioManager(initial_balance=self.config.get('initial_balance', 10000.0))
        self.execution = ExecutionEngine(self.config)
        # Load strategy parameters (if any)
        params_path = Path(__file__).parent / "strategy_params.json"
        if params_path.is_file():
            with open(params_path, "r", encoding="utf-8") as f:
                self.strategy_params = yaml.safe_load(f)
        else:
            self.strategy_params = {'type': 'trend'}  # default
        self.strategy = build_strategy(self.strategy_params)

    def run_cycle(self):
        # Fetch market data for each symbol (latest price & 1m candles)
        snapshots = {}
        for symbol in self.config.get('symbols', []):
            price = get_price(symbol)
            ohlcv = get_ohlcv(symbol, timeframe='1m', limit=2)  # last two candles for EMA cross
            indicators = calculate_indicators(ohlcv)
            regime = detect_regime(indicators['price'], indicators['ema50'], indicators['atr'], self.config.get('volatility_threshold', 0.05))
            snapshots[symbol] = {
                'price': price,
                'indicators': indicators,
                'regime': regime,
            }
        # Simple loop over symbols – evaluate strategy
        for symbol, data in snapshots.items():
            signal = self.strategy(data['indicators'], data['regime'])
            if signal and self.risk_manager.can_open_position():
                # Determine stop‑loss and take‑profit (fixed percentages for demo)
                entry = data['price']
                sl = entry * (1 - 0.02) if signal == 'buy' else entry * (1 + 0.02)
                tp = entry * (1 + 0.04) if signal == 'buy' else entry * (1 - 0.04)
                atr = data['indicators']['atr']
                if not self.risk_manager.evaluate_trade(entry, sl, tp, atr):
                    continue
                size = self.risk_manager.position_size(abs(entry - sl))
                exec_res = self.execution.execute_order(symbol, signal, entry, size)
                trade_record = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'symbol': symbol,
                    'side': signal,
                    'entry_price': entry,
                    'size': size,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'fee': exec_res.get('fee'),
                    'reason': 'strategy_signal',
                }
                log_trade(trade_record)
                # For paper mode we simulate an immediate fill and close for demo
                # In real use you would keep the position open until SL/TP hit.
                # Here we close instantly and compute P&L
                exit_price = tp if signal == 'buy' else sl
                pnl = (exit_price - entry) * size if signal == 'buy' else (entry - exit_price) * size
                pnl -= exec_res.get('fee')
                trade_record['exit_price'] = exit_price
                trade_record['pnl'] = pnl
                # Update portfolio & risk manager
                self.portfolio.add_position(None)  # placeholder – not tracking live positions here
                self.risk_manager.record_trade_outcome(pnl)
                # Log the completed trade (including exit)
                log_trade(trade_record)
        # End of cycle – could update portfolio metrics, drawdowns etc.

    def start(self):
        poll_interval = self.config.get('poll_interval', 60)
        while True:
            self.run_cycle()
            time.sleep(poll_interval)

if __name__ == '__main__':
    agent = TradingAgent()
    agent.start()
