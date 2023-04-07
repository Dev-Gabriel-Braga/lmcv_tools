class Artifact:
   def __init__(self, name: str, file_extension: str, data: str = ''):
      self.name = name
      self.file_extension = file_extension
      self.data = data
   
   @property
   def file_name(self) -> str:
      return self.name + '.' + self.file_extension
   
   # Para Implementar
   def generate(self):
      return self.data

class Material:
   def __init__(self, elastic_modulus: float, poisson_coefficient: float, density: float) -> None:
      self.E = elastic_modulus
      self.nu = poisson_coefficient
      self.pho = density

      # Calculando Módulo Volumétrico
      self.K = self.E / (3 * (1 - 2 * self.nu))

      # Calculando Módulo de Cisalhamento
      self.G = self.E / (2 * (1 + self.nu))

class MicromechanicalModel:
   # Funções de Homogeneização Privadas
   def _voight(self, volume_fractions: list[float]):
      E, nu, pho = 0, 0, 0
      for V, M in zip(volume_fractions, self.materials):
         E += V * M.E
         nu += V * M.nu
         pho += V * M.pho
      return E, nu, pho

   def _mori_tanaka(self, volume_fractions: list[float]):
      # Definindo Valores Especiais
      V, M = volume_fractions, self.materials
      V1, V2 = V[0], V[1]
      K1, K2 = M[0].K, M[1].K
      G1, G2 = M[0].G, M[1].G
      FG = (G1 * (9 * K1 + 8 * G1)) / (6 * (K1 + 2 * G1))
      FK = 4 * G1 / 3

      # Calculando Módulo Volumétrico
      K = K1 + V2 / ((1 / (K2 - K1)) + (V1 / (K1 + FK)))

      # Calculando Módulo de Cisalhamento
      G = G1 + V2 / ((1 / (G2 - G1)) + (V1 / (G1 + FG)))

      # Calculando Propriedades Efetivas
      E = (9 * K * G) / (3 * K + G)
      nu = (3 * K - 2 * G) / (2 * (3 * K + G))

      # Densidade Calculada pelo Modelo de Voight
      pho = V1 * M[0].pho + V2 * M[1].pho

      return E, nu, pho

   # Relação Modelo/Função de Homogeneização
   homogenize_functions = {
      'voight': _voight,
      'mori_tanaka': _mori_tanaka
   }

   def __init__(self, name: str, materials: list[Material]) -> None:
      self.name = name
      self.materials = materials
      try:
         self._homogenize = MicromechanicalModel.homogenize_functions[name]
      except KeyError:
         raise ValueError(f'Micromechanical Model "{name}" is not supported.')
   
   def homogenize(self, volume_fractions: list[float]):
      return self._homogenize(self, volume_fractions)

class ElementConfiguration:
   # Elementos Suportados
   supported_types = {'Solid', 'Shell'}

   def __init__(self, type: str, number_integration_points: int):
      if type not in ElementConfiguration.supported_types:
         raise ValueError(f'Element Type "{type}" is not supported.')
      self.type = type
      self.number_integration_points = number_integration_points

class VirtualLaminas(Artifact):
   def __init__(
      self,
      laminas_count: int,
      laminas_thickness: float,
      power_law_exponent: float,
      element_configuration: ElementConfiguration,
      micromechanical_model: MicromechanicalModel
   ):
      super().__init__('virtual_laminas', 'inp')
      self.laminas_count = laminas_count
      self.laminas_thickness = laminas_thickness
      self.power_law_exponent = power_law_exponent
      self.element_configuration = element_configuration
      self.micromechanical_model = micromechanical_model
   
   def volume_fraction(self, z: float):
      return (1 - z) ** self.power_law_exponent

   def generate(self):
      # Inicializando Dados
      inp_data = ''

      # Gerando Materiais no Formato Inp
      material_names = list()
      index = 1
      step = 1 / self.laminas_count
      z = step / 2
      while z < 1:
         # Gerando e Armazando Nome de Material
         name =  f'FGM-L{index}'
         material_names.append(name)

         # Homogeneizando Propriedades
         volume_fractions = [self.volume_fraction(z)]
         volume_fractions.append(1 - volume_fractions[0])
         E, nu, pho = self.micromechanical_model.homogenize(volume_fractions)

         # Adicionando Dados
         inp_data += f'*Material, name={name}\n    *Density\n    {pho:.3f},\n    *Elastic\n    {E:.3f}, {nu:.3f}\n'
         
         z += step
         index += 1
      
      # Preparando para Escrever Lâminas
      inp_data += '*Part, name=Virtual_Part\n*Node\n    1, 1.0, 1.0, 0.0\n    2, 0.0, 1.0, 0.0\n    3, 0.0, 0.0, 0.0\n    4, 1.0, 0.0, 0.0\n*Element, type=S4R\n    1, 1, 2, 3, 4\n*Elset, elset=Virtual\n    1'
      element_type = self.element_configuration.type
      points = self.element_configuration.number_integration_points
      rotation_angle = 0

      # Adaptando Espessura ao Tipo Elemento
      thickness = self.laminas_thickness
      if self.element_configuration.type == 'Shell':
         thickness /= self.laminas_count

      # Escrevendo Lâmina por Lâmina   
      inp_data += f'\n*{element_type} Section, elset=Virtual, composite\n'
      for index, material in enumerate(material_names):
         inp_data += f'    {thickness}, {points}, {material}, {rotation_angle}, Ply-{index + 1}\n'
      inp_data += '*End Part'

      # Inseridos dados Inp no Atributo de Dados
      self.data = inp_data