import requests, json
base='https://api.delta.exchange/v2'
resp=requests.get(f'{base}/products')
resp.raise_for_status()
for p in resp.json()['result']:
    if 'BTC' in p['symbol']:
        print(p['symbol'], p['id'])
