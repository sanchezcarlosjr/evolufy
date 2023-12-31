import numpy as np
from cvxopt import matrix
from cvxopt import solvers
from evolufy.information import AvailableInformation
from geneticalgorithm2 import geneticalgorithm2 as ga
from geneticalgorithm2 import Generation


class InvestmentStrategy:
    def optimize(self, information: AvailableInformation):
        return information


class ModernPortfolioTheory:
    def __init__(self):
        self.returns = None
        self.dim = 1
        self.solution = None
        self.covariance_matrix = np.array([])
        self.expected_returns = np.array([])

    def optimize(self, information: AvailableInformation):
        returns = information.valuate()
        self.returns  = returns
        self.expected_returns = np.mean(returns, axis=0)
        self.dim = returns.shape[1]
        self.covariance_matrix = np.cov(returns.T)
        P = matrix(2 * self.covariance_matrix, tc="d")
        q = matrix(-information.risk_level * self.expected_returns, tc="d")
        A = matrix(np.ones((1, self.dim)), tc="d")
        b = matrix(1.0)
        self.solution = solvers.qp(P=P, q=q, A=A, b=b)
        for index, entry in enumerate(self.solution['x']):
            information.update_weight(index, entry)
        return information

    def represent_solution(self):
        w_opt = np.array(self.solution['x']).T
        ERp_opt = w_opt @ self.expected_returns
        varRp_opt = w_opt @ self.covariance_matrix @ w_opt.T
        stdevRp_opt = np.sqrt(varRp_opt)
        return varRp_opt - ERp_opt, ERp_opt, varRp_opt, stdevRp_opt


class GeneticModernPortfolioTheory(ModernPortfolioTheory):
    def __init__(self):
        super().__init__()
        self.covariance_matrix = np.array([])
        self.expected_returns = np.array([])

    def generate_fitness_function(self, q):
        def fitness_function(w):
            if abs(np.sum(w) - 1) > 10 ** -5:
                return 10 ** 10 + np.linalg.norm(w - 1)
            return np.sqrt(w.T @ self.covariance_matrix @ w) - q * self.expected_returns.T @ w

        return fitness_function

    def optimize(self, information: AvailableInformation):
        super().optimize(information)

        varbound = [(-1, 1)] * self.dim

        model = ga(function=self.generate_fitness_function(information.risk_level), dimension=self.dim, variable_type='real',
                   variable_boundaries=varbound,
                   algorithm_parameters={'max_num_iteration': 50, 'population_size': 20000,
                                         'mutation_probability': 0.5, 'elit_ratio': 0.1, 'parents_portion': 0.3,
                                         'selection_type': 'tournament', 'crossover_type': 'shuffle',
                                         'max_iteration_without_improv': None})
        x = np.array(self.solution['x']).T
        print("Quadratic programming solution:", x)
        samples = np.concatenate([x, x * np.random.normal(0, 1, (19999, self.dim))])
        self.solution = model.run(no_plot=True, start_generation=Generation(variables=samples, scores=None),
                                  studEA=True)
        for index, entry in enumerate(self.solution.variable):
            information.update_weight(index, entry)
        return information

    def represent_solution(self):
        w_opt = np.array(self.solution.variable).T
        ERp_opt = w_opt @ self.expected_returns
        varRp_opt = w_opt @ self.covariance_matrix @ w_opt.T
        stdevRp_opt = np.sqrt(varRp_opt)
        return varRp_opt - ERp_opt, ERp_opt, varRp_opt, stdevRp_opt
