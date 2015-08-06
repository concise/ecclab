#!/usr/bin/env python3
"""

This python3 module provides:

    q                           the order of the elliptic curve group

    (xZ, yZ)                    the zero point, aka the point at infinity

    (xG, yG)                    the base point

    is_valid_ec_point(x, y)     checks if (x, y) is a valid EC point

    add(x1, y1, x2, y2)         computes (x3, y3) = (x1, y1) + (x2, y2)

    scalarmul(x, y, k)          computes (x4, y4) = [k](x, y)

    y_candidates_from_x(x)      computes (y0, y1) so that both (x, y0) and
                                (x, y1) are valid non-zero EC points, where
                                y0 is an even number and y1 is an odd number

The last three functions listed above will raise a ValueError exception when
the input is bad.  Here is a list of their execution time measured on a 64-bit
platform by repeating the operations with random inputs 10000 times:

    Python Function             Execution Time
    ---------------------       -----------------
    y_candidates_from_x         0.20 milliseconds
    add                         0.23 milliseconds
    scalarmul                   4.05 milliseconds

"""

p    = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a    = -3
b    = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
bbbb = (4 * b) % p
xG   = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
yG   = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q    = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
xZ   = 0
yZ   = 0

def _SELF_CHECK():
    assert { int } >= set(map(type, [ p, a, b, xG, yG, q, xZ, yZ ]))
    assert p >= 5 and is_prime(p) and p & 3 == 3
    assert q >= 2 and is_prime(q)
    assert (xG * xG * xG + a * xG + b - yG * yG) % p == 0
    assert (xZ * xZ * xZ + a * xZ + b - yZ * yZ) % p != 0
    assert scalarmul(xG, yG,  0) == (xZ, yZ)
    assert scalarmul(xG, yG,  0) == add(*( scalarmul(xG, yG, -1) + (xG, yG) ))
    assert scalarmul(xG, yG, -1) == add(*( scalarmul(xG, yG, -2) + (xG, yG) ))
    assert scalarmul(xG, yG, -2) == add(*( scalarmul(xG, yG, -3) + (xG, yG) ))
    r = 0xb27b5dc31f118d6104b33c31dd871aab2c5f3e79736b3f82767af62e9d16b041
    s = 0x58fecaddfe0680d37ac1768ac214b4998dc788572261f8865e4b117253b2caf3
    t = r + s
    xR, yR = scalarmul(xG, yG, r)
    xS, yS = scalarmul(xG, yG, s)
    xT, yT = scalarmul(xG, yG, t)
    assert (xT, yT) == add(xR, yR, xS, yS)
    assert (xT, yT) == add(xT, yT, xZ, yZ)
    assert (xT, yT) == add(xZ, yZ, xT, yT)
    assert add(xT, yT, xT, yT) == scalarmul(xT, yT, 2)

def inv_mod_p(n):
    return pow(n, p - 2, p)

