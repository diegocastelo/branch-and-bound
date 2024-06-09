from machine import Machine
from machineSCIP import MachineSCIP
from node import Node

def read_data(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    first_line = lines[0].split()
    num_variables = int(first_line[0])
    num_conditions = int(first_line[1])

    objective = list(map(int, lines[1].split()))
    constraints = []
    for i in range(2, 2 + num_conditions):
        constraints.append(list(map(int, lines[i].split())))

    return objective, num_variables, constraints


if __name__ == '__main__':
    objective, num_variables, constraints = read_data("input.txt")

    machine = Machine(objective, num_variables, constraints)

    machineSCIP = MachineSCIP(objective, num_variables, constraints)
    scip_solution, scip_cost = machineSCIP.solve()
    print(f"SCIP:\nSolução ótima: {scip_solution}\nCusto: {scip_cost}\n")

    initial_solution, status = machine.solve()

    initial_cost = sum(initial_solution[i] * objective[i] for i in range(num_variables))
    root = Node(solution=initial_solution, cost=initial_cost, status=status, indexes=[], signs=[], values=[])

    optimal_solution, optimal_cost = machine.branch_and_bound(root)

    print(f"GLOP + Branch and Bound\nSolução ótima: {optimal_solution}\nCusto: {optimal_cost}")

    if optimal_solution == scip_solution and optimal_cost == scip_cost:
        print("Os resultados do SCIP e do GLOP + Branch and Bound estão iguais!")
    else:
        print("Os resultados do SCIP e do GLOP + Branch and Bound não estão iguais!")

