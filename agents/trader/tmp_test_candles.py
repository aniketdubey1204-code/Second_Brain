import requests, pandas as pd, datetime
symbol='BTCUSD'
resolution='15m'
count=10
end=int(datetime.datetime.now().timestamp())
if resolution=='5m':
    start=end-count*5*60
elif resolution=='15m':
    start=end-count*15*60
elif resolution=='1h':
    start=end-count*60*60
else:
    start=end-count*15*60
url='https://api.india.delta.exchange/v2/history/candles'
params={'symbol':symbol,'resolution':resolution,'start':str(start),'end':str(end)}
resp=requests.get(url,params=params,timeout=10)
print('status',resp.status_code)
print(resp.text[:500])
