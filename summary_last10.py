import json, datetime, collections, sys
path = r'D:\OpenClaw\workspace\second-brain\trading_bot\logs\trades.json'
with open(path) as f:
    data = json.load(f)
last10 = data[-10:]
win_counts = collections.Counter()
total_counts = collections.Counter()
time_counts = collections.Counter()
loss_trades = []
for t in last10:
    strat = t.get('reason')
    pnl = t.get('pnl',0)
    total_counts[strat] += 1
    if pnl > 0:
        win_counts[strat] += 1
    else:
        loss_trades.append(t)
    dt = datetime.datetime.fromisoformat(t['timestamp'].replace('Z','+00:00'))
    hour = dt.hour
    time_counts[hour] += pnl
win_rates = {k: win_counts[k]/total_counts[k] for k in total_counts}
best_strategy = max(win_rates, key=win_rates.get) if win_rates else None
false_symbols = list({t['symbol'] for t in loss_trades})
best_hour = max(time_counts, key=time_counts.get) if time_counts else None
print(json.dumps({
    "best_strategy": best_strategy,
    "win_rate": win_rates.get(best_strategy),
    "false_symbols": false_symbols,
    "best_hour": best_hour,
    "loss_trades": loss_trades
}, indent=2))