import unittest
import os

class DefaultTest(unittest.TestCase):
   def default_test(self, artifact_name: str, artifact_extension: str, test_id: str, args: list):
      # Definindo paths
      path = 'tests/benchmark/generate/'
      artifact_path = f'{path}{artifact_name}.{artifact_extension}'
      exp_path = f'{artifact_path[:-4]}_exp_{test_id}.{artifact_extension}'

      # Gerando Artefato
      args_joined = ' '.join(args)
      command = f'python -m lmcv_tools generate {artifact_name} {artifact_path} {args_joined}'
      code = os.system(command)
      self.assertEqual(code, 0, 'A geração falhou.')

      # Comparando Artefato com o Resultado Esperado
      artifact_file = open(artifact_path, 'r')
      exp_file = open(exp_path, 'r')
      artifact_data = artifact_file.read()
      exp_data = exp_file.read()
      artifact_file.close()
      exp_file.close()
      self.assertEqual(artifact_data, exp_data, 'O Artefato está incorreto.')

      # Removendo Arquivo .csv Gerado
      os.remove(artifact_path)

class TestVirtualLaminas(DefaultTest):
   def test_voight_model(self):
      name = 'virtual_laminas'
      ext = 'inp'
      test_id = 'voight'
      args = ['40', '0.25', '1.0', 'voight', 'Solid', '3', '380.0', '90.0', '0.30', '0.27', '1000', '2000']
      self.default_test(name, ext, test_id, args)
   
   def test_mori_tanaka_model(self):
      name = 'virtual_laminas'
      ext = 'inp'
      test_id = 'mori_tanaka'
      args = ['40', '0.25', '1.0', 'mori_tanaka', 'Solid', '3', '380.0', '90.0', '0.30', '0.27', '1000', '2000']
      self.default_test(name, ext, test_id, args)