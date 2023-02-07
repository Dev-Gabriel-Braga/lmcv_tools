from .entity import Entity

class Node(Entity):
   def __init__(self):
      super().__init__()
      self.dat_template = '\n%NODE\n{}\n\n%NODE.COORD\n{}\n{}'
      self.inp_keyword = '\*Node'
      n = '(-?\d+.\d*e?-?\+?\d*)'
      self.inp_format = f'(\d+),\s*{n},\s*{n},\s*{n}'
   
   def build_dat_entity(self):
      # Extraindo Dados da Seção inp
      self.extract_raw_data()

      # Tratando Dados e Construindo a Seção dat
      n_nodes = len(self.raw_data)
      coords = ''

      for coord in self.raw_data:
         info = list(map(float, coord))
         info[0] = int(info[0])
         coords += '{0}   {1}   {2}   {3}\n'.format(*info)
      
      self.dat_entity = self.dat_template.format(n_nodes, n_nodes, coords)
