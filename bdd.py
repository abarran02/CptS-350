from pyeda.boolalg.bdd import BinaryDecisionDiagram
from pyeda.inter import *

def bddvar_set(symbol: str, length: int) -> list[BDDVariable]:
    return [bddvar(f"{symbol * 2}" + str(i)) for i in range(length)]

# bad practice global vars but useful for de-duplication
symbol_i = 'x'
symbol_j = 'y'
# generate lists of vars xx0, xx1, ...
vars_i = bddvar_set(symbol_i, 5)
vars_j = bddvar_set(symbol_j, 5)

def initialize_graph() -> list[list[bool]]:
    matrix = [[False] * 32 for _ in range(32)]

    # iterate over all nodes
    for j in range(32):
        for i in range(32):
            # there is an edge from node i to node j if it satisfies this condition
            if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32:
                matrix[j][i] = True

    return matrix

def node_to_expr(node_id: int, symbol: str) -> Expression:
    id_bin = format(node_id, 'b').rjust(5, '0')

    expr_strs = []
    for idx in range(5):
        node_name = f"{symbol * 2}{idx}"
        expr_strs.append(node_name if int(id_bin[idx]) else f"~{node_name}")

    return expr(" & ".join(expr_strs))

def combine_to_bdd(expr_list: list[Expression]) -> BinaryDecisionDiagram:
    # build BDD from all expressions
    full_expr = expr_list[0]
    for node in expr_list[1:]:
        full_expr |= node

    return expr2bdd(full_expr)

def graph_to_bdd(graph: list[list[bool]]) -> BinaryDecisionDiagram:
    edge_list = []
    for j in range(32):
        for i in range(32):
            # there is an edge from node i to node j
            if graph[j][i]:
                node_i = node_to_expr(i, symbol_i)
                node_j = node_to_expr(j, symbol_j)
                edge_list.append(node_i & node_j)

    return combine_to_bdd(edge_list)

def node_set_to_bdd(nodes: list[bool], symbol: str) -> BinaryDecisionDiagram:
    # convert the node to an expression if it is marked True in 'nodes'
    expr_list = [node_to_expr(node_id, symbol) for node_id in range(len(nodes)) if nodes[node_id]]
    return combine_to_bdd(expr_list)

def add_reachability(rr1: BinaryDecisionDiagram, rr2: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    # assume 'z' is an unused symbol in rr
    vars_z = bddvar_set('z', 5)
    
    # define BDDs from x to z, then z to y
    one_step = rr1.compose({vars_i[idx]: vars_z[idx] for idx in range(5)})
    two_step = rr2.compose({vars_j[idx]: vars_z[idx] for idx in range(5)})

    # combine steps and eliminate existiential quantifier
    return expr2bdd(one_step & two_step).smoothing(vars_z)

def rr_to_rr2(rr: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    return add_reachability(rr, rr)

def transitive_closure(rr: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    bdd = rr
    
    # fixed point algorithm for transitive closure
    while True:
        prev_bdd = bdd
        bdd = bdd | add_reachability(bdd, rr)

        # bdd has same truth table after compose
        if bdd.equivalent(prev_bdd):
            break

    return bdd

def check_node_exists(bdd: BinaryDecisionDiagram, node_id: int, node_symbol: str) -> bool:
    id_bin = format(node_id, 'b').rjust(5, '0')
    vars = bddvar_set(node_symbol, 5)

    node = {}
    for idx in range(5):
        node[vars[idx]] = int(id_bin[idx])

    restricted = bdd.restrict(node)
    return restricted.is_one()

def check_edge_exists(bdd: BinaryDecisionDiagram, node_i: int, node_j: int) -> bool:
    i_bin = format(node_i, 'b').rjust(5, '0')
    j_bin = format(node_j, 'b').rjust(5, '0')

    # build dictionary of edge from bddvars
    edge = {}
    for idx in range(5):
        edge[vars_i[idx]] = int(i_bin[idx])
        edge[vars_j[idx]] = int(j_bin[idx])

    restricted = bdd.restrict(edge)
    return restricted.is_one()
