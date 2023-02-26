from sys import exit

# Funções Globais
def show(message: str):
   print(message)

def error(message: str):
   print(f'ERROR: {message}')
   exit(1)
