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
            x = pow(x, 2, n) # x = pow(a, s * (2 ** j), n)
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
    if n & 1 == 0:
        return False
    if n == 2 or n == 3:
        return True

    # False means n is composite
    # True  means n is probably prime
    return probabilistic_primality_test(n, security_level=128)


if __name__ == '__main__':

    def p_gen():
        from time import time
        from random import randint
        a = 0x8000000000000000000000000000000000000000000000000000000000000001
        b = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        candidate = None
        t1 = time()
        for _ in range(1000):
            n = randint(a, b) | a
            if is_prime(n):
                candidate = n
                break
        t2 = time()
        interval = (t2-t1)*1e3
        if candidate:
            msg = 'We found a probable prime in {:f} milliseconds:\n0x{:064x}\n'
            msg = msg.format(interval, candidate)
        else:
            msg = 'No prime was found in 1000 tries in {:f} milliseconds\n'
            msg = msg.format(interval)
        print(msg)

    def p_test(n):
        from time import time
        t1 = time()
        result = is_prime(n)
        t2 = time()
        interval = (t2-t1)*1e3
        msg = '0x{:064x}\n{} a prime, tested in {:f} milliseconds\n'
        msg = msg.format(n, 'is probably' if result else 'is not', interval)
        print(msg)

    p_gen()
    p_test(0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff)
    p_test(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551)
    p_test(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632553)
    p_test(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632549)
