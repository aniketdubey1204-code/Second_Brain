from trading_bot.agent import TradingAgent

if __name__ == '__main__':
    agent = TradingAgent()
    agent.run_cycle()
    print('One cycle completed')
