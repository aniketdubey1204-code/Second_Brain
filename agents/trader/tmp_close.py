import json, os, sys
sys.path.append('.')
from trader import close_trade, load_json
pos = load_json('open_positions.json')['positions'][0]
print('Before close, positions:', load_json('open_positions.json'))
close_trade(pos, 73995.0, 'Test close')
print('After close, positions:', load_json('open_positions.json'))
