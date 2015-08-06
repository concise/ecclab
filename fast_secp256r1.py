"""

This python3 module provides:

    q                           the order of the elliptic curve group

    (xZ, yZ)                    the point at infinity

    (xG, yG)                    the base point

    is_valid_ec_point(x, y)     checks if (x, y) is a valid EC point

    add(x1, y1, x2, y2)         computes (x3, y3) = (x1, y1) + (x2, y2)

    mul(x, y, k)                computes (x4, y4) = [k](x, y)

    y_candidates_from_x(x)      computes (y0, y1) so that both (x, y0) and
                                (x, y1) are valid EC points where y0 is an
                                even number while y1 is an odd number

The last three functions listed above will raise a ValueError exception when
the input is bad.  Here is a list of their execution time measured on a 64-bit
platform by repeating the operations with random inputs 10000 times:

    Python Function             Execution Time
    ---------------------       -----------------
    y_candidates_from_x         0.21 milliseconds
    add                         0.23 milliseconds
    mul                         4.58 milliseconds

"""

p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = -3
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
xG = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
yG = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
xZ = 0
yZ = 0

def _SELF_CHECK():
    from primality_test import is_prime
    assert is_prime(p)
    assert is_prime(q)
    assert p % 4 == 3
    assert (xZ ** 3 + a * xZ + b - yZ ** 2) % p != 0
    assert (xG ** 3 + a * xG + b - yG ** 2) % p == 0
    assert mul(xG, yG,  0) == (xZ, yZ)
    assert mul(xG, yG,  0) == add(*(mul(xG, yG, -1) + (xG, yG)))
    assert mul(xG, yG, -1) == add(*(mul(xG, yG, -2) + (xG, yG)))
    assert mul(xG, yG, -2) == add(*(mul(xG, yG, -3) + (xG, yG)))
    i = 0x58fecaddfe0680d37ac1768ac214b4998dc788572261f8865e4b117253b2caf3
    j = 0xb27b5dc31f118d6104b33c31dd871aab2c5f3e79736b3f82767af62e9d16b041
    assert mul(xG, yG, i + j) == add(*(mul(xG, yG, i) + mul(xG, yG, j)))

def inv_mod_p(n):
    return pow(n, p - 2, p)

def sqrt_mod_p(n):
    return pow(n, (p + 1) // 4, p)

def is_an_element_in_Fp(e):
    return type(e) is int and 0 <= e <= p - 1

def y_candidates_from_x(x):
    if not is_an_element_in_Fp(x):
        raise ValueError('x is not an element of Fp')
    yy = (x ** 3 + a * x + b) % p
    y = sqrt_mod_p(yy)
    if yy != y ** 2 % p:
        raise ValueError('x is not an x-coordinate of some EC point')
    return (y, p - y) if (y & 1 == 0) else (p - y, y)

def is_valid_ec_point(xP, yP):
    if not (is_an_element_in_Fp(xP) and is_an_element_in_Fp(yP)):
        return False
    elif (xP, yP) == (xZ, yZ):
        return True
    else:
        lhs = (yP ** 2) % p
        rhs = (xP ** 3 + a * xP + b) % p
        return lhs == rhs

def simple_ADD(x1, y1, x2, y2):
    slope = (y2 - y1) * inv_mod_p(x2 - x1) % p
    x3 = (slope ** 2 - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3

def simple_DOUBLE(x1, y1):
    slope = (3 * x1 ** 2 + a) * inv_mod_p(2 * y1) % p
    x4 = (slope ** 2 - 2 * x1) % p
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
def AddDblCoZ(
    X1, X2, Z, xD,
    _a_=a, _4b_=(4*b)%p
):
    R2 = ( Z ** 2    ) % p
    R3 = ( _a_ * R2  ) % p
    R1 = ( Z * R2    ) % p
    R2 = ( _4b_ * R1 ) % p
    R1 = ( X2 ** 2   ) % p
    R5 = ( R1 - R3   ) % p
    R4 = ( R5 ** 2   ) % p
    R1 = ( R1 + R3   ) % p
    R5 = ( X2 * R1   ) % p
    R5 = ( R5 + R5   ) % p
    R5 = ( R5 + R5   ) % p
    R5 = ( R5 + R2   ) % p
    R1 = ( R1 + R3   ) % p
    R3 = ( X1 ** 2   ) % p
    R1 = ( R1 + R3   ) % p
    X1 = ( X1 - X2   ) % p
    X2 = ( X2 + X2   ) % p
    R3 = ( X2 * R2   ) % p
    R4 = ( R4 - R3   ) % p
    R3 = ( X1 ** 2   ) % p
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

def RecoverFullCoordinatesCoZ(
    X1, X2, Z, xD, yD,
    _a_=a, _4b_=(4*b)%p
):
    R1 = ( xD * Z    ) % p
    R2 = ( X1 - R1   ) % p
    R3 = ( R2 ** 2   ) % p
    R4 = ( R3 * X2   ) % p
    R2 = ( R1 * X1   ) % p
    R1 = ( X1 + R1   ) % p
    X2 = ( Z ** 2    ) % p
    R3 = ( _a_ * X2  ) % p
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
    R4 = ( _4b_ * R2 ) % p
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
def mul(xP, yP, k):
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

_SELF_CHECK()


if __name__ == '__main__':

    from random import randint
    from time import time

    k = randint(0, q - 1)
    t1 = time()
    xQ, yQ = mul(xG, yG, k)
    t2 = time()
    time_interval = (t2 - t1) * 1000
    print('Compute Q = [k]G')
    print('time =', time_interval, 'milliseconds')
    print('k    = ' + hex(k))
    print('xQ   = ' + hex(xQ))
    print('yQ   = ' + hex(yQ))
    print()

    v = randint(0, q - 1)
    w = randint(0, q - 1)
    u = v + w
    xV, yV = mul(xG, yG, v)
    xW, yW = mul(xG, yG, w)
    xU1, yU1 = mul(xG, yG, u)
    t1 = time()
    xU2, yU2 = add(xV, yV, xW, yW)
    t2 = time()
    time_interval = (t2 - t1) * 1000
    print('Compute R = P + Q')
    print('time =', time_interval, 'milliseconds')
    print('It is', xU1 == xU2 and yU1 == yU2, 'that: [v]G+[w]G = [v+w]G')
    print()

    t = randint(0, q - 1)
    xT, yT = mul(xG, yG, t)
    t1 = time()
    yT0, yT1 = y_candidates_from_x(xT)
    t2 = time()
    time_interval = (t2 - t1) * 1000
    print('Compute y from x')
    print('time =', time_interval, 'milliseconds')
    if yT in {yT0, yT1}:
        print('OK')
    else:
        print('NG')
    print()
