import requests, json
url='https://api.india.delta.exchange/v2/tickers/BTCUSD'
r=requests.get(url, timeout=10)
print(r.status_code)
print(r.text)
