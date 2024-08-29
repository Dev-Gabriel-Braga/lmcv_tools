import re
from math import floor
from ..interface import searcher
from .geometry import (
   bezier_equiv_coord, 
   bernstein_polynomial,
   NURBS_Surface,
   GeometricalTransformer
)
from .simulation import (
   SimulationModel,
   Node,
   ElementGeometry,
   ElementGroup,
   IsotropicMaterial,
   FunctionallyGradedMaterial,
   HIM_3D_Section,
   FGM_3D_Section
)

class INP_Interpreter:
   def __init__(self):
      self.model = SimulationModel()
      self.reference = searcher.get_database('translation_reference')['inp']
   
   def read_nodes(self, inp_data: str):
      # Identificando Nodes
      keyword_format = '\*Node\n([^*]*)'
      node = '(-?\d+.\d*e?-?\+?\d*)'
      line_format = f'(\d+),\s*{node},\s*{node}(?:,\s*{node})?'

      # Inserindo Nodes
      lines_data = re.findall(keyword_format, inp_data)[0]
      nodes = re.findall(line_format, lines_data)
      for node in nodes:
         ide, x, y, z = node

         # Convertendo Valores
         ide = int(ide)
         x, y = float(x), float(y)
         z = 0.0 if z == '' else float(z)

         self.model.add_node(ide, x, y, z)
   
   def read_node_sets(self, inp_data: str):
      # Identificando Conjuntos de Nodes
      keyword_format = '\*Nset\s*,\s*nset=([^,\n]+)([^*]+)'
      sets_data = re.findall(keyword_format, inp_data)

      # Tratando Informações
      for set_data in sets_data:
         # Nomeando Informações
         set_name = set_data[0]
         first_break_line_index = set_data[1].index('\n')
         set_params = set_data[1][:first_break_line_index]
         set_numbers = set_data[1][first_break_line_index + 1:]
         
         # Obtendo Números (Ides de Nodes ou Parâmetros de Range)
         number_format = '(\d+)'
         numbers = re.findall(number_format, set_numbers)
         numbers = list(map(int, numbers))

         # Tratando de Acordo com o tipo do Conjunto
         if 'generate' in set_params:
            numbers[1] += 1
            self.model.node_sets[set_name] = range(*numbers)
         else:
            self.model.node_sets[set_name] = numbers
   
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

         # Criando Geometria
         geometry_ide = self.model.add_element_geometry(
            type_info['shape'],
            type_info['base'],
            type_info['grade'],
            type_info['n_nodes'],
            type_info['n_dimensions']
         )

         # Criando Grupo de Elementos
         self.model.add_element_group(group_ide, geometry_ide, type_info.get('theory'))

         # Inserindo Elementos
         for element in elements:
            ide, *node_ides = map(int, element)
            self.model.add_element(group_ide, ide, node_ides)
         
         # Incrementando Ide do Grupo
         group_ide += 1
   
   def read_element_sets(self, inp_data: str):
      # Identificando Conjuntos de Elementos
      keyword_format = '\*Elset\s*,\s*elset=([^,\n]+)([^*]+)'
      sets_data = re.findall(keyword_format, inp_data)

      # Tratando Informações
      for set_data in sets_data:
         # Nomeando Informações
         set_name = set_data[0]
         set_params, set_numbers, *_ = set_data[1].split('\n')
         
         # Obtendo Números (Ides de Nodes ou Parâmetros de Range)
         number_format = '(\d+)\s*,?'
         numbers = re.findall(number_format, set_numbers)
         numbers = list(map(int, numbers))

         # Tratando de Acordo com o tipo do Conjunto
         if 'generate' in set_params:
            self.model.element_sets[set_name] = range(*numbers)
         else:
            self.model.element_sets[set_name] = numbers

   def read_supports(self, inp_data: str):
      # Identificando Supports
      keyword_format = '\*Boundary([^*]+)'
      supports_data = re.findall(keyword_format, inp_data)

      # Tratando Informações
      for support_data in supports_data:
         # Obtendo Informações
         line_format = '(\S+)\s*,\s*(\d+|\w+)\s*(?:,\s*(\d+))?'
         lines_data = re.findall(line_format, support_data)

         for line_data in lines_data:
            # Verificando Natureza do Alvo da Condição de Support
            try:
               # O Alvo é um Node
               boundary_target = int(line_data[0])
            except ValueError:
               # O Alvo é um Node Set
               boundary_target = line_data[0]

            # Verificando Natureza do Início da Condição de Support
            try:
               # O Início é um Índice
               boundary_start = int(line_data[1]) - 1
            except ValueError:
               # O Início é um Tipo
               boundary_start = line_data[1]
            
            # Determinando Índices de Condição com Base no Alvo
            if (type(boundary_start) is int):
               # Verificando se há um Índice de Fim
               if line_data[2]:
                  boundary_end = int(line_data[2]) - 1
               else:
                  boundary_end = boundary_start
               indexes = range(boundary_start, boundary_end + 1)
            else:
               # Tentando Identificar Tipo de Condição
               try:
                  indexes = self.reference['boundary_types'][boundary_start]
               except KeyError:
                  raise KeyError(f'The Boundary Type "{boundary_start}" is not supported.')

            # Tratando Adição de Supports de acordo com o Alvo
            if type(boundary_target) is int:
               for index in indexes:
                  self.model.add_support(boundary_target, self.model.supported_dofs[index])
            else:
               for node_ide in self.model.node_sets[boundary_target]:
                  for index in indexes:
                     self.model.add_support(node_ide, self.model.supported_dofs[index])

   def read(self, inp_data: str):
      # Interpretando Nodes
      self.read_nodes(inp_data)
      self.read_node_sets(inp_data)

      # Interpretando Elementos
      self.read_elements(inp_data)
      self.read_element_sets(inp_data)

      # Interpretando Supports
      self.read_supports(inp_data)

class DAT_Interpreter:
   # Funções Privadas de Adição de Elementos Específicos
   def _add_bezier_triangles(self, group_ide: int, lines_data: str, element_theory: str):
      # Identificando Elementos
      int_ide = '(\d+)'
      property_ides = '\s+\d+' * 3 + '\s+(\d+)'
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
            geometry_ide = self.model.add_element_geometry(
               shape = 'Triangle',
               base = 'Bezier',
               grade = grade,
               n_nodes = len(node_ides),
               n_dimensions = 2
            )
            self.model.add_element_group(group_ide, geometry_ide, element_theory)
            group_ide += 1

         # Inserindo Elementos
         self.model.add_element(grade_to_group[grade], ide, node_ides)
      
      # Retornando Último Valor de Ide de Grupo
      return group_ide

   def _add_bezier_surface(self, group_ide: int, lines_data: str, element_theory: str):
      # Identificando Elementos
      int_ide = '(\d+)'
      property_ides = '\s+\d+' * 3 + '\s+(\d+)' * 2
      line_format = int_ide + property_ides + '\s+(.+)'
      elements = re.findall(line_format, lines_data)
      
      # Ides de Grupos Relacionados com o Grau dos Elementos
      grade_to_group = dict()

      # Analisando Cada Elemento
      for ide, grade_1, grade_2, node_ides in elements:
         # Tipificando Valores
         ide = int(ide)
         grade_1 = int(grade_1)
         grade_2 = int(grade_2)
         grade = (grade_1, grade_2)
         node_ides = list(map(int, node_ides.split()))

         # Verificando se Grupo com o Grau do Elemento Já Existe
         if grade not in grade_to_group:
            grade_to_group[grade] = group_ide
            geometry_ide = self.model.add_element_geometry(
               shape = 'Quadrilateral',
               base = 'Bezier',
               grade = grade,
               n_nodes = len(node_ides),
               n_dimensions = 2
            )
            self.model.add_element_group(group_ide, geometry_ide, element_theory)
            group_ide += 1

         # Inserindo Elementos
         self.model.add_element(grade_to_group[grade], ide, node_ides)
      
      # Retornando Último Valor de Ide de Grupo
      return group_ide
   
   def _add_bspline_elements(self, group_ide: int, lines_data: str, element_theory: str):
      # Identificando Elementos
      int_ide = '(\d+)'
      property_ides = '\s+\d+' * 2 + '\s+(\d+)'
      line_format = int_ide + property_ides + '\s+(.+)'
      elements = re.findall(line_format, lines_data)
      
      # Ides de Grupos Relacionados com o Grau dos Elementos
      geometry_to_info = dict()

      # Analisando Cada Elemento
      for ide, geometry_ide, knot_span in elements:
         # Tipificando Valores
         ide = int(ide)
         geometry_ide = int(geometry_ide)
         knot_span = list(map(int, knot_span.split()))

         # Recuperando Geometria
         geometry = self.model.element_geometries[geometry_ide]

         # Verificando se Ide do Patch Já foi Usado
         if geometry_ide not in geometry_to_info:
            # Gerando Matrix do Node Space
            node_space_matrix = list()
            n = [len(kv) - p - 1 for kv, p in zip(geometry.knot_vectors, geometry.grade)]
            if geometry.n_dimensions == 2:
               for i in range(0, len(geometry.node_space), n[0]):
                  node_space_matrix.append(geometry.node_space[i:i + n[0]])
            else:
               for i in range(0, len(geometry.node_space), (n[1]) * (n[0])):
                  node_space_matrix.append(list())
                  for j in range(i, i + (n[1]) * (n[0]), n[0]):
                     node_space_matrix[-1].append(geometry.node_space[j:j + n[0]])

            # Calculando Multiplicidade dos Knots
            unit_knots = [
               list(sorted(set(kv)))
               for kv in geometry.knot_vectors
            ]
            
            # Adicionando Informações Pertinentes
            geometry_to_info[geometry_ide] = {
               'group_ide': group_ide,
               'node_space_matrix': node_space_matrix,
               'unit_knots': unit_knots
            }
            self.model.add_element_group(group_ide, geometry_ide, element_theory)
            group_ide += 1

         # Recuperando Matriz do Node Space e Multiplicidade dos Knots
         unit_knots = geometry_to_info[geometry_ide]['unit_knots']
         node_space_matrix = geometry_to_info[geometry_ide]['node_space_matrix']
         node_ides = list()

         # Renomeando Informações para Simplificar
         kvs = geometry.knot_vectors
         ks = knot_span
         ps = geometry.grade
         us = unit_knots

         # Calculando Pontos de Paradas dos Ranges da Node Space Matrix
         stop = list()
         for kv, k, u in zip(kvs, ks, us):
            stop.append(kv.index(u[k]))
         
         # Tratamento para Elementos 2D
         if geometry.n_dimensions == 2:
            for i in range(stop[1] - ps[1] - 1, stop[1]):
               for j in range(stop[0] - ps[0] - 1, stop[0]):
                  node_ides.append(node_space_matrix[i][j])

         # Tratamento para Elementos 3D
         else:
            for i in range(stop[2] - ps[2] - 1, stop[2]):
               for j in range(stop[1] - ps[1] - 1, stop[1]):
                  for l in range(stop[0] - ps[0] - 1, stop[0]):
                     node_ides.append(node_space_matrix[i][j][l])

         # Inserindo Elementos
         self.model.add_element(
            geometry_to_info[geometry_ide]['group_ide'], 
            ide,
            node_ides,
            knot_span
         )
      
      # Retornando Último Valor de Ide de Grupo
      return group_ide

   # Funções Privadas de Leitura de Material
   def _read_material_isotropic(self, line_data: str) -> None:
      line_data = line_data.split()
      for i in range(0, len(line_data), 3):
         # Separando Valores
         try:
            material_ide, E, nu = line_data[i:i + 3]
         except ValueError:
            raise ValueError('An Isotropic Material does not have the necessary data in .dat file definition.')

         # Convertendo Valores
         material_ide = int(material_ide)
         E = float(E)
         nu = float(nu)

         # Cadastrando Material
         material = IsotropicMaterial(E, nu, 0.0)
         self.model.materials[material_ide] = material

   def _read_material_density(self, line_data: str) -> None:
      line_data = line_data.split()
      for i in range(0, len(line_data), 2):
         # Separando Valores
         try:
            material_ide, rho = line_data[i:i + 2]
         except ValueError:
            raise ValueError('A Density definition of Isotropic Material is not correct in .dat file.')
         
         # Convertendo Valores
         material_ide = int(material_ide)
         rho = float(rho)

         # Verificando se Há um Material Istrópico para Atribuir a Densidade
         if not self.model.materials.get(material_ide):
            raise IndexError(f'The Material with ID "{material_ide}" does not exist.')
         elif not isinstance(self.model.materials[material_ide], IsotropicMaterial):
            raise TypeError(f'The Material with ID "{material_ide}" is not an Isotropic Material.')
         else:
            self.model.materials[material_ide].rho = rho
   
   def _read_material_fgm(self, line_data: str) -> None:
      line_data = line_data.split()
      for i in range(0, len(line_data), 8):
         # Separando Valores
         try:
            material_ide, E1, nu1, rho1, E2, nu2, rho2, mm = line_data[i:i + 8]
         except ValueError:
            raise ValueError('A FGM Material does not have necessary data in .dat file definition.')
         
         # Convertendo Valores
         material_ide = int(material_ide)
         E1, E2 = float(E1), float(E2)
         nu1, nu2 = float(nu1), float(nu2)
         rho1, rho2 = float(rho1), float(rho2)
         mm = int(mm)

         # Verificando se Há Suporte Para o Modelo Micromecânico Fornecido
         mm_relation = DAT_Interpreter.supported_materials['FGM']['mm_relation']
         try:
            mm = mm_relation[mm]
         except KeyError:
            str_supported = ', '.join(f'{n} (\'{m}\')' for n, m in mm_relation.items())
            raise ValueError(f'The FGM Micromechanical Model "{mm}" is not supported, only: {str_supported}.')

         # Cadastrando Material
         m1 = IsotropicMaterial(E1, nu1, rho1)
         m2 = IsotropicMaterial(E2, nu2, rho2)
         material = FunctionallyGradedMaterial(mm, [m1, m2])
         self.model.materials[material_ide] = material

   # Funções Privadas de Escrita de Material
   def _write_material_isotropic(group: dict[int, IsotropicMaterial]) -> str:
      # Iniciando Output
      n_materials = len(group)
      span = len(str(max(group.keys())))
      output = f'\n%MATERIAL.ISOTROPIC\n{n_materials}\n'

      # Escrevendo Cada Material
      for ide, material in group.items():
         output += f'{ide:<{span}}   {material.E:.8e}   {material.nu:.3f}\n'

      # Escrevendo Densidades
      output += f'\n%MATERIAL.DENSITY\n{n_materials}\n'
      for ide, material in group.items():
         output += f'{ide:<{span}}   {material.rho:.8e}\n'
      
      return output

   def _write_material_fgm(group: dict[int, FunctionallyGradedMaterial]) -> str:
      # Iniciando Output
      n_materials = len(group)
      span = len(str(max(group.keys())))
      output = f'\n%MATERIAL.FGM\n{n_materials}\n'

      # Escrevendo Cada Material
      mm_relation = DAT_Interpreter.supported_materials['FGM']['mm_relation']
      for ide, material in group.items():
         # Tentando Determinar o Número do Modelo Micromecânico
         for n, mm_name in mm_relation.items():
            if mm_name == material.micromechanical_model:
               mm_number = n
               break
         else:
            raise ValueError(f'The FGM Micromechanical Model "{material.micromechanical_model}" of Material with ID "{ide}" is not supported for .dat files.')

         # Segregando Materiais
         m1, m2 = material.materials

         # Escrevendo Material
         output += f'{ide:<{span}}   {m1.E:.8e}   {m1.nu:.3f}   {m1.rho:.8e}   {m2.E:.8e}   {m2.nu:.3f}   {m2.rho:.8e}   {mm_number}\n'
      
      return output

   # Materiais Suportados
   supported_materials = {
      'ISOTROPIC': {
         'class': IsotropicMaterial,
         'read': _read_material_isotropic,
         'write': _write_material_isotropic
      },
      'DENSITY': {
         'read': _read_material_density
      },
      'FGM': {
         'class': FunctionallyGradedMaterial,
         'read': _read_material_fgm,
         'write': _write_material_fgm,
         'mm_relation': {
            1: 'voigt',
            2: 'mori_tanaka'
         }
      }
   }

   # Funções Privadas de Leitura de Seção
   def _read_section_him_3d(self, line_data: str) -> None:
      line_data = line_data.split()
      for i in range(0, len(line_data), 2):
         # Separando Valores
         try:
            section_ide, material_ide = map(int, line_data[i:i + 2])
         except ValueError:
            raise ValueError('A Homogeneous Isotropic 3D Section does not have the necessary data in .dat file definition.')

         # Cadastrando Seção
         section = HIM_3D_Section(material_ide)
         self.model.sections[section_ide] = section

   def _read_section_fgm_3d(self, line_data: str) -> None:
      line_data = line_data.split()
      n_volume_fractions = 0
      i = 0
      while i < len(line_data):
         # Separando Valores
         try:
            # Lendo Dados Conhecidos
            section_ide, material_ide, n_volume_fractions = map(int, line_data[i:i + 3])
            
            # Calculando o Index de Início da Próxima Seção
            next_section_index = i + 3 + 2 * n_volume_fractions
            
            # Lendo ID dos Nós e sua Respectiva Fração de Volume
            volume_fractions = dict()
            for j in range(i + 3, next_section_index, 2):
               node_ide = int(line_data[j])
               volume_fraction = float(line_data[j + 1])
               volume_fractions[node_ide] = volume_fraction

         except ValueError:
            raise ValueError('A FGM 3D Section does not have the necessary data in .dat file definition.')

         # Cadastrando Seção
         section = FGM_3D_Section(material_ide, volume_fractions)
         self.model.sections[section_ide] = section

         # Definindo Próximo Index
         i = next_section_index

   # Funções Privadas de Escrita de Seção
   def _write_section_him_3d(group: dict[int, HIM_3D_Section]) -> str:
      # Iniciando Output
      n_sections = len(group)
      span = len(str(max(group.keys())))
      output = f'\n%SECTION.HOMOGENEOUS.ISOTROPIC.3D\n{n_sections}\n'

      # Escrevendo Cada Seção
      for ide, section in group.items():
         output += f'{ide:<{span}}   {section.material_ide}\n'
      
      return output

   def _write_section_fgm_3d(group: dict[int, FGM_3D_Section]) -> str:
      # Iniciando Output
      n_sections = len(group)
      span = len(str(max(group.keys())))
      output = f'\n%SECTION.FGM.3D\n{n_sections}\n'

      # Escrevendo Cada Seção
      for ide, section in group.items():
         output += f'{ide:<{span}}   {section.material_ide}   {len(section.volume_fractions)}\n'
         
         # Escrevendo Cada Fração de Volume
         node_span = len(str(max(section.volume_fractions.keys())))
         for node_ide, volume_fraction in section.volume_fractions.items():
            output += f'{node_ide:<{node_span}}   {volume_fraction:.8e}\n'
      
      return output

   # Seções Suportadas
   supported_sections = {
      'HOMOGENEOUS.ISOTROPIC.3D': {
         'class': HIM_3D_Section,
         'read': _read_section_him_3d,
         'write': _write_section_him_3d
      },
      'FGM.3D': {
         'class': FGM_3D_Section,
         'read': _read_section_fgm_3d,
         'write': _write_section_fgm_3d
      }
   }

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
   
   def read_node_solver_order(self, dat_data: str) -> str:
      # Identificando Ordem de Resolução
      keyword_format = '%NODE.SOLVER.ORDER\n\d+\n([^%]*)'

      # Inserindo Ordem de Resolução
      node_ides = re.findall(keyword_format, dat_data)
      if len(node_ides) > 0:
         self.model.node_solver_order = [int(ide) for ide in node_ides[0].split()]

   def read_patches(self, dat_data: str):
      # Identificando Patches
      keyword_format = '%PATCH\n(\d+)\n([^%]*)'
      lines_data = re.findall(keyword_format, dat_data)

      # Verificando se Há Patches
      if len(lines_data) > 0:
         # Nomeando Dados
         n_patches = int(lines_data[0][0])
         lines_data = lines_data[0][1]
         supported_types = '|'.join(["'" + st + "'" for st in self.reference['patch_types']])
         patch_start_format = f'(\d+)\s+({supported_types})\s+1'

         # Separando Patches
         for _ in range(n_patches):
            # Localizando Dados Iniciais do Patch
            result = re.search(patch_start_format, lines_data)
            patch_ide, patch_type = result.groups()
            patch_ide = int(patch_ide)
            patch_type = patch_type[1:-1]
            index_start = result.end()

            # Determinando Geometria do Patch
            patch_geometry = self.reference['patch_types'][patch_type]

            # Localizando Dados Finais do Patch
            result = re.search(patch_start_format, lines_data[index_start:])
            index_end = None
            if result:
               index_end = result.start() + index_start
            
            # Lendo Knot Vectors
            patch_data = lines_data[index_start:index_end]
            knot_vectors = list()
            grade = list()
            while True:
               vector_format = "(\d+)\s+'General'\s+(\d+)"
               vector_result = re.search(vector_format, patch_data)

               # Parando Loop se Nenhum Knot Vector for Encontrado
               if not vector_result:
                  break

               # Atualizando Patch Data para Não incluir o Início do Patch Atual
               patch_data = patch_data[vector_result.end():]

               # Lendo Informações Básicas do Knot Vector
               grade_i, n_knots_i = vector_result.groups()
               grade_i = int(grade_i)
               n_knots_i = int(n_knots_i)

               # Fatiando Itens do Patch Data e Lendo Knots e Multiplicidades
               patch_data_splited = patch_data.split()
               knot_set = [float(patch_data_splited[i]) for i in range(n_knots_i)]
               knot_multiplicity = [int(patch_data_splited[i]) for i in range(n_knots_i, 2 * n_knots_i)]
               
               # Construindo Vetor de Knot
               knot_vector = []
               for knot, multiplicity in zip(knot_set, knot_multiplicity):
                  knot_vector += [knot] * multiplicity
               
               # Salvando Valores 
               knot_vectors.append(knot_vector)
               grade.append(grade_i)

            # Lendo Node Space
            node_space = [int(n) for n in patch_data_splited[2 * n_knots_i:]]

            # Calculando Número de Nodes por Elementos
            n_nodes = 1
            for p in grade:
               n_nodes *= p + 1

            # Adicionando Patch como Uma Geometria
            self.model.element_geometries[patch_ide] = ElementGeometry(
               shape = patch_geometry['shape'],
               base = patch_geometry['base'],
               grade = grade,
               n_nodes = n_nodes,
               n_dimensions = patch_geometry['n_dimensions'],
               knot_vectors =  knot_vectors,
               node_space = node_space
            )
            
            # Descartando Patch Localizado
            lines_data = lines_data[index_start:]

   def read_elements(self, dat_data: str):
      # Identificando Grupos de Elementos
      keyword_format = '%ELEMENT\.(.*)\n\d+\n([^%]*)'
      groups_data = re.findall(keyword_format, dat_data)

      # Analisando Cada Grupo
      group_ide = 1
      for element_type, lines_data in groups_data:
         # Dividindo Tipo e Teoria do Grupo de Elementos
         element_theory = None
         if element_type not in self.reference['elements']: 
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
         
         # Adaptando Leitura - Elementos de Bezier
         if type_info['base'] == 'Bezier':
            if type_info['shape'] == 'Triangle':
               group_ide = self._add_bezier_triangles(group_ide, lines_data, element_theory)
            elif type_info['shape'] == 'Quadrilateral':
               group_ide = self._add_bezier_surface(group_ide, lines_data, element_theory)
            else:
               raise KeyError(f'The Shape \"{type_info["shape"]}\" with Base \"{type_info["base"]}\" is not supported for .dat files.')
         
         # Adaptando Leitura - Elementos de BSpline
         elif type_info['base'] == 'BSpline':
            group_ide = self._add_bspline_elements(group_ide, lines_data, element_theory)
         
         # Adaptando Leitura - Elementos de Langrange
         else:
            int_ide = '(\d+)'
            node_ide = '\s+' + int_ide
            property_ides = '\s+\d+' * 2
            line_format = int_ide + property_ides + type_info['n_nodes'] * node_ide
            elements = re.findall(line_format, lines_data)

            # Criando Geometria
            geometry_ide = self.model.add_element_geometry(
               type_info['shape'],
               type_info['base'],
               type_info['grade'],
               type_info['n_nodes'],
               type_info['n_dimensions']
            )

            # Criando Grupo de Elementos
            self.model.add_element_group(group_ide, geometry_ide, element_theory)

            # Inserindo Elementos
            for element in elements:
               ide, *node_ides = map(int, element)
               self.model.add_element(group_ide, ide, node_ides)
         
         # Incrementando Ide do Grupo
         group_ide += 1
   
   def read_supports(self, dat_data: str):
      # Identificando Supports
      keyword_format = '%NODE\.SUPPORT\n\d+\n([^%]*)'
      bool_dof = '\s+(\d)'
      line_format = f'(\d+){bool_dof * 6}'

      # Inserindo Supports
      lines_data = re.findall(keyword_format, dat_data)
      if len(lines_data) > 0:
         supports = re.findall(line_format, lines_data[0])
         for support in supports:
            node_ide, *bool_dofs = support
            node_ide = int(node_ide)
            for index, bd in enumerate(bool_dofs):
               if bd == '1':
                  dof = self.model.supported_dofs[index]
                  self.model.add_support(node_ide, dof)

   def read_materials(self, dat_data: str):
      # Identificando Materiais
      keyword_format = '%MATERIAL\.(.+)\n\d+\n([^%]*)'

      # Inserindo Materiais
      lines_data = re.findall(keyword_format, dat_data)
      for line_data in lines_data:
         # Extraindo Informações
         type, line_data = line_data

         # Tentando Ler Material de Acordo com o Tipo
         try:
            read_function = DAT_Interpreter.supported_materials[type]['read']
            read_function(self, line_data)
         except KeyError:
            raise KeyError(f'The Material Type "{type}" is not supported for .dat files.')

   def read_sections(self, dat_data: str):
      # Identificando Seções
      keyword_format = '%SECTION\.(.+)\n\d+\n([^%]*)'

      # Inserindo Seções
      lines_data = re.findall(keyword_format, dat_data)
      for line_data in lines_data:
         # Extraindo Informações
         type, line_data = line_data

         # Tentando Ler Seção de Acordo com o Tipo
         try:
            read_function = DAT_Interpreter.supported_sections[type]['read']
            read_function(self, line_data)
         except KeyError:
            raise KeyError(f'The Section Type "{type}" is not supported for .dat files.')

   def read(self, dat_data: str):
      # Interpretando Nodes
      self.read_nodes(dat_data)

      # Interpretando Ordem de Resolução
      self.read_node_solver_order(dat_data)

      # Interpretando Patches
      self.read_patches(dat_data)

      # Interpretando Elementos
      self.read_elements(dat_data)

      # Interpretando Supports
      self.read_supports(dat_data)

      # Interpretando Materiais
      self.read_materials(dat_data)

      # Interpretando Seções
      self.read_sections(dat_data)
   
   def write_nodes(self) -> str:
      # Parâmetros Iniciais
      n_nodes = len(self.model.nodes)
      span = len(str(n_nodes))
      output = f'\n%NODE\n{n_nodes}\n\n%NODE.COORD\n{n_nodes}\n'

      # Escrevendo Cada Node
      weighted_nodes = list()
      for ide, node in self.model.nodes.items():
         offset = span - len(str(ide))
         offset = ' ' * offset
         output += f'{ide}{offset}   {node.x:+.8e}   {node.y:+.8e}   {node.z:+.8e}\n'

         # Verificando se Node tem Peso
         if node.weight:
            weighted_nodes.append(ide)

      # Escrevendo Pesos
      n_weights = len(weighted_nodes)
      if n_weights > 0:
         max_width = len(str(n_weights))
         output += f'\n%CONTROL.POINT.WEIGHT\n{n_weights}\n'
         for ide in weighted_nodes:
            output += f'{ide:<{max_width}}   {self.model.nodes[ide].weight:.6e}\n'
      
      return output
   
   def write_node_solver_order(self) -> str:
      # Parâmetros Iniciais
      solver_order = self.model.node_solver_order
      n = len(solver_order)
      output = f'\n%NODE.SOLVER.ORDER\n{n}\n'

      # Escrevendo Ordem
      max_width = len(str(n))
      for index in range(0, len(solver_order), 15):
         output += ' '.join([f'{node_ide:>{max_width}}' for node_ide in solver_order[index:index + 15]])
         output += '\n'
      
      return output

   def write_patches(self) -> str:
      # Procurando uma Geometria de base BSpline
      patch_ides = list()
      for ide, geometry in self.model.element_geometries.items():
         if geometry.base == 'BSpline':
            patch_ides.append(ide)
      
      # Escrevendo Patches se Houver Necessidade
      output = ''
      n_patches = len(patch_ides)
      if n_patches > 0:
         # Escrevendo Keyword do Patch
         output += f'\n%PATCH\n{n_patches}\n'
         
         # Escrevendo cada Patch
         for patch_ide in patch_ides:
            # Determinando Tipo do Patch
            patch_type = ''
            patch_geometry = self.model.element_geometries[patch_ide]
            for type, patch_info in self.reference['patch_types'].items():
               if (
                  patch_info['shape'] == patch_geometry.shape and
                  patch_info['n_dimensions'] == patch_geometry.n_dimensions
               ):
                  patch_type = type
                  break
            else:
               raise ValueError(f'Patch Type for "BSpline {patch_geometry.shape}" with {patch_geometry.n_dimensions} dimension(s) is not supported for writing.')
            
            # Escrevendo Definição Básica de um Patch
            output += f'{patch_ide} \'{patch_type}\' 1\n'

            # Escrevendo Vetores de Knot
            for degree, knot_vector in zip(patch_geometry.grade, patch_geometry.knot_vectors):
               knot_set = list(set(knot_vector))
               knot_set.sort()
               n_knot_set = len(knot_set)
               knot_multiplicity = ' '.join([str(knot_vector.count(k)) for k in knot_set])
               knot_set = '\n'.join([f'{k:.6e}' for k in knot_set])
               output += f'{degree}   \'General\'   {n_knot_set}\n{knot_set}\n{knot_multiplicity}\n'
            
            # Escrevendo Nodes
            max_width = len(str(len(self.model.nodes)))
            for index in range(0, len(patch_geometry.node_space), 15):
               output += ' '.join([f'{node_ide:>{max_width}}' for node_ide in patch_geometry.node_space[index:index + 15]])
               output += '\n'

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
         geometry = self.model.element_geometries[group.geometry_ide]

         # Pesquisando Label - Elementos de Lagrange
         if geometry.base == 'Lagrange':
            for reference_type, reference_geometry in self.reference['elements'].items():
               if (
                  reference_geometry['shape'] == geometry.shape and
                  reference_geometry['base'] == geometry.base and
                  reference_geometry['grade'] == geometry.grade and
                  reference_geometry['n_nodes'] == geometry.n_nodes and
                  reference_geometry['n_dimensions'] == geometry.n_dimensions
               ):
                  element_type = reference_type
                  break
            else:
               raise ValueError(f'The "{geometry.base} {geometry.shape}" Geometry with grade {geometry.grade} and {geometry.n_nodes} nodes and {geometry.n_dimensions} dimensions is not supported for .dat files.')
         
         # Pesquisando Label - Elementos de Bezier e BSpline
         else:
            for reference_type, reference_geometry in self.reference['elements'].items():
               if (
                  reference_geometry['shape'] == geometry.shape and
                  reference_geometry['base'] == geometry.base and
                  reference_geometry['n_dimensions'] == geometry.n_dimensions
               ):
                  element_type = reference_type
                  break
            else:
               raise ValueError(f'The "{geometry.base} {geometry.shape}" Geometry with {geometry.n_dimensions} dimensions is not supported for .dat files.')

         # Verificando se Elemento Tem uma Teoria
         if group.theory:
            for dat_theory, reference_theory in self.reference['theories'].items():
               if reference_theory == group.theory:
                  element_type = f'{dat_theory}.{element_type}'
                  break
            else:
               raise ValueError(f'The Theory "{group.theory}" is not supported for .dat files.')

         output += f'\n%ELEMENT.{element_type}\n{n_elements}\n'

         # Escrevendo Cada Elemento - Elementos de Lagrange
         if geometry.base == 'Lagrange':
            # Alterando Informações para casos Especiais
            if geometry.shape == 'Line':
               more_info = '1'
            else:
               more_info = '1  1'
            
            for ide, element in group.elements.items():
               offset = span - len(str(ide))
               offset = ' ' * offset
               node_ides = '   '.join([ f'{nis:>{node_ide_span}}' for nis in element.node_ides ])
               output += f'{ide}{offset}   {more_info}   {node_ides}\n'
         
         # Escrevendo Cada Elemento - Elementos de Bezier
         elif geometry.base == 'Bezier':
            more_info = f'1  1  1  {geometry.grade}'
            for ide, element in group.elements.items():
               offset = span - len(str(ide))
               offset = ' ' * offset
               node_ides = '   '.join([ f'{nis:>{node_ide_span}}' for nis in element.node_ides ])
               output += f'{ide}{offset}   {more_info}   {node_ides}\n'
         
         # Escrevendo Cada Elemento - Elementos de Bezier
         elif geometry.base == 'BSpline':
            more_info = f'1  1  {group.geometry_ide}'
            for ide, element in group.elements.items():
               offset = span - len(str(ide))
               offset = ' ' * offset
               knot_spans = '   '.join([ f'{k:<{node_ide_span}}' for k in element.knot_span ])
               output += f'{ide}{offset}   {more_info}   {knot_spans}\n'

      output = f'\n%ELEMENT\n{total_elements}\n' + output
      return output
   
   def write_supports(self) -> str:
      # Parâmetros Iniciais
      n_supports = len(self.model.supports)
      span = len(str(n_supports))
      output = f'\n%NODE.SUPPORT\n{n_supports}\n'

      # Escrevendo Cada Support
      for node_ide, dofs in self.model.supports.items():
         offset = span - len(str(node_ide))
         offset = ' ' * offset
         dofs_str = [
            '1' if dof in dofs else '0' 
            for dof in self.model.supported_dofs
         ]
         dofs_str = ' '.join(dofs_str)
         output += f'{node_ide}{offset}   {dofs_str}\n'
      return output
   
   def write_materials(self) -> str:
      # Parâmetros Iniciais
      n_materials = len(self.model.materials)
      output = f'\n%MATERIAL\n{n_materials}\n'

      # Criando Grupos de Materiais
      groups = dict()
      for type in DAT_Interpreter.supported_materials.keys():
         groups[type] = dict()

      # Tentando Organizar Materiais em Grupos
      for ide, material in self.model.materials.items():
         # Verificando se o Material é Supportado
         for type, s in DAT_Interpreter.supported_materials.items():
            if s.get('class') and isinstance(material, s['class']):
               groups[type][ide] = material
               break
         else:
            raise TypeError(f'The Material Type "{material.__class__.__name__}" is not supported for .dat files.')
      
      # Escrevendo Grupos
      for type, group in groups.items():
         if len(group) > 0:
            output += self.supported_materials[type]['write'](group)

      return output
   
   def write_sections(self) -> str:
      # Parâmetros Iniciais
      n_sections = len(self.model.sections)
      output = f'\n%SECTION\n{n_sections}\n'

      # Criando Grupos de Seções
      groups = dict()
      for type in DAT_Interpreter.supported_sections.keys():
         groups[type] = dict()

      # Tentando Organizar Seções em Grupos
      for ide, section in self.model.sections.items():
         # Verificando se a Seção é Supportada
         for type, s in DAT_Interpreter.supported_sections.items():
            if s.get('class') and isinstance(section, s['class']):
               groups[type][ide] = section
               break
         else:
            raise TypeError(f'The Section Type "{section.__class__.__name__}" is not supported for .dat files.')
      
      # Escrevendo Grupos
      for type, group in groups.items():
         if len(group) > 0:
            output += self.supported_sections[type]['write'](group)

      return output

   def write(self) -> str:
      # Inicializando Output
      output = '%HEADER\n'

      # Escrevendo Nodes
      if len(self.model.nodes) > 0:
         output += self.write_nodes()

      # Escrevendo Supports
      if len(self.model.supports) > 0:
         output += self.write_supports()
      
      # Escrevendo Materiais
      if len(self.model.materials) > 0:
         output += self.write_materials()

      # Escrevendo Seções
      if len(self.model.sections) > 0:
         output += self.write_sections()

      # Escrevendo Ordem de Resolução
      if len(self.model.node_solver_order) > 0:
         output += self.write_node_solver_order()

      # Escrevendo Patches
      output += self.write_patches()

      # Escrevendo Elementos
      if len(self.model.element_groups) > 0:
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
      self.gt = GeometricalTransformer()
   
   def tesselate_bezier_curve(self, grade: int, points: list[Node], n_regions: int):
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
   
   def write_bezier_triangles(self, grade: int, group: ElementGroup) -> str:
      # Parâmetros Iniciais
      output = ''
      p = grade
      nodes_total = int(3 + 3 * (p - 1) + ((p - 2) * (p - 1) / 2))
      indexes_corner = [1, nodes_total - p, nodes_total]

      # Index dos Nodes Intermediários
      ie1 = [int(1 + ((i + 1) * (i + 2) / 2)) for i in range(p - 1)]
      ie2 = [nodes_total - p + 1 + i for i in range(p - 1)]
      ie3 = [int((i + 2) * (i + 3) / 2) for i in range(p - 1)]
      ie3.reverse()
      indexes_by_edge = [ie1, ie2, ie3]

      # Escrevendo Path de Cada Elemento
      for element in group.elements.values():
         # Inicializando Path
         output += f'\n      <path d="'

         # Lado 1 - Ponto Incial
         node_corner_1 = self.model.nodes[element.node_ides[indexes_corner[0] - 1]]
         output += f'M {node_corner_1.x:.8e} {node_corner_1.y:.8e} '

         # Construindo Curvas de Bezier para Cada Lado
         for indexes_edge, index_corner in zip(indexes_by_edge, indexes_corner[1:] + [indexes_corner[0]]):
            # Obtendo Pontos do Lado
            node_corner_2 = self.model.nodes[element.node_ides[index_corner - 1]]
            points = [self.model.nodes[element.node_ides[i - 1]] for i in indexes_edge]
            points.append(node_corner_2)
            points.insert(0, node_corner_1)

            # Calculando Fator de Colinearidade dos Pontos
            c_factor = self.gt.calculate_colinearity([[p.x, p.y] for p in points])

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
   
   def write_bspline_surface(self, geometry: ElementGeometry, group: ElementGroup) -> str:
      # Montando Matriz de Identificadores do Pontos de Controle
      output = ''
      control_points_ides = list()
      n_basis_u = len(geometry.knot_vectors[0]) - geometry.grade[0] - 1
      n_basis_v = len(geometry.knot_vectors[1]) - geometry.grade[1] - 1
      for i in range(n_basis_u):
         control_points_ides.append(geometry.node_space[i::n_basis_u])
      
      # Criando Pontos de Controle e Pesos
      control_points = [
         [
            [
               self.model.nodes[control_points_ides[i][j]].x,
               self.model.nodes[control_points_ides[i][j]].y
            ]
            for j in range(n_basis_v)
         ]
         for i in range(n_basis_u)
      ]
      weights = [
         [
            self.model.nodes[control_points_ides[i][j]].weight or 1.0
            for j in range(n_basis_v)
         ]
         for i in range(n_basis_u)
      ]

      # Criando Superfície NURBS
      nurbs_surface = NURBS_Surface(
         degree = geometry.grade,
         knot_vectors = geometry.knot_vectors,
         control_points = control_points,
         weights = weights
      )

      # Criando Intervalos Paramétricos de Elementos
      d_u, d_v = geometry.grade
      d_u *= 2
      d_v *= 2
      k_u = sorted(list(set(geometry.knot_vectors[0])))
      k_v = sorted(list(set(geometry.knot_vectors[1])))
      for j in range(len(k_v) - 1):
         v1, v2 = k_v[j:j + 2]
         v = [v1 + k * (v2 - v1) / (d_v) for k in range(d_v)]
         v.append(v2)
         for i in range(len(k_u) - 1):
            u1, u2 = k_u[i:i + 2]
            u = [u1 + k * (u2 - u1) / (d_u) for k in range(d_u)]
            u.append(u2)

            # Criando Pontos da Fronteira do Elemento
            edges = [
               [
                  nurbs_surface(ui, v1)
                  for ui in u
               ],
               [
                  nurbs_surface(u2, vi)
                  for vi in v
               ],
               [
                  nurbs_surface(ui, v2)
                  for ui in list(reversed(u))
               ],
               [
                  nurbs_surface(u1, vi)
                  for vi in list(reversed(v))
               ]
            ]

            # Iniciando Path do Elemento
            output += f'\n      <path d="'

            # Escrevendo Ponto Inicial
            output += f'M {edges[0][0][0]:.8e} {edges[0][0][1]:.8e} '

            # Percorendo Lados
            for edge in edges:
               # Resumindo Path em Uma linha reta para um fator baixo
               c_factor = self.gt.calculate_colinearity(edge)
               if c_factor < 0.1:
                  output += f'L {edge[-1][0]:.8e} {edge[-1][1]:.8e} '

               # Tesselando Curva se o Fator de Colinearidade for Alto
               else:
                  for index in range(1, len(edge) - 1, 2):
                     x_c = bezier_equiv_coord(edge[index][0], edge[index - 1][0], edge[index + 1][0])
                     y_c = bezier_equiv_coord(edge[index][1], edge[index - 1][1], edge[index + 1][1])
                     output += f'Q {x_c:.8e} {y_c:.8e}, {edge[index + 1][0]:.8e} {edge[index + 1][1]:.8e} '
            
            # Finalizando Path
            output += 'Z" />'
      return output

   def write_finite_elements(self, grade: int, group: ElementGroup) -> str:
      output = ''

      # Tratamento para Elementos Lineares
      if grade == 1:
         for element in group.elements.values():
            output += '\n      <polygon points="'

            # Escrevendo Cada Ponto
            for ide in element.node_ides:
               node = self.model.nodes[ide]
               output += f'{node.x:.8e},{node.y:.8e} ' 
            output += '" />'

      # Tratamento para Elementos Quadráticos
      else:
         for element in group.elements.values():
            # Escrevendo Ponto Inicial
            node = self.model.nodes[element.node_ides[0]]
            output += f'\n      <path d="M {node.x:.8e} {node.y:.8e} '

            # Escrevendo Lados como Curvas Quadráticas de Bezier
            for i in list(range(2, len(element.node_ides), 2)) + [0]:
               n2 = self.model.nodes[element.node_ides[i]]
               nc = self.model.nodes[element.node_ides[i - 1]]
               n0 = self.model.nodes[element.node_ides[i - 2]]
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
         # Identificando Geometria do Grupo
         geometry = self.model.element_geometries[group.geometry_ide]

         # Tratamento para Elementos de Bezier
         if geometry.shape == 'Triangle' and geometry.base == 'Bezier':
            output += self.write_bezier_triangles(geometry.grade, group)
         
         # Tratamento para Superfícies B-Spline
         elif geometry.shape == 'Quadrilateral' and geometry.base == 'BSpline':
            output += self.write_bspline_surface(geometry, group)

         # Tratamento para Elementos Finitos Tradicionais
         else:
            output += self.write_finite_elements(geometry.grade, group)

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