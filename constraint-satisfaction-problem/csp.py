from constraint import *
problem = Problem()


def add_l_junction_constraint(x, y):
    problem.addConstraint(lambda a, b: (a == 'R' and b == 'P') or
                                       (a == 'R' and b == 'R') or
                                       (a == 'P' and b == 'R') or
                                       (a == 'A' and b == 'M') or
                                       (a == 'A' and b == 'A') or
                                       (a == 'M' and b == 'A'),
                          (x, y))


def add_arrow_junction_constraint(x, y, z):
    problem.addConstraint(lambda a, b, c: (a == 'A' and b == 'P' and c == 'A') or
                                          (a == 'M' and b == 'P' and c == 'M') or
                                          (a == 'P' and b == 'M' and c == 'P'),
                          (x, y, z))


def add_fork_junction_constraint(x, y, z):
    problem.addConstraint(lambda a, b, c: (a == 'A' and b == 'A' and c == 'M') or
                                          (a == 'M' and b == 'A' and c == 'A') or
                                          (a == 'A' and b == 'M' and c == 'A') or
                                          (a == 'P' and b == 'P' and c == 'P') or
                                          (a == 'M' and b == 'M' and c == 'M'),
                          (x, y, z))


# Initialize edges
possible_edges = ['A', 'R', 'M', 'P']
for i in range(15):
    problem.addVariable(i, possible_edges)

# Build Polyhedron
add_l_junction_constraint(0, 1)
add_l_junction_constraint(4, 5)
add_l_junction_constraint(6, 7)
add_fork_junction_constraint(3, 2, 13)
add_fork_junction_constraint(8, 10, 9)
add_fork_junction_constraint(11, 12, 14)
add_arrow_junction_constraint(7, 8, 0)
add_arrow_junction_constraint(1, 9, 2)
add_arrow_junction_constraint(3, 14, 4)
add_arrow_junction_constraint(5, 12, 6)
add_arrow_junction_constraint(11, 13, 10)

# Generate and print solution
solution = problem.getSolutions()
index = 0
for row in solution:
    print(solution[index])
    index += 1