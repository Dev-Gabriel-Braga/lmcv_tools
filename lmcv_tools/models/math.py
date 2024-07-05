# --------------------------------------------------
# 1 - Matrix - Classes Relacionadas
# --------------------------------------------------

class Matrix:
    # Método Construtor
    def __init__(self, n_rows: int, n_columns: int):
        # Definindo Número de Linhas e Colunas
        self.n_rows = n_rows
        self.n_colmuns = n_columns

        # Inicializando Elementos
        self._elements = [[0 for j in range(n_columns)] for i in range(n_rows)]

    # Métodos Públicos
    def fill(self, scalar: float):
        for i in range(self.n_rows):
            for j in range(self.n_colmuns):
                self[i, j] = scalar

    def fill_diagonal(self, scalar: float):
        for i in range(self.n_rows):
            for j in range(self.n_colmuns):
                if i == j:
                    self[i, j] = scalar

    def copy(self):
        copy_matrix = Matrix(self.n_rows, self.n_colmuns)
        copy_matrix._elements = [row.copy() for row in self._elements]
        return copy_matrix
    
    def to_list(self) -> list[list[int]]:
        return self._elements

    # Métodos Privados
    def _verify_index(self, index: tuple[int]):
        # Verificando Tamanho da Tupla
        if type(index) is not tuple or len(index) != 2:
            raise IndexError('The index tuple to get an item from an Matrix object must contain exactly 2 int indexes.')

    # Métodos Especiais
    def __str__(self) -> str:
        return f'Matrix(\n' + '\n'.join([
            '   ' + '   '.join([
                f'{self._elements[i][j]:.5e}'
                for j in range(self.n_colmuns)
            ])
            for i in range(self.n_rows)
        ]) + '\n)'

    def __getitem__(self, index: tuple[int]):
        self._verify_index(index)
        return self._elements[index[0]][index[1]]
    
    def __setitem__(self, index: tuple[int], scalar: float):
        self._verify_index(index)
        self._elements[index[0]][index[1]] = scalar

    def __add__(self, other):
        # Verificando se a Adição é apenas entre Matrizes
        if type(other) is not type(self):
            raise TypeError(f"Unsupported operand for +: {type(self).__name__}' and '{type(other).__name__}'")
        
        # Verificando se a Dimensão é a Mesma
        if self.n_rows != other.n_rows or self.n_colmuns != self.n_colmuns:
            raise ValueError(f'The Matrices must have the same dimensions.')
        
        # Criando Matriz de Soma
        sum_matrix = Matrix(self.n_rows, self.n_colmuns)
        for i in range(self.n_rows):
            for j in range(self.n_colmuns):
                sum_matrix[i, j] = self[i, j] + other[i, j]
        return sum_matrix
    
    def __mul__(self, other):
        # Tratando Caso do Outro Operando ser Int ou Float
        if type(other) is int or type(other) is float:
            mul_matrix = self.copy()
            for i in range(self.n_rows):
                for j in range(self.n_colmuns):
                    mul_matrix[i, j] *= other
            return mul_matrix
        
        # Tratando Caso do Outro Operando ser uma Matrix
        if type(other) is type(self):
            # Verificando de o N° de Colunas de O1 = N° de Colunas de O2 
            if self.n_colmuns != other.n_rows:
                raise ValueError('For Matrix Multiplication, the number of columns of the firts operand must be equal to number of rows of the second operand.')

            # Performando Multiplicação de Matrizes
            mul_matrix = Matrix(self.n_rows, other.n_colmuns)
            for i in range(self.n_rows):
                for j in range(other.n_colmuns):
                    for k in range(self.n_colmuns):
                        mul_matrix[i, j] += self[i, k] * other[k, j]
            return mul_matrix

        # Tratando Caso da Operação não ser Compatível
            raise TypeError(f"Unsupported operand for +: {type(self).__name__}' and '{type(other).__name__}'")
        
    def __rmul__(self, other):
        # Tratando Caso do Outro Operando ser Int ou Float
        if type(other) is int or type(other) is float:
            return self * other
        
    def __sub__(self, other):
        return other * (-1) + self
