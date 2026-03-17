import requests, pandas as pd, json
url='https://api.india.delta.exchange/v2/history/candles'
params={'symbol':'BTCUSD','resolution':'15m','count':100}
r=requests.get(url, params=params, timeout=10)
print('status', r.status_code)
js=r.json()
print('keys', js.keys())
data=js.get('result', [])
print('len', len(data))
if data:
    df=pd.DataFrame(data)
    print(df.head())