def sqrt_mod_p(n):
    return pow(n, (p + 1) // 4, p)

def is_an_element_in_Fp(e):
    return type(e) is int and 0 <= e <= p - 1

def y_candidates_from_x(x):
    if not is_an_element_in_Fp(x):
        raise ValueError('x is not an element of Fp')
    yy = (x * x * x + a * x + b) % p
    y = sqrt_mod_p(yy)
    if yy != y * y % p:
        raise ValueError('x is not an x-coordinate of some non-zero EC point')
    return (y, p - y) if (y & 1 == 0) else (p - y, y)

def is_valid_ec_point(xP, yP):
    if not (is_an_element_in_Fp(xP) and is_an_element_in_Fp(yP)):
        return False
    elif (xP, yP) == (xZ, yZ):
        return True
    else:
        lhs = (yP * yP) % p
        rhs = (xP * xP * xP + a * xP + b) % p
        return lhs == rhs

def simple_ADD(x1, y1, x2, y2):
    slope = (y2 - y1) * inv_mod_p(x2 - x1) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3

def simple_DOUBLE(x1, y1):
    slope = (3 * x1 * x1 + a) * inv_mod_p(2 * y1) % p
    x4 = (slope * slope - 2 * x1) % p
    y4 = (slope * (x1 - x4) - y1) % p
    return x4, y4

#
# Given P1 and P2
# Compute P1 + P2
#
def add(xP1, yP1, xP2, yP2):
    if not is_valid_ec_point(xP1, yP1):
        raise ValueError('(xP1, yP1) is not an EC point')
    if not is_valid_ec_point(xP2, yP2):
        raise ValueError('(xP2, yP2) is not an EC point')
    if (xP1, yP1) == (xZ, yZ):
        return xP2, yP2
    elif (xP2, yP2) == (xZ, yZ):
        return xP1, yP1
    elif xP1 == xP2 and yP1 != yP2:
        return xZ, yZ
    elif xP1 == xP2 and yP1 == yP2:
        return simple_DOUBLE(xP1, yP1)
    else:
        return simple_ADD(xP1, yP1, xP2, yP2)

#
# Given P, Q, and the x-coordinate of Q - P
# Compute P + Q and [2]Q
#
# Given (X1, X2, Z, xD)
# Compute (X1', X2', Z')
#
# P  = ( X1  / Z  ,  ... )
# Q  = ( X2  / Z  ,  ... )
# D  = ( xD       ,  ... ) = Q - P
# P' = ( X1' / Z' ,  ... ) = P + Q
# Q' = ( X2' / Z' ,  ... ) = [2]Q
#
# This is the Algorithm 5 from the paper "Memory-Constrained Implementations
# of Elliptic Curve Cryptography in Co-Z Coordinate Representation"
#
def AddDblCoZ(X1, X2, Z, xD):
    R2 = ( Z * Z     ) % p
    R3 = ( a * R2    ) % p
    R1 = ( Z * R2    ) % p
    R2 = ( bbbb * R1 ) % p
    R1 = ( X2 * X2   ) % p
    R5 = ( R1 - R3   ) % p
    R4 = ( R5 * R5   ) % p
    R1 = ( R1 + R3   ) % p
    R5 = ( X2 * R1   ) % p
    R5 = ( R5 + R5   ) % p
    R5 = ( R5 + R5   ) % p
    R5 = ( R5 + R2   ) % p
    R1 = ( R1 + R3   ) % p
    R3 = ( X1 * X1   ) % p
    R1 = ( R1 + R3   ) % p
    X1 = ( X1 - X2   ) % p
    X2 = ( X2 + X2   ) % p
    R3 = ( X2 * R2   ) % p
    R4 = ( R4 - R3   ) % p
    R3 = ( X1 * X1   ) % p
    R1 = ( R1 - R3   ) % p
    X1 = ( X1 + X2   ) % p
    X2 = ( X1 * R1   ) % p
    X2 = ( X2 + R2   ) % p
    R2 = ( Z * R3    ) % p
    Z  = ( xD * R2   ) % p
    X2 = ( X2 - Z    ) % p
    X1 = ( R5 * X2   ) % p
    X2 = ( R3 * R4   ) % p
    Z  = ( R2 * R5   ) % p
    return X1, X2, Z

#
# This is the Algorithm 7 from the paper "Memory-Constrained Implementations
# of Elliptic Curve Cryptography in Co-Z Coordinate Representation"
#
def RecoverFullCoordinatesCoZ(X1, X2, Z, xD, yD):
    R1 = ( xD * Z    ) % p
    R2 = ( X1 - R1   ) % p
    R3 = ( R2 * R2   ) % p
    R4 = ( R3 * X2   ) % p
    R2 = ( R1 * X1   ) % p
    R1 = ( X1 + R1   ) % p
    X2 = ( Z * Z     ) % p
    R3 = ( a * X2    ) % p
    R2 = ( R2 + R3   ) % p
    R3 = ( R2 * R1   ) % p
    R3 = ( R3 - R4   ) % p
    R3 = ( R3 + R3   ) % p
    R1 = ( yD + yD   ) % p
    R1 = ( R1 + R1   ) % p
    R2 = ( R1 * X1   ) % p
    X1 = ( R2 * X2   ) % p
    R2 = ( X2 * Z    ) % p
    Z  = ( R2 * R1   ) % p
    R4 = ( bbbb * R2 ) % p
    X2 = ( R4 + R3   ) % p
    return X1, X2, Z

#
# Given P and k where 2 <= k <= ord(P) - 2
# Compute [k]P
#
def MontgomeryLadderCoZ(xP, yP, k):
    X1, X2, Z = AddDblCoZ(0, xP, 1, xP)
    X1 = (xP * Z) % p
    k_bit_sequence = tuple(map(int,bin(k)[2:]))
    for ki in k_bit_sequence[1:]:
        if ki == 0:
            X2, X1, Z = AddDblCoZ(X2, X1, Z, xP)
        else:
            X1, X2, Z = AddDblCoZ(X1, X2, Z, xP)
    XX, YY, ZZ = RecoverFullCoordinatesCoZ(X1, X2, Z, xP, yP)
    iZZ = inv_mod_p(ZZ)
    return (XX * iZZ) % p, (YY * iZZ) % p

#
# Given P and k
# Compute [k]P
#
def scalarmul(xP, yP, k):
    if not is_valid_ec_point(xP, yP):
        raise ValueError('(xP, yP) is not an EC point')
    if not type(k) is int:
        raise ValueError('k is not an integer')
    k = k % q
    if (xP, yP) == (xZ, yZ) or k == 0:
        return xZ, yZ
    elif k == 1:
        return xP, yP
    elif k == q - 1:
        return xP, p - yP
    else:
        return MontgomeryLadderCoZ(xP, yP, k)

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

_SELF_CHECK()


if __name__ == '__main__':

    from random import randint
    from time import time

    k = randint(0, q - 1)
    t1 = time()
    xQ, yQ = scalarmul(xG, yG, k)
    t2 = time()
    time_interval = (t2 - t1) * 1e3
    print('Compute Q = [k]G')
    print('time =', time_interval, 'milliseconds')
    print('k    = ' + hex(k))
    print('xQ   = ' + hex(xQ))
    print('yQ   = ' + hex(yQ))
    print()

    v = randint(0, q - 1)
    w = randint(0, q - 1)
    u = v + w
    xV, yV = scalarmul(xG, yG, v)
    xW, yW = scalarmul(xG, yG, w)
    xU1, yU1 = scalarmul(xG, yG, u)
    t1 = time()
    xU2, yU2 = add(xV, yV, xW, yW)
    t2 = time()
    time_interval = (t2 - t1) * 1e3
    print('Compute R = P + Q')
    print('time =', time_interval, 'milliseconds')
    print('It is', xU1 == xU2 and yU1 == yU2, 'that: [v]G+[w]G = [v+w]G')
    print()

    t = randint(0, q - 1)
    xT, yT = scalarmul(xG, yG, t)
    t1 = time()
    yT0, yT1 = y_candidates_from_x(xT)
    t2 = time()
    time_interval = (t2 - t1) * 1e3
    print('Compute y from x')
    print('time =', time_interval, 'milliseconds')
    if yT in { yT0, yT1 }:
        print('OK')
    else:
        print('NG')
    print()
