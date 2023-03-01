from ..interface import filer
from ..models.translation_entities import (
   Node, 
   Element
)

# Funções Globais
def translate(inp_data: str):
   # Instanciando Objetos
   node = Node()
   element = Element()

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
   inp_data = filer.read(inp_path)

   # Convertendo Sintaxe dos Dados do .inp
   dat_data = translate(inp_data)

   # Escrevendo Tradução no .dat
   filer.write(dat_path, dat_data)
