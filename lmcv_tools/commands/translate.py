from ..interface import messenger
from ..models.translation_components import Node, Element

# Objetos Globais
node = Node()
element = Element()

# Funções Globais
def read_inp_file(inp_path: str) -> str:
   try:
      inp_file = open(inp_path, 'r')
      inp_data = inp_file.read()
   except OSError:
      messenger.error('Could not open the .inp file.')
   inp_file.close()
   return inp_data

def write_dat_file(dat_path: str, dat_data: str):
   try:
      dat_file = open(dat_path, 'w')
      dat_file.write(dat_data)
   except OSError:
      messenger.error('Could not create the .dat file.')
   dat_file.close()

def convert_syntax(inp_data: str):
   # Iniciando Estrutura do .dat
   dat_data = '%HEADER\n'

   # Convertendo Nodes
   dat_data += node.convert(inp_data)

   # Convertendo Elementos
   dat_data += element.convert(inp_data)

   # Finalizando Estrutura do .dat
   dat_data += '\n%END'

   return dat_data

def start(inp_path: str, dat_path: str):
   # Lendo Arquivo .inp
   inp_data = read_inp_file(inp_path)

   # Convertendo Sintaxe dos Dados do .inp
   dat_data = convert_syntax(inp_data)

   # Escrevendo Tradução no .dat
   write_dat_file(dat_path, dat_data)
