from .section import Section

class Node(Section):
   def __init__(self):
      super().__init__()
      self.dat_template = '\n%NODE\n{}\n\n%NODE.COORD\n{}\n{}'
      self.inp_keyword = '\*Node'
      self.inp_format = '(\d+),\s*(-?\d+.\d*),\s*(-?\d+.\d*),\s*(-?\d+.\d*)'
   
   def build_dat_section(self):
      # Extraindo Dados da Seção inp
      self.extract_raw_data()

      # Tratando Dados e Construindo a Seção dat
      n_nodes = len(self.raw_data)
      coords = ''

      for coord in self.raw_data:
         info = list(map(float, coord))
         info[0] = int(info[0])
         coords += '{0}   {1}   {2}   {3}\n'.format(*info)
      
      self.dat_section = self.dat_template.format(n_nodes, n_nodes, coords)
