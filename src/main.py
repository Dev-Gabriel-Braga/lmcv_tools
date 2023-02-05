# A ordem dos nodes muda para um elemento BRICK8 dependendo do Software.
# No Abaqus, trabalhamos com o eixo x, lendo os node no sentido horário e contrariando o eixo (Ponto inicial acima do eixo).
# No FAST, trabalhamos com o eixo z, lendo os nodes no sentido anti-horário e contrariando o eixo (Ponto inicial no eixo).
# Do Abaqus -> FAST, a ordem dos nodes fica: 5, 1, 2, 6, 8, 4, 3, 7

# Importando Bibliotecas
import re

# Definindo Funções
def translate_elements(element_type, inp_elements):
   # Limpando Entrada e Definindo Saída
   inp_elements = inp_elements.strip()
   inp_elements = inp_elements.split('\n')
   n_elements = len(inp_elements)
   description = ''
   template = '\n%ELEMENT\n{}\n\n'

   # Diferenciando Elementos
   if element_type == 'C3D8' or element_type == 'C3D8R':
      # Complementando Template
      template += '%ELEMENT.BRICK8\n{}\n{}'

      # Formatando Informações de Cada Elemento
      for element in inp_elements:
         info = list(map(int, element.split(',')))
         line = '{0}   1  1   {5}   {1}   {2}   {6}   {8}   {4}   {3}   {7}\n'
         description += line.format(*info)
   else:
      print('Tem esse elemento aí não oh.')

   return template.format(n_elements, n_elements, description)

def translate_nodes(inp_nodes):
   # Limpando Entrada e Definindo Saída
   inp_nodes = inp_nodes.strip()
   inp_nodes = inp_nodes.split('\n')
   n_nodes = len(inp_nodes)
   coords = ''
   template = '\n%NODE\n{}\n\n%NODE.COORD\n{}\n{}'

   # Formatando as Coordenadas de Cada Node
   for node in inp_nodes:
      info = list(map(float, node.split(',')))
      coords += f'{int(info[0])}   {info[1]}   {info[2]}   {info[3]}\n'

   return template.format(n_nodes, n_nodes, coords)

def main():
   # Abrindo Arquivos de Trabalho
   file_abaqus = open('Teste.inp', 'r')
   file_fast = open('Teste.dat', 'w')

   # Lendo Dados do Arquivo do Abaqus
   inp_data = file_abaqus.read()

   # Definindo Estrutura Básica do Arquivo FAST
   dat_data = '%HEADER\n'

   # Buscando a Localização dos Nodes
   loc = re.search('\*Node', inp_data)
   index_start = loc.end()
   loc = re.search('\*', inp_data[index_start:])
   index_end = index_start + loc.start()

   # Traduzindo os Nodes
   dat_nodes = translate_nodes(inp_data[index_start:index_end])
   dat_data += dat_nodes

   # Buscando Localização dos Elementos
   loc = re.search('\*Element, type=(.*)', inp_data)
   index_start = loc.end()
   element_type = loc.groups()[0]
   loc = re.search('\*', inp_data[index_start:])
   index_end = index_start + loc.start()

   # Traduzindo os Elementos
   dat_elements = translate_elements(element_type, inp_data[index_start:index_end])
   dat_data += dat_elements

   # Escrevendo Dados Traduzidos
   dat_data += '\n%END'
   file_fast.write(dat_data)

   # Fechando Arquivos
   file_abaqus.close()
   file_fast.close()

# Diretiva Geral do Arquivo
if __name__ == '__main__':
   main()