from ..interface import filer, messenger
from ..models.extraction_components import (
   Condition,
   Attribute
)

# Funções Globais
def change(attribute_name: str, attribute_value: str, dat_data: str, condition: str = None):
   # Instanciando Tabela de Resultado e Condição de Atributos
   attribute = Attribute(attribute_name)
      
   # Alterando Valor do Atributo no .dat
   attribute_condition = Condition(condition)
   changed_data = attribute.change_to(attribute_value, dat_data, attribute_condition)
   
   return changed_data

def start(changes_terms: list[str], dat_path: str, condition: str):
   # Lendo Arquivo .dat
   dat_data = filer.read(dat_path)

   # Gerando Dados com Alterações
   changed_data = change(changes_terms[0], changes_terms[1], dat_data, condition)

   # Escrevendo Alterações no .dat
   filer.write(dat_path, changed_data)