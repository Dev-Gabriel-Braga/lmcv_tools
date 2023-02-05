from .section import Section

class Node(Section):
   def __init__(self):
      self.dat_template = '\n%NODE\n{}\n\n%NODE.COORD\n{}\n{}'
      self.inp_keyword = '\*Node'
   
   def convert(self, inp_data: str) -> str:
      # Buscando Seção dos Nodes nos Dados .inp
      inp_nodes, _ = self.find_data(inp_data)

      # Tratando Dados Encontrados
      inp_nodes = inp_nodes.strip()
      inp_nodes = inp_nodes.split('\n')
      
      # Formatando as Coordenadas de Cada Node
      n_nodes = len(inp_nodes)
      coords = ''
      for node in inp_nodes:
         info = list(map(float, node.split(',')))
         coords += f'{int(info[0])}   {info[1]}   {info[2]}   {info[3]}\n'

      return self.dat_template.format(n_nodes, n_nodes, coords)