from math import (
    sin,
    cos,
    radians,
    factorial,
    comb
)

# --------------------------------------------------
# 1 - B-Splines - Classes Relacionadas
# --------------------------------------------------
class BSpline:
    def __init__(self, degree: int, knot_vector: list[float], control_points: list[list]) -> None:
        self.degree = degree
        self.knot_vector = knot_vector.copy()
        self.n_basis = len(knot_vector) - degree - 1
        self.control_points = control_points.copy()
        self.dimension = len(control_points[0])
    
    def basis(self, p: int, i: int, t: float):
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
            N += N1 / D1 * self.basis(p - 1, i, t)
        if D2 != 0.0:
            N += N2 / D2 * self.basis(p - 1, i + 1, t)
        return N
    
    def knot_insertion_alpha(self, k: int, knot: float, i: int):
        p = self.degree
        if i <= (k - p):
            alpha = 1
        elif (i >= (k - p + 1)) and (i <= k):
            alpha = knot - self.knot_vector[i]
            alpha /= (self.knot_vector[i + p] - self.knot_vector[i])
        elif i >= (k + 1):
            alpha = 0
        return alpha
        
    def knot_insertion(self, k: int, knot: float):
        # Adicionando Knot
        p = self.degree
        new_knot_vector = self.knot_vector.copy()
        new_knot_vector.insert(k + 1, knot)

        # Criando Novos Pontos de Controle
        new_control_points = list()
        for i in range(0, self.n_basis + 1):
            # Determinando Alfa
            alpha = self.knot_insertion_alpha(k, knot, i)

            # Calculando Pontos
            control_point = [0] * self.dimension
            for d in range(self.dimension):
                if alpha:
                    control_point[d] += alpha * self.control_points[i][d]
                if (1 - alpha):
                    control_point[d] += (1 - alpha) * self.control_points[i - 1][d]
            new_control_points.append(control_point.copy())
        
        # Atualizando Atributos
        self.n_basis += 1
        self.knot_vector = new_knot_vector
        self.control_points = new_control_points
    
    def knot_insertions(self, knots: list[float]):
        for knot in reversed(knots):
            self.knot_insertion(self.degree, knot)
    
    def degree_elevation(self, times: float):
        # Verificando se a B-Spline é Equivalente à uma Curva de Bézier
        if len(set(self.knot_vector)) != 2:
            raise RuntimeError('The Curve must be a Bézier Equivalent Curve.')

        # Calculando Novo Número de Funções de Base
        t = times
        s = len(set(self.knot_vector)) - 2
        new_n_basis = self.n_basis + t * (s + 1)

        # Calculando Novo Vetor de Knots
        new_knot_vector = list()
        added_knots = set()
        for knot in self.knot_vector:
            new_multiplicity = self.knot_vector.count(knot) + t
            if knot not in added_knots:
                new_knot_vector.extend([knot] * new_multiplicity)
                added_knots.add(knot)

        # Criando Novos Pontos de Controle
        p = self.degree
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
        self.degree += t
        self.n_basis = new_n_basis
        self.knot_vector = new_knot_vector
        self.control_points = new_control_points
        
    def __call__(self, t: float):
        point = list()
        for d in range(self.dimension):
            point.append(sum([
                self.basis(self.degree, i, t) * self.control_points[i][d]
                for i in range(self.n_basis)
            ]))
        return point

# --------------------------------------------------
# 2 - NURBS - Classes Relacionadas
# --------------------------------------------------
class NURBS(BSpline):
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
        for i in range(0, self.n_basis + 1):
            # Determinando Alfa
            alpha = self.knot_insertion_alpha(k, knot, i)

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
        p = self.degree
        s = len(set(self.knot_vector)) - 2
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
            self.basis(self.degree, i, t) * self.weights[i]
            for i in range(self.n_basis)
        ])

        # Calculando Cada Dimensão do Ponto
        for d in range(self.dimension):
            N = sum([
                self.basis(self.degree, i, t) * self.control_points[i][d] * self.weights[i]
                for i in range(self.n_basis)
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
# 4 - Projeção - Funções Relacionadas
# --------------------------------------------------
def projection_isometric(x: float, y: float, z: float):
   theta = radians(30)
   u = x * cos(theta) - y * cos(theta)
   v = x * sin(theta) + y * sin(theta) + z
   return u, v