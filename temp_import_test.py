import traceback
try:
    import trading_bot.agent as ta
    print('Import succeeded')
except Exception as e:
    traceback.print_exc()
