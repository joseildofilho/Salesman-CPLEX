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

    I = range(len(adj_matrix))
    J = range(len(adj_matrix[0]))
    T = range(1, n_vertices + 1)

    # Criando variaveis
    # Assim fica, para cada vertice, temos um coeficiente d_{i,j} para um somatorio de variaveis de uso y_{i,j,t}

    global x
    x = 'X_(%i_%i)' # Variável X

    coeficientes_x = []
    lower_bounds_x = [] 
    upper_bounds_x = [] 
    tipos_x        = ''     
    nomes_x        = []
    for i in I:
        # por algum motivo místico o programa só funciona com a tabela, completa
        for j in J:
            coeficientes_x.append(adj_matrix[i][j])
            lower_bounds_x.append(0)
            upper_bounds_x.append(1)
            tipos_x += 'I'
            nomes_x.append(x % (i,j))

    # Check se as variáveis estão em quantidades iguais P.S.: o Teste é feito no olho kkkk'
    print(len(coeficientes_x), len(lower_bounds_x), len(upper_bounds_x), len(tipos_x), len(nomes_x))

    prob.variables.add(obj=coeficientes_x, 
            lb=lower_bounds_x, 
            ub=upper_bounds_x, 
            types=tipos_x,
            names=nomes_x)

    for j in J:
        equation_i_j = []
        coeff_i_j    = []
        row_i_j = [[equation_i_j, coeff_i_j]]
    
        equation_j_i = []
        coeff_j_i    = []
        row_j_i = [[equation_j_i, coeff_j_i]]
        for i in I:
            if j != i:
                equation_i_j += [x % (i,j)]            
                coeff_i_j      += [1.]

                equation_j_i += [x % (j,i)]            
                coeff_j_i      += [1.]

        prob.linear_constraints.add(lin_expr=row_i_j, senses='E', rhs=[1], names=['ARESTA_CHEGA_EM_J_%i' % j])
        prob.linear_constraints.add(lin_expr=row_j_i, senses='E', rhs=[1], names=['ARESTA_SAIND_EM_J_%i' % j])

    return prob

def where(prob, k, n):
    for i in range(0, n):
        if prob.solution.get_values(x % (k, i)):
            return (k, i)

if __name__ == '__main__':
    try:
        n, adj_matrix = read_instance(sys.argv[1])
        prob = create_problem(n, adj_matrix)
        prob.solve()
        ready = False
        while not ready:
            for i in range(n):
                path = {}
                current = where(prob, i, n)
                while current[0] not in path and len(path) < n:
                    path[current[0]] = current
                    current = where(prob, current[1], n)
                    print(current)
                if len(path) != n:
                    equation = []
                    coeff    = []
                    row = [[equation, coeff]]
                    for v in path.values():
                        equation += [x % v]
                        coeff.append(1)
                    prob.linear_constraints.add(lin_expr=row, senses='L', rhs=[len(path) - 1], names=['PROIBIDO %i %i' % v])
                else:
                    ready = True
                    break
                prob.solve()
        prob.write('modelo.lp')
    except CplexError as e:
        print(e)

    print('Solution status =', prob.solution.get_status())

    print(prob.solution.status[prob.solution.get_status()])
    print('Solution value=', prob.solution.get_objective_value())

    print('Solution:')
    for i in range(len(adj_matrix)):
        for j in range(len(adj_matrix[0])):
            if prob.solution.get_values('X_(%i_%i)' % (i,j)):
                print('X_(%i_%i)' % (i,j))
                break
 
