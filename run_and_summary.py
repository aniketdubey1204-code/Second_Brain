from trading_bot.agent import TradingAgent
import time

agent = TradingAgent()
# Run a few cycles
for i in range(3):
    agent.run_cycle()
    time.sleep(0.5)
# Print portfolio summary
print('Portfolio Summary:')
print(agent.portfolio.summary())
