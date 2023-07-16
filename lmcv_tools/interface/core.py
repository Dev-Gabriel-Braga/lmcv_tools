from . import messenger, searcher
from ..models.custom_errors import CommandError

# Constantes Globais
version = '0.0.9'
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
help_messages = searcher.get_database('help_messages')

# Funções Pré-processamento de Comandos
def show_version(args: list[str] = []):
   messenger.show(f'LMCV Tools - v{version}')

def show_help(args: list[str] = []):   
   # Coletando Dados da Mensagem de Ajuda com base nos Argumentos.
   try:
      command = 'default' if len(args) == 0 else args[0]
      message = help_messages[command]
   except KeyError:
      raise CommandError(f'There is no command named "{command}".')
   
   # Gerando Mensagem
   messenger.show(f"Usage: {message['usage']}\n")
   for title, points in message['topics'].items():
      # Exibindo Título do Tópico
      messenger.show(f"{title}:")

      # Determinando Largura Máxima da Primera Coluna dos Pontos do Tópico
      max_width = 0
      for name in points.keys():
         len_name = len(name)
         if len_name > max_width:
            max_width = len_name
      max_width += 3

      # Exibindo Pontos do Tópico
      for name, description in points.items():
         # Dividindo Descrição em Linhas
         lines = description.split('. ')

         # Exibindo a Primeira Linha
         firt_line = f"\n{name:<{max_width}}|   {lines[0]}."
         messenger.show(firt_line)

         # Exibindo Demais Linhas
         for line in lines[1:]:
            # Quebrando Linhas para Terem 80 Caracteres
            max_size = 79 - (max_width + 5)
            offset = ' ' * max_width
            while len(line) > max_size:
               crop_index = line[0:max_size].rfind(' ')
               cropped_line = line[0:crop_index]
               line = line[crop_index + 1:]
               messenger.show(f"{offset}|   {cropped_line}")
            messenger.show(f"{offset}|   {line}.")

      # Quebra de Linha Final do Tópico
      messenger.show('')

def pre_translate(args: list[str]):
   from ..commands import translate

   # Verificando Path do Input
   try:
      input_path = args[0]
   except IndexError:
      raise CommandError('An Input File Path is required.')

   # Verificando Extensão do Output
   try:
      if 'to' != args[1]:
         raise CommandError('"to" keyword after Input File Path is required.')
   except IndexError:
      raise CommandError('"to" keyword after Input File Path is required.')
   try:
      output_extension = args[2]
   except IndexError:
      raise CommandError('An Extension for Output File after "to" keyword is required.')
   
   # Iniciando Tradução
   translate.start(input_path, output_extension, args[3:])

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

def pre_generate(args: list[str]):
   from ..commands import generate
   
   # Verificando se um Artefato foi Dado
   if len(args) == 0:
      raise CommandError('An Artifact must be given.', help=True)

   # Iniciando Comando
   artifact = args[0]
   generate.start(artifact, args[1:])

# Relação Comando/Função
commands = {
   'version': show_version,
   'help': show_help,
   'translate': pre_translate,
   'extract': pre_extract,
   'generate': pre_generate
}

# Funções de Inicialização
def execute_command(name: str, args: list[str]):
   # Encapsulando Execução para Tratamento Padrão de Erros
   try:
      # Tentando Identificar o Comando
      try:
         command_function = commands[name]
      except KeyError:
         raise CommandError('Unknown command.', help=True)

      # Executando Comando
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
      if len(args) == 0:
         continue
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
