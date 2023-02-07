import re

class Entity:
   # Padrão a ser seguido nas Sub-Classes
   def __init__(self):
      self.dat_template = ''
      self.dat_entity = ''
      self.inp_keyword = ''
      self.inp_format = ''
      self.inp_entity = ''
      self.matches = None
      self.raw_data = []
   
   def find_inp_entity(self, inp_data: str):
      # Buscando a Localização da Entidade
      match_1 = re.search(self.inp_keyword, inp_data)
      index_start = match_1.end()

      match_2 = re.search('\*', inp_data[index_start:])
      index_end = index_start + match_2.start()

      self.inp_entity = inp_data[index_start:index_end]
      self.matches = [match_1, match_2]
   
   def extract_raw_data(self):
      self.raw_data = re.findall(self.inp_format, self.inp_entity)

   # Deve ser Implementado nas Sub-Classes
   def build_dat_entity(self):
      pass
   
   def convert(self, inp_data: str) -> str:
      # Buscando Seção nos Dados .inp
      self.find_inp_entity(inp_data)

      # Tratando os Dados Extraidos e Constrindo Seção .dat
      self.build_dat_entity()

      return self.dat_entity
