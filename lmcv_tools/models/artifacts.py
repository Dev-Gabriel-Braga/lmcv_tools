from ..interface import searcher
from .simulation import (
   SimulationModel,
   FunctionallyGradedMaterial
)
from .interpreters import (
   DAT_Interpreter
)
from .geometry import NURBS

# --------------------------------------------------
# 1 - Classe Abstrata de Artefato
# --------------------------------------------------
class Artifact:
   def __init__(self, name: str, file_extension: str, data: str = ''):
      self.name = name
      self.file_extension = file_extension
      self.data = data
   
   @property
   def file_name(self) -> str:
      return self.name + '.' + self.file_extension
   
   # Para Implementar
   def generate(self):
      return self.data

# --------------------------------------------------
# 2 - Classes do Artefato "virtual_laminas"
# --------------------------------------------------
class ElementConfiguration:
   # Elementos Suportados
   supported_types = {'Solid', 'Shell'}

   def __init__(self, type: str, number_integration_points: int):
      if type not in ElementConfiguration.supported_types:
         raise ValueError(f'Element Type "{type}" is not supported.')
      self.type = type
      self.number_integration_points = number_integration_points

class VirtualLaminas(Artifact):
   def __init__(
      self,
      laminas_count: int,
      thickness: float,
      power_law_exponent: float,
      element_configuration: ElementConfiguration,
      fgm: FunctionallyGradedMaterial,
      smart: bool = False
   ):
      super().__init__('virtual_laminas', 'inp')
      self.laminas_count = laminas_count
      self.thickness = thickness
      self.power_law_exponent = power_law_exponent
      self.element_configuration = element_configuration
      self.fgm = fgm
      self.smart = smart
   
   def volume_fraction(self, z: float):
      return 1 - z ** self.power_law_exponent
   
   def z_coordinate(self, V: float):
      return (1 - V) ** (1 / self.power_law_exponent)

   def same_thickness_laminas(self):
      step = 1 / self.laminas_count
      points = [step / 2 + i * step for i in range(self.laminas_count)]
      fractions = [self.volume_fraction(z) for z in points]
      if self.element_configuration.type == 'Solid':
         thickness = [self.thickness for _ in range(self.laminas_count)]
      else:
         thickness = [step * self.thickness for _ in range(self.laminas_count)]
      return fractions, thickness

   def smart_laminas(self):
      # Variáveis Iniciais
      n = self.laminas_count
      p = self.power_law_exponent
      V = self.volume_fraction
      z = self.z_coordinate
      fractions_z = list()
      fractions_V = list()
      thickness_z = list()
      thickness_V = list()
      
      # Calculando Z de Referência
      if p == 1:
         z_ref = 0.5
      else:
         z_ref = p ** (-1 / (p - 1))
      
      # Decidindo se a Região de Prioridade z está à Esquerda ou Direita
      V_ref = V(z_ref)
      slope_tendency = -p * (p - 1) * z_ref ** (p - 2)
      if slope_tendency > 0:
         l_V = 1 - V_ref
         l_z = 1 - z_ref
      else:
         l_V = V_ref
         l_z = z_ref

      # Parâmetros da Região de Prioridade V
      n_V = round(l_z * n)
      step_V = l_V / n_V
      if slope_tendency > 0:
         z_0 = 0
         V_i = 1 - step_V / 2
      else:
         z_0 = z_ref
         V_i = V_ref - step_V / 2

      # Gerando Laminas da Região de Prioridade V 
      for _ in range(n_V):
         # Calculando Espessura Variável
         h_i = z(V_i - step_V / 2) - z_0

         # Registrando Informações
         fractions_V.append(V_i)
         thickness_V.append(h_i)

         # Atualizando Fração de Volume e Referência para Espessura
         V_i -= step_V
         z_0 += h_i
      
      # Parâmetros da Região de Prioridade z
      n_z = n - n_V
      step_z = l_z / n_z
      if slope_tendency > 0:
         z_i = z_ref + step_z / 2
      else:
         z_i = step_z / 2

      # Gerando Laminas da Região de Prioridade z
      for _ in range(n_z):
         fractions_z.append(V(z_i))
         thickness_z.append(step_z)
         z_i += step_z
      
      # Mesclando Regiões
      if slope_tendency > 0:
         fractions = fractions_V + fractions_z
         thickness = thickness_V + thickness_z
      else:
         fractions = fractions_z + fractions_V
         thickness = thickness_z + thickness_V

      # Corrigindo Espessura
      thickness = [t * self.thickness for t in thickness]

      return fractions, thickness

   def generate(self):
      # Inicializando Dados
      inp_data = ''

      # Gerados Dados de Lâminas
      laminas = self.smart_laminas() if self.smart else self.same_thickness_laminas()

      # Escrevendo Materiais
      material_names = list()
      index = 1
      for V in laminas[0]:
         # Gerando e Armazando Nome de Material
         name =  f'FGM-L{index}'
         material_names.append(name)

         # Homogeneizando Propriedades
         E, nu, rho = self.fgm.homogenize([V, 1 - V])

         # Adicionando Dados
         inp_data += f'*Material, name={name}\n    *Density\n    {rho:.7E},\n    *Elastic\n    {E:.7E}, {nu:.3f}\n'
         
         index += 1
      
      # Preparando para Escrever Lâminas
      inp_data += '*Part, name=Virtual_Part\n*Node\n    1, 1.0, 1.0, 0.0\n    2, 0.0, 1.0, 0.0\n    3, 0.0, 0.0, 0.0\n    4, 1.0, 0.0, 0.0\n*Element, type=S4R\n    1, 1, 2, 3, 4\n*Elset, elset=Virtual\n    1'
      element_type = self.element_configuration.type
      int_points = self.element_configuration.number_integration_points
      rotation_angle = 0

      # Escrevendo Lâmina por Lâmina
      inp_data += f'\n*{element_type} Section, elset=Virtual, composite\n'
      index = 1
      for h, material in zip(laminas[1], material_names):
         inp_data += f'    {h:.7E}, {int_points}, {material}, {rotation_angle}, Ply-{index}\n'
         index += 1
      inp_data += '*End Part'

      # Inseridos dados Inp no Atributo de Dados
      self.data = inp_data

