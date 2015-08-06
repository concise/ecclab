#!/usr/bin/env python3

def is_prime(n):

    # generates min(k, n - 3) integers in the range [2, n - 2]
    def random_integers(n, k):
        import random
        if k >= n - 3:
            yield from range(2, n - 1)
        elif n <= 0xffff:
            yield from random.sample(range(2, n - 1), k)
        else:
            for _ in range(k):
                yield random.randint(2, n - 2)

    # test the primality of n using a
    def rabin_miller_test(n, r, s, a):
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            return True
        for j in range(1, r):
            x = (x * x) % n
            if x == 1:
                return False
            if x == n - 1:
                return True
        return False

    # repeat the test a few times until the required security level is met
    def probabilistic_primality_test(n, security_level):
        k = (security_level >> 1) + (security_level & 1)
        r, s = 0, n - 1
        while (s & 1) == 0:
            r, s = (r + 1), (s >> 1)
        for a in random_integers(n, k):
            if rabin_miller_test(n, r, s, a):
                continue
            else:
                return False
        return True

    if type(n) is not int:
        raise TypeError('is_prime() accepts an integer greater than 1')
    if n < 2:
        raise ValueError('is_prime() accepts an integer greater than 1')
    if n == 2 or n == 3:
        return True
    if n & 1 == 0:
        return False

    # False means n is composite
    # True  means n is probably prime
    return probabilistic_primality_test(n, security_level=128)


if __name__ == '__main__':

    def generate_a_prime_number(max_bit_length=256):
        from random import randint
        for _ in range(4 * max_bit_length):
            n = randint(2, (1 << max_bit_length) - 1)
            if is_prime(n):
                return n

    p = generate_a_prime_number(4)
    if p:
        print(p)
    else:
        print('Cannot find a prime number under limited time')
