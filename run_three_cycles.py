import time
from trading_bot.agent import TradingAgent

agent = TradingAgent()
for i in range(3):
    print(f'--- Cycle {i+1} ---')
    agent.run_cycle()
    time.sleep(1)
