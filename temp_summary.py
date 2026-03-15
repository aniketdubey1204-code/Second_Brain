import json, sys
path = r'D:\OpenClaw\workspace\second-brain\trading_bot\logs\trades.json'
with open(path) as f:
    data = json.load(f)

total = sum(t.get('pnl',0) for t in data)
counts = {}
for t in data:
    sym = t.get('symbol','')
    counts[sym] = counts.get(sym,0)+1
print('Trades:', len(data))
print('Total P&L:', total)
for sym,cnt in counts.items():
    print(sym, cnt)
