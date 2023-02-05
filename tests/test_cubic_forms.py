import unittest
import os

class TestCubicForms(unittest.TestCase):

   def test_cube_1x1(self):
      # Definindo paths
      inp_path = 'tests/benchmark/Cube_1x1.inp'
      dat_path = inp_path[:-3] + 'dat'

      # Traduzindo Benchmark de 1 Cubo com 1 Elemento C3D8
      code = os.system(f'ftrans -t {inp_path}')
      self.assertEqual(code, 0)