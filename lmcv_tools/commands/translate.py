from ..interface import filer, searcher
from ..models.translation_components import (
   INP_Interpreter,
   DAT_Interpreter,
   SVG_Interpreter
)

# Funções de Tradução
def inp_to_dat(input_data: str):
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
      # Pegando Reordenação da Referência
      nodes_reordering = reference['nodes_reordering'][group.geometry.name][str(group.geometry.grade)]

      # Sobescrevendo Ordem dos Nodes
      for ide, node_ides in group.elements.items():
         node_ides = [node_ides[i - 1] for i in nodes_reordering ]
         dat_interpreter.model.element_groups[group_ide].elements[ide] = node_ides

   # Retornando Tradução
   return dat_interpreter.write()

def dat_to_svg(input_data: str):
   # Instanciando Interpretadores
   dat_interpreter = DAT_Interpreter()
   svg_interpreter = SVG_Interpreter()

   # Interpretando Input
   dat_interpreter.read(input_data)

   # Convertendo Sistema de Coordenadas
   x_coords = [n.x for n in dat_interpreter.model.nodes.values()]
   y_coords = [n.y for n in dat_interpreter.model.nodes.values()]
   x_min = min(x_coords)
   x_max = max(x_coords)
   delta_x = x_max - x_min
   y_min = min(y_coords)
   y_max = max(y_coords)
   delta_y = y_max - y_min
   scale_coeff = (90 / delta_x) if delta_x > delta_y else (90 / delta_y)
   for ide, node in dat_interpreter.model.nodes.items():
      # Ajustando Coordenadas para Eixo Padrão do SVG (Tudo Positivo | Eixo Vertical Invertido)
      x = node.x - x_min
      y = abs(node.y - y_max)

      # Ajustando Escala e Posição
      x = x * scale_coeff + 5
      y = y * scale_coeff + 5

      svg_interpreter.model.add_node(ide, x, y, 0, node.weight)
   svg_interpreter.model.element_groups = dat_interpreter.model.element_groups

   # Retornando Tradução
   return svg_interpreter.write()

# Traduções Suportadas
supported_translations = {
   ('.inp', '.dat'): inp_to_dat,
   ('.dat', '.svg'): dat_to_svg
}

def start(input_path: str, output_extension: str):
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
   output_data = translation_function(input_data)

   # Escrevendo Tradução no Output
   output_path = input_path[:last_dot_index] + output_extension
   filer.write(output_path, output_data)
