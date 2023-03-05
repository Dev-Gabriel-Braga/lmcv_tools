from sys import exit

# Funções Globais
def show(message: str):
   print(message)

def error(message: str, name: str = 'CommandError', help: bool = False):
   if help:
      message += '\nPlease, use help command (lmcv_tools help).'
   print(f'{name}: {message}')
   exit(1)
