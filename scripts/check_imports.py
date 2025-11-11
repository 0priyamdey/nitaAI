import importlib

mods = [
    'langchain.chains',
    'langchain.chains.combine_documents',
    'langchain_core.prompts',
    'langchain_community.vectorstores',
    'langchain_community.embeddings',
    'langchain_openai'
]

for m in mods:
    try:
        importlib.import_module(m)
        print(m, 'OK')
    except Exception as e:
        print(m, 'ERROR', repr(e))
