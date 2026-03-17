import requests, json, pandas as pd
url='https://api.india.delta.exchange/v2/history/candles'
params={'symbol':'BTCUSD','resolution':'15m','count':100}
resp=requests.get(url, params=params, timeout=10)
print('Status', resp.status_code)
print('Response', resp.text[:200])
