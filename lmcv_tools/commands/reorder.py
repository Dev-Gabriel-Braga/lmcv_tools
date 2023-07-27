from itertools import combinations
from scipy.sparse import lil_matrix, csr_array
from scipy.sparse.csgraph import reverse_cuthill_mckee as rcm
from ..interface import filer
from ..models.translation_components import DAT_Interpreter

# Funções de Reordenação
def reorder_rcm(graph: csr_array) -> list[int]:
   # Executando Algoritmo de Reordenação
   rcm_order = rcm(graph, True)
   
   # Corrigindo Ordenamento Imprório da Implementação do Scipy
   new_order = [0] * len(rcm_order)
   for index, value in enumerate(rcm_order):
      new_order[value] = index + 1
   
   return new_order

# Métodos de Reordenação Suportados
supported_methods = {
   'rcm': reorder_rcm
}

# Função de Inicialização
def start(method: str, dat_path: str):
   # Verificando se o Método de Reordenação é Suportado
   try:
      reordering_function = supported_methods[method]
   except KeyError:
      raise KeyError(f'The method "{method}" is not supported.')

   # Lendo Arquivo .dat
   dat_data = filer.read(dat_path)

   # Interpretando Informações
   dat_interpreter = DAT_Interpreter()
   dat_interpreter.read(dat_data)
   model = dat_interpreter.model

   # Criando Matriz do Grafo para Reordenação
   n = len(model.nodes)
   graph = lil_matrix((n, n))
   for group in model.element_groups.values():
      for nodes in group.elements.values():
         for i, j in combinations(nodes, 2):
            i -= 1
            j -= 1
            graph[i, j] = True
            graph[j, i] = True
   graph = graph.tocsr()

   # Reordenando
   new_order = reordering_function(graph)

   # Adicionando Reordenação ao Modelo de Simulação
   dat_interpreter.model.node_solver_order = new_order

   # Gerando e Incluindo Codificação da Ordem no Arquivo .dat
   order_data = dat_interpreter.write_node_solver_order()
   dat_data = dat_data.replace('%ELEMENT\n', order_data[1:] + '\n%ELEMENT\n')
   filer.write(dat_path, dat_data)
