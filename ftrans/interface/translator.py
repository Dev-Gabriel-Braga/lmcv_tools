from .messenger import Messenger
from ..models.node import Node
from ..models.element import Element

class Translator:
   # Atributos Estáticos
   node = Node()
   element = Element()

   # Métodos Estáticos
   @staticmethod
   def read_inp_file(inp_path: str) -> str:
      try:
         inp_file = open(inp_path, 'r')
         inp_data = inp_file.read()
      except OSError:
         Messenger.error('Could not open the .inp file.')
      inp_file.close()
      return inp_data

   @staticmethod
   def write_dat_file(dat_path: str, dat_data: str):
      try:
         dat_file = open(dat_path, 'w')
         dat_file.write(dat_data)
      except OSError:
         Messenger.error('Could not create the .dat file.')
      dat_file.close()

   @staticmethod
   def convert_syntax(inp_data: str):
      # Iniciando Estrutura do .dat
      dat_data = '%HEADER\n'

      # Convertendo Nodes
      dat_data += Translator.node.convert(inp_data)

      # Convertendo Elementos
      dat_data += Translator.element.convert(inp_data)

      # Finalizando Estrutura do .dat
      dat_data += '\n%END'

      return dat_data

   @staticmethod
   def translate(inp_path: str, dat_path: str):
      # Lendo Arquivo .inp
      inp_data = Translator.read_inp_file(inp_path)

      # Convertendo Sintaxe dos Dados do .inp
      dat_data = Translator.convert_syntax(inp_data)

      # Escrevendo Tradução no .dat
      Translator.write_dat_file(dat_path, dat_data)
