import re
from ..interface import messenger, searcher

class Entity:
   # Padrão a ser seguido nas Sub-Classes
   def __init__(self):
      self.dat_template = ''
      self.dat_entity = ''
      self.inp_format = ''
      self.inp_entities = []
   
   def extract_inp_entities(self, inp_data: str):
      self.inp_entities = re.findall(self.inp_format, inp_data)
   
   def extract_raw_data(self, format: str, raw_data: str):
      return re.findall(format, raw_data)

   # Deve ser Implementado nas Sub-Classes
   def build_dat_entity(self):
      pass
   
   def convert(self, inp_data: str) -> str:
      # Buscando Entidade nos Dados .inp
      self.extract_inp_entities(inp_data)

      # Tratando os Dados Extraidos e Constrindo Seção .dat
      self.build_dat_entity()

      return self.dat_entity

class Node(Entity):
   def __init__(self):
      super().__init__()
      self.dat_template = '\n%NODE\n{}\n\n%NODE.COORD\n{}\n{}'
      self.inp_format = '\*Node\n([^*]*)'
   
   def build_dat_entity(self):
      # Extraindo Dados Brutos da Entidade Inp
      entity = self.inp_entities[0]
      n = '(-?\d+.\d*e?-?\+?\d*)'
      format = f'(\d+),\s*{n},\s*{n},\s*{n}'
      nodes = self.extract_raw_data(format, entity)

      # Tratando Dados e Construindo a Seção dat
      n_nodes = len(nodes)
      span = len(str(n_nodes))
      coords = ''

      for node in nodes:
         info = list(map(float, node))
         info[0] = int(info[0])
         offset = span - len(str(info[0]))
         offset = ' ' * offset
         coords += '{0}{4}   {1:+.8e}   {2:+.8e}   {3:+.8e}\n'.format(*info, offset)
      
      self.dat_entity = self.dat_template.format(n_nodes, n_nodes, coords)

class Element(Entity):
   def __init__(self):
      super().__init__()
      self.dat_template = '\n%ELEMENT\n{}\n'
      self.inp_format = '\*Element, type=(.*)\n([^*]*)'
      self.element_relations = searcher.get_database('element_relations')

   def build_dat_entity(self):
      # Analisando Entitades de Elementos Caso a Caso
      total_elements = 0
      sub_template = '\n%ELEMENT.{}\n{}\n{}'
      elements_groups = []

      for entity in self.inp_entities:
         inp_element_type = entity[0]

         # Relacionando Elementos inp com Elementos dat
         try:
            dat_element_type = self.element_relations['inp_to_dat'][inp_element_type]
            dat_reference = self.element_relations['dat_reference'][dat_element_type]
         except KeyError:
            messenger.error(f'Element {inp_element_type} in .inp file is not supported in this version.')

         # Extraindo Dados da Seção inp
         int_id = '(\d+)'
         node_id = ',\s*' + int_id
         format = int_id + dat_reference['n_nodes'] * node_id
         elements = self.extract_raw_data(format, entity[1])

         # Tratando Dados e Construindo a Seção dat
         n_elements = len(elements)
         total_elements += n_elements
         span = len(str(n_elements))
         description = ''

         for element in elements:
            info = list(map(int, element))

            # Inserindo Id do Elemento, Seção e Ordem de Integração
            element_id = info.pop(0)
            offset = span - len(str(element_id))
            offset = ' ' * offset
            description += f'{element_id}{offset}   1  1'

            # Inserindo nova ordem de elementos
            for index in dat_reference['reorder']:
               description += f'   {info[index - 1]}'
            description += '\n'
         
         # Quardando as Informações do Grupo de Elementos
         elements_groups.append((dat_element_type, n_elements, description))

      # Organizando todas as Informações no Template
      self.dat_entity = self.dat_template.format(total_elements)

      for typ, n, desc in elements_groups:
         self.dat_entity += sub_template.format(typ, n, desc)
