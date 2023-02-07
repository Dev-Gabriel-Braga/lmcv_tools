from .section import Section
from ..interface.searcher import Searcher
from ..interface.messenger import Messenger

class Element(Section):
   def __init__(self):
      super().__init__()
      self.dat_template = '\n%ELEMENT\n{}\n\n%ELEMENT.{}\n{}\n{}'
      self.inp_keyword = '\*Element, type=(.*)'
      self.element_relations = Searcher.get_database('element_relations')

   def build_dat_section(self):
      # Determinando Tipo dos Elementos
      inp_element_type = self.matches[0].groups()[0]

      # Relacionando Elementos inp com Elementos dat
      try:
         dat_element_type = self.element_relations['inp_to_dat'][inp_element_type]
         dat_reformat = self.element_relations['dat_reformat'][dat_element_type]
         self.inp_format = self.element_relations['inp_format'][inp_element_type]
      except KeyError:
         Messenger.error(f'Element {inp_element_type} in .inp file is not supported in this version.')

      # Extraindo Dados da Seção inp
      self.extract_raw_data()

      # Tratando Dados e Construindo a Seção dat
      n_elements = len(self.raw_data)
      description = ''

      for element in self.raw_data:
         info = list(map(int, element))
         description += dat_reformat.format(*info) + '\n'

      self.dat_section = self.dat_template.format(
         n_elements,
         dat_element_type,
         n_elements,
         description
      )
