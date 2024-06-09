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
        for i in range(self.num_variables):  # Corrigido para iterar sobre um range
            self.decision_variables.append(self.solver.IntVar(0, self.infinity, f'x{i}'))

    def set_constraints(self):
        for i, array in enumerate(self.constraints):
            constraint = self.solver.RowConstraint(array[-1], self.infinity, f'constraint_{i}')
            for j, coefficient in enumerate(array[:-1]):
                constraint.SetCoefficient(self.decision_variables[j], coefficient)

    def set_objective(self):
        for i in range(self.num_variables):  # Corrigido para iterar sobre um range
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

    def solver_pl_node(self, indexes, sign, value):
        for i in range(len(indexes)):
            new_node = Node(indexes=indexes, sign=sign, value=value)
            constraint_expr = sum(self.decision_variables[idx] * new_node.sign[idx] for idx in new_node.indexes)
            if new_node.value == 'lower':
                self.solver.add(constraint_expr >= 0)
            elif new_node.value == 'upper':
                self.solver.add(constraint_expr <= 0)
            status = self.solver.solver()
            if status == pywraplp.Solver.OPTIMAL:
                new_node.solution = [var.solution_value() for var in self.decision_variables]
                new_node.cost = sum(
                    new_node.solution[i] * self.objectiveCoefficients[i] for i in range(self.num_variables))
                return new_node
            elif status == pywraplp.Solver.INFEASIBLE:
                return "SOLUÇÃO INVIÁVEL"
            elif all(isinstance(item, int) for item in new_node.value):
                return "VALORES INTEIROS"

            # elif solução quebrada pior que uma solução de valores inteiros

        return None

    def branch_and_bound(self, root):
        open_nodes = [
            Node(indexes=list(range(self.num_variables)), sign=[1] * self.num_variables, value='lower', solution=root, cost= sum(
                    root[i] * self.objectiveCoefficients[i] for i in range(self.num_variables)))]
        best_node = None
        best_cost = float('inf')

        while open_nodes:
            current_node = open_nodes.pop(0)
            if current_node.cost >= best_cost:
                continue
            print(f"Exploring node with cost {current_node.cost}")
            result = self.solver_pl_node(current_node.indexes, current_node.sign, current_node.value)
            if result:
                if result.cost < best_cost:
                    best_node = result
                    best_cost = result.cost
                    open_nodes.append(Node(indexes=result.indexes, sign=result.sign, value='lower'))
                    open_nodes.append(Node(indexes=result.indexes, sign=result.sign, value='upper'))
        return best_node
