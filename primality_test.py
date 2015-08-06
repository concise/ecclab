#!/usr/bin/env python3

def is_prime(n):
    """
    False means n is composite number
    True means n is a prime number with probability > (1 - 2**(-128))
    """
    assert type(n) is int and n >= 2
    if n == 2 or n == 3:
        return True
    if n & 1 == 0:
        return False

    def rabin_miller_test(n, level=128):
        assert type(n) is int and n >= 5 and n & 1 == 1
        r, s = 0, n - 1
        while (s & 1) == 0:
            r, s = (r + 1), (s >> 1)
        assert type(r) is int and r >= 1
        assert type(s) is int and s >= 1 and s & 1 == 1
        assert n == ((2 ** r) * s) + 1
        assert type(level) is int and level >= 1

        def random_integers(n, k):
            """
            generates min(k, n - 3) integers in the range [2, n - 2]
            """
            assert type(n) is int and n >= 5 and n & 1 == 1
            assert type(k) is int and k >= 0
            import random
            if k >= n - 3:
                yield from range(2, n - 1)
            elif n <= 0xffff:
                yield from random.sample(range(2, n - 1), k)
            else:
                for _ in range(k):
                    yield random.randint(2, n - 2)

        def rabin_miller_test_one_round(n, r, s, a):
            x = pow(a, s, n)
            if x == 1:
                return True
            if x == n - 1:
                return True
            for j in range(1, r):
                x = pow(x, 2, n) # x = pow(a, s * (2 ** j), n)
                if x == 1:
                    return False
                if x == n - 1:
                    return True
            return False

        k = (level >> 1) + (level & 1)
        for a in random_integers(n, k):
            if rabin_miller_test_one_round(n, r, s, a):
                continue
            else:
                return False
        return True

    return rabin_miller_test(n, level=128)


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
