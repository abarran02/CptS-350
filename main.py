import pyeda

def initialize_graph() -> list[list[int]]:
    matrix = [[False] * 32 for _ in range(32)]

    # iterate over all nodes
    for i in range(32):
        for j in range(32):
            # there is an edge from node i to node j if it satisfies this condition
            if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32:
                matrix[j][i] = True
    
    return matrix

def generate_primes(stop: int) -> list[int]:
    # using Sieve of Eratosthenes algorithm
    primes = []
    is_prime = [True] * (stop)
    is_prime[0] = is_prime[1] = False

    for p in range(2, stop):
        if is_prime[p]:
            primes.append(p)
            for i in range(p * p, stop, p):
                is_prime[i] = False

    return primes

if __name__ == "__main__" :
    g = initialize_graph()

    even = [True if i % 2 == 0 else False for i in range(32)]
    
    prime_list = generate_primes(32)
    prime = [True if i in prime_list else False for i in range(32)]
