"""Scheduler module.
Orchestrates periodic tasks: market data polling, strategy execution, optimizer runs,
and daily report generation.
Uses simple ``while True`` loop with ``time.sleep``; can be replaced with APScheduler later.
"""
import time
import threading
from datetime import datetime
from typing import Callable

class Scheduler:
    def __init__(self):
        self.tasks = []  # list of (interval_seconds, callable, last_run)

    def add_task(self, interval_seconds: int, func: Callable, name: str = None):
        self.tasks.append({'interval': interval_seconds, 'func': func, 'last': 0, 'name': name or func.__name__})

    def start(self, daemon: bool = True):
        def run_loop():
            while True:
                now = time.time()
                for t in self.tasks:
                    if now - t['last'] >= t['interval']:
                        try:
                            t['func']()
                        except Exception as e:
                            print(f"[Scheduler] Task {t['name']} raised: {e}")
                        t['last'] = now
                time.sleep(0.5)
        thread = threading.Thread(target=run_loop, daemon=daemon)
        thread.start()
        return thread
