#!/usr/bin/env python3

p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = -3
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
xG = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
yG = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

_inv  = lambda n: pow(n, p - 2, p)
_sqrt = lambda n: pow(n, (p + 1) // 4, p)

def _is_valid_group_element(xP, yP):
    if (xP, yP) == (0, 0):
        return True
    else:
        lhs = (yP ** 2) % p
        rhs = (xP ** 3 + a * xP + b) % p
        return lhs == rhs

def _dumb_DOUBLE(x1, y1):
    slope = (3 * x1 ** 2 + a) * _inv(2 * y1) % p
    x4 = (slope ** 2 - 2 * x1) % p
    y4 = (slope * (x1 - x4) - y1) % p
    return x4, y4

def _dumb_ADD(x1, y1, x2, y2):
    slope = (y2 - y1) * _inv(x2 - x1) % p
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
    assert _is_valid_group_element(xP1, yP1)
    assert _is_valid_group_element(xP2, yP2)
    if (xP1, yP1) == (0, 0):
        return xP2, yP2
    elif (xP2, yP2) == (0, 0):
        return xP1, yP1
    elif xP1 == xP2 and yP1 != yP2:
        return 0, 0
    elif xP1 == xP2 and yP1 == yP2:
        return _dumb_DOUBLE(xP1, yP1)
    else:
        return _dumb_ADD(xP1, yP1, xP2, yP2)

def _AddDblCoZ(X1, X2, Z, xD, _a_=a, _4b_=(4*b)%p):
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

def _RecoverFullCoordinatesCoZ(X1, X2, Z, xD, yD, _a_=a, _4b_=(4*b)%p):
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

def _MontgomeryLadder(xP, yP, k):
    #
    # Given P and k
    # Compute Q = [k]Q
    #
    # P = ( xP ,  yP )
    # Q = ( xQ ,  yQ )
    #
    # 2 <= k <= q-2  where  q = ord(P)
    #
    X1, X2, Z = _AddDblCoZ(0, xP, 1, xP)
    X1 = (xP * Z) % p
    k_bit_sequence = tuple(map(int,bin(k)[2:]))
    for ki in k_bit_sequence[1:]:
        if ki == 0:
            X2, X1, Z = _AddDblCoZ(X2, X1, Z, xP)
        else:
            X1, X2, Z = _AddDblCoZ(X1, X2, Z, xP)
    XX, YY, ZZ = _RecoverFullCoordinatesCoZ(X1, X2, Z, xP, yP)
    assert ((ZZ * (YY ** 2 - b * ZZ ** 2)) % p ==
            (XX * (XX ** 2 + a * ZZ ** 2)) % p)
    return ((XX * pow(ZZ, p - 2, p)) % p,
            (YY * pow(ZZ, p - 2, p)) % p)

def mul(xP, yP, k):
    #
    # Given P and k
    # Compute Q = [k]Q
    #
    # P = ( xP ,  yP )
    # Q = ( xQ ,  yQ )
    #
    assert type(xP) is int and 0 <= xP <= p - 1
    assert type(yP) is int and 0 <= yP <= p - 1
    assert _is_valid_group_element(xP, yP)
    assert type(k) is int
    k = k % q
    if (xP, yP) == (0, 0) or k == 0:
        return 0, 0
    elif k == 1:
        return xP, yP
    elif k == q - 1:
        return xP, p - yP
    else:
        return _MontgomeryLadder(xP, yP, k)


if __name__ == '__main__':

    from random import randint
    from time import time

    k = randint(0, q - 1)
    t1 = time()
    xQ, yQ = mul(xG, yG, k) # 4.8 milliseconds on average
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
    xU2, yU2 = add(xV, yV, xW, yW) # 0.23 milliseconds on average
    t2 = time()
    time_interval = (t2 - t1) * 1000

    print('Compute R = P + Q')
    print('time =', time_interval, 'milliseconds')
    print('It is', xU1 == xU2 and yU1 == yU2, 'that: [v]G+[w]G = [v+w]G')
