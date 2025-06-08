from math import (
    pi,
    sin,
    cos,
    factorial,
    comb
)
from ..models.math import (
    Matrix
)

# --------------------------------------------------
# 1 - B-Splines - Classes Relacionadas
# --------------------------------------------------
class BSpline_Basis:
    def __init__(self, degree: int, knot_vector: list[float]) -> None:
        self.degree = degree
        self.knot_vector = knot_vector.copy()
        self.n_basis = len(knot_vector) - degree - 1
    
    def alpha(self, k: int, knot: float, i: int):
        p = self.degree
        if i <= (k - p):
            alpha = 1
        elif (i >= (k - p + 1)) and (i <= k):
            alpha = knot - self.knot_vector[i]
            alpha /= (self.knot_vector[i + p] - self.knot_vector[i])
        elif i >= (k + 1):
            alpha = 0
        return alpha
    
    def knot_spans(self):
        p = self.degree
        for i in range(len(self.knot_vector) - p - 1):
            k1 = self.knot_vector[i]
            k2 = self.knot_vector[i + p + 1]
            yield (k1, k2)

    def not_null_spans(self, t: float):
        not_null_knot_spans = list()
        for i, (k1, k2) in enumerate(self.knot_spans()):
            if t >= k1 and t <= k2:
                not_null_knot_spans.append(i)
        return not_null_knot_spans

    def __call__(self, p: int, i: int, t: float):
        # Recursão - Caso Base
        if p == 0:
            if t >= self.knot_vector[i] and t <= self.knot_vector[i + 1]:
                return 1
            else:
                return 0
            
        # Recursão - Caso Geral
        N1 = t - self.knot_vector[i]
        D1 = self.knot_vector[i + p] - self.knot_vector[i]
        N2 = self.knot_vector[i + p + 1] - t
        D2 = self.knot_vector[i + p + 1] - self.knot_vector[i + 1]
        N = 0.0
        if D1 != 0.0:
            N += N1 / D1 * self.__call__(p - 1, i, t)
        if D2 != 0.0:
            N += N2 / D2 * self.__call__(p - 1, i + 1, t)
        return N

class BSpline_Curve:
    def __init__(self, degree: int, knot_vector: list[float], control_points: list[list]) -> None:
        self.basis = BSpline_Basis(degree, knot_vector)
        self.control_points = control_points.copy()
        self.dimension = len(control_points[0])
        
    def knot_insertion(self, k: int, knot: float):
        # Adicionando Knot
        new_knot_vector = self.basis.knot_vector.copy()
        new_knot_vector.insert(k + 1, knot)

        # Criando Novos Pontos de Controle
        new_control_points = list()
        for i in range(0, self.basis.n_basis + 1):
            # Determinando Alfa
            alpha = self.basis.alpha(k, knot, i)

            # Calculando Pontos
            control_point = [0] * self.dimension
            for d in range(self.dimension):
                if alpha:
                    control_point[d] += alpha * self.control_points[i][d]
                if (1 - alpha):
                    control_point[d] += (1 - alpha) * self.control_points[i - 1][d]
            new_control_points.append(control_point.copy())
        
        # Atualizando Atributos
        self.basis.n_basis += 1
        self.basis.knot_vector = new_knot_vector
        self.control_points = new_control_points
    
    def knot_insertions(self, knots: list[float]):
        for knot in reversed(knots):
            self.knot_insertion(self.basis.degree, knot)
    
    def degree_elevation(self, times: float):
        # Verificando se a B-Spline é Equivalente à uma Curva de Bézier
        if len(set(self.basis.knot_vector)) != 2:
            raise RuntimeError('The Curve must be a Bézier Equivalent Curve.')

        # Calculando Novo Número de Funções de Base
        t = times
        s = len(set(self.basis.knot_vector)) - 2
        new_n_basis = self.basis.n_basis + t * (s + 1)

        # Calculando Novo Vetor de Knots
        new_knot_vector = list()
        added_knots = set()
        for knot in self.basis.knot_vector:
            new_multiplicity = self.basis.knot_vector.count(knot) + t
            if knot not in added_knots:
                new_knot_vector.extend([knot] * new_multiplicity)
                added_knots.add(knot)

        # Criando Novos Pontos de Controle
        p = self.basis.degree
        new_control_points = list()
        for i in range(0, p + t + 1):
            control_point = [0] * self.dimension
            for d in range(self.dimension):
                control_point[d] = sum(
                    comb(p, j) * comb(t, i - j) * self.control_points[j][d] / comb(p + t, i)
                    for j in range(
                        max(0, i - t),
                        min(p, i) + 1
                    )
                )
            new_control_points.append(control_point)
        
        # Atualizando Atributos
        self.basis.degree += t
        self.basis.n_basis = new_n_basis
        self.basis.knot_vector = new_knot_vector
        self.control_points = new_control_points
        
    def __call__(self, t: float):
        point = list()
        for d in range(self.dimension):
            point.append(sum([
                self.basis(self.basis.degree, i, t) * self.control_points[i][d]
                for i in self.basis.not_null_spans(t)
            ]))
        return point
    
