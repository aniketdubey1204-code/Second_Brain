import os, sys, json
from binance import Client

def load_config():
    return {
        "api_key": os.getenv('BINANCE_API_KEY'),
        "api_secret": os.getenv('BINANCE_API_SECRET')
    }

def execute_order(params):
    cfg = load_config()
    client = Client(cfg['api_key'], cfg['api_secret'])
    symbol = params['symbol']
    side = params['side']
    qty = params['quantity']
    order = client.create_order(
        symbol=symbol,
        side=side,
        type='MARKET',
        quantity=qty
    )
    return order

def main():
    # Expect JSON on stdin with trade parameters
    data = json.load(sys.stdin)
    result = execute_order(data)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
