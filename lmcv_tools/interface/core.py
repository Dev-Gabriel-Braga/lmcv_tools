from ..controllers.translator import Translator
from .messenger import Messenger

class Core:
   # Atributos Estáticos
   version = '0.0.2'

   # Métodos Estáticos
   @staticmethod
   def show_version():
      Messenger.show(f'LMCV Tools - v{Core.version}')
   
   @staticmethod
   def show_welcome():
      Core.show_version()
      message = '''
LMCV Tools is a command line tool that provides a series of useful functionali-
ties for the day-to-day simulations of the "Laboratório de Mecânica Computacio-
nal e Visualização" of the "Universidade Federal do Ceará" (UFC). To get help, 
use the command bellow:

[lmcv_tools help]'''
      Messenger.show(message)

   @staticmethod
   def show_help():
      Core.show_version()
      message = '''
Usage: lmcv_tools [command] [args]

Possible commands:

version     |   Show version.

help        |   Show help text.

translate   |   Translate .inp file in .dat file.
            |   Example: lmcv_tools translate [path/to/.inp] [path/to/.dat]
            |   If the path to the .dat is not given, it will be the same as the
            |   .inp file.'''
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
      else:
         command_name = args[0]
         if command_name == 'version':
            Core.show_version()
         elif command_name == 'help':
            Core.show_help()
         elif command_name == 'translate':
            Core.translate(args[1:])
         else:
            Messenger.error('Unknown command. Please, read help text (lmcv_tools help).')
