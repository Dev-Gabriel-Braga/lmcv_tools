# Classes de Entidades de Simulação
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
      self.elements = dict()

class Element:
   def __init__(self, node_ides: list[int], knot_span: list[int] = None):
      self.node_ides = node_ides
      self.knot_span = knot_span

class SimulationModel:
   def __init__(self):
      # Nodes - Atributos Relacionados
      self.nodes = dict()
      self.node_sets = dict()
      self.node_solver_order = list()

      # Elements - Atributos Relacionados
      self.element_geometries = dict()
      self.element_groups = dict()
      self.element_sets = dict()

      # Supports - Atributos Relacionados
      self.supports = dict()
      self.supported_dofs = ('u', 'v', 'w', 'rx', 'ry', 'rz')
   
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
   ):
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