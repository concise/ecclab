#!/usr/bin/env python3
"""
This module provides:

  q                     the order of the elliptic curve group
  (xZ, yZ)              the point at infinity
  (xG, yG)              the base point
  add(x1, y1, x2, y2)   compute (x3, y3) = (x1, y1) + (x2, y2)
  mul(x, y, k)          compute (x4, y4) = [k](x, y)

On a 64-bit platform:

  add() needs 0.24 milliseconds on average
  mul() needs 4.55 milliseconds on average

"""

# domain parameters for secp256r1
p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = -3
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
xG = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
yG = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# choose a point outside the curve to denote the point at infinity
xZ, yZ = 0, 0

# multiplicative inverse modulo p
inv  = lambda n: pow(n, p - 2, p)

# square root modulo p
sqrt = lambda n: pow(n, (p + 1) // 4, p)

def y_candidates_from_x(x):
    if not (type(x) is int and 0 <= x <= p - 1):
        raise ValueError('x is not an element of Fp')
    yy = (x ** 3 + a * x + b) % p
    y = sqrt(yy)
    if yy != y ** 2 % p:
        raise ValueError('x is not an x-coordinate of some EC point')
    return (y, p - y) if (y & 1 == 0) else (p - y, y)

def is_valid_group_element(xP, yP):
    if not (
        type(xP) is int and 0 <= xP <= p - 1 and
        type(yP) is int and 0 <= yP <= p - 1
    ):
        return False
    elif (xP, yP) == (xZ, yZ):
        return True
    else:
        lhs = (yP ** 2) % p
        rhs = (xP ** 3 + a * xP + b) % p
        return lhs == rhs

def simple_DOUBLE(x1, y1):
    slope = (3 * x1 ** 2 + a) * inv(2 * y1) % p
    x4 = (slope ** 2 - 2 * x1) % p
    y4 = (slope * (x1 - x4) - y1) % p
    return x4, y4

def simple_ADD(x1, y1, x2, y2):
    slope = (y2 - y1) * inv(x2 - x1) % p
    x3 = (slope ** 2 - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3

def add(xP1, yP1, xP2, yP2):
    #
    # Given P1 and P2
    # Compute Q = P1 + P2
    #
    # P1 = ( xP1 ,  yP1 )
    # P2 = ( xP2 ,  yP2 )
    # Q  = ( xQ  ,  yQ  )
    #
    if not is_valid_group_element(xP1, yP1):
        raise ValueError('(xP1, yP1) is not an EC point')
    if not is_valid_group_element(xP2, yP2):
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

def AddDblCoZ(X1, X2, Z, xD, _a_=a, _4b_=(4*b)%p):
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
    # Given (P, Q) as well as the x-coordinate of Q - P
    # Compute (P + Q, 2Q)
    #
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
    X1, X2, Z, xD, yD, _a_=a, _4b_=(4*b)%p
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

def MontgomeryLadder(xP, yP, k):
    #
    # Given P and k
    # Compute Q = [k]Q
    #
    # P = ( xP ,  yP )
    # Q = ( xQ ,  yQ )
    #
    # 2 <= k <= q-2  where  q = ord(P)
    #
    X1, X2, Z = AddDblCoZ(0, xP, 1, xP)
    X1 = (xP * Z) % p
    k_bit_sequence = tuple(map(int,bin(k)[2:]))
    for ki in k_bit_sequence[1:]:
        if ki == 0:
            X2, X1, Z = AddDblCoZ(X2, X1, Z, xP)
        else:
            X1, X2, Z = AddDblCoZ(X1, X2, Z, xP)
    XX, YY, ZZ = RecoverFullCoordinatesCoZ(X1, X2, Z, xP, yP)
    iZZ = inv(ZZ)
    return (XX * iZZ) % p, (YY * iZZ) % p

def mul(xP, yP, k):
    #
    # Given P and k
    # Compute Q = [k]Q
    #
    # P = ( xP ,  yP )
    # Q = ( xQ ,  yQ )
    #
    if not is_valid_group_element(xP, yP):
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
        return MontgomeryLadder(xP, yP, k)


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
