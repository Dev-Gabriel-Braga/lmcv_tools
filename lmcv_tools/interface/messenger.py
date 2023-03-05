from sys import exit

# Funções Globais
def show(message: str):
   print(message)

def error(message: str, name: str = 'CommandError', help: bool = False):
   # Exibindo Mensagem de Erro
   print(f'{name}: {message}')

   # Terminando Processo (Se não Estiver no Modo Interativo)
   from .core import in_interactive_mode
   if not in_interactive_mode:
      exit(1)
