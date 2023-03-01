from sys import exit

# Funções Globais
def show(message: str):
   print(message)

def error(message: str, context: str = 'Syntax', help: bool = False):
   if help:
      message += '\nPlease, use help command (lmcv_tools help).'
   print(f'{context} Error: {message}')
   exit(1)
