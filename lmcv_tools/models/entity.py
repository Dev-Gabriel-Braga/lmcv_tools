import re

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
