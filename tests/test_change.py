import unittest
import os

class DefaultTest(unittest.TestCase):
   def default_test(self, benchmark_name: str, benchmark_id: str, attribute: str, value: str, condition: str = None):
      # Definindo paths
      dat_path = 'tests/benchmark/change/' + benchmark_name + '.dat'
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

      # Alterando Atributo
      command = f'python -m lmcv_tools change {attribute} to {value} in {temp_path}'
      if condition:
         command += f' where {condition}'
      code = os.system(command)
      self.assertEqual(code, 0, 'A alteração falhou.')

      # Comparando Alteração com o Resultado Esperado
      temp_file = open(temp_path, 'r')
      exp_file = open(exp_path, 'r')
      temp_data = temp_file.read()
      exp_data = exp_file.read()
      temp_file.close()
      exp_file.close()
      self.assertEqual(temp_data, exp_data, 'A alteração está incorreta.')

      # Removendo Arquivo Temporário Gerado
      os.remove(temp_path)

class TestUnconditionedChanges(DefaultTest):
   def test_material_isotropic_E(self):
      self.default_test(
         'ThreeBarTruss', 
         'material_isotropic_E',
         'material.isotropic.E',
         '300.0e+09'
      )
   
   def test_material_isotropic_poisson(self):
      self.default_test(
         'ThreeBarTruss', 
         'material_isotropic_poisson',
         'material.isotropic.poisson',
         '0.5'
      )

   def test_section_bar_circle_radius(self):
      self.default_test(
         'ThreeBarTruss', 
         'section_bar_circle_radius',
         'section.bar.circle.radius',
         '2.40000e-03'
      )

class TestConditionedChanges(DefaultTest):
   def test_condition_1(self):
      self.default_test(
         'ThreeBarTruss', 
         'condition_1',
         'section.bar.circle.radius',
         '2.40000e-03',
         'section.id = 2'
      )