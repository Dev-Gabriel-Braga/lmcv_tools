from .translator import Translator
from .messenger import Messenger

class Core:
   # Atributos Estáticos
   version = '0.0.1'

   # Métodos Estáticos
   @staticmethod
   def show_version():
      Messenger.show(f'FAST Translator - v{Core.version}')

   @staticmethod
   def unknown_args():
      Messenger.show('Unknown arguments. Please, read help text (ftrans -h).')
   
   @staticmethod
   def show_welcome():
      Core.show_version()
      message = '''
FAST Translator is a command line tool to translate .inp files created by Abaqus
in .dat files for FAST (Finite element AnalysiS Tool). Use the command bellow to
get help:

[ftrans -h]  or  [ftrans  --help]'''
      Messenger.show(message)

   @staticmethod
   def show_help():
      Core.show_version()
      message = '''
Usage: ftrans [args]

Possible args:

-h  or  --help        |   Show help text.

-v  or  --version     |   Show version.

-t  or  --translate   |   Translate .inp file in .dat file.
                      |   Example: ftrans -t [path/to/.inp] [path/to/.dat]
                      |   If the path to the .dat is not given, it will be the 
                      |   same as the .inp.'''
      Messenger.show(message)

   @staticmethod
   def translate(file_paths: list[str]):
      # Verificando Path do .inp
      try:
         inp_path = file_paths[0]
      except IndexError:
         Messenger.error('The Path to .inp file is required.')

      # Verificando Path do .dat
      try:
         dat_path = file_paths[1]
      except IndexError:
         dat_path = inp_path[:-3] + 'dat'
      
      # Traduzindo Arquivo .inp
      Translator.translate(inp_path, dat_path)

   @staticmethod
   def start(args: list[str]):
      # Tratando Argumentos
      if len(args) == 0:
         Core.show_welcome()
      elif args[0] in ['-h', '--help']:
         Core.show_help()
      elif args[0] in ['-v', '--version']:
         Core.show_version()
      elif args[0] in ['-t', '--translate']:
         Core.translate(args[1:])
      else:
         Core.unknown_args()
