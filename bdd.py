from pyeda.boolalg.bdd import BinaryDecisionDiagram
from pyeda.inter import *


def initialize_graph() -> list[list[bool]]:
    matrix = [[False] * 32 for _ in range(32)]

    # iterate over all nodes
    for j in range(32):
        for i in range(32):
            # there is an edge from node i to node j if it satisfies this condition
            if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32:
                matrix[j][i] = True

    return matrix

def node_to_expr(node_id: int, var_symbol: str) -> Expression:
    id_bin = format(node_id, 'b').rjust(5, '0')

    expr_strs = []
    for idx in range(5):
        node_name = f"{var_symbol * 2}{idx}"
        expr_strs.append(node_name if int(id_bin[idx]) else f"~{node_name}")

    return expr(" & ".join(expr_strs))

def graph_to_bdd(graph: list[list[bool]], start_symbol: str, end_symbol: str) -> BinaryDecisionDiagram:
    edge_list = []
    for j in range(32):
        for i in range(32):
            # there is an edge from node i to node j
            if graph[j][i]:
                node_i = node_to_expr(i, start_symbol)
                node_j = node_to_expr(j, end_symbol)
                edge_list.append(node_i & node_j)

    # build sum of edge expressions for BDD
    full_expr = edge_list[0]
    for edge in edge_list[1:]:
        full_expr |= edge

    return expr2bdd(full_expr)

def rr_to_rr2(rr: BinaryDecisionDiagram, symbol_i: str, symbol_j: str) -> BinaryDecisionDiagram:
    vars_i = [bddvar(f"{symbol_i * 2}" + str(i)) for i in range(5)]
    vars_j = [bddvar(f"{symbol_j * 2}" + str(i)) for i in range(5)]
    # assume 'z' is an unused symbol in rr
    vars_z = [bddvar(f"{'z' * 2}" + str(i)) for i in range(5)]
    
    one_step = rr.compose({vars_i[idx]: vars_z[idx] for idx in range(5)})
    two_step = rr.compose({vars_j[idx]: vars_z[idx] for idx in range(5)})

    # combine steps and eliminate existiential quantifier
    return expr2bdd(one_step & two_step).smoothing(vars_z)

def check_edge_exists(bdd: BinaryDecisionDiagram, node_i: int, symbol_i: str, node_j: int, symbol_j: str) -> bool:
    i_bin = format(node_i, 'b').rjust(5, '0')
    j_bin = format(node_j, 'b').rjust(5, '0')
    # generate lists of vars xx0, xx1, ...
    vars_i = [bddvar(f"{symbol_i * 2}" + str(i)) for i in range(5)]
    vars_j = [bddvar(f"{symbol_j * 2}" + str(i)) for i in range(5)]

    # build dictionary of edge from bddvars
    edge = {}
    for idx in range(5):
        edge[vars_i[idx]] = int(i_bin[idx])
        edge[vars_j[idx]] = int(j_bin[idx])

    restricted = bdd.restrict(edge)
    return not restricted.is_zero()
