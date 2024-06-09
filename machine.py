from ortools.linear_solver import pywraplp

class Machine:
    def __init__(self, objective, num_variables, constraints):
        self.objectiveCoefficients = objective
        self.num_variables = num_variables
        self.constraints = constraints
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.infinity = self.solver.infinity()
        self.decision_variables = []
        self.objective = self.solver.Objective()

    def set_decision_variables(self):
        for i in range(self.num_variables):  # Corrigido para iterar sobre um range
            self.decision_variables.append(self.solver.NumVar(0, self.infinity, f'x{i}'))

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
    
    def solverPLnode(self, indexes,sign,value):
        for i in range(len(indexes)):
            new_node = Node(indexes=indexes, sign=sign, value=value)
            constraint_expr = sum(self.decision_variables[idx] * new_node.sign[idx] for idx in new_node.indexes)
            if new_node.value == 'lower':
                self.solver.add(constraint_expr >= 0)
            elif new_node.value == 'upper':
                self.solver.add(constraint_expr <=0)
            status = self.solver.solver()
            if status == pywraplp.Solver.OPTIMAL:
                new_node.solution = [var.solution_value() for var in self.decision_variables]
                new_node.cost = sum(new_node.solution[i] * self.objectiveCoefficients[i] for i in range(self.num_variables))
                return new_node
        return None
    
