import json, os, sys, datetime, subprocess, shlex, time, textwrap

# Helper to run a shell command and capture output
def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}\nstderr: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout.strip()

# Fetch price from Delta Exchange API
def fetch_price(symbol):
    url = f"https://api.delta.exchange/v2/tickers?symbol={symbol}"
    try:
        import urllib.request, json as _json
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = _json.load(resp)
        # data structure: {"result": [{"last": ...}] or similar
        ticker = data.get('result', [{}])[0]
        return float(ticker.get('last') or ticker.get('last_price') or ticker.get('price') or 0)
    except Exception as e:
        print(f"Failed to fetch {symbol}: {e}", file=sys.stderr)
        return None

# Run Tavily search via bundled script
def tavily_search(query, max_results=5):
    # Path to the tavily search script (relative to workspace)
    script_path = os.path.expanduser('D:/OpenClaw/workspace/second-brain/skills/openclaw-tavily-search/scripts/tavily_search.py')
    if not os.path.isfile(script_path):
        print('Tavily script not found', file=sys.stderr)
        return []
    cmd = f"python3 {shlex.quote(script_path)} --query {shlex.quote(query)} --max-results {max_results} --format brave"
    out = run_cmd(cmd)
    if not out:
        return []
    try:
        return json.loads(out).get('results', [])
    except Exception as e:
        print(f'Failed to parse tavily output: {e}', file=sys.stderr)
        return []

def determine_regime(news_items):
    # Simple heuristic: look for bullish keywords
    bullish_keywords = ['bullish', 'rally', 'upward', 'buy', 'pump']
    for item in news_items:
        snippet = (item.get('snippet') or '').lower()
        if any(k in snippet for k in bullish_keywords):
            return 'aggressive'
    return 'neutral'

def log_trade(trade):
    log_path = os.path.join(os.getcwd(), 'trades.log')
    with open(log_path, 'a') as f:
        f.write(json.dumps(trade) + '\n')

def update_positions(position):
    pos_path = os.path.join(os.getcwd(), 'open_positions.json')
    if os.path.isfile(pos_path):
        with open(pos_path, 'r') as f:
            try:
                positions = json.load(f)
            except Exception:
                positions = []
    else:
        positions = []
    positions.append(position)
    with open(pos_path, 'w') as f:
        json.dump(positions, f, indent=2)

def main():
    symbols = {'BTCUSDT': 'BTC', 'ETHUSDT': 'ETH', 'SOLUSDT': 'SOL'}
    prices = {}
    for sym, name in symbols.items():
        p = fetch_price(sym)
        if p is None:
            continue
        prices[name] = p

    if not prices:
        print('No prices fetched', file=sys.stderr)
        return

    # Fetch crypto news via Tavily
    news = tavily_search('latest crypto news whale movements after-hours sentiment', max_results=5)

    regime = determine_regime(news)

    # Simple aggressive condition: regime aggressive and any price > 0
    if regime == 'aggressive':
        # Choose BTC for demo
        asset = 'BTC'
        price = prices.get(asset)
        if price:
            trade = {
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'asset': asset,
                'side': 'buy',
                'quantity': 0.001,  # small paper position
                'price': price,
                'regime': regime,
                'notes': 'Paper trade from market-scan-power cron',
            }
            log_trade(trade)
            position = {
                'asset': asset,
                'quantity': trade['quantity'],
                'entry_price': price,
                'opened_at': trade['timestamp']
            }
            update_positions(position)
            print(f"Executed paper trade: {trade}")
        else:
            print('Price not available for asset', asset, file=sys.stderr)
    else:
        print('Regime neutral, no trade executed')

if __name__ == '__main__':
    main()
