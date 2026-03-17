import json, datetime, collections, sys, os

trades_path = r'D:\OpenClaw\workspace\second-brain\trading_bot\logs\trades.json'
with open(trades_path, 'r') as f:
    data = json.load(f)
# Get last 10 trades
last10 = data[-10:]
win_counts = collections.Counter()
total_counts = collections.Counter()
time_profit = collections.Counter()
loss_trades = []
for t in last10:
    strat = t.get('reason')
    pnl = t.get('pnl', 0)
    total_counts[strat] += 1
    if pnl > 0:
        win_counts[strat] += 1
    else:
        loss_trades.append(t)
    # parse timestamp
    dt = datetime.datetime.fromisoformat(t['timestamp'].replace('Z', '+00:00'))
    hour = dt.hour
    time_profit[hour] += pnl
# win rates per strategy
win_rates = {k: win_counts[k] / total_counts[k] for k in total_counts}
best_strategy = max(win_rates, key=win_rates.get) if win_rates else None
best_win_rate = win_rates.get(best_strategy)
false_symbols = list({t['symbol'] for t in loss_trades})
best_hour = max(time_profit, key=time_profit.get) if time_profit else None
result = {
    'best_strategy': best_strategy,
    'best_win_rate': round(best_win_rate, 3) if best_win_rate is not None else None,
    'false_symbols': false_symbols,
    'best_hour_utc': best_hour,
    'loss_trades': loss_trades,
}
print(json.dumps(result, indent=2))
