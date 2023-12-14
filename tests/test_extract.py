import unittest
import os

class DefaultTest(unittest.TestCase):
   def default_test(self, benchmark_name: str, benchmark_id: str, attributes: list[str], condition: str):
      # Definindo paths
      pos_path = 'tests/benchmark/extract/' + benchmark_name + '.pos'
      csv_path = pos_path[:-3] + 'csv'
      exp_path = pos_path[:-4] + '_exp_'+ benchmark_id + '.csv'

      # Extraindo Dados
      attributes_joined = ' '.join(attributes)
      command = f'python -m lmcv_tools extract {attributes_joined} from {pos_path}'
      if condition:
         command += f' where {condition}'
      code = os.system(command)
      self.assertEqual(code, 0, 'A extração falhou.')

      # Comparando Extração com o Resultado Esperado
      csv_file = open(csv_path, 'r')
      exp_file = open(exp_path, 'r')
      csv_data = csv_file.read()
      exp_data = exp_file.read()
      csv_file.close()
      exp_file.close()
      self.assertEqual(csv_data, exp_data, 'A extração está incorreta.')

      # Removendo Arquivo .csv Gerado
      os.remove(csv_path)

class TestSingleAttributes(DefaultTest):
   def test_step_id(self):
      benchmark = ('CirclePlate_Plastic', 'step_id')
      attributes = ['step.id']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_factor(self):
      benchmark = ('CirclePlate_Plastic', 'step_factor')
      attributes = ['step.factor']
      condition = ''
      self.default_test(*benchmark, attributes, condition)

   def test_node_id(self):
      benchmark = ('CirclePlate_Plastic', 'node_id')
      attributes = ['node.id']
      condition = ''
      self.default_test(*benchmark, attributes, condition)

   def test_node_coord_0(self):
      benchmark = ('CirclePlate_Plastic', 'node_coord_0')
      attributes = ['node.coord[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_node_coord_1(self):
      benchmark = ('CirclePlate_Plastic', 'node_coord_1')
      attributes = ['node.coord[1]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_node_coord_2(self):
      benchmark = ('CirclePlate_Plastic', 'node_coord_2')
      attributes = ['node.coord[2]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_node_displacement_0(self):
      benchmark = ('CirclePlate_Plastic', 'step_node_displacement_0')
      attributes = ['step.node.displacement[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_node_displacement_1(self):
      benchmark = ('CirclePlate_Plastic', 'step_node_displacement_1')
      attributes = ['step.node.displacement[1]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_node_displacement_2(self):
      benchmark = ('CirclePlate_Plastic', 'step_node_displacement_2')
      attributes = ['step.node.displacement[2]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_element_id(self):
      benchmark = ('CirclePlate_Plastic', 'element_id')
      attributes = ['element.id']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_element_info_0(self):
      benchmark = ('CirclePlate_Plastic', 'element_info_0')
      attributes = ['element.info[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_element_info_2(self):
      benchmark = ('CirclePlate_Plastic', 'element_info_2')
      attributes = ['element.info[2]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_gauss_scalar_0(self):
      benchmark = ('CirclePlate_Plastic', 'step_gauss_scalar_0')
      attributes = ['step.gauss.scalar[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_gauss_scalar_3(self):
      benchmark = ('CirclePlate_Plastic', 'step_gauss_scalar_3')
      attributes = ['step.gauss.scalar[3]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)

   def test_step_element_gauss_scalar_data_0(self):
      benchmark = ('CirclePlate_Plastic', 'step_element_gauss_scalar_data_0')
      attributes = ['step.element.gauss.scalar.data[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_element_gauss_scalar_data_15(self):
      benchmark = ('CirclePlate_Plastic', 'step_element_gauss_scalar_data_15')
      attributes = ['step.element.gauss.scalar.data[15]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)

   def test_step_nodal_scalar_0(self):
      benchmark = ('CirclePlate_Plastic', 'step_nodal_scalar_0')
      attributes = ['step.nodal.scalar[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_nodal_scalar_3(self):
      benchmark = ('CirclePlate_Plastic', 'step_nodal_scalar_3')
      attributes = ['step.nodal.scalar[3]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)

   def test_step_element_nodal_scalar_data_0(self):
      benchmark = ('CirclePlate_Plastic', 'step_element_nodal_scalar_data_0')
      attributes = ['step.element.nodal.scalar.data[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_step_element_nodal_scalar_data_31(self):
      benchmark = ('CirclePlate_Plastic', 'step_element_nodal_scalar_data_31')
      attributes = ['step.element.nodal.scalar.data[31]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_buckling_id(self):
      benchmark = ('SquarePlate', 'buckling_id')
      attributes = ['buckling.id']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_buckling_factor(self):
      benchmark = ('SquarePlate', 'buckling_factor')
      attributes = ['buckling.factor']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_buckling_node_displacement_0(self):
      benchmark = ('SquarePlate', 'buckling_node_displacement_0')
      attributes = ['buckling.node.displacement[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_buckling_node_displacement_1(self):
      benchmark = ('SquarePlate', 'buckling_node_displacement_1')
      attributes = ['buckling.node.displacement[1]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_buckling_node_displacement_2(self):
      benchmark = ('SquarePlate', 'buckling_node_displacement_2')
      attributes = ['buckling.node.displacement[2]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_vibration_id(self):
      benchmark = ('HeartPlate', 'vibration_id')
      attributes = ['vibration.id']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_vibration_factor(self):
      benchmark = ('HeartPlate', 'vibration_factor')
      attributes = ['vibration.factor']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_vibration_node_displacement_0(self):
      benchmark = ('HeartPlate', 'vibration_node_displacement_0')
      attributes = ['vibration.node.displacement[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_vibration_node_displacement_1(self):
      benchmark = ('HeartPlate', 'vibration_node_displacement_1')
      attributes = ['vibration.node.displacement[1]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_vibration_node_displacement_2(self):
      benchmark = ('HeartPlate', 'vibration_node_displacement_2')
      attributes = ['vibration.node.displacement[2]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)

class TestMultipleAttributes(DefaultTest):
   def test_multiple_1(self):
      benchmark = ('CirclePlate_Plastic', 'multiple_1')
      attributes = ['step.id', 'step.factor']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_multiple_2(self):
      benchmark = ('CirclePlate_Plastic', 'multiple_2')
      attributes = ['step.factor', 'step.node.displacement[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_multiple_3(self):
      benchmark = ('CirclePlate_Plastic', 'multiple_3')
      attributes = ['step.node.displacement[0]', 'node.id', 'node.coord[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_multiple_unrelated_1(self):
      benchmark = ('CirclePlate_Plastic', 'multiple_ur_1')
      attributes = ['node.id', 'step.id']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
   def test_multiple_unrelated_2(self):
      benchmark = ('CirclePlate_Plastic', 'multiple_ur_2')
      attributes = ['node.id', 'step.id', 'node.coord[0]']
      condition = ''
      self.default_test(*benchmark, attributes, condition)
   
class TestCondition(DefaultTest):
   def test_condition_equal(self):
      benchmark = ('CirclePlate_Plastic', 'cond_eq')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id = 5'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_less(self):
      benchmark = ('CirclePlate_Plastic', 'cond_ls')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id "<" 5'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_greater(self):
      benchmark = ('CirclePlate_Plastic', 'cond_gt')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id ">" 5'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_less_or_equal(self):
      benchmark = ('CirclePlate_Plastic', 'cond_le')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id "<=" 5'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_greater_or_equal(self):
      benchmark = ('CirclePlate_Plastic', 'cond_ge')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id ">=" 5'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_different(self):
      benchmark = ('CirclePlate_Plastic', 'cond_df')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id "!=" 5'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_in_1(self):
      benchmark = ('CirclePlate_Plastic', 'cond_in_1')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id in 1:4'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_in_2(self):
      benchmark = ('CirclePlate_Plastic', 'cond_in_2')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id in 1:11:2'
      self.default_test(*benchmark, attributes, condition)

   def test_condition_and(self):
      benchmark = ('CirclePlate_Plastic', 'cond_and')
      attributes = ['step.id', 'step.factor']
      condition = 'step.id "<" 9 and step.factor ">" 1.6'
      self.default_test(*benchmark, attributes, condition)
   
   def test_condition_or(self):
      benchmark = ('CirclePlate_Plastic', 'cond_or')
      attributes = ['step.id', 'step.factor']
      condition = 'step.factor "<" 0.5 or step.factor ">" 2.5'
      self.default_test(*benchmark, attributes, condition)