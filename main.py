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
    scip_solution, statusSCIP = machineSCIP.solve()
    print(f"Best solution: {scip_solution} with cost {statusSCIP}\n\n\n")
    initial_solution, status = machine.solve()

    initial_cost = sum(initial_solution[i] * objective[i] for i in range(num_variables))
    root = Node(solution=initial_solution, cost=initial_cost, status=status, indexes=[], signs=[], values=[])

    result = machine.branch_and_bound(root)


    # bnb = BranchAndBound(info)



    #
    # if root:
    #     print("Solução ótima encontrada:")
    #     for i, value in enumerate(root):
    #         print(f'x{i + 1} = {value}')
    # else:
    #     print("Nenhuma solução ótima encontrada.")





    # if not all(isinstance(item, int) for item in root):
    #     solution = machine.branch_and_bound(root)
    # else:
    #     solution = root
    #
    # if solution:
    #     print("Solução ótima encontrada:")
    #     for i, value in enumerate(solution):
    #         print(f'x{i+1} = {value}')
    # else:
    #     print("Nenhuma solução ótima encontrada.")