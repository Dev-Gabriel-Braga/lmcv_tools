from inspect import signature
from ..interface import filer
from ..models.graphics import PromptGenerateVirtualLaminas
from ..models.custom_errors import CommandError
from ..models.artifacts import (
   VirtualLaminas,
   ElementConfiguration,
   Cuboid,
   NURBS_Rectangle,
   NURBS_Cuboid
)
from ..models.simulation import (
   IsotropicMaterial,
   FunctionallyGradedMaterial
)

# Funções de Geração de Artefatos
def generate_virtual_laminas(
   laminas_count: int,
   element_type: str,
   thickness: float,
   number_integration_points: int,
   power_law_exponent: float,
   micromechanical_model: str,
   E1: float,
   E2: float,
   nu1: float,
   nu2: float,
   rho1: float,
   rho2: float,
   smart: bool
) -> VirtualLaminas:
   # Instanciando Configuração do Elemento
   element = ElementConfiguration(element_type, number_integration_points)

   # Instanciando Materiais
   materials = list()
   materials.append(IsotropicMaterial(E1, nu1, rho1))
   materials.append(IsotropicMaterial(E2, nu2, rho2))

   # Instanciando FGM
   fgm = FunctionallyGradedMaterial(micromechanical_model, materials)
   
   # Instanciando Artefato de Lâminas Virtuais
   virtual_laminas = VirtualLaminas(
      laminas_count,
      thickness,
      power_law_exponent,
      element,
      fgm,
      smart
   )
   virtual_laminas.generate()

   return virtual_laminas

def generate_cuboid(
   element_type: str, 
   dimensions: list[float], 
   discretization: list[int]
) -> Cuboid:
   # Instanciando Artefato
   cuboid = Cuboid(element_type, dimensions, discretization)

   # Gerando Cuboid
   cuboid.generate()

   # Retornando Cuboid
   return cuboid

def generate_nurbs_rectangle(
   degrees: list[int],
   dimensions: list[float],
   discretization: list[int]
) -> NURBS_Rectangle:
   # Instanciando Artefato
   nurbs_rectangle = NURBS_Rectangle(degrees, dimensions, discretization)

   # Gerando Rectangle
   nurbs_rectangle.generate()

   # Retornando Rectangle
   return nurbs_rectangle

def generate_nurbs_cuboid(
   degrees: list[int],
   dimensions: list[float],
   discretization: list[int]
) -> NURBS_Cuboid:
   # Instanciando Artefato
   nurbs_cuboid = NURBS_Cuboid(degrees, dimensions, discretization)

   # Gerando Cuboid
   nurbs_cuboid.generate()

   # Retornando Cuboid
   return nurbs_cuboid

# Funções de Parâmetros de Artefatos
def params_virtual_laminas(args: list[str]) -> dict:
   # Iniciando Parâmetros
   params = dict()
   
   # Exibindo Interface Gráfica para Preencher Parâmetros (Se não Houver Parâmetros)
   if len(args) == 0:
      window = PromptGenerateVirtualLaminas(params)
      window.start()

      # Conferindo se Há um Caminho
      if params.get('path') is not None:
         if params['path'] != '':
            args = [params['path']]
         del params['path']

   # Tentando Coletar Parâmetros Dados 
   else:
      try:
         reference = dict(signature(generate_virtual_laminas).parameters)
         index = 0
         for name, param_obj in reference.items():
            type_class = param_obj.annotation
            if type_class is bool:
               params[name] = False if args.pop(0) == 'False' else True
            else:   
               params[name] = type_class(args.pop(0))
            index += 1
      except IndexError:
         raise CommandError('Invalid number of arguments.', help=True)
   
   return params, args

def params_cuboid(args: list[str]) -> dict:
   # Iniciando Parâmetros
   params = dict()

   # Tentando Converter Tipos de Dados
   params['element_type'] = args[0]
   params['dimensions'] = list(map(float, args[1:4]))
   params['discretization'] = list(map(int, args[4:7]))
   
   return params, args[7:]

def params_nurbs_rectangle(args: list[str]) -> dict:
   # Iniciando Parâmetros
   params = dict()

   # Tentando Converter Tipos de Dados
   params['degrees'] = list(map(int, args[0:2]))
   params['dimensions'] = list(map(float, args[2:4]))
   params['discretization'] = list(map(int, args[4:6]))
   
   return params, args[6:]

def params_nurbs_cuboid(args: list[str]) -> dict:
   # Iniciando Parâmetros
   params = dict()

   # Tentando Converter Tipos de Dados
   params['degrees'] = list(map(int, args[0:3]))
   params['dimensions'] = list(map(float, args[3:6]))
   params['discretization'] = list(map(int, args[6:9]))
   
   return params, args[9:]

# Relação Artefato/Funções
artifacts = {
   'virtual_laminas': {
      'params': params_virtual_laminas,
      'generate': generate_virtual_laminas
   },
   'cuboid': {
      'params': params_cuboid,
      'generate': generate_cuboid
   },
   'nurbs_rectangle': {
      'params': params_nurbs_rectangle,
      'generate': generate_nurbs_rectangle
   },
   'nurbs_cuboid': {
      'params': params_nurbs_cuboid,
      'generate': generate_nurbs_cuboid
   }
}

# Funções de Inicialização
def start(artifact_name: str, args: list[str]) -> str:
   try:
      # Coletando Parâmetros
      params_function = artifacts[artifact_name]['params']
      params, args = params_function(args)

      # Gerando Artefato
      generate_function = artifacts[artifact_name]['generate']
      artifact = generate_function(**params)

   except KeyError:
      raise CommandError(f'Unknown Artifact "{artifact_name}"')
   except TypeError:
      raise CommandError('Not all arguments were correctly passed.')

   # Escrevendo Arquivo do Artefato
   try:
      path = args[0]
   except IndexError:
      path = artifact.file_name
   filer.write(path, artifact.data)
