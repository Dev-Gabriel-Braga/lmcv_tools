from . import messenger
from ..models.custom_errors import CommandError

# Constantes Globais
version = '0.0.3'
in_interactive_mode = False
message_welcome = '''
LMCV Tools is a command line tool that provides a series of useful functionali-
ties for the day-to-day simulations of the "Laboratório de Mecânica Computacio-
nal e Visualização" of the "Universidade Federal do Ceará" (UFC). 

Since a command was not typed, interactive mode was started. Here, you can type
multiple commands in sequence interactively:

To get help | type the command "help"
To exit     | type the command "exit"
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

extract     |   Extract attributes from .pos file to CSV format.
            |   Example: lmcv_tools extract [attributes] from [path/to/.pos]
            |   Additional Syntaxes:
            |   [...] where [condition]
            |   [...] to [path/to/.csv]
'''

# Funções Pré-processamento de Comandos
def show_version(args: list[str] = []):
   messenger.show(f'LMCV Tools - v{version}')

def show_help(args: list[str] = []):
   show_version()
   messenger.show(message_help)

def pre_translate(file_paths: list[str]):
   from ..commands import translate

   # Verificando Path do .inp
   try:
      inp_path = file_paths[0]
   except IndexError:
      raise CommandError('The Path to .inp file is required.')

   # Verificando Path do .dat
   try:
      dat_path = file_paths[1]
   except IndexError:
      dat_path = inp_path[:-3] + 'dat'
   
   # Traduzindo Arquivo .inp
   translate.start(inp_path, dat_path)

def pre_extract(terms: list[str]):
   from ..commands import extract

   # Verificando Sintaxe Básica da Sentença
   if 'from' not in terms:
      raise CommandError('The keyword "from" is required.', help=True)
   
   # Verificando se ao menos 1 Atributo foi fornecido
   index = terms.index('from')
   attributes = terms[:index]
   if len(attributes) == 0:
      raise CommandError('At least one attribute before "from" is required.')

   # Verificando se o Path do Arquivo .pos foi fornecido
   try:
      pos_path = terms[index + 1]
   except IndexError:
      raise CommandError('The path to .pos file after "from" is required.')
   
   # Verificando se um Path para o .csv foi fornecido
   csv_path = pos_path[:-3] + 'csv'
   index_to = 0
   if 'to' in terms[index + 1:]:
      index_to = terms.index('to')
      try:
         csv_path = terms[index_to + 1]
      except IndexError:
         raise CommandError('The Syntax "to [path/to/.csv]" is optional, but it is incomplete.')
   
   # Verificando se uma Condição foi fornecida
   condition = None
   if 'where' in terms[index + 1:]:
      index_where = terms.index('where')
      if index_to > index_where:
         condition = terms[index_where + 1:index_to]
      else:
         condition = terms[index_where + 1:]
      if len(condition) == 0:
         raise CommandError('The Syntax "where [condition]" is optional, but it is incomplete.')
      condition = ' '.join(condition)

   # Extraindo Itens do Arquivo .pos
   extract.start(attributes, pos_path, condition, csv_path)

# Relação Comando/Função
commands = {
   'version': show_version,
   'help': show_help,
   'translate': pre_translate,
   'extract': pre_extract,
}

# Funções de Inicialização
def execute_command(name: str, args: list[str]):
   # Tentando Identificar o Comando
   try:
      command_function = commands[name]
   except KeyError:
      raise CommandError('Unknown command.', help=True)
   
   # Tentando Executar o Comando
   try:
      command_function(args)
   except Exception as exc:
      # Exibindo Mensagem de Erro com o Contexto da Exceção
      name = exc.__class__.__name__
      message = exc.args[0]
      messenger.error(message, name)

def show_welcome():
   show_version()
   messenger.show(message_welcome)

def start_interactive_mode():
   # Informando que o Modo Interativo foi Iniciado
   global in_interactive_mode
   in_interactive_mode = True

   # Exibindo Mensagem de Boas-Vindas
   show_welcome()

   # Iniciando Loop
   while True:
      # Lendo Argumentos
      args = input('>> ').split()

      # Executando Comando
      command_name = args[0]
      if command_name == 'exit':
         break
      execute_command(command_name, args[1:])

def start(args: list[str]):
   # Iniciando Modo Interativo (Se não houver Argumentos)
   if len(args) == 0:
      start_interactive_mode()

   # Executando Comando Único
   else:
      execute_command(args[0], args[1:])
