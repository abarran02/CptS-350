import unittest

from bdd import *


class BDDTests(unittest.TestCase):
    def setUp(self):
        self.even_bools = [True if i % 2 == 0 else False for i in range(32)]

        prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]  # known graph size
        self.prime_bools = [True if i in prime_list else False for i in range(32)]

        self.g = initialize_graph()

    def test_even(self):
        even = node_set_to_bdd(self.even_bools, 'x')

        # check EVEN(14) exists
        node_exists = check_node_exists(even, 14, 'x')
        self.assertTrue(node_exists)

        # EVEN(13) does not exist
        node_void = check_node_exists(even, 13, 'x')
        self.assertFalse(node_void)

    def test_prime(self):
        prime = node_set_to_bdd(self.prime_bools, 'y')

        # check PRIME(7) exists
        node_exists = check_node_exists(prime, 7, 'y')
        self.assertTrue(node_exists)

        # PRIME(2) does not exist
        node_void = check_node_exists(prime, 2, 'y')
        self.assertFalse(node_void)

    def test_rr(self):
        rr = graph_to_bdd(self.g)

        # check RR(27,3) exists
        edge_exists = check_edge_exists(rr, 27, 3)
        self.assertTrue(edge_exists)

        # RR(27,3) does not exist
        edge_void = check_edge_exists(rr, 16, 20)
        self.assertFalse(edge_void)

    def test_rr2(self):
        rr = graph_to_bdd(self.g)
        rr2 = rr_to_rr2(rr)

        # check RR2(27, 6) exists
        edge_exists = check_edge_exists(rr2, 27, 6)
        self.assertTrue(edge_exists)

        # RR2(27, 9) does not exist
        edge_void = check_edge_exists(rr2, 27, 9)
        self.assertFalse(edge_void)

    def test_rr2star(self):
        rr = graph_to_bdd(self.g)
        rr2 = rr_to_rr2(rr)
        rr2star = transitive_closure(rr2)

        # same edge from rr2 should still exist
        edge_exists = check_edge_exists(rr2star, 27, 6,)
        self.assertTrue(edge_exists)

    def test_statementA(self):
        # putting it all together
        # for each node u in PRIME, there is a node v in EVEN such that u can reach vin a positive even number of steps.
        rr = graph_to_bdd(self.g)
        rr2 = rr_to_rr2(rr)
        rr2star = transitive_closure(rr2)

        # get BDDs for PRIME and EVEN
        prime = node_set_to_bdd(self.prime_bools, 'x')
        even = node_set_to_bdd(self.even_bools, 'y')
        
        # even nodes in RR2star
        even_nodes_even_steps = even & rr2star
        vars_y = bddvar_set('y', 5)
        # eliminate existential quantifier
        some_v = even_nodes_even_steps.smoothing(vars_y)

        # logical equivalent of -> ("if then")
        if_prime_then_v = ~prime | some_v
        # eliminate universal quantifier
        vars_x = bddvar_set('x', 5)
        result = ~((~if_prime_then_v).smoothing(vars_x))

        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
