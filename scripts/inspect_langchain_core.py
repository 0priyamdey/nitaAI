import importlib

modules = [
    'langchain_core.chains',
    'langchain_core.chains.combine_documents',
]

for m in modules:
    try:
        mod = importlib.import_module(m)
        print(m, 'OK')
        names = [n for n in dir(mod) if 'create' in n.lower() or 'chain' in n.lower()]
        print('matches:', names[:50])
    except Exception as e:
        print(m, 'ERROR', repr(e))
