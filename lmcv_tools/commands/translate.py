from ..interface import filer, searcher
from ..models.translation_components import (
   INP_Interpreter,
   DAT_Interpreter
)

# Funções de Tradução
def inp_to_dat(input_data: str):
   # Instanciando Interpretadores
   inp_interpreter = INP_Interpreter()
   dat_interpreter = DAT_Interpreter()

   # Interpretando Input
   inp_interpreter.read(input_data)

   # Traduzindo Elementos
   new_element_groups = dict()
   translation = searcher.get_database('translation_reference')['inp_to_dat']
   for element_type, elements in inp_interpreter.model.element_groups.items():
      # Criando Novo Grupo Com Tipo Traduzido
      element_type = translation['element_types'][element_type]
      type_geometry = element_type.split('.')[-1]
      nodes_reordering = translation['nodes_reordering'][type_geometry]
      new_element_groups[element_type] = dict()

      # Reordenando Nodes
      for ide, node_ides in elements.items():
         node_ides = [node_ides[i - 1] for i in nodes_reordering ]
         new_element_groups[element_type][ide] = node_ides
   
   # Substituindo Elementos Pela Tradução
   inp_interpreter.model.element_groups = new_element_groups

   # Transferindo Modelos de Simulação Interpretados
   dat_interpreter.model = inp_interpreter.model

   # Retornando Tradução
   return dat_interpreter.write()

def dat_to_svg():
   pass

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
