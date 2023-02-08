import json
from importlib.resources import files

class Searcher:
   # Atributos Estáticos
   databases_files = files('lmcv_tools.databases')

   # Métodos Estáticos
   @staticmethod
   def get_database(json_name: str) -> dict:
      # Abrindo Arquivo JSON da Base de Dados
      json_file = Searcher.databases_files.joinpath(json_name + '.json')
      json_file = json_file.open('r')
      json_data = json.load(json_file)
      return json_data
