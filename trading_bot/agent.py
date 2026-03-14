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
        # System monitor for self‑diagnosis & self‑healing
        from .system_monitor import SystemMonitor
        self.monitor = SystemMonitor(self.config)

    def run_cycle(self):
        """Execute one trading cycle with session‑aware, multi‑timeframe strategy selection.
        - Detect market session (Asia/London/NewYork).
        - Fetch 15 m, 5 m and 1 m data.
        - Determine market regime (trending, sideways, high volatility).
        - Choose appropriate strategy (trend, grid, mean‑reversion).
        - Apply multi‑timeframe entry filters.
        - Enforce trade‑limit (max 3 trades per hour per symbol).
        - Log diagnostics and performance summary.
        """
        from datetime import datetime, timezone
        import os
        from ta.trend import EMAIndicator
        from ta.momentum import RSIIndicator

        # ------------------------------------------------------------------
        # Helper: market session based on UTC hour
        def get_market_session():
            utc_hour = datetime.utcnow().hour
            if 0 <= utc_hour < 7:
                return 'Asia'
            if 7 <= utc_hour < 13:
                return 'London'
            if 13 <= utc_hour < 22:
                return 'NewYork'
            return 'OffHours'

        # Helper: regime detection using EMA50/200 and ATR
        def detect_regime_multi(ema50, ema200, atr, vol_thresh):
            diff = abs(ema50 - ema200) / ema200
            if atr > vol_thresh:
                return 'high_volatility'
            if diff > 0.02:  # >2% distance → trending
                return 'trending'
            return 'sideways'

        session = get_market_session()
        # Initialise trade‑limit tracker if not present
        if not hasattr(self, '_trade_history'):
            self._trade_history = {sym: [] for sym in self.config.get('symbols', [])}

        # ------------------------------------------------------------------
        # Process each symbol
        for symbol in self.config.get('symbols', []):
            # ----- fetch multi‑timeframe data -----
            price = get_price(symbol)
            df_15 = get_ohlcv(symbol, timeframe='15m', limit=100)
            df_5 = get_ohlcv(symbol, timeframe='5m', limit=100)
            df_1 = get_ohlcv(symbol, timeframe='1m', limit=100)
            # ----- compute indicators -----
            # 15 m EMA50 & EMA200
            ema50_15 = EMAIndicator(df_15['close'], window=50).ema_indicator().iloc[-1]
            ema200_15 = EMAIndicator(df_15['close'], window=200).ema_indicator().iloc[-1]
            # 5 m EMA9 & EMA21
            ema9_5 = EMAIndicator(df_5['close'], window=9).ema_indicator().iloc[-1]
            ema21_5 = EMAIndicator(df_5['close'], window=21).ema_indicator().iloc[-1]
            # 1 m RSI
            rsi_1 = RSIIndicator(df_1['close'], window=14).rsi().iloc[-1]
            # ATR from 15 m (use calculate_indicators for convenience)
            atr_15 = calculate_indicators(df_15)['atr']

            # ----- regime detection -----
            regime = detect_regime_multi(ema50_15, ema200_15, atr_15, self.config.get('volatility_threshold', 0.05))

            # ----- strategy selection -----
            chosen_strategy = 'none'
            signal = None
            # High volatility → mean reversion
            if regime == 'high_volatility':
                if rsi_1 < 30:
                    signal = 'buy'
                elif rsi_1 > 70:
                    signal = 'sell'
                chosen_strategy = 'volatility_mean_reversion'
            # Sideways market → grid strategy (prefer during Asia session)
            elif regime == 'sideways' or (session == 'Asia' and regime != 'trending'):
                grid_step = 0.005  # 0.5% grid
                lower = price * (1 - grid_step)
                upper = price * (1 + grid_step)
                if price <= lower:
                    signal = 'buy'
                elif price >= upper:
                    signal = 'sell'
                chosen_strategy = 'grid'
            # Trending market → trend‑following (allowed in London/NewYork)
            elif regime == 'trending' and session in ['London', 'NewYork']:
                if ema9_5 > ema21_5 and 40 <= rsi_1 <= 60:
                    signal = 'buy'
                elif ema9_5 < ema21_5 and 40 <= rsi_1 <= 60:
                    signal = 'sell'
                chosen_strategy = 'trend_following'
            else:
                chosen_strategy = 'none'

            # ----- trade‑limit enforcement -----
            now_ts = datetime.utcnow().timestamp()
            # purge old entries (>1 h)
            self._trade_history[symbol] = [t for t in self._trade_history[symbol] if now_ts - t < 3600]
            if len(self._trade_history[symbol]) >= 3:
                signal = None
                chosen_strategy += '_limit_exceeded'

            # ----- risk & execution -----
            if signal and self.risk_manager.can_open_position():
                sl = price * (1 - 0.015) if signal == 'buy' else price * (1 + 0.015)
                tp = price * (1 + 0.03) if signal == 'buy' else price * (1 - 0.03)
                if not self.risk_manager.evaluate_trade(price, sl, tp, atr_15):
                    signal = None
                else:
                    size = self.risk_manager.position_size(abs(price - sl))
                    exec_res = self.execution.execute_order(symbol, signal, price, size)
                    trade_record = {
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'symbol': symbol,
                        'side': signal,
                        'entry_price': price,
                        'size': size,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'fee': exec_res.get('fee'),
                        'reason': chosen_strategy,
                    }
                    # Immediate close for paper demo
                    exit_price = tp if signal == 'buy' else sl
                    pnl = (exit_price - price) * size if signal == 'buy' else (price - exit_price) * size
                    pnl -= exec_res.get('fee')
                    trade_record['exit_price'] = exit_price
                    trade_record['pnl'] = pnl
                    log_trade(trade_record)
                    # Record trade time for limit enforcement
                    self._trade_history[symbol].append(now_ts)
                    # Update portfolio & risk manager
                    self.portfolio.add_position(None)
                    self.risk_manager.record_trade_outcome(pnl)
                    # Log completed trade
                    log_trade(trade_record)
            # ----- debug logging -----
            debug_line = f"{datetime.utcnow().isoformat()}Z | {symbol} | session:{session} | regime:{regime} | strategy:{chosen_strategy} | decision:{signal or 'none'}\n"
            debug_path = os.path.join(os.path.dirname(__file__), "logs", "strategy_debug.log")
            with open(debug_path, "a", encoding="utf-8") as dbg:
                dbg.write(debug_line)
        # ------------------------------------------------------------------
        # Performance summary
        perf_path = os.path.join(os.path.dirname(__file__), "..", "logs", "PERFORMANCE_STATUS.md")
        with open(perf_path, "w", encoding="utf-8") as pf:
            pf.write(f"## Performance Status {datetime.utcnow().isoformat()}Z\n")
            pf.write(f"- Account balance: {self.portfolio.account_balance:.2f}\n")
            pf.write(f"- Realized PnL: {self.portfolio.realized_pnl:.2f}\n")
            pf.write(f"- Total trades: {self.portfolio.trade_count}\n")
            win_rate = (self.portfolio.win_count / self.portfolio.trade_count * 100) if self.portfolio.trade_count else 0.0
            pf.write(f"- Win rate: {win_rate:.2f}%\n")
            pf.write(f"- Current market session: {session}\n")
            pf.write(f"- Active strategy: {chosen_strategy}\n")
        # End of cycle

    def start(self):
        poll_interval = self.config.get('poll_interval', 60)
        while True:
            self.run_cycle()
            time.sleep(poll_interval)

if __name__ == '__main__':
    agent = TradingAgent()
    agent.start()
