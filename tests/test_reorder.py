import unittest
import os

class DefaultTest(unittest.TestCase):
   def default_test(self, benchmark_name: str, benchmark_id: str, method: str):
      # Definindo paths
      dat_path = 'tests/benchmark/reorder/' + benchmark_name + '.dat'
      temp_path = dat_path[:-4] + '_temp.dat'
      exp_path = dat_path[:-4] + '_exp_'+ benchmark_id + '.dat'

      # Copiando Dados para Arquivo Temporário de Teste
      dat_file = open(dat_path, 'r')
      dat_data = dat_file.read()
      dat_file.close()
      temp_file = open(temp_path, 'w')
      temp_file.write(dat_data)
      temp_file.close()
      del dat_data

      # Executando Reordenação
      command = f'python -m lmcv_tools reorder {method} {temp_path}'
      code = os.system(command)
      self.assertEqual(code, 0, 'A extração falhou.')

      # Comparando Reordenação com o Resultado Esperado
      exp_file = open(exp_path, 'r')
      exp_data = exp_file.read()
      exp_file.close()
      temp_file = open(temp_path, 'r')
      temp_data = temp_file.read()
      temp_file.close()
      self.assertEqual(temp_data, exp_data, 'A extração está incorreta.')

      # Removendo Arquivo Temporário Gerado
      os.remove(temp_path)

class TestMethods(DefaultTest):
   def test_rcm(self):
      benchmark = ('ComplexPipe', 'rcm')
      self.default_test(*benchmark, 'rcm')
   