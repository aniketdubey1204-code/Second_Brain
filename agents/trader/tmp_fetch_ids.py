import requests, json, sys
base='https://api.delta.exchange/v2'
resp=requests.get(f'{base}/products')
resp.raise_for_status()
data=resp.json()
for p in data['result'][:20]:
    print(p['symbol'], p['id'])
