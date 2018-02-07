""" Gurobi Solver for Rule Placement ILP """

from gurobipy import *
import numpy as np


# directly solve rule placement ILP
def sw_fl_alloc(weight, flow_route, sw_Kj, num_flows):
    # switch-flow allocation matrix A
    # number of OF switches in network
    l = len(sw_Kj.keys())
    # number of flows N
    N = num_flows
    # sw_lst
    sw_lst = sorted(sw_Kj.keys())


    A = [] # row: l, col: N
    MapA = np.zeros([l, N]) # row: l, col: N; 0: known, 1: unknown 


    # create a new model
    m = Model("sw_fl_alloc")
    m.setParam('OutputFlag', False)

    # create variables
    for fl in range(N):
        switches = flow_route[str(fl)]
	switches = [sw for sw in switches if sw in sw_lst]
        for sw in switches:
            row = sw_lst.index(sw)
            MapA[row][fl] = 1
   
    for i in range(l):
        row = []
        for j in range(N):
            if MapA[i][j] == 0:
                row.append(0)
            else:
                row.append(m.addVar(vtype=GRB.BINARY, name="A_{0}_{1}".format(i, j)))
        A.append(row)
    print "number of variables: ", np.matrix(MapA).sum()

    # integrate new variables
    m.update()

    # set objective
    Obj = LinExpr()
    for fl in range(N):
        Obj += quicksum(A[i][fl]* weight[fl] for i in range(l))
    m.setObjective(Obj, GRB.MAXIMIZE)

    # First constraint: for each switch at most k_{j} flows are measured here
    for i in range(l):
        m.addConstr(
            quicksum(A[i][fl] for fl in range(N)) <= sw_Kj[sw_lst[i]], "c0_sw_{0}".format(sw_lst[i]))

    # Third constraint: one flow can not be allocated to more than one switches
    for fl in range(N):
        m.addConstr(
            quicksum(A[i][fl] for i in range(l)) <= 1, "c2_fl_{0}".format(fl))

    m.optimize()
    print m.objVal

    # return results
    results = []
    for i in range(l):
        for j in range(N):
            if MapA[i][j] == 0:
                results.append(A[i][j])
            else:
                results.append(A[i][j].x)
    return np.reshape(results, (l, N))


