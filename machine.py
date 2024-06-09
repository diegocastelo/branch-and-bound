from ortools.linear_solver import pywraplp
from node import Node
import math

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
            self.decision_variables.append(self.solver.NumVar(0, self.infinity, f'x{i}'))

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
            return [var.solution_value() for var in self.decision_variables], status
        else:
            return None

    def solve_pl_model(self, indexes, signs, values):
        aux_solver = pywraplp.Solver.CreateSolver('GLOP')
        objective = aux_solver.Objective()
        decision_variables = []

        for i in range(self.num_variables):
            decision_variables.append(aux_solver.NumVar(0, self.infinity, f'x{i}'))

        for i, array in enumerate(self.constraints):
            constraint = aux_solver.RowConstraint(array[-1], self.infinity, f'constraint_{i}')
            for j, coefficient in enumerate(array[:-1]):
                constraint.SetCoefficient(decision_variables[j], coefficient)

        num_constraints = len(indexes)

        for i in range(num_constraints):
            constraint = None

            if signs[i] == '<=':
                constraint = aux_solver.RowConstraint(-aux_solver.infinity(), values[i], '')
            elif signs[i] == '>=':
                constraint = aux_solver.RowConstraint(values[i], aux_solver.infinity(), '')

            constraint.SetCoefficient(decision_variables[indexes[i]], 1)

        for i in range(self.num_variables):
            objective.SetCoefficient(decision_variables[i], self.objectiveCoefficients[i])

        objective.SetMinimization()

        status = aux_solver.Solve()
        node = Node()
        node.solution = [var.solution_value() for var in decision_variables]
        node.cost = sum(node.solution[i] * self.objectiveCoefficients[i] for i in range(len(node.solution)))
        node.signs = signs
        node.values = values
        node.indexes = indexes
        node.status = status
        # print(aux_solver.ExportModelAsLpFormat(False))
        # print(f"{node.solution} cost: {node.cost}")
        return node


    def is_integer_solution(self, solution):
        return all(float(x).is_integer() for x in solution)

    def create_child_nodes(self, node):
        for i, x in enumerate(node.solution):
            # print(x)
            if not float(x).is_integer():
                lower_bound = math.floor(x)
                upper_bound = math.ceil(x)

                lower_indexes = node.indexes + [i]
                lower_signs = node.signs + ["<="]
                lower_values = node.values + [lower_bound]

                upper_indexes = node.indexes + [i]
                upper_signs = node.signs + [">="]
                upper_values = node.values + [upper_bound]

                lower_node = self.solve_pl_model(lower_indexes, lower_signs, lower_values)
                upper_node = self.solve_pl_model(upper_indexes, upper_signs, upper_values)

                return [lower_node, upper_node]

        return []

    def branch_and_bound(self, root):
        open_nodes = [root]
        best_solution = None
        best_cost = float('inf')

        array_zeros = []
        for i in root.solution:
            array_zeros.append(0.0)

        while open_nodes:
            current_node = open_nodes.pop(0)
            if current_node.solution == array_zeros:
                continue
            # print(current_node.solution)
            if self.is_integer_solution(current_node.solution):
                if current_node.cost < best_cost:
                    best_solution = current_node.solution
                    best_cost = current_node.cost
            elif current_node.status == pywraplp.Solver.INFEASIBLE:
                continue
            elif best_cost < current_node.cost:
                continue
            else:
                child_nodes = self.create_child_nodes(current_node)
                open_nodes.extend(child_nodes)

        if best_solution is not None:
            return best_solution, best_cost
        else:
            return "Nenhuma solução viável encontrada.", "Custo inexistente"