# --------------------------------------------------
# 3 - Classes do Artefato "cuboid"
# --------------------------------------------------
class Cuboid(Artifact):
   # Funções de Geração de Coordenadas e Incidência de Elementos
   def _brick20_coordinates(self):
      # Renomeando Atributos
      width, height, deep = self.dimensions
      nx, ny, nz = self.discretization

      # Calculando Valores Necessários
      delta_x = width / nx
      delta_y = height / ny
      delta_z = deep / nz
      x_values = [delta_x / 2 * i for i in range(2 * nx + 1)]
      y_values = [delta_y / 2 * i for i in range(2 * ny + 1)]
      z_values = [delta_z / 2 * i for i in range(2 * nz + 1)]

      # Gerando Coordenadas
      ide = 1
      for i_z, z in enumerate(z_values):
         # Mudando Valores de y com base em z
         ys = y_values if i_z % 2 == 0 else y_values[::2]

         for i_y, y in enumerate(ys):
            # Mudando Valores de x com base em y e z
            xs = x_values
            if (
               ((i_z % 2 == 0) and (i_y % 2 == 1)) or
               (i_z % 2 == 1)
            ):
               xs = x_values[::2]

            for x in xs:
               self.model.add_node(ide, x, y, z)
               ide += 1

   def _brick20_incidence(self, i: int) -> list[int]:
      # Inicializando Variáveis
      nx, ny, _ = self.discretization
      inc = [0] * 20
      x_order = i % nx
      if x_order == 0: x_order = nx
      layer_order = i % (nx * ny)
      if layer_order == 0: layer_order = nx * ny
      y_order = layer_order // nx
      if layer_order % nx != 0: y_order += 1
      z_order = i // (nx * ny)
      if i % (nx * ny) != 0: z_order += 1
      
      # Determinando Nó Inicial
      inc[0] = (2 * x_order - 1) + (y_order - 1) * (3 * nx + 2) + (z_order - 1) * ((nx + 1) * (ny + 1) + (2 * nx + 1) * (2 * ny + 1) - nx * ny)

      # Camada 1
      inc[1] = inc[0] + 1
      inc[2] = inc[0] + 2
      inc[3] = inc[0] + 2 * nx + 3 - x_order
      inc[4] = inc[3] + nx + 1 + x_order
      inc[5] = inc[4] - 1
      inc[6] = inc[4] - 2
      inc[7] = inc[3] - 1

      # Camada 2
      inc[8] = inc[0] + 2 * nx - x_order + 2 + (ny + 1 - y_order) * (3 * nx + 2) + (y_order - 1) * (nx + 1)
      inc[9] = inc[8] + 1
      inc[10] = inc[8] + nx + 2
      inc[11] = inc[10] - 1
      
      # Camada 3
      inc[12] = inc[8] + nx - x_order + 1 + (ny + 1 - y_order) * (nx + 1) + (y_order - 1) * (3 * nx + 2) + 2 * (x_order - 1) + 1
      inc[13] = inc[12] + 1
      inc[14] = inc[12] + 2
      inc[15] = inc[12] + 2 * nx + 3 - x_order
      inc[16] = inc[15] + nx + 1 + x_order
      inc[17] = inc[16] - 1
      inc[18] = inc[16] - 2
      inc[19] = inc[15] - 1

      # Ordenando Conforme o FAST
      fast_order = [12, 13, 14, 15, 16, 17, 18, 19, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7]
      inc = [inc[i] for i in fast_order]

      return inc

   # Elementos Suportados
   supported_elements = {
      'BRICK20': {
         'coordinates': _brick20_coordinates,
         'incidence': _brick20_incidence
      }
   }

   def __init__(
      self,
      element_type: str,
      dimensions: list[float],
      discretization: list[int]
   ):
      # Chamando Construtor da Superclasse
      super().__init__('cuboid', 'dat')

      # Verificando se Tipo de Elemento Fornecido é Suportado
      if element_type not in Cuboid.supported_elements.keys():
         raise ValueError(f'Element Type "{element_type}" is not supported for cuboid generation.')   

      # Verificando se o Número de Dimensões e Discretização foram passadas Corretamente
      if len(dimensions) != 3:
         raise ValueError('A Cuboid needs exactly 3 dimensions (width, height and deep).')
      if len(discretization) != 3:
         raise ValueError('A Cuboid needs exactly 3 discretization values (number of elements in width, height and deep).')

      # Atribuindo Atributos
      self.element_type = element_type
      self.dimensions = dimensions
      self.discretization = discretization
      self.model = SimulationModel()
      self._coordinates = Cuboid.supported_elements[element_type]['coordinates']
      self._incidence = Cuboid.supported_elements[element_type]['incidence']
      self.reference = searcher.get_database('translation_reference')

   def coordinates(self):
      return self._coordinates(self)
   
   def incidence(self, i: int) -> list[int]:
      return self._incidence(self, i)
   
   def geometry(self) -> int:
      element_info = self.reference['dat']['elements'][self.element_type]
      return self.model.add_element_geometry(**element_info)

   def generate(self):
      # Renomeando Atributos
      nx, ny, nz = self.discretization

      # Gerando Coordenadas e Nodes
      self.coordinates()

      # Configurações dos Elementos
      geometry_ide = self.geometry()
      self.model.add_element_group(1, geometry_ide, None)

      # Gerando Elementos (BRICK20)
      for i in range(nx * ny * nz):
         # Gerando Incidência
         nodal_incidence = self.incidence(i + 1)

         # Cadastrando Elemento
         self.model.add_element(
            group_ide = 1,
            ide = i + 1,
            node_ides = nodal_incidence
         )

      # Escrevendo Dados do .dat
      dati = DAT_Interpreter()
      dati.model = self.model
      self.data = dati.write()