class BSpline_Surface:
    def __init__(
        self, 
        degree: list[int],
        knot_vectors: list[list[float]],
        control_points: list[list[list]]
    ) -> None:
        self.basis = [BSpline_Basis(p, kv) for p, kv in zip(degree, knot_vectors)]
        self.control_points = control_points.copy()
        self.dimension = len(control_points[0][0])
        
    def __call__(self, u: float, v: float):
        point = list()
        for d in range(self.dimension):
            point.append(sum([
                (
                    self.basis[0](self.degree[0], i, u) *
                    self.basis[1](self.degree[1], j, v) *
                    self.control_points[i][j][d]
                )
                for j in self.basis[1].not_null_spans(v)
                for i in self.basis[0].not_null_spans(u)
            ]))
        return point

# --------------------------------------------------
# 2 - NURBS - Classes Relacionadas
# --------------------------------------------------
class NURBS_Curve(BSpline_Curve):
    def __init__(
        self, 
        degree: int, 
        knot_vector: list[float], 
        control_points: list[list],
        weights: list[float]
    ) -> None:
        # Chamando Construtor da Super-Classe
        super().__init__(degree, knot_vector, control_points)

        # Conferindo Pesos dos Pontos de Controle
        if len(weights) != len(control_points):
            raise ValueError('The number of weights and the number of control points must be the same.')
        self.weights = weights.copy()
    
    def knot_insertion(self, k: int, knot: float):
        # Fazer Inserção de Knot para Pesos
        new_weights = list()
        for i in range(0, self.basis.n_basis + 1):
            # Determinando Alfa
            alpha = self.basis.alpha(k, knot, i)

            # Calculando Peso
            weight = 0.0
            if alpha:
                weight += alpha * self.weights[i]
            if (1 - alpha):
                weight += (1 - alpha) * self.weights[i - 1]
            new_weights.append(weight)

        # Atualizando Pontos de Controle a Partir dos Pesos
        for d in range(self.dimension):
            for i in range(len(self.control_points)):
                self.control_points[i][d] *= self.weights[i]

        # Fazendo Inserção de Knot da Super-Classe
        super().knot_insertion(k, knot)

        # Atualizando Pesos
        self.weights = new_weights.copy()

        # Atualizando Pontos de Controle a Partir dos Pesos
        for d in range(self.dimension):
            for i in range(len(self.control_points)):
                self.control_points[i][d] /= self.weights[i]
    
    def degree_elevation(self, times: float):
        # Fazendo Elevação de Grau para Pesos
        t = times
        p = self.basis.degree
        s = len(set(self.basis.knot_vector)) - 2
        new_weights = list()
        for i in range(0, p + s + t + 1):
            weight = sum(
                comb(p, j) * comb(t, i - j) * self.weights[j] / comb(p + t, i)
                for j in range(
                    max(0, i - t),
                    min(p, i) + 1
                )
            )
            new_weights.append(weight)
        
        # Atualizando Pontos de Controle a Partir dos Pesos
        for d in range(self.dimension):
            for i in range(len(self.control_points)):
                self.control_points[i][d] *= self.weights[i]

        # Fazendo Elevação de Grau da Super-Classe
        super().degree_elevation(times)

        # Atualizando Pesos
        self.weights = new_weights.copy()

        # Atualizando Pontos de Controle a Partir dos Pesos
        for d in range(self.dimension):
            for i in range(len(self.control_points)):
                self.control_points[i][d] /= self.weights[i]

    def __call__(self, t: float):
        # Inicializando Ponto
        point = list()

        # Calculando Denominador Comum da NURBS
        D = sum([
            self.basis(self.basis.degree, i, t) * self.weights[i]
            for i in range(self.basis.n_basis)
        ])

        # Calculando Cada Dimensão do Ponto
        for d in range(self.dimension):
            N = sum([
                self.basis(self.basis.degree, i, t) * self.control_points[i][d] * self.weights[i]
                for i in self.basis.not_null_spans(t)
            ])
            point.append(N / D)
        
        return point

