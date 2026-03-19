$env:PYTHONPATH='trading_bot'; python - <<'PY'
import sys, os
sys.path.append('trading_bot')
from agent import TradingAgent
TradingAgent().run_cycle()
PY