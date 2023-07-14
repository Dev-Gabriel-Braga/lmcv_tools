from ..interface import searcher
from .geometry import bezier_equiv_coord, bernstein_polynomial
import re
from math import floor

class SimulationModel:
   def __init__(self):
      self.nodes = dict()
      self.element_groups = dict()
   
   def add_node(self, ide: int, x: float, y: float, z: float, weight: float = None):
      self.nodes[ide] = self.Node(x, y, z, weight)
   
   def add_element_group(self, ide: int, geometry, theory: str):
      self.element_groups[ide] = self.ElementGroup(geometry, theory)

   def add_element(self, group_ide: int, ide: int, node_ides: list[float]):
      for node_ide in node_ides:
         if node_ide not in self.nodes:
            raise KeyError(f'The Node with ide = {node_ide} does not exist.')
      self.element_groups[group_ide].elements[ide] = node_ides
   
   class Node:
      def __init__(self, x: float, y: float, z: float, weight: float = None):
         self.x = x
         self.y = y
         self.z = z
         self.weight = weight
   
   class ElementGeometry:
      def __init__(self, name: str, grade: int, n_nodes: int):
         self.name = name
         self.grade = grade
         self.n_nodes = n_nodes

   class ElementGroup:
      def __init__(self, geometry, theory: str):
         self.geometry = geometry
         self.theory = theory
         self.elements = dict()

class INP_Interpreter:
   def __init__(self):
      self.model = SimulationModel()
      self.reference = searcher.get_database('translation_reference')['inp']
   
   def read_nodes(self, inp_data: str):
      # Identificando Nodes
      keyword_format = '\*Node\n([^*]*)'
      node = '(-?\d+.\d*e?-?\+?\d*)'
      line_format = f'(\d+),\s*{node},\s*{node},\s*{node}'

      # Inserindo Nodes
      lines_data = re.findall(keyword_format, inp_data)[0]
      nodes = re.findall(line_format, lines_data)
      for node in nodes:
         ide, x, y, z = map(float, node)
         ide = int(ide)
         self.model.add_node(ide, x, y, z)
   
   def read_elements(self, inp_data: str):
      # Identificando Grupos de Elementos
      keyword_format = '\*Element, type=(.*)\n([^*]*)'
      groups_data = re.findall(keyword_format, inp_data)

      # Analisando Cada Grupo
      group_ide = 1
      for element_type, lines_data in groups_data:
         # Identificando Elementos
         try:
            type_info = self.reference['elements'][element_type]
         except KeyError:
            raise KeyError(f'The Element Type "{element_type}" is not supported  for .inp files.')
         int_ide = '(\d+)'
         node_ide = ',\s*' + int_ide
         line_format = int_ide + type_info['n_nodes'] * node_ide
         elements = re.findall(line_format, lines_data)

         # Criando Grupo de Elementos
         geometry = SimulationModel.ElementGeometry(
            name = type_info['geometry'],
            grade = type_info['grade'],
            n_nodes = type_info['n_nodes']
         )
         self.model.add_element_group(group_ide, geometry, type_info.get('theory'))

         # Inserindo Elementos
         for element in elements:
            ide, *node_ides = map(int, element)
            self.model.add_element(group_ide, ide, node_ides)
         
         # Incrementando Ide do Grupo
         group_ide += 1

   def read(self, inp_data: str):
      # Interpretando Nodes
      self.read_nodes(inp_data)

      # Interpretando Elementos
      self.read_elements(inp_data)

class DAT_Interpreter:
   def __init__(self):
      self.model = SimulationModel()
      self.reference = searcher.get_database('translation_reference')['dat']
   
   def read_nodes(self, dat_data: str):
      # Identificando Nodes
      keyword_format = '%NODE\n\d+\n\n%NODE.COORD\n\d+\n([^%]*)'
      node = '([+-]?\d+.\d+e?[+-]?\d*)'
      line_format = f'(\d+)\s+{node}\s+{node}\s+{node}'

      # Inserindo Nodes
      lines_data = re.findall(keyword_format, dat_data)[0]
      nodes = re.findall(line_format, lines_data)
      for node in nodes:
         ide, x, y, z = map(float, node)
         ide = int(ide)
         self.model.add_node(ide, x, y, z)
      
      # Identificando Pesos
      keyword_format = '%CONTROL.POINT.WEIGHT\n\d+\n([^%]*)'
      line_format = f'(\d+)\s+([+-]?\d+.\d+e?[+-]?\d*)'

      # Inserindo Nodes
      lines_data = re.findall(keyword_format, dat_data)
      if lines_data:
         lines_data = lines_data[0]
         weights = re.findall(line_format, lines_data)
         for node_ide, weight in weights:
            node_ide = int(node_ide)
            weight = float(weight)
            if weight == 1.0:
               continue
            self.model.nodes[node_ide].weight = weight

   def read_elements(self, inp_data: str):
      # Identificando Grupos de Elementos
      keyword_format = '%ELEMENT\.(.*)\n\d+\n([^%]*)'
      groups_data = re.findall(keyword_format, inp_data)

      # Analisando Cada Grupo
      group_ide = 1
      for element_type, lines_data in groups_data:
         # Dividindo Tipo e Teoria do Grupo de Elementos
         element_theory = None
         splited = element_type.split('.')
         if len(splited) > 1:
            # Tentando Identificar Teoria de Elemento
            element_theory = splited[0]
            try:
               element_theory = self.reference['theories'][element_theory]
            except KeyError:
               raise KeyError(f'The Element Theory "{element_theory}" is not supported for .dat files.')
            
            # Corrigindo Tipo de Elemento
            element_type = '.'.join(splited[1:])

         # Identificando Elementos
         try:
            type_info = self.reference['elements'][element_type]
         except KeyError:
            raise KeyError(f'The Element Type "{element_type}" is not supported for .dat files.')
         int_ide = '(\d+)'
         node_ide = '\s+' + int_ide
         property_ides = '\s+\d+' * 2

         # Leitura para Triângulos de Bezier
         if type_info['geometry'] == 'BezierTriangle':
            # Identificando Elementos
            property_ides += '\s+\d+\s+(\d+)'
            line_format = int_ide + property_ides + '\s+(.+)'
            elements = re.findall(line_format, lines_data)
            
            # Ides de Grupos Relacionados com o Grau dos Elementos
            grade_to_group = dict()

            # Analisando Cada Elemento
            for ide, grade, node_ides in elements:
               # Tipificando Valores
               ide = int(ide)
               grade = int(grade)
               node_ides = list(map(int, node_ides.split()))

               # Verificando se Grupo com o Grau do Elemento Já Existe
               if grade not in grade_to_group:
                  grade_to_group[grade] = group_ide
                  geometry = SimulationModel.ElementGeometry(
                     name = type_info['geometry'],
                     grade = grade,
                     n_nodes = len(node_ides)
                  )
                  self.model.add_element_group(group_ide, geometry, element_theory)
                  group_ide += 1

               # Inserindo Elementos
               self.model.add_element(grade_to_group[grade], ide, node_ides)

         # Leitura para Elementos Finitos
         else:
            line_format = int_ide + property_ides + type_info['n_nodes'] * node_ide
            elements = re.findall(line_format, lines_data)

            # Criando Grupo de Elementos
            geometry = SimulationModel.ElementGeometry(
               name = type_info['geometry'],
               grade = type_info['grade'],
               n_nodes = type_info['n_nodes']
            )
            self.model.add_element_group(group_ide, geometry, element_theory)

            # Inserindo Elementos
            for element in elements:
               ide, *node_ides = map(int, element)
               self.model.add_element(group_ide, ide, node_ides)
         
         # Incrementando Ide do Grupo
         group_ide += 1

   def read(self, dat_data: str):
      # Interpretando Nodes
      self.read_nodes(dat_data)

      # Interpretando Elementos
      self.read_elements(dat_data)
   
   def write_nodes(self) -> str:
      # Parâmetros Iniciais
      n_nodes = len(self.model.nodes)
      span = len(str(n_nodes))
      output = f'\n%NODE\n{n_nodes}\n\n%NODE.COORD\n{n_nodes}\n'

      # Escrevendo Cada Node
      for ide, node in self.model.nodes.items():
         offset = span - len(str(ide))
         offset = ' ' * offset
         output += f'{ide}{offset}   {node.x:+.8e}   {node.y:+.8e}   {node.z:+.8e}\n'
      
      return output

   def write_elements(self) -> str:
      # Parâmetros Iniciais
      output = ''
      total_elements = 0
      n_nodes = len(self.model.nodes)
      node_ide_span = len(str(n_nodes))

      # Escrevendo Cada Grupo de Elemento
      for group in self.model.element_groups.values():
         # Parâmetros Iniciais
         n_elements = len(group.elements)
         total_elements += n_elements
         span = len(str(n_elements))

         # Buscando Tipo de Elemento Correspondente às Propriedades do Elemento
         element_type = ''
         for reference_type, reference_geometry in self.reference['elements'].items():
            if (
               reference_geometry['geometry'] == group.geometry.name and
               reference_geometry['grade'] == group.geometry.grade and
               reference_geometry['n_nodes'] == group.geometry.n_nodes
            ):
               element_type = reference_type
               break
         else:
            raise ValueError(f'The Geometry "{group.geometry.name}" with grade {group.geometry.grade} and {group.geometry.n_nodes} nodes is not supported for .dat files.')
         
         # Verificando se Elemento Tem uma Teoria
         if group.theory:
            for dat_theory, reference_theory in self.reference['theories'].items():
               if reference_theory == group.theory:
                  element_type = f'{dat_theory}.{element_type}'
                  break
            else:
               raise ValueError(f'The Theory "{group.theory}" is not supported for .dat files.')

         output += f'\n%ELEMENT.{element_type}\n{n_elements}\n'

         # Escrevendo Cada Elemento
         for ide, node_ides in group.elements.items():
            offset = span - len(str(ide))
            offset = ' ' * offset
            node_ides = '   '.join([ f'{nis:>{node_ide_span}}' for nis in node_ides ])
            more_info = '1  1'
            if group.geometry.name == 'BezierTriangles':
               more_info += f'  1  {group.geometry.grade}'
            output += f'{ide}{offset}   {more_info}   {node_ides}\n'

      output = f'\n%ELEMENT\n{total_elements}\n' + output
      return output

   def write(self) -> str:
      # Inicializando Output
      output = '%HEADER\n'

      # Escrevendo Nodes
      output += self.write_nodes()

      # Escrevendo Elementos
      output += self.write_elements()

      # Finalizando Output
      output += '\n%END'
      
      return output