class NURBS_Surface(BSpline_Surface):
    def __init__(
        self, 
        degree: list[int],
        knot_vectors: list[list[float]],
        control_points: list[list[list]],
        weights: list[list[float]]
    ) -> None:
        super().__init__(degree, knot_vectors, control_points)
        self.weights = weights
        
    def __call__(self, u: float, v: float) -> list[float]:
        point = list()
        
        # Calculando índices de Knot Spans não nulos
        U_not_null_knot_spans = self.basis[0].not_null_spans(u)
        V_not_null_knot_spans = self.basis[1].not_null_spans(v)

        # Calculando Denominador Comum da NURBS
        D = sum([
            self.basis[0](self.basis[0].degree, i, u) *
            self.basis[1](self.basis[1].degree, j, v) *
            self.weights[i][j]
            for j in V_not_null_knot_spans
            for i in U_not_null_knot_spans
        ])

        for d in range(self.dimension):
            N = sum([
                (
                    self.basis[0](self.basis[0].degree, i, u) *
                    self.basis[1](self.basis[1].degree, j, v) *
                    self.control_points[i][j][d] *
                    self.weights[i][j]
                )
                for j in V_not_null_knot_spans
                for i in U_not_null_knot_spans
            ])
            point.append(N / D)
        return point

# --------------------------------------------------
# 3 - Curvas de Bézier - Funções Relacionadas
# --------------------------------------------------
def bezier_equiv_coord(c: float, c0: float, c2: float):
   return 2 * c - 0.5 * (c0 + c2)

def bernstein_polynomial(index: int, grade: int, region: float):
   # Renomeando Parâmetros para Facilitar os Cálculos
   i, p, t = index, grade, region
   
   # Verificando Validade dos Parâmetros
   if i < 0 or i > p:
      raise ValueError(f'Index {i} does not exist for Bernstein Polynomial with Grade {p}.')
   
   # Calculando Polinômio na Região Informada
   return (factorial(p) / (factorial(i) * factorial(p - i))) * t ** i * (1 - t) ** (p - i)

# --------------------------------------------------
# 4 - Transformador - Classes Relacionadas
# --------------------------------------------------
class GeometricalTransformer:
    # Matrizes de Rotação
    def Rx(self, angle: float):
        angle = angle * pi / 180
        Rot = Matrix(4, 4)
        Rot[0, 0] = 1
        Rot[1, 1] = cos(angle)
        Rot[1, 2] = sin(angle)
        Rot[2, 1] = -sin(angle)
        Rot[2, 2] = cos(angle)
        Rot[3, 3] = 1
        return Rot
    
    def Ry(self, angle: float):
        angle = angle * pi / 180
        Rot = Matrix(4, 4)
        Rot[0, 0] = cos(angle)
        Rot[0, 2] = -sin(angle)
        Rot[1, 1] = 1
        Rot[2, 0] = sin(angle)
        Rot[2, 2] = cos(angle)
        Rot[3, 3] = 1
        return Rot
    
    def Rz(self, angle: float):
        angle = angle * pi / 180
        Rot = Matrix(4, 4)
        Rot[0, 0] = cos(angle)
        Rot[0, 1] = sin(angle)
        Rot[1, 0] = -sin(angle)
        Rot[1, 1] = cos(angle)
        Rot[2, 2] = 1
        Rot[3, 3] = 1
        return Rot
    
    # Métodos Públicos
    def calculate_centroid(self, points: list[list[float]]) -> list[float]:
        n_points = len(points)
        n_coordinates = len(points[0])
        centroid = n_coordinates * [0]
        for point in points:
            for i in range(n_coordinates):
                centroid[i] += point[i]
        for i in range(n_coordinates):
            centroid[i] /= n_points
        return centroid
    
    def calculate_colinearity(self, points: list[list[float]]) -> float:
      factor = 0
      for i in range(0, len(points) - 2):
         diag1 = points[i][0] * points[i + 1][1] + points[i + 1][0] * points[i + 2][1] + points[i + 2][0]  * points[i][1]
         diag2 = points[i][0] * points[i + 2][1] + points[i + 1][0] * points[i][1] + points[i + 2][0]  * points[i + 1][1]
         factor += abs(diag1 - diag2)
      return abs(factor)

    def homogenize_coordinates(self, x: float, y: float, z: float, h: float) -> Matrix:
        h_matrix = Matrix(1, 4)
        h_matrix[0, 0] = x * h
        h_matrix[0, 1] = y * h
        h_matrix[0, 2] = z * h
        h_matrix[0, 3] = 1
        return h_matrix
    
    def heterogenize_coordinates(self, h_matrix: Matrix) -> list[float]:
        if h_matrix.n_rows != 1 or h_matrix.n_colmuns != 4:
            raise ValueError('The homogenized coordinates matrix must have 1 row and 4 columns.')
        h_matrix = h_matrix.to_list()[0]
        coordinates = [h_matrix[i] / h_matrix[3] for i in range(3)]
        return coordinates
    
    def translate(self, x: float, y: float, z: float, tx: float, ty: float, tz: float):
        # Homogenizando Coordenadas
        h = self.homogenize_coordinates(x, y, z, 1)

        # Gerando Matriz de Translação 3D
        Trans = Matrix(4, 4)
        Trans.fill_diagonal(1)
        Trans[3, 0] = tx
        Trans[3, 1] = ty
        Trans[3, 2] = tz

        # Transladando e Retornando Pontos
        ht = h * Trans
        return self.heterogenize_coordinates(ht)

    def rotate(self, x: float, y: float, z: float, rotations: list[Matrix]) -> tuple[float]:
        # Homogenizando Coordenadas
        h = self.homogenize_coordinates(x, y, z, 1)

        # Gerando Matriz de Rotação 3D
        Rot = Matrix(4, 4)
        Rot.fill_diagonal(1.0)
        for rotation in rotations:
            Rot = Rot * rotation

        # Rotacionando e Retornando Pontos
        hr = h * Rot
        return self.heterogenize_coordinates(hr)
    
    def project_parallel(self, x: float, y: float, z: float) -> tuple[float]:
        return x, y
    
    def project_perspective(self, x: float, y: float, z: float, x_cop: float, y_cop: float, z_cop: float) -> tuple[float]:
        # Homogenizando Coordenadas
        h = self.homogenize_coordinates(x, y, z, 1)

        # Gerando Matriz de Projeção
        P = Matrix(4, 4)
        P[0, 0] = 1
        P[1, 1] = 1
        P[2, 0] = - x_cop / z_cop 
        P[2, 1] = - y_cop / z_cop 
        P[2, 3] = - 1 / z_cop 
        P[3, 3] = 1

        # Projetando e Retornando Pontos
        hp = h * P
        u, v, n = self.heterogenize_coordinates(hp)
        return u, v