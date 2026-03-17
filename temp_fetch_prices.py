import requests, json, sys
url='https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd'
try:
    r=requests.get(url, timeout=10)
    r.raise_for_status()
    data=r.json()
    print(json.dumps(data))
except Exception as e:
    print('Error:', e, file=sys.stderr)
