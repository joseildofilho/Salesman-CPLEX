import cplex
import sys
from cplex.exceptions import CplexError

def read_instance(filePath):
    f = open(filePath, "r")
    n = int(f.readline())
    adjMatrix = []

    for i in range(n):
       l = f.readline()
       row = [int(i) for i in l.split()]
       adjMatrix.append(row) 

    return n,adjMatrix

def create_problem(n_vertices, adj_matrix):

    prob = cplex.Cplex()
    prob.objective.set_sense(prob.objective.sense.minimize)

    # Criando variáveis X's
    coeficientes_x = [0] * (n_vertices ** 2)
    lower_bounds_x = [0] * (n_vertices ** 2)
    upper_bounds_x = [1] * (n_vertices ** 2)
    tipos          = 'I' * (n_vertices ** 2)
    nomes_x        = ['X_%i_%i' % (vertice, color) 
            for color in range(n_vertices) 
                for vertice in range(n_vertices)]

    prob.variables.add(obj=coeficientes_x, 
            lb=lower_bounds_x, 
            ub=upper_bounds_x, 
            types=tipos,
            names=nomes_x)
    # Criando variáveis Y's
    coeficientes_y = [1] * n_vertices
    lower_bounds_y = [0] * n_vertices
    upper_bounds_y = [1] * n_vertices
    tipos          = 'I' * n_vertices
    nomes_y        = ['Y_%i' % i for i in range(n_vertices)]

    prob.variables.add(obj=coeficientes_y, 
            lb=lower_bounds_y, 
            ub=upper_bounds_y, 
            types=tipos,
            names=nomes_y)

    for color in range(n_vertices):
        for vertice in range(n_vertices):
            row = [[['X_%i_%i' % (vertice, color), 'Y_%i' % color], [1.0,-1.0]]]
            prob.linear_constraints.add(lin_expr = row, senses='L', rhs=[0], names=["COR_%i_PINTA_VERTICE_%i" % (color, vertice)])

    for i in range(n_vertices):
        for j in range(i+1, n_vertices):
            if adj_matrix[i][j] == 1:
                for color in range(n_vertices):
                    row = [[['X_%i_%i' % (i, color), 'X_%i_%i' % (j, color), 'Y_%i'% color], [1.0,1.0,-1.0]]]
                    prob.linear_constraints.add(lin_expr = row, senses='L', rhs=[0], names=['CONFLITO_R1_(%i, %i)_R2_%i' % (i,j,color)])

    for j in range(n_vertices):
        row = [[['X_%i_%i' % (j, color) for color in range(n_vertices)], [1.0] * n_vertices]]
        prob.linear_constraints.add(lin_expr = row, senses='E', rhs=[1], names=['VERTICE_%i_COR_%i' % (j,color)])

    return prob

if __name__ == '__main__':
    try:
        n, adj_matrix = read_instance(sys.argv[1])
        prob = create_problem(n, adj_matrix)
        prob.write('modelo.lp')
        prob.solve()
    except CplexError as e:
        print(e)
    # solution.get_status() returns an integer code
    print("Solution status = ", prob.solution.get_status(), ":")
    # the following line prints the corresponding string
    print(prob.solution.status[prob.solution.get_status()])
    print("Solution value  = ", prob.solution.get_objective_value())

    print("Solution:")
    for i in range(n):
        for j in range(n):
            if prob.solution.get_values("X_%i_%i" % (i,j)):
                print(i,j)
 
