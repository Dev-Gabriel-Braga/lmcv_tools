# --------------------------------------------------
# 1 - Classes do Modelo de Simulação
# --------------------------------------------------
class SimulationModel:
   def __init__(self):
      # Nodes - Atributos Relacionados
      self.nodes = dict[int, Node]()
      self.node_sets = dict[str, set]()
      self.node_solver_order = list[int]()

      # Elements - Atributos Relacionados
      self.element_geometries = dict[int, ElementGeometry]()
      self.element_groups = dict[int, ElementGroup]()
      self.element_sets = dict[str, set]()

      # Supports - Atributos Relacionados
      self.supports = dict[int, set]()
      self.supported_dofs = ('u', 'v', 'w', 'rx', 'ry', 'rz')

      # Materials - Atributos Relacionados
      self.materials = dict[int, Material]()

      # Sections - Atributos Relacionados
      self.sections = dict[int, Section]()
   
   # Métodos - Adição de Entidades
   def add_node(
      self, 
      ide: int, 
      x: float, 
      y: float, 
      z: float, 
      weight: float = None
   ):
      self.nodes[ide] = Node(x, y, z, weight)
   
   def add_element_geometry(
      self,
      shape: str,
      base: str,
      grade: int | list[int],
      n_nodes: int,
      n_dimensions: int,
      knot_vectors: list[list[float]] = None, 
      node_space: list[int] = None
   ) -> int:
      # Verificando se Geometria Já Existe
      for geometry_ide, element_geometry in self.element_geometries.items():
         if (
            (shape == element_geometry.shape) and
            (base == element_geometry.base) and
            (grade == element_geometry.grade) and
            (n_nodes == element_geometry.n_nodes) and
            (n_dimensions == element_geometry.n_dimensions)
         ):
            if base == 'BSpline':
               if knot_vectors == element_geometry.knot_vectors and node_space == element_geometry.node_space:
                  break
               continue
            break
      else:
         # Criando Geometria (Já que não Existe)
         geometry_ide = len(self.element_geometries) + 1
         self.element_geometries[geometry_ide] = ElementGeometry(shape, base, grade, n_nodes, n_dimensions, knot_vectors, node_space)

      # Retornando Ide da Geometria
      return geometry_ide
   
   def add_element_group(self, ide: int, geometry_ide, theory: str):
      if geometry_ide not in self.element_geometries:
         raise ValueError(f'The Element Geometry with ide = {geometry_ide} does not exist.')
      self.element_groups[ide] = ElementGroup(geometry_ide, theory)

   def add_element(
      self, group_ide: int,
      ide: int,
      node_ides: list[int], 
      knot_span: list[int] = None
   ):
      # Verificando se Ides de Nodes são Válidos
      for node_ide in node_ides:
         if node_ide not in self.nodes:
            raise ValueError(f'The Node with ide = {node_ide} does not exist.')
      
      # Criando Elemento
      self.element_groups[group_ide].elements[ide] = Element(node_ides, knot_span)
   
   def add_support(self, node_ide: int, dof: str):
      # Verificando Entradas
      if node_ide not in self.nodes:
         raise ValueError(f'The Node with ide = {node_ide} does not exist.')
      if dof not in self.supported_dofs:
         raise ValueError(f'The Degree of Freedom "{dof}" is not supported.')
      
      # Relacionando Grau de Liberdade Restrito com o Node
      if self.supports.get(node_ide) is None:
         self.supports[node_ide] = set()
      self.supports[node_ide].add(dof)

# --------------------------------------------------
# 2 - Classes Relacionadas à Malha
# --------------------------------------------------
class Node:
   def __init__(self, x: float, y: float, z: float, weight: float = None):
      self.x = x
      self.y = y
      self.z = z
      self.weight = weight

class ElementGeometry:
   def __init__(
      self,
      shape: str, 
      base: str, 
      grade: int | list[int],
      n_nodes: int,
      n_dimensions: int,
      knot_vectors: list[list[float]] = None, 
      node_space: list[int] = None
   ):
      # Atributos de Geometrias em Geral
      self.shape = shape
      self.base = base
      self.grade = grade
      self.n_nodes = n_nodes
      self.n_dimensions = n_dimensions

      # Atributos de Geometria com Base BSpline
      self.knot_vectors = knot_vectors
      self.node_space = node_space

class ElementGroup:
   def __init__(self, geometry_ide: int, theory: str):
      self.geometry_ide = geometry_ide
      self.theory = theory
      self.elements = dict[int, Element]()

