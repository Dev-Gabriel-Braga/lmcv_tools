import unittest
import os

class DefaultTest(unittest.TestCase):
   def default_test(self, benchmark_name: str):
      # Definindo paths
      inp_path = 'tests/benchmark/translate/' + benchmark_name + '.inp'
      dat_path = inp_path[:-3] + 'dat'
      exp_path = inp_path[:-4] + '_exp.dat'

      # Traduzindo Benchmark
      code = os.system(f'python -m lmcv_tools translate {inp_path}')
      self.assertEqual(code, 0, 'A tradução falhou.')

      # Comparando Tradução com o Resultado Esperado
      dat_file = open(dat_path, 'r')
      exp_file = open(exp_path, 'r')
      dat_data = dat_file.read()
      exp_data = exp_file.read()
      dat_file.close()
      exp_file.close()
      self.assertEqual(dat_data, exp_data, 'A tradução está incorreta.')

      # Removendo Arquivo .dat Gerado
      os.remove(dat_path)

class Test2D(DefaultTest):
   def test_triangle_S3_1x1(self):
      self.default_test('Triangle_S3_1x1')

   def test_triangle_S3_2x2(self):
      self.default_test('Triangle_S3_2x2')

   def test_triangle_STRI65_1x1(self):
      self.default_test('Triangle_STRI65_1x1')

   def test_triangle_STRI65_2x2(self):
      self.default_test('Triangle_STRI65_2x2')

   def test_square_S4_1x1(self):
      self.default_test('Square_S4_1x1')
   
   def test_square_S4_2x2(self):
      self.default_test('Square_S4_2x2')

   def test_square_S8R_1x1(self):
      self.default_test('Square_S8R_1x1')
   
   def test_square_S8R_2x2(self):
      self.default_test('Square_S8R_2x2')
   
   def test_circle_S3_S4R_4x4(self):
      self.default_test('Circle_S3_S4R_4x4')

   def test_complex_part_S8R_2x2(self):
      self.default_test('ComplexPart_S8R')

class Test3D(DefaultTest):
   def test_cube_C3D8_1x1x1(self):
      self.default_test('Cube_C3D8_1x1x1')

   def test_cube_C3D8_2x2x2(self):
      self.default_test('Cube_C3D8_2x2x2')
   
   def test_cube_C3D20_1x1x1(self):
      self.default_test('Cube_C3D20_1x1x1')

   def test_cube_C3D20_2x2x2(self):
      self.default_test('Cube_C3D20_2x2x2')

   def test_complex_part_C3D20R(self):
      self.default_test('ComplexPart_C3D20R')
