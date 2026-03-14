import importlib, sys
mods = ['pandas','numpy','requests','yaml']
for m in mods:
    try:
        importlib.import_module(m)
        print(m, 'OK')
    except Exception as e:
        print(m, 'FAIL', e)
forb = ['pandas_ta','ta','numba']
for f in forb:
    try:
        importlib.import_module(f)
        print(f, 'UNEXPECTED')
    except Exception:
        print(f, 'NOT present')