class Element:
   def __init__(self, node_ides: list[int], knot_span: list[int] = None):
      self.node_ides = node_ides
      self.knot_span = knot_span

# --------------------------------------------------
# 3 - Classes Relacionadas a Materiais
# --------------------------------------------------
class Material:
   pass

class IsotropicMaterial(Material):
   def __init__(self, elastic_modulus: float, poisson_coefficient: float, density: float) -> None:
      self.E = elastic_modulus
      self.nu = poisson_coefficient
      self.rho = density

      # Calculando Módulo Volumétrico
      self.K = self.E / (3 * (1 - 2 * self.nu))

      # Calculando Módulo de Cisalhamento
      self.G = self.E / (2 * (1 + self.nu))

class FunctionallyGradedMaterial(Material):
   # Funções de Homogeneização Privadas
   def _voigt(self, volume_fractions: list[float]):
      E, nu, rho = 0, 0, 0
      for V, M in zip(volume_fractions, self.materials):
         E += V * M.E
         nu += V * M.nu
         rho += V * M.rho
      return E, nu, rho
   
   def _hashin_shtrikman(bound: str):
      def function(self, volume_fractions: list[float]) -> list[float]:
         # Definindo Valores Especiais
         V, M = volume_fractions, self.materials
         V1, V2 = V[0], V[1]
         K1, K2 = M[0].K, M[1].K
         G1, G2 = M[0].G, M[1].G
         rho_1, rho_2 = M[0].rho, M[1].rho

         # Valores Iniciais do que é Matriz e do que são as Inclusões
         Vm, Vi = V1, V2
         Km, Ki = K1, K2
         Gm, Gi = G1, G2
         rho_m, rho_i = rho_1, rho_2

         # Trocando Ordem com base no Bound Escolhido
         if (
            bound == 'upper' and M[0].E < M[1].E or
            bound == 'lower' and M[0].E > M[1].E
         ):
            Vm, Vi = V2, V1
            Km, Ki = K2, K1
            Gm, Gi = G2, G1
            rho_m, rho_i = rho_2, rho_1

         # Calculando Valores Auxilizares
         FK = (3 * Vm) / (3 * Km + 4 * Gm)
         FG = 6 * Vm * (Km + 2 * Gm) / (5 * Gm * (3 * Km + 4 * Gm))

         # Calculando Módulo Volumétrico
         K = Km + Vi / ((1 / (Ki - Km)) + FK)

         # Calculando Módulo de Cisalhamento
         G = Gm + Vi / ((1 / (Gi - Gm)) + FG)

         # Calculando Propriedades Efetivas
         E = (9 * G * K) / (G + 3 * K)
         nu = (3 * K - 2 * G) / (2 * (G + 3 * K))

         # Densidade Calculada pelo Modelo de voigt
         rho = Vi * rho_i + Vm * rho_m

         return E, nu, rho
      return function

   # Relação Modelo/Função de Homogeneização
   homogenize_functions = {
      'voigt': _voigt,
      'mori_tanaka': _hashin_shtrikman('lower'),
      'hashin_shtrikman_upper_bound': _hashin_shtrikman('upper'),
      'hashin_shtrikman_lower_bound': _hashin_shtrikman('lower'),
   }

   def __init__(self, micromechanical_model: str, materials: list[IsotropicMaterial]) -> None:
      self.micromechanical_model = micromechanical_model
      self.materials = materials
      try:
         self._homogenize = FunctionallyGradedMaterial.homogenize_functions[micromechanical_model]
      except KeyError:
         raise ValueError(f'Micromechanical Model "{micromechanical_model}" is not supported.')
   
   def homogenize(self, volume_fractions: list[float]):
      return self._homogenize(self, volume_fractions)

# --------------------------------------------------
# 4 - Classes Relacionadas a Seções
# --------------------------------------------------
class Section:
   def __init__(self, material_ide: int) -> None:
      self.material_ide = material_ide

class HIM_3D_Section(Section):
   def __init__(self, material_ide: int) -> None:
      # Chamando Construtor da Superclasse
      super().__init__(material_ide)

class FGM_3D_Section(Section):
   def __init__(self, material_ide: int, volume_fractions: dict[int, float]) -> None:
      # Chamando Construtor da Superclasse
      super().__init__(material_ide)

      # Atribuindo Atributos
      self.volume_fractions = volume_fractions