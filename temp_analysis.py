import json, sys
path='D:/OpenClaw/workspace/second-brain/master_trading_battle.json'
lines=open(path,encoding='utf-8').read().splitlines()
closed=[]
for line in reversed(lines):
    try:
        obj=json.loads(line)
    except:
        continue
    if obj.get('cumulative_pnl',0)!=0 and obj.get('status')!='ACTIVE':
        closed.append(obj)
        if len(closed)>=10:
            break
print(json.dumps(closed, indent=2))