# --------------------------------------------------
# 4 - Classes do Artefato "nurbs_rectangle"
# --------------------------------------------------
class NURBS_Rectangle(Artifact):
   def __init__(
      self,
      degrees: list[int],
      dimensions: list[float],
      discretization: list[int]
   ):
      # Chamando Construtor da Superclasse
      super().__init__('nurbs_rectangle', 'dat')  

      # Verificando se o Número de Dimensões e Discretização foram passadas Corretamente
      if len(degrees) != 2:
         raise ValueError('A NURBS Rectangle needs exactly 2 degrees (degrees in width and height).')
      if len(dimensions) != 2:
         raise ValueError('A NURBS Rectangle needs exactly 2 dimensions (width and height).')
      if len(discretization) != 2:
         raise ValueError('A NURBS Rectangle needs exactly 2 discretization values (number of elements in width and height).')

      # Atribuindo Atributos
      self.degrees = degrees
      self.dimensions = dimensions
      self.discretization = discretization
      self.model = SimulationModel()

   def coordinates(self) -> list[NURBS]:
      # Renomeando Atributos
      dx, dy = self.degrees
      width, height = self.dimensions
      nx, ny = self.discretization

      # Calculando Valores Necessários (Em X)
      nurbs_x = NURBS(1, [0, 0, 1, 1], [[0.0], [width]], [1.0, 1.0])
      nurbs_x.degree_elevation(dx - 1)
      x_knots = [i / nx for i in range(1, nx)]
      nurbs_x.knot_insertions(x_knots)
      x_values = [cp[0] for cp in nurbs_x.control_points]

      # Calculando Valores Necessários (Em y)
      nurbs_y = NURBS(1, [0, 0, 1, 1], [[0.0], [height]], [1.0, 1.0])
      nurbs_y.degree_elevation(dy - 1)
      y_knots = [i / ny for i in range(1, ny)]
      nurbs_y.knot_insertions(y_knots)
      y_values = [cp[0] for cp in nurbs_y.control_points]

      # Gerando Coordenadas
      ide = 1
      for y in y_values:
         for x in x_values:
            self.model.add_node(ide, x, y, 0.0, 1.0)
            ide += 1

      return nurbs_x, nurbs_y

   def generate(self):
      # Renomeando Atributos
      dx, dy = self.degrees
      nx, ny = self.discretization

      # Gerando Coordenadas e Nodes
      nurbs_x, nurbs_y = self.coordinates()

      # Configurações dos Elementos
      node_space = list(
         map(
            lambda n: n + 1,
            range(len(self.model.nodes))
         )
      )
      geometry_ide = self.model.add_element_geometry(
         shape = 'Quadrilateral',
         base = 'BSpline',
         grade = [nurbs_x.degree, nurbs_y.degree],
         n_nodes = (nurbs_x.degree + 1) * (nurbs_y.degree + 1),
         n_dimensions = 2,
         knot_vectors = [nurbs_x.knot_vector, nurbs_y.knot_vector],
         node_space = node_space,
      )
      self.model.add_element_group(1, geometry_ide, 'ShallowShell')

      # Gerando Matriz do Node Space
      node_space_matrix = list()
      for i in range(0, len(node_space), nx + dx):
         node_space_matrix.append(node_space[i:i + nx + dx])

      # Gerando Elementos
      ide = 1
      for ks2 in range(ny):
         for ks1 in range(nx):
            # Determinando Nodes do Elemento
            node_ides = list()
            for i in range(ks2, ks2 + dy + 1):
               for j in range(ks1, ks1 + dx + 1):
                  node_ides.append(node_space_matrix[i][j])

            # Cadastrando Elemento
            self.model.add_element(
               group_ide = 1,
               ide = ide,
               node_ides = node_ides,
               knot_span = [ks1 + 1, ks2 + 1]
            )
            ide += 1

      # Escrevendo Dados do .dat
      dati = DAT_Interpreter()
      dati.model = self.model
      self.data = dati.write()
   
