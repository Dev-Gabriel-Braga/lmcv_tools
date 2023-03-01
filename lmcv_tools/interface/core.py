from . import messenger

# Constantes Globais
version = '0.0.3'
message_welcome = '''
LMCV Tools is a command line tool that provides a series of useful functionali-
ties for the day-to-day simulations of the "Laboratório de Mecânica Computacio-
nal e Visualização" of the "Universidade Federal do Ceará" (UFC). To get help, 
use the command bellow:

[lmcv_tools help]
'''
message_help = '''
Usage: lmcv_tools [command] [args]

Possible commands:

version     |   Show version.

help        |   Show help text.

translate   |   Translate .inp file in .dat file.
            |   Example: lmcv_tools translate [path/to/.inp] [path/to/.dat]
            |   If the path to the .dat is not given, it will be the same as the
            |   .inp file.
'''

# Funções Globais
def show_version():
   messenger.show(f'LMCV Tools - v{version}')

def show_welcome():
   show_version()
   messenger.show(message_welcome)

def show_help():
   show_version()
   messenger.show(message_help)

def pre_translate(file_paths: list[str]):
   from ..commands import translate

   # Verificando Path do .inp
   try:
      inp_path = file_paths[0]
   except IndexError:
      messenger.error('The Path to .inp file is required.')

   # Verificando Path do .dat
   try:
      dat_path = file_paths[1]
   except IndexError:
      dat_path = inp_path[:-3] + 'dat'
   
   # Traduzindo Arquivo .inp
   translate.start(inp_path, dat_path)

def start(args: list[str]):
   # Tratando Argumentos
   try:
      if len(args) == 0:
         show_welcome()
      else:
         command_name = args[0]
         if command_name == 'version':
            show_version()
         elif command_name == 'help':
            show_help()
         elif command_name == 'translate':
            pre_translate(args[1:])
         else:
            messenger.error('Unknown command.', help=True)
   except Exception as exc:
      # Exibindo Mensagem de Erro com o Contexto da Exceção
      context = exc.args[0]
      message = ' ' + exc.args[1] if len(exc.args) > 1 else 'Something Wrong.'
      messenger.error(message, context)
