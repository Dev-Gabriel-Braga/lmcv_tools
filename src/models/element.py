from .section import Section

class Element(Section):
   def __init__(self):
      self.dat_template = '\n%ELEMENT\n{}\n\n%ELEMENT.{}\n{}\n{}'
      self.inp_keyword = '\*Element, type=(.*)'

      # Definindo Correspondência entre Elementos inp e Elementos dat
      self.types = {
         'C3D8': [
            'BRICK8',
            '{0}   1  1   {5}   {1}   {2}   {6}   {8}   {4}   {3}   {7}\n'
         ]
      }
   
   def convert(self, inp_data: str) -> str:
      # Buscando Seção dos Elementos nos Dados .inp
      inp_elements, matches = self.find_data(inp_data)

      # Tratando Dados Encontrados
      inp_elements = inp_elements.strip()
      inp_elements = inp_elements.split('\n')
      
      # Determinando Tipo dos Elementos
      inp_element_type = matches[0].groups()[0]

      # Relacionando Elementos inp com Elementos dat
      try:
         dat_element_type, line = self.types[inp_element_type]
      except KeyError:
         print(f'Element {inp_element_type} in .inp file is not supported in this version.')

      # Formatando Informações de Cada Elemento
      n_elements = len(inp_elements)
      description = ''
      for element in inp_elements:
         info = list(map(int, element.split(',')))
         description += line.format(*info)

      return self.dat_template.format(
         n_elements,
         dat_element_type,
         n_elements,
         description
      )