# --------------------------------------------------
# 5 - Classes do Artefato "nurbs_cuboid"
# --------------------------------------------------
class NURBS_Cuboid(Artifact):
   def __init__(
      self,
      degrees: list[int],
      dimensions: list[float],
      discretization: list[int]
   ):
      # Chamando Construtor da Superclasse
      super().__init__('nurbs_cuboid', 'dat')  

      # Verificando se o Número de Dimensões e Discretização foram passadas Corretamente
      if len(degrees) != 3:
         raise ValueError('A NURBS Cuboid needs exactly 3 degrees (degrees in width, height and deep).')
      if len(dimensions) != 3:
         raise ValueError('A NURBS Cuboid needs exactly 3 dimensions (width, height and deep).')
      if len(discretization) != 3:
         raise ValueError('A NURBS Cuboid needs exactly 3 discretization values (number of elements in width, height and deep).')

      # Atribuindo Atributos
      self.degrees = degrees
      self.dimensions = dimensions
      self.discretization = discretization
      self.model = SimulationModel()

   def coordinates(self) -> list[NURBS]:
      # Renomeando Atributos
      dx, dy, dz = self.degrees
      width, height, deep = self.dimensions
      nx, ny, nz = self.discretization

      # Calculando Valores Necessários (Em X)
      nurbs_x = NURBS(1, [0, 0, 1, 1], [[0.0], [width]], [1.0, 1.0])
      nurbs_x.degree_elevation(dx - 1)
      x_knots = [i / nx for i in range(1, nx)]
      nurbs_x.knot_insertions(x_knots)
      x_values = [cp[0] for cp in nurbs_x.control_points]

      # Calculando Valores Necessários (Em y)
      nurbs_y = NURBS(1, [0, 0, 1, 1], [[0.0], [height]], [1.0, 1.0])
      nurbs_y.degree_elevation(dy - 1)
      y_knots = [i / ny for i in range(1, ny)]
      nurbs_y.knot_insertions(y_knots)
      y_values = [cp[0] for cp in nurbs_y.control_points]

      # Calculando Valores Necessários (Em z)
      nurbs_z = NURBS(1, [0, 0, 1, 1], [[0.0], [deep]], [1.0, 1.0])
      nurbs_z.degree_elevation(dz - 1)
      z_knots = [i / nz for i in range(1, nz)]
      nurbs_z.knot_insertions(z_knots)
      z_values = [cp[0] for cp in nurbs_z.control_points]

      # Gerando Coordenadas
      ide = 1
      for z in reversed(z_values):
         for y in y_values:
            for x in x_values:
               self.model.add_node(ide, x, y, z, 1.0)
               ide += 1

      return nurbs_x, nurbs_y, nurbs_z

   def generate(self):
      # Renomeando Atributos
      dx, dy, dz = self.degrees
      nx, ny, nz = self.discretization

      # Gerando Coordenadas e Nodes
      nurbs_x, nurbs_y, nurbs_z = self.coordinates()

      # Configurações dos Elementos
      node_space = list(
         map(
            lambda n: n + 1,
            range(len(self.model.nodes))
         )
      )
      geometry_ide = self.model.add_element_geometry(
         shape = 'Hexahedron',
         base = 'BSpline',
         grade = [nurbs_x.degree, nurbs_y.degree, nurbs_z.degree],
         n_nodes = (nurbs_x.degree + 1) * (nurbs_y.degree + 1) * (nurbs_z.degree + 1),
         n_dimensions = 3,
         knot_vectors = [nurbs_x.knot_vector, nurbs_y.knot_vector, nurbs_z.knot_vector],
         node_space = node_space,
      )
      self.model.add_element_group(1, geometry_ide, None)

      # Gerando Matriz do Node Space
      node_space_matrix = list()
      for i in range(0, len(node_space), (ny + dy) * (nx + dx)):
         node_space_matrix.append(list())
         for j in range(i, i + (ny + dy) * (nx + dx), nx + dx):
            node_space_matrix[-1].append(node_space[j:j + nx + dx])

      # Gerando Elementos
      ide = 1
      for ks3 in range(nz):
         for ks2 in range(ny):
            for ks1 in range(nx):
               # Determinando Nodes do Elemento
               node_ides = list()
               for i in range(ks3, ks3 + dz + 1):
                  for j in range(ks2, ks2 + dy + 1):
                     for l in range(ks1, ks1 + dx + 1):
                        node_ides.append(node_space_matrix[i][j][l])

               # Cadastrando Elemento
               self.model.add_element(
                  group_ide = 1,
                  ide = ide,
                  node_ides = node_ides,
                  knot_span = [ks1 + 1, ks2 + 1, ks3 + 1]
               )
               ide += 1

      # Escrevendo Dados do .dat
      dati = DAT_Interpreter()
      dati.model = self.model
      self.data = dati.write()