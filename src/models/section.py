import re

class Section:
   def __init__(self):
      self.dat_template = ''
      self.inp_keyword = ''
   
   def find_data(self, inp_data: str):
      # Buscando a Localização da Seção
      match_1 = re.search(self.inp_keyword, inp_data)
      index_start = match_1.end()

      match_2 = re.search('\*', inp_data[index_start:])
      index_end = index_start + match_2.start()

      return inp_data[index_start:index_end], [match_1, match_2]
   
   def convert(self, inp_data: str):
      pass