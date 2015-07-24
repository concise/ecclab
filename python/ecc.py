__all__ = ['q', 'G', 'E_add', 'E_scalar_multiply', 'E_x_mod_q', 'E_from_bytes']

q = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff

def _in_GFp(obj):
    return (type(obj) is tuple and len(obj) == 2
            and obj[0] == 'GFp' and type(obj[1]) is int)

def GFp_eq(a, b):
    assert _in_GFp(a)
    assert _in_GFp(b)
    _, aa = a
    _, bb = b
    return (aa - bb) % p == 0

def GFp_neg(a):
    assert _in_GFp(a)
    _, aa = a
    return 'GFp', (-aa) % p

def GFp_add(a, b):
    assert _in_GFp(a)
    assert _in_GFp(b)
    _, aa = a
    _, bb = b
    return 'GFp', (aa + bb) % p

def GFp_mul(a, b):
    assert _in_GFp(a)
    assert _in_GFp(b)
    _, aa = a
    _, bb = b
    return 'GFp', (aa * bb) % p

def GFp_inv(a):
    assert _in_GFp(a)
    _, aa = a
    if (aa % p) == 0:
        raise ZeroDivisionError
    return 'GFp', pow(aa, p - 2, p)

A = ('GFp', -3)

B = ('GFp', 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)

Z = ('E', False, ('GFp', 0), ('GFp', 0))

G = ('E', True,
  ('GFp', 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296),
  ('GFp', 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5))

def _in_E(obj):
    return (type(obj) is tuple and len(obj) == 4
            and obj[0] == 'E'
            and type(obj[1]) is bool
            and _in_GFp(obj[2]) and _in_GFp(obj[3]))

def E_eq(P, Q):
    assert _in_E(P)
    assert _in_E(Q)
    _, Pnonzero, XP, YP = P
    _, Qnonzero, XQ, YQ = Q
    return Pnonzero == Qnonzero and GFp_eq(XP, XQ) and GFp_eq(YP, YQ)

def E_neg(P):
    assert _in_E(P)
    if E_eq(P, Z):
        return Z
    _, _, XP, YP = P
    return 'E', True, XP, GFp_neg(YP)

def E_double(P):
    assert _in_E(P)
    if E_eq(P, Z):
        return Z
    _, _, XP, YP = P
    T = GFp_mul(GFp_add(GFp_mul(('GFp', 3), GFp_mul(XP, XP)), A),
                GFp_inv(GFp_mul(('GFp', 2), YP)))
    XR = GFp_add(GFp_mul(T, T), GFp_neg(GFp_mul(('GFp', 2), XP)))
    YR = GFp_add(GFp_mul(T, GFp_add(XP, GFp_neg(XR))), GFp_neg(YP))
    return 'E', True, XR, YR

def E_add(P, Q):
    assert _in_E(P)
    assert _in_E(Q)
    if E_eq(P, Z):
        return Q
    if E_eq(Q, Z):
        return P
    if E_eq(P, E_neg(Q)):
        return Z
    if E_eq(P, Q):
        return E_double(P)
    _, _, XP, YP = P
    _, _, XQ, YQ = Q
    T = GFp_mul(GFp_add(YP, GFp_neg(YQ)), GFp_inv(GFp_add(XP, GFp_neg(XQ))))
    XR = GFp_add(GFp_add(GFp_mul(T, T), GFp_neg(XP)), GFp_neg(XQ))
    YR = GFp_add(GFp_mul(T, GFp_add(XP, GFp_neg(XR))), GFp_neg(YP))
    return 'E', True, XR, YR

def E_scalar_multiply(P, k):
    assert _in_E(P)
    assert type(k) is int
    if E_eq(P, Z):
        return Z
    k %= q
    k_bit_length = k.bit_length()
    T = Z
    for i in range(k_bit_length-1,-1,-1):
        bit = (k >> i) & 1
        T = E_double(T)
        if bit == 1:
            T = E_add(T, P)
    return T

def E_x_mod_q(P):
    raise NotImplementedError

def E_from_bytes(stream):
    raise NotImplementedError
