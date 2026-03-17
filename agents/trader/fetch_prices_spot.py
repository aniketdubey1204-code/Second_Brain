import requests
symbols=['BTCUSD','ETHUSD','SOLUSD']
base='https://api.india.delta.exchange/v2/tickers/'
for s in symbols:
    r=requests.get(base+s, timeout=10)
    if r.ok:
        data=r.json().get('result',{})
        price=data.get('spot_price')
        print(f"{s}: {price}")
    else:
        print(f"{s}: error {r.status_code}")
