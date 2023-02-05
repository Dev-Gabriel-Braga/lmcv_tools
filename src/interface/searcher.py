import json
from os.path import dirname

class Searcher:
   # Atributos Estáticos
   databases_path = dirname(__file__) + '\..\databases'

   # Métodos Estáticos
   @staticmethod
   def get_database(json_name: str) -> dict:
      # Abrindo Arquivo JSON da Base de Dados
      json_path = f'{Searcher.databases_path}/{json_name}.json'
      json_file = open(json_path, 'r')
      json_data = json.load(json_file)
      return json_data
