from ..interface import filer
from ..models.extraction_components import (
   ResultTable,
   Condition,
   Attribute
)

# Funções Globais
def extract(attributes: list[str], pos_data: str, condition: str = None) -> ResultTable:
   # Instanciando Tabela de Resultado e Condição de Atributos
   result_table = ResultTable([])
   attributes_condition = Condition(condition)
   
   # Analisando cada Atributo
   for attribute_name in attributes:
      # Instanciando Atributo
      attribute = Attribute(attribute_name)
      
      # Extraindo Dados Relativos ao Atributo dos Dados do .pos
      table = attribute.extract_from(pos_data, attributes_condition)

      # Cruzando Novos Dados com a Tabela de Resultado Final
      result_table = result_table.join(table)
   
   # Reordenando Dados
   result_table.reorder(attributes)
   
   return result_table

def start(attributes: list[str], pos_path: str, condition: str, csv_path: str):
   # Lendo Arquivo .pos
   pos_data = filer.read(pos_path)

   # Extraindo Dados e Convertendo para o Formato CSV
   table = extract(attributes, pos_data, condition)
   csv_data = table.to_csv()

   # Escrevendo Extração no .csv
   filer.write(csv_path, csv_data)