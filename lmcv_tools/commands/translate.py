from ..interface import filer, searcher
from ..models.geometry import GeometricalTransformer
from ..models.interpreters import (
   INP_Interpreter,
   DAT_Interpreter,
   SVG_Interpreter
)

# Funções de Tradução
def inp_to_dat(input_data: str, flags: dict[str, str]):
   # Instanciando Interpretadores
   inp_interpreter = INP_Interpreter()
   dat_interpreter = DAT_Interpreter()

   # Interpretando Input
   inp_interpreter.read(input_data)

   # Transferindo Modelo de Simulação Interpretado
   dat_interpreter.model = inp_interpreter.model

   # Reordenando Nodes
   reference = searcher.get_database('translation_reference')['inp_to_dat']
   for group_ide, group in dat_interpreter.model.element_groups.items():
      # Idenfiticando Geometria do Grupo
      geometry = dat_interpreter.model.element_geometries[group.geometry_ide]
      
      # Pegando Reordenação da Referência
      nodes_reordering = reference['nodes_reordering'][geometry.shape][str(geometry.grade)]

      # Sobescrevendo Ordem dos Nodes
      for ide, element in group.elements.items():
         node_ides = [element.node_ides[i - 1] for i in nodes_reordering ]
         dat_interpreter.model.add_element(group_ide, ide, node_ides)

   # Retornando Tradução
   return dat_interpreter.write()

def dat_to_svg(input_data: str, flags: dict[str, str]):
   # Instanciando Interpretadores
   dat_interpreter = DAT_Interpreter()
   svg_interpreter = SVG_Interpreter()

   # Interpretando Input
   dat_interpreter.read_nodes(input_data)
   dat_interpreter.read_patches(input_data)
   dat_interpreter.read_elements(input_data)

   # Transferindo Modelos de Simulação
   svg_interpreter.model = dat_interpreter.model

   # Instanciando Transformador Geométrico e Configurações Padrões de Projeção
   gt = GeometricalTransformer()
   projection_type = 'parallel'
   rotations = list()

   # Identificando Configurações de Projeção a partir das Flags
   if len(flags) > 0:
      flag_keys = flags.keys()

      # Identificando Tipo de Projeção
      if ('-p' in flag_keys) or ('--projection' in flag_keys): 
         projection_type = flags.get('-p') or flags.get('--projection')
         if projection_type not in ('parallel', 'perspective'):
            raise ValueError(f'The projection type "{projection_type}" is not supported.')

         # Tratando Caso de Tipo de Projeção ser "perspective"
         if projection_type == 'perspective':
            try:
               x_cop = float(flags['-x'])
               y_cop = float(flags['-y'])
               z_cop = float(flags['-z'])
            except KeyError:
               raise ValueError(f'The projection type "perspective" requires 3 other flags: -x, -y and -z (the coordinates of the projection center).')

      # Lendo Rotações a Partir das Flags, se Ouverem
      for flag, value in flags.items():
         if (flag == '--Rx') or (flag == '--Ry') or (flag == '--Rz'):
            angle = float(value)
            rotations.append(
               gt.Rx(angle) if flag == '--Rx' else
               gt.Ry(angle) if flag == '--Ry' else
               gt.Rz(angle)
            )
   
   # Transportando Centroid para a Origem
   coordinates = [(n.x, n.y, n.z) for n in dat_interpreter.model.nodes.values()]
   centroid = gt.calculate_centroid(coordinates)
   coordinates = [gt.translate(*c, -centroid[0], -centroid[1], -centroid[2]) for c in coordinates]

   # Rotacionando Coordenadas
   coordinates = [gt.rotate(*c, rotations) for c in coordinates]

   # Projetando Coordenadas
   coordinates = [
      gt.project_parallel(*c)
      if projection_type == 'parallel' else
      gt.project_perspective(*c, x_cop, y_cop, z_cop)
      for c in coordinates
   ]
   u = [iso[0] for iso in coordinates]
   v = [iso[1] for iso in coordinates]

   # Ajustando Coordenadas ao Sistema SVG
   u_min = min(u)
   u_max = max(u)
   delta_u = u_max - u_min
   v_min = min(v)
   v_max = max(v)
   delta_v = v_max - v_min
   scale_coeff = (90 / delta_u) if delta_u > delta_v else (90 / delta_v)
   for (ide, node), u_i, v_i in zip(dat_interpreter.model.nodes.items(), u, v):
      # Ajustando Coordenadas para Eixo Padrão do SVG (Tudo Positivo | Eixo Vertical Invertido)
      x = u_i - u_min
      y = abs(v_i - v_max)

      # Ajustando Escala e Posição
      x = x * scale_coeff + 5
      y = y * scale_coeff + 5

      svg_interpreter.model.add_node(ide, x, y, 0, node.weight)

   # Retornando Tradução
   return svg_interpreter.write()

# Traduções Suportadas
supported_translations = {
   ('.inp', '.dat'): inp_to_dat,
   ('.dat', '.svg'): dat_to_svg
}

def start(input_path: str, output_extension: str, args: list[str], flags: dict[str, str]):
   # Lendo Arquivo de Input
   input_data = filer.read(input_path)

   # Verificando se a Tradução é Suportada
   last_dot_index = input_path.rfind('.')
   input_extension = input_path[last_dot_index:]
   format_pair = (input_extension, output_extension)
   try:
      translation_function = supported_translations[format_pair]
   except KeyError:
      raise KeyError(f'The translation of {input_extension} to {output_extension} is not supported.')
   
   # Traduzindo
   output_data = translation_function(input_data, flags)

   # Escrevendo Tradução no Output
   output_path = input_path[:last_dot_index] + output_extension
   filer.write(output_path, output_data)
