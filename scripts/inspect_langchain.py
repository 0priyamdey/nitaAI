import importlib, pkgutil
import langchain
print('langchain package location:', langchain.__file__)
print('top-level attrs:', [a for a in dir(langchain) if not a.startswith('_')])
print('\nSubmodules found:')
for finder, name, ispkg in pkgutil.iter_modules(langchain.__path__):
    print(' -', name, 'pkg' if ispkg else 'mod')
