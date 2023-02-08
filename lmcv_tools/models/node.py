from .entity import Entity

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
