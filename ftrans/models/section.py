import re

class Section:
   # Padrão a ser seguido nas Sub-Classes
   def __init__(self):
      self.dat_template = ''
      self.dat_section = ''
      self.inp_keyword = ''
      self.inp_format = ''
      self.inp_section = ''
      self.matches = None
      self.raw_data = []
   
   def find_inp_section(self, inp_data: str):
      # Buscando a Localização da Seção
      match_1 = re.search(self.inp_keyword, inp_data)
      index_start = match_1.end()

      match_2 = re.search('\*', inp_data[index_start:])
      index_end = index_start + match_2.start()

      self.inp_section = inp_data[index_start:index_end]
      self.matches = [match_1, match_2]
   
   def extract_raw_data(self):
      self.raw_data = re.findall(self.inp_format, self.inp_section)

   # Deve ser Implementado nas Sub-Classes
   def build_dat_section(self):
      pass
   
   def convert(self, inp_data: str) -> str:
      # Buscando Seção nos Dados .inp
      self.find_inp_section(inp_data)

      # Tratando os Dados Extraidos e Constrindo Seção .dat
      self.build_dat_section()

      return self.dat_section
