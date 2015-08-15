__all__ = ('G', 'n', 'add', 'mul')

G = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296 \
  , 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

def add(P1, P2):
    #assert is_valid_point(P1)
    #assert is_valid_point(P2)
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    if P1[0] != P2[0]:
        return AFFINE_POINT_ADDITION(P1, P2)
    if P1[1] == P2[1]: # != 0
        return AFFINE_POINT_DOUBLING(P1)
    return None

def mul(k, P):
    #assert type(k) is int
    #assert is_valid_point(P)
    k = k % n
    if k == 0 or P is None:
        return None
    if k == 1:
        return P
    if k == n - 1:
        x, y = P
        return x, p - y # -y % p where y != 0
    return MontgomeryLadderScalarMultiply(k, P)






def ecdsa_double_base_scalar_multiplication(t, u, Q):
    #assert type(t) is int and 0 <= t <= n - 1
    #assert type(u) is int and 1 <= u <= n - 1
    #assert is_valid_point(Q) and Q is not None
    tG = mul(t, G)
    uQ = mul(u, Q)
    R = add(tG, uQ)
    return R

def y_candidates_from_x(xP):
    #assert type(xP) is int
    y_squared = (xP * xP * xP + a * xP + b) % p
    y = pow(y_squared, (p + 1) // 4, p)
    if y * y % p != y_squared:
        raise ValueError
    return (y, p - y) if (y & 1 == 0) else (p - y, y)

def is_valid_point(P):
    return (P is None or (type(P) is tuple and len(P) == 2 and
            type(P[0]) is int and 0 <= P[0] <= p - 1 and
            type(P[1]) is int and 0 <= P[1] <= p - 1 and
            (P[0] * P[0] * P[0] + a * P[0] + b - P[1] * P[1]) % p == 0))






p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = -3
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
_4b_ = 4 * b % p

def inv_mod_p(n):
    return pow(n, p - 2, p)

def AFFINE_POINT_ADDITION(P1, P2):
    #assert is_valid_point(P1) and P1 is not None
    #assert is_valid_point(P2) and P2 is not None
    x1, y1 = P1
    x2, y2 = P2
    #assert x1 != x2
    v = ((y2 - y1) * inv_mod_p(x2 - x1)) % p
    x3 = (v * v - x1 - x2) % p
    y3 = (v * (x1 - x3) - y1) % p
    return x3, y3

def AFFINE_POINT_DOUBLING(P1):
    #assert is_valid_point(P1) and P1 is not None
    x1, y1 = P1
    #assert y1 != 0
    w = ((3 * x1 * x1 + a) * inv_mod_p(2 * y1)) % p
    x4 = (w * w - 2 * x1) % p
    y4 = (w * (x1 - x4) - y1) % p
    return x4, y4

def msb_first_bit_string(n):
    #assert type(n) is int and n >= 0
    return tuple(map(int,bin(n)[2:]))

def MontgomeryLadderScalarMultiply(k, P):
    #assert type(k) is int and 2 <= k <= n - 2
    #assert is_valid_point(P) and P is not None
    if k > n // 2:
        flipped = True
        k = n - k
    else:
        flipped = False
    xP, yP = P
    X1, X2, Z = CoZIdDbl(xP, yP)
    for bit in msb_first_bit_string(k)[1:]:
        if bit == 1:
            X1, X2, Z = CoZDiffAddDbl(X1, X2, Z, xD=xP)
        if bit == 0:
            X2, X1, Z = CoZDiffAddDbl(X2, X1, Z, xD=xP)
    X, Y, Z = CoZRecover(X1, X2, Z, xD=xP, yD=yP)
    iZ = inv_mod_p(Z)
    return (X * iZ) % p, ((Y * iZ) % p if not flipped else (-Y * iZ) % p)

def CoZIdDbl(x, y):
    Z  = ( 4 * y * y      ) % p
    X1 = ( Z * x          ) % p
    t  = ( 3 * x * x + a  ) % p
    X2 = ( t * t - 2 * X1 ) % p
    return X1, X2, Z

def CoZDiffAddDbl(X1, X2, Z, xD):
    R2 = ( Z * Z     ) % p
    R3 = ( a * R2    ) % p
    R1 = ( Z * R2    ) % p
    R2 = ( _4b_ * R1 ) % p
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

def CoZRecover(X1, X2, Z, xD, yD):
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
    R4 = ( _4b_ * R2 ) % p
    X2 = ( R4 + R3   ) % p
    return X1, X2, Z
