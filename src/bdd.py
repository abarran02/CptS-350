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
    """Initialize a graph of 32 nodes where there is an edge from
    node i to node j if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32

    Returns:
        list[list[bool]]: Matrix of true/false, where true indicates an edge from node i to node j
    """
    matrix = [[False] * 32 for _ in range(32)]

    # iterate over all nodes
    for j in range(32):
        for i in range(32):
            # there is an edge from node i to node j if it satisfies this condition
            if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32:
                matrix[j][i] = True

    return matrix

def node_to_expr(node_id: int, symbol: str) -> Expression:
    """Convert a node with binary id to an expression

    Args:
        node_id (int): base 10 id representation
        symbol (str): for variable naming, like 'x'

    Returns:
        Expression: boolean expression, like "xx0 & xx1 & ~xx2 ..."
    """
    id_bin = format(node_id, 'b').rjust(5, '0')

    expr_strs = []
    for idx in range(5):
        node_name = f"{symbol * 2}{idx}"  # like 'xx0'
        expr_strs.append(node_name if int(id_bin[idx]) else f"~{node_name}")  # like xx0 or ~xx0 for true/false

    return expr(" & ".join(expr_strs))

def combine_to_bdd(expr_list: list[Expression]) -> BinaryDecisionDiagram:
    """Performs logical OR on all elements to generate BDD

    Args:
        expr_list (list[Expression]): list of graph nodes or edges

    Returns:
        BinaryDecisionDiagram: BDD representation of graph
    """
    # build BDD from all expressions
    full_expr = expr_list[0]
    for node in expr_list[1:]:
        full_expr |= node

    return expr2bdd(full_expr)

def graph_to_bdd(graph: list[list[bool]]) -> BinaryDecisionDiagram:
    """Convert a given matrix representation of a graph to a BDD

    Args:
        graph (list[list[bool]]): Graph matrix defining edges from nodes i to nodes j

    Returns:
        BinaryDecisionDiagram: BDD over xx0, xx1 ...; yy0, yy1 ...
    """
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
    """Convert a set of nodes to a BDD, no edges

    Args:
        nodes (list[bool]): Defines nodes in set, as true (exists) or false (does not exist)
        symbol (str): variable symbol for set, like 'x' for 'xx0'

    Returns:
        BinaryDecisionDiagram: BDD over xx0, xx1 ...
    """
    # convert the node to an expression if it is marked True in 'nodes'
    expr_list = [node_to_expr(node_id, symbol) for node_id in range(len(nodes)) if nodes[node_id]]
    return combine_to_bdd(expr_list)

def extend_reachability(rr1: BinaryDecisionDiagram, rr2: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    """Extend reachability from nodes of one BDD to the other

    Args:
        rr1 (BinaryDecisionDiagram): starting BDD
        rr2 (BinaryDecisionDiagram): ending BDD

    Returns:
        BinaryDecisionDiagram: BDD with reachability in two steps from rr1 to rr2
    """
    # assume 'z' is an unused symbol in rr
    vars_z = bddvar_set('z', 5)

    # define BDDs from x to z, then z to y
    one_step = rr1.compose({vars_i[idx]: vars_z[idx] for idx in range(5)})
    two_step = rr2.compose({vars_j[idx]: vars_z[idx] for idx in range(5)})

    # combine steps and eliminate existiential quantifier
    return (one_step & two_step).smoothing(vars_z)

def rr_to_rr2(rr: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    """Generate BDD of reachability in two steps of rr

    Args:
        rr (BinaryDecisionDiagram): BDD to extend

    Returns:
        BinaryDecisionDiagram: two step extended BDD
    """
    return extend_reachability(rr, rr)

def transitive_closure(rr: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    """Perform the fixed point algorithm for transitive closure on rr

    Args:
        rr (BinaryDecisionDiagram): BDD to extend

    Returns:
        BinaryDecisionDiagram: infinite extended BDD
    """
    bdd = rr

    # fixed point algorithm for transitive closure
    while True:
        prev_bdd = bdd
        bdd = bdd | extend_reachability(bdd, rr)

        # bdd has same truth table after compose
        if bdd.equivalent(prev_bdd):
            break

    return bdd

def check_node_exists(bdd: BinaryDecisionDiagram, node_id: int, node_symbol: str) -> bool:
    """Determine whether the given node exists in the given BDD

    Args:
        bdd (BinaryDecisionDiagram): BDD to check existence in
        node_id (int): node to check existence of
        node_symbol (str): variable symbol of the node

    Returns:
        bool: node exists (true) or node does not exist (false)
    """
    id_bin = format(node_id, 'b').rjust(5, '0')
    vars = bddvar_set(node_symbol, 5)

    node = {}
    for idx in range(5):
        node[vars[idx]] = int(id_bin[idx])  # get true/false for each character of binary id

    restricted = bdd.restrict(node)
    return restricted.is_one()

def check_edge_exists(bdd: BinaryDecisionDiagram, node_i: int, node_j: int) -> bool:
    """Determine whether the given edge exists in the given BDD

    Args:
        bdd (BinaryDecisionDiagram): BDD to check existence in
        node_i (int): starting node
        node_j (int): ending node

    Returns:
        bool: edge exists (true) or edge does not exist (false)
    """
    i_bin = format(node_i, 'b').rjust(5, '0')
    j_bin = format(node_j, 'b').rjust(5, '0')

    # build dictionary of edge from bddvars
    edge = {}
    for idx in range(5):
        edge[vars_i[idx]] = int(i_bin[idx])
        edge[vars_j[idx]] = int(j_bin[idx])

    restricted = bdd.restrict(edge)
    return restricted.is_one()
