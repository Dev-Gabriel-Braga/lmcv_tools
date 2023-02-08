from .entity import Entity
from ..interface.searcher import Searcher
from ..interface.messenger import Messenger

class Element(Entity):
   def __init__(self):
      super().__init__()
      self.dat_template = '\n%ELEMENT\n{}\n\n%ELEMENT.{}\n{}\n{}'
      self.inp_keyword = '\*Element, type=(.*)'
      self.element_relations = Searcher.get_database('element_relations')

   def build_dat_entity(self):
      # Determinando Tipo dos Elementos
      inp_element_type = self.matches[0].groups()[0]

      # Relacionando Elementos inp com Elementos dat
      try:
         dat_element_type = self.element_relations['inp_to_dat'][inp_element_type]
         dat_reference = self.element_relations['dat_reference'][dat_element_type]
         int_id = '(\d+)'
         node_id = ',\s*' + int_id
         self.inp_format = int_id + dat_reference['n_nodes'] * node_id
      except KeyError:
         Messenger.error(f'Element {inp_element_type} in .inp file is not supported in this version.')

      # Extraindo Dados da Seção inp
      self.extract_raw_data()

      # Tratando Dados e Construindo a Seção dat
      n_elements = len(self.raw_data)
      span = len(str(n_elements))
      description = ''

      for element in self.raw_data:
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

      self.dat_entity = self.dat_template.format(
         n_elements,
         dat_element_type,
         n_elements,
         description
      )
