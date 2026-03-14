import traceback
from trading_bot.agent import TradingAgent
try:
    TradingAgent().run_cycle()
except Exception:
    traceback.print_exc()