class SVG_Interpreter:
   def __init__(self):
      self.model = SimulationModel()
      self.node_radius = 1
      self.node_color = '#a95e5e'
      self.element_color = '#fcff5e'
      self.element_stroke_width = 1
      self.element_stroke_color = 'black'

   def calculate_colinearity(self, points: list[SimulationModel.Node]) -> float:
      factor = 0
      for i in range(0, len(points) - 2):
         diag1 = points[i].x * points[i + 1].y + points[i + 1].x * points[i + 2].y + points[i + 2].x * points[i].y
         diag2 = points[i].x * points[i + 2].y + points[i + 1].x * points[i].y + points[i + 2].x * points[i + 1].y
         factor += abs(diag1 - diag2)
      return abs(factor)
   
   def tesselate_bezier_curve(self, grade: int, points: list[SimulationModel.Node], n_regions: int):
      # Variáveis Iniciais
      tesselated_points = list()
      p = grade
      h = 1 / (n_regions - 1)

      # Gerando Pontos da Curva
      for nr in range(n_regions):
         # Calculando Região do Espaço Paramétrico
         t = nr * h
         
         # Calculando Ponto Cartesiano Correspondente
         weight_sum, coord_x, coord_y = 0, 0, 0
         for point, i in zip(points, range(0, p + 1)):
            bp = bernstein_polynomial(i, p, t)
            w = point.weight or 1
            weight_sum += bp * w
            coord_x += bp * point.x * w
            coord_y += bp * point.y * w
         coord_x /= weight_sum
         coord_y /= weight_sum
         tesselated_points.append([coord_x, coord_y])
      
      # Corrigindo Pontos Ímpares para Coordenada Equivalente na Representação de Curva de Bezier Quadrática
      for i in range(1, len(tesselated_points), 2):
         tesselated_points[i][0] = bezier_equiv_coord(tesselated_points[i][0], tesselated_points[i - 1][0], tesselated_points[i + 1][0])
         tesselated_points[i][1] = bezier_equiv_coord(tesselated_points[i][1], tesselated_points[i - 1][1], tesselated_points[i + 1][1])
      
      # Retornando Pontos Tesselados (Excluindo o Primeiro)
      return tesselated_points[1:]

   def write_nodes(self) -> str:
      # Inicializando Node Output
      output = f'\n   <g id="Nodes" fill="{self.node_color}">'

      # Escrevendo Cada Node
      for node in self.model.nodes.values():
         output += f'\n      <circle cx="{node.x:.8e}" cy="{node.y:.8e}" r="{self.node_radius}" />'
      
      output += '\n   </g>'
      return output
   
   def write_bezier_triangles(self, group: SimulationModel.ElementGroup) -> str:
      # Parâmetros Iniciais
      output = ''
      p = group.geometry.grade
      nodes_total = int(3 + 3 * (p - 1) + ((p - 2) * (p - 1) / 2))
      indexes_corner = [1, nodes_total - p, nodes_total]

      # Index dos Nodes Intermediários
      ie1 = [int(1 + ((i + 1) * (i + 2) / 2)) for i in range(p - 1)]
      ie2 = [nodes_total - p + 1 + i for i in range(p - 1)]
      ie3 = [int((i + 2) * (i + 3) / 2) for i in range(p - 1)]
      ie3.reverse()
      indexes_by_edge = [ie1, ie2, ie3]

      # Escrevendo Path de Cada Elemento
      for node_ides in group.elements.values():
         # Inicializando Path
         output += f'\n      <path d="'

         # Lado 1 - Ponto Incial
         node_corner_1 = self.model.nodes[node_ides[indexes_corner[0] - 1]]
         output += f'M {node_corner_1.x:.8e} {node_corner_1.y:.8e} '

         # Construindo Curvas de Bezier para Cada Lado
         for indexes_edge, index_corner in zip(indexes_by_edge, indexes_corner[1:] + [indexes_corner[0]]):
            # Obtendo Pontos do Lado
            node_corner_2 = self.model.nodes[node_ides[index_corner - 1]]
            points = [self.model.nodes[node_ides[i - 1]] for i in indexes_edge]
            points.append(node_corner_2)
            points.insert(0, node_corner_1)

            # Calculando Fator de Colinearidade dos Pontos
            c_factor = self.calculate_colinearity(points)

            # Resumindo Path em Uma linha reta para um fator baixo
            if c_factor < 0.1:
               output += f'L {node_corner_2.x:.8e} {node_corner_2.y:.8e} '

            # Tesselando Curva com Base no Fator
            else:
               # Definindo Discretização da Tesselação com Base no Fator de Colinearidade
               n_regions = (2 * p - 1) + (2 * floor(c_factor / 50))

               # Gerando Pontos de Tesselação
               tp = self.tesselate_bezier_curve(p, points, n_regions)

               for i in range(0, len(tp), 2):
                  output += f'Q {tp[i][0]:.8e} {tp[i][1]:.8e}, {tp[i + 1][0]:.8e} {tp[i + 1][1]:.8e} '
            
            node_corner_1 = node_corner_2

         output += 'Z" />'
      
      return output

   def write_finite_elements(self, group: SimulationModel.ElementGroup):
      output = ''

      # Tratamento para Elementos Lineares
      if group.geometry.grade == 1:
         for node_ides in group.elements.values():
            output += '\n      <polygon points="'

            # Escrevendo Cada Ponto
            for ide in node_ides:
               node = self.model.nodes[ide]
               output += f'{node.x:.8e},{node.y:.8e} ' 
            output += '" />'

      # Tratamento para Elementos Lineares
      else:
         for node_ides in group.elements.values():
            # Escrevendo Ponto Inicial
            node = self.model.nodes[node_ides[0]]
            output += f'\n      <path d="M {node.x:.8e} {node.y:.8e} '

            # Escrevendo Lados como Curvas Quadráticas de Bezier
            for i in list(range(2, len(node_ides), 2)) + [0]:
               n2 = self.model.nodes[node_ides[i]]
               nc = self.model.nodes[node_ides[i - 1]]
               n0 = self.model.nodes[node_ides[i - 2]]
               x1 = bezier_equiv_coord(nc.x, n0.x, n2.x)
               y1 = bezier_equiv_coord(nc.y, n0.y, n2.y)
               output += f'Q {x1:.8e} {y1:.8e}, {n2.x:.8e} {n2.y:.8e} ' 
            output += 'Z" />'
      return output

   def write_elements(self) -> str:
      # Inicializando Node Output
      output = f'\n   <g id="Elements" fill="{self.element_color}" stroke="{self.element_stroke_color}" stroke-width="{self.element_stroke_width}">'

      # Escrevendo Cada Grupo de Elemento
      for group in self.model.element_groups.values():
         # Tratamento para Elementos de Bezier
         if group.geometry.name == 'BezierTriangle':
            output += self.write_bezier_triangles(group)

         # Tratamento para Elementos Finitos Tradicionais
         else:
            output += self.write_finite_elements(group)

      output += '\n   </g>'
      return output

   def write(self) -> str:
      # Inicializando Output
      output = '<svg width="100" height="100" version="1.1" xmlns="http://www.w3.org/2000/svg">'

      # Calculando Raio dos Nodes e Largura do Delinado dos Elementos Ideais
      self.node_radius = 9.5 / (len(self.model.nodes) - 1) ** 0.5 + 0.1
      self.element_stroke_width = self.node_radius * 0.5

      # Escrevendo Elementos
      output += self.write_elements()

      # Escrevendo Nodes
      output += self.write_nodes()

      # Finalizando Output
      output += '\n</svg>'
      
      return output