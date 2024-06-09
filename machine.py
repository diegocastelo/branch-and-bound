from ortools.linear_solver import pywraplp
from node import Node


class Machine:
    def __init__(self, objective, num_variables, constraints):
        self.objectiveCoefficients = objective
        self.num_variables = num_variables
        self.constraints = constraints
        self.solver = pywraplp.Solver.CreateSolver('GLOP')
        self.infinity = self.solver.infinity()
        self.decision_variables = []
        self.objective = self.solver.Objective()

    def set_decision_variables(self):
        for i in range(self.num_variables):
            self.decision_variables.append(self.solver.IntVar(0, self.infinity, f'x{i}'))

    def set_constraints(self):
        for i, array in enumerate(self.constraints):
            constraint = self.solver.RowConstraint(array[-1], self.infinity, f'constraint_{i}')
            for j, coefficient in enumerate(array[:-1]):
                constraint.SetCoefficient(self.decision_variables[j], coefficient)

    def set_objective(self):
        for i in range(self.num_variables):
            self.objective.SetCoefficient(self.decision_variables[i], self.objectiveCoefficients[i])
        self.objective.SetMinimization()

    def solve(self):
        self.set_decision_variables()
        self.set_constraints()
        self.set_objective()
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            return [var.solution_value() for var in self.decision_variables]
        else:
            return None

    def solve_pl_model(self, indices, sinais, valores):
        aux_solver = pywraplp.Solver.CreateSolver('GLOP')
        objective = aux_solver.Objective()
        decision_variables = []

        for i in range(self.num_variables):
            decision_variables.append(aux_solver.IntVar(0, self.infinity, f'x{i}'))

        for i, array in enumerate(self.constraints):
            constraint = aux_solver.RowConstraint(array[-1], self.infinity, f'constraint_{i}')
            for j, coefficient in enumerate(array[:-1]):
                constraint.SetCoefficient(decision_variables[j], coefficient)

        num_constraints = len(indices)

        for i in range(num_constraints):
            constraint = None

            if sinais[i] == '<=':
                constraint = aux_solver.RowConstraint(-aux_solver.infinity(), valores[i], '')
            elif sinais[i] == '>=':
                constraint = aux_solver.RowConstraint(valores[i], aux_solver.infinity(), '')

            constraint.SetCoefficient(decision_variables[indices[i]], 1)

        for i in range(self.num_variables):
            objective.SetCoefficient(decision_variables[i], self.objectiveCoefficients[i])

        objective.SetMinimization()

        aux_solver.Solve()
        values = [var.solution_value() for var in decision_variables]
        cost = sum(values[i] * self.objectiveCoefficients[i] for i in range(len(values)))

        return values, cost
