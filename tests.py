import unittest

from bdd import *


class BDDTests(unittest.TestCase):
    def setUp(self):
        self.even = [True if i % 2 == 0 else False for i in range(32)]

        prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]  # known graph size
        self.prime = [True if i in prime_list else False for i in range(32)]

        self.g = initialize_graph()

    def test_even(self):
        self.assertTrue(self.even[14])
        self.assertFalse(self.even[13])

    def test_prime(self):
        self.assertTrue(self.prime[7])
        self.assertFalse(self.prime[2])

    def test_rr(self):
        rr = graph_to_bdd(self.g, 'x', 'y')

        # check RR(27,3) exists
        edge_exists = check_edge_exists(rr, 27, 'x', 3, 'y')
        self.assertTrue(edge_exists)

        # RR(27,3) does not exist
        edge_void = check_edge_exists(rr, 16, 'x', 20, 'y')
        self.assertFalse(edge_void)

    def test_rr2(self):
        rr = graph_to_bdd(self.g, 'x', 'y')
        rr2 = rr_to_rr2(rr, 'x', 'y')

        # check RR2(27, 6) exists
        edge_exists = check_edge_exists(rr2, 27, 'x', 6, 'y')
        self.assertTrue(edge_exists)

        # RR2(27, 9) does not exist
        edge_void = check_edge_exists(rr2, 27, 'x', 9, 'y')
        self.assertFalse(edge_void)

if __name__ == '__main__':
    unittest.main()
