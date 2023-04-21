from ..interface import searcher
import re

class SimulationModel:
   def __init__(self):
      self.nodes = dict()
      self.element_groups = dict()
   
   def add_node(self, ide: int, x: float, y: float, z: float):
      self.nodes[ide] = (x, y, z)
   
   def add_element_group(self, element_type: str):
      self.element_groups[element_type] = dict()

   def add_element(self, element_type: str, ide: int, node_ides: list[float]):
      self.element_groups[element_type][ide] = node_ides

class INP_Interpreter:
   def __init__(self):
      self.model = SimulationModel()
   
   def read_nodes(self, inp_data: str):
      # Identificando Nodes
      keyword_format = '\*Node\n([^*]*)'
      coord = '(-?\d+.\d*e?-?\+?\d*)'
      line_format = f'(\d+),\s*{coord},\s*{coord},\s*{coord}'

      # Inserindo Nodes
      lines_data = re.findall(keyword_format, inp_data)[0]
      nodes = re.findall(line_format, lines_data)
      for node in nodes:
         ide, x, y, z = map(float, node)
         ide = int(ide)
         self.model.add_node(ide, x, y, z)
   
   def read_elements(self, inp_data: str):
      # Identificando Grupos de Elementos
      keyword_format = '\*Element, type=(.*)\n([^*]*)'
      groups_data = re.findall(keyword_format, inp_data)

      # Analisando Cada Grupo
      for element_type, lines_data in groups_data:
         # Identificando Elementos
         n_nodes = searcher.get_database('translation_reference')['inp']['elements'][element_type]['n_nodes']
         int_ide = '(\d+)'
         node_ide = ',\s*' + int_ide
         line_format = int_ide + n_nodes * node_ide
         elements = re.findall(line_format, lines_data)

         # Inserindo Elementos
         self.model.add_element_group(element_type)
         for element in elements:
            ide, *node_ides = map(int, element)
            self.model.add_element(element_type, ide, node_ides)

   def read(self, inp_data: str):
      # Interpretando Nodes
      self.read_nodes(inp_data)

      # Interpretando Elementos
      self.read_elements(inp_data)

class DAT_Interpreter:
   def __init__(self):
      self.model = SimulationModel()
   
   def write_nodes(self) -> str:
      # Parâmetros Iniciais
      n_nodes = len(self.model.nodes)
      span = len(str(n_nodes))
      output = f'\n%NODE\n{n_nodes}\n\n%NODE.COORD\n{n_nodes}\n'

      # Escrevendo Cada Node
      for ide, coords in self.model.nodes.items():
         offset = span - len(str(ide))
         offset = ' ' * offset
         output += '{0}{4}   {1:+.8e}   {2:+.8e}   {3:+.8e}\n'.format(ide, *coords, offset)
      
      return output

   def write_elements(self) -> str:
      # Parâmetros Iniciais
      output = ''
      total_elements = 0
      n_nodes = len(self.model.nodes)
      node_ide_span = len(str(n_nodes))

      # Escrevendo Cada Grupo de Elemento
      for element_type, elements in self.model.element_groups.items():
         n_elements = len(elements)
         total_elements += n_elements
         span = len(str(n_elements))
         output += f'\n%ELEMENT.{element_type}\n{n_elements}\n'

         # Escrevendo Cada Elemento
         for ide, node_ides in elements.items():
            offset = span - len(str(ide))
            offset = ' ' * offset
            node_ides = '   '.join([ f'{nis:>{node_ide_span}}' for nis in node_ides ])
            output += f'{ide}{offset}   1  1   {node_ides}\n'

      output = f'\n%ELEMENT\n{total_elements}\n' + output
      return output

   def write(self) -> str:
      # Inicializando Output
      output = '%HEADER\n'

      # Escrevendo Nodes
      output += self.write_nodes()

      # Escrevendo Elementos
      output += self.write_elements()

      # Finalizando Output
      output += '\n%END'
      
      return output
