import os
from binance import Client
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
# Test 1
try:
    client.ping()
    print('PING: OK')
except Exception as e:
    print(f'PING FAILED: {e}')
# Test 2
try:
    price = client.get_symbol_ticker(symbol='BTCUSDT')
    print(f'PRICE: {price}')
except Exception as e:
    print(f'PRICE FAILED: {e}')
# Test 3
try:
    candles = client.get_klines(symbol='BTCUSDT', interval='4h', limit=5)
    print(f'CANDLES: Got {len(candles)} candles')
    print(f'Latest close: {candles[-1][4]}')
except Exception as e:
    print(f'CANDLES FAILED: {e}')
