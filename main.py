from machine import Machine

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

    print("Objective:", objective)
    print("Variables:", num_variables)
    print("Constraints:", constraints)

    return objective, num_variables, constraints


if __name__ == '__main__':
    objective, num_variables, constraints = read_data("input.txt")

    machine = Machine(objective, num_variables, constraints)
    root = machine.solve()

    if not all(isinstance(item, int) for item in root):
        solution = machine.branch_and_bound(root)
    else:
        solution = root

    if solution:
        print("Solução ótima encontrada:")
        for i, value in enumerate(solution):
            print(f'x{i+1} = {value}')
    else:
        print("Nenhuma solução ótima encontrada.")