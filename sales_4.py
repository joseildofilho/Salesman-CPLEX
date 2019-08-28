import cplex
import sys
from cplex.exceptions import CplexError
from tsp_parser import read_path
from tsplib95 import tsplib95
from networkx import to_numpy_array

def read_instance(filePath):
    f = open(filePath, "r")
    n = int(f.readline())
    adjMatrix = []

    for i in range(n):
       l = f.readline()
       row = [int(i) for i in l.split()]
       adjMatrix.append(row) 

    return n,adjMatrix

def create_problem(n_vertices, adj_matrix, c):

    prob = c
    prob.objective.set_sense(prob.objective.sense.minimize)

    I = range(len(adj_matrix))
    J = range(len(adj_matrix[0]))
    T = range(1, n_vertices + 1)

    # Criando variaveis
    # Assim fica, para cada vertice, temos um coeficiente d_{i,j} para um somatorio de variaveis de uso y_{i,j,t}

    y = 'Y_(%i_%i)_%i' # Variável Y

    coeficientes_y = []
    lower_bounds_y = [] 
    upper_bounds_y = [] 
    tipos_y        = ''     
    nomes_y        = []
    for i in I:
        # por algum motivo místico o programa só funciona com a tabela, completa
        for j in J:
            for t in T:
                coeficientes_y.append(adj_matrix[i][j])
                lower_bounds_y.append(0)
                upper_bounds_y.append(1)
                tipos_y += 'I'
                nomes_y.append(y % (i,j,t))

    # Check se as variáveis estão em quantidades iguais P.S.: o Teste é feito no olho kkkk'
    #print(len(coeficientes_y), len(lower_bounds_y), len(upper_bounds_y), len(tipos_y), len(nomes_y))

    prob.variables.add(obj=coeficientes_y, 
            lb=lower_bounds_y, 
            ub=upper_bounds_y, 
            types=tipos_y,
            names=nomes_y)

    # Para todo vértice, exceto o V(0), e toda variavel y pelo tempo t


    for j in J:
        equation_i_j = []
        coeff_i_j    = []
        row_i_j      = [[equation_i_j, coeff_i_j]]

        equation_j_i = []
        coeff_j_i    = []
        row_j_i      = [[equation_j_i, coeff_j_i]]

        for i in I:
            if j != i:
                equation_i_j += [y % (i, j, t) for t in T]
                coeff_i_j    += [1.0] * len(T)

                equation_j_i += [y % (j, i, t) for t in T]
                coeff_j_i    += [1.0] * len(T)

        prob.linear_constraints.add(lin_expr = row_i_j, senses='E', rhs=[1], names=["ARESTA_I_%i_J_%i" % (i,j)])
        prob.linear_constraints.add(lin_expr = row_j_i, senses='E', rhs=[1], names=["ARESTA_J_%i_I_%i" % (j,i)])

    for t in T:
        equation = []
        coeff    = []
        row = [[equation, coeff]]

        equation += [y % (i,j,t) for i in I for j in J] 
        coeff    += [1.0] * len(J) * len(I)

        prob.linear_constraints.add(lin_expr = row, senses='E', rhs=[1], names=['ARESTA_EM_USO_I_%i_J_%i' % (i,j)])
    
    start = 0

    for j in range(len(adj_matrix[0])):
        equation = []
        coeff    = []
        row      = [[equation, coeff]]
        if j != start:
            for i in I:
                if i != j:
                    for t in T:
                        equation += [y % (i,j,t), y % (j,i,t)]
                        coeff    += [t, -t]
            prob.linear_constraints.add(lin_expr = row, senses='E', rhs=[1], names=['FLUXO_DE_I_%i_PARA_J_%i' % (i,j)])

    return prob

if __name__ == '__main__':
    c = cplex.Cplex()
    c.parameters.timelimit.set(30)
    try:
        adj_matrix = to_numpy_array(tsplib95.load_problem(sys.argv[1]).get_graph())
        n = len(adj_matrix)
        prob = create_problem(n, adj_matrix, c)
        prob.write('modelo.lp')
        prob.solve()
    except CplexError as e:
        print(e)

    print('Solution status =', prob.solution.get_status())

    print(prob.solution.status[prob.solution.get_status()])
    print('Solution value=', prob.solution.get_objective_value())

    print('Solution:')
    for t in range(1,1+n):
        for i in range(len(adj_matrix)):
            for j in range(len(adj_matrix[0])):
                if prob.solution.get_values('Y_(%i_%i)_%i' % (i,j,t)):
                    print('Y_(%i_%i)_%i' % (i,j,t))
 
