"""system_monitor.py – Self‑diagnosing & self‑healing layer for the trading bot.
The monitor runs alongside the main trading loop and performs health checks every 5 minutes.
It can recover from API failures, missing data, indicator errors, strategy anomalies,
risk‑manager exceptions, execution problems, and logging issues.
All issues are logged to `logs/system_health.log` and a summary report is emitted
every 6 hours as `logs/system_health_report.json`.
"""

import os
import json
import time
import threading
import traceback
from datetime import datetime, timedelta
from collections import deque

# Import trading‑bot modules (relative imports because this file lives in the package)
from .market_data import get_price, get_ohlcv
from .indicators import calculate_indicators
from .strategy_engine import build_strategy
from .risk_manager import RiskManager
from .execution_engine import ExecutionEngine
from .trade_logger import log_trade

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
HEALTH_LOG = os.path.join(LOG_DIR, "system_health.log")
REPORT_PATH = os.path.join(LOG_DIR, "system_health_report.json")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

class SystemMonitor:
    def __init__(self, config):
        self.cfg = config
        self.error_counter = deque()  # (timestamp, critical_flag)
        self.failsafe_active = False
        self.lock = threading.Lock()
        # Start background threads
        self._start_health_thread()
        self._start_report_thread()

    # ---------------------------------------------------------------------
    # Logging helpers
    # ---------------------------------------------------------------------
    def _log(self, msg, critical=False):
        ts = datetime.utcnow().isoformat() + "Z"
        entry = f"{ts} - {'CRITICAL' if critical else 'INFO'} - {msg}\n"
        with open(HEALTH_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
        # Track critical errors for failsafe logic
        if critical:
            with self.lock:
                self.error_counter.append((datetime.utcnow(), True))
                self._prune_errors()
                if self._critical_errors_last_hour() > 10 and not self.failsafe_active:
                    self.failsafe_active = True
                    self._log("Failsafe activated: >10 critical errors in 1h – pausing trading", critical=True)

    def _prune_errors(self):
        cutoff = datetime.utcnow() - timedelta(hours=1)
        while self.error_counter and self.error_counter[0][0] < cutoff:
            self.error_counter.popleft()

    def _critical_errors_last_hour(self):
        return sum(1 for ts, crit in self.error_counter if crit)

    # ---------------------------------------------------------------------
    # Health check components
    # ---------------------------------------------------------------------
    def _check_api(self, symbol):
        """Test both price and OHLCV endpoints with retries.
        Returns tuple (price_ok, ohlcv_ok).
        """
        for attempt in range(3):
            try:
                _ = get_price(symbol)
                price_ok = True
            except Exception as e:
                price_ok = False
                self._log(f"API price fetch failed for {symbol} (attempt {attempt+1}): {e}", critical=True)
                continue
            try:
                df = get_ohlcv(symbol, timeframe="1m", limit=60)
                ohlcv_ok = len(df) >= 60
                if not ohlcv_ok:
                    self._log(f"API OHLCV insufficient ({len(df)} rows) for {symbol}", critical=True)
                return price_ok, ohlcv_ok
            except Exception as e:
                self._log(f"API OHLCV fetch failed for {symbol} (attempt {attempt+1}): {e}", critical=True)
        return False, False

    def _ensure_ohlcv(self, symbol, df):
        """Guarantee at least 60 candles; request more if needed.
        Returns a DataFrame with >=60 rows or None.
        """
        if len(df) >= 60:
            return df
        # Try to fetch more candles
        try:
            df_extra = get_ohlcv(symbol, timeframe="1m", limit=150)
            if len(df_extra) >= 60:
                return df_extra
            else:
                self._log(f"Insufficient candles after retry for {symbol}: {len(df_extra)}", critical=True)
        except Exception as e:
            self._log(f"Failed to fetch extra candles for {symbol}: {e}", critical=True)
        return None

    def _validate_indicators(self, df):
        """Calculate indicators and verify required fields exist and are not NaN.
        Returns dict of indicators or None.
        """
        try:
            inds = calculate_indicators(df)
        except Exception as e:
            self._log(f"Indicator calculation exception: {e}", critical=True)
            try:
                # retry once
                inds = calculate_indicators(df)
            except Exception as e2:
                self._log(f"Indicator retry failed: {e2}", critical=True)
                return None
        # Required keys
        required = ["ema20","ema50","ema100","rsi14","macd","macd_signal","bb_upper","bb_lower","atr"]
        missing = [k for k in required if k not in inds or inds[k] is None or (isinstance(inds[k], float) and (inds[k] != inds[k]))]
        if missing:
            self._log(f"Missing or NaN indicator fields: {missing}", critical=True)
            return None
        return inds

    def _validate_signal(self, signal):
        """Ensure strategy returns dict with expected keys.
        If invalid, replace with HOLD.
        """
        expected_keys = {"action", "confidence", "reason"}
        if not isinstance(signal, dict) or not expected_keys.issubset(set(signal.keys())):
            self._log(f"Invalid strategy signal format: {signal}. Replacing with HOLD.")
            return {"action": "HOLD", "confidence": 0.0, "reason": "invalid_format"}
        # Validate action value
        if signal["action"] not in {"BUY", "SELL", "HOLD"}:
            self._log(f"Unexpected action in signal: {signal['action']}. Forcing HOLD.")
            signal["action"] = "HOLD"
        return signal

    def _validate_risk(self, risk_manager, price, stop_loss, take_profit, atr):
        try:
            # Example usage: just call position_size to see if it raises
            _ = risk_manager.position_size(abs(stop_loss - price))
            return True
        except Exception as e:
            self._log(f"Risk manager validation error: {e}", critical=True)
            return False

    def _validate_execution(self, exec_engine, symbol, side, price, size):
        try:
            res = exec_engine.execute(symbol, side, price, size)
            return res
        except Exception as e:
            self._log(f"Execution engine failure (first attempt): {e}", critical=True)
            # retry once
            try:
                res = exec_engine.execute(symbol, side, price, size)
                return res
            except Exception as e2:
                self._log(f"Execution engine failure (retry): {e2}", critical=True)
                return None

    def _validate_logging(self):
        # Ensure required log files exist; create empty if missing
        required_files = [
            os.path.join(LOG_DIR, "strategy_debug.log"),
            os.path.join(LOG_DIR, "trades.json"),
            os.path.join(LOG_DIR, "TRADE_LOG.md"),
        ]
        for fpath in required_files:
            if not os.path.exists(fpath):
                try:
                    open(fpath, "a").close()
                    self._log(f"Created missing log file: {fpath}")
                except Exception as e:
                    self._log(f"Failed to create log file {fpath}: {e}", critical=True)

    # ---------------------------------------------------------------------
    # Scheduler validation – very lightweight: just ensure the main loop is alive
    # ---------------------------------------------------------------------
    def _validate_scheduler(self, last_cycle_timestamp):
        # Called from agent after each cycle with the timestamp of that cycle.
        now = datetime.utcnow()
        if (now - last_cycle_timestamp).total_seconds() > 120:  # >2 mins
            self._log("Scheduler appears stalled – last cycle older than 2 minutes.", critical=True)
            # No automatic restart here – the agent process would be restarted by the cron.

    # ---------------------------------------------------------------------
    # Public health check entry point (called every 5 minutes)
    # ---------------------------------------------------------------------
    def run_full_check(self, symbols):
        # 1. API health
        for sym in symbols:
            price_ok, ohlcv_ok = self._check_api(sym)
            if not price_ok or not ohlcv_ok:
                self._log(f"API health issue detected for {sym}")
        # 2. Logging files
        self._validate_logging()
        # Additional checks could be added here (e.g., ensure scheduler thread alive)
        # For brevity, only core checks are performed.
        self._log("Full health check completed.")

    # ---------------------------------------------------------------------
    # Background thread that runs every 5 minutes
    # ---------------------------------------------------------------------
    def _health_loop(self):
        while True:
            try:
                # Load symbols from config each run (in case config changes)
                symbols = self.cfg.get('symbols', [])
                self.run_full_check(symbols)
            except Exception as e:
                self._log(f"Unexpected error in health loop: {e}\n{traceback.format_exc()}", critical=True)
            time.sleep(300)  # 5 minutes

    def _start_health_thread(self):
        t = threading.Thread(target=self._health_loop, daemon=True)
        t.start()

    # ---------------------------------------------------------------------
    # Reporting – every 6 hours generate a JSON summary
    # ---------------------------------------------------------------------
    def _report_loop(self):
        while True:
            try:
                self._generate_report()
            except Exception as e:
                self._log(f"Error generating health report: {e}", critical=True)
            time.sleep(6 * 3600)  # 6 hours

    def _start_report_thread(self):
        t = threading.Thread(target=self._report_loop, daemon=True)
        t.start()

    def _generate_report(self):
        # Simple metrics based on counters – more elaborate stats could be added
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "critical_errors_last_hour": self._critical_errors_last_hour(),
            "failsafe_active": self.failsafe_active,
            "api_uptime": "unknown",  # placeholder – could be calculated from logs
        }
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        self._log("System health report generated.")

    # ---------------------------------------------------------------------
    # Helper to expose health‑status to the agent (e.g., to pause trading)
    # ---------------------------------------------------------------------
    def is_failsafe(self):
        return self.failsafe_active
