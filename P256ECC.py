# E(0)                  the additive identity, aka the point at infinity
# E(1)                  the selected base point generating the cyclic group
# E(..., ...)           the factory function for an element in the group E
# E_from_bytes(...)     construct an element in E from an X9.62 encoded stream
# E_to_bytes(...)       convert an element in E into an octet string
# E_contains(...)       check if a Python object is a valid element in E
# E_take_x_mod_q(M)     returns the value of x-coordinate of M modulo q
# E_eq(M, N)            returns whether or not M is equal to N
# E_neg(M)              returns the value N such that (M + N) == E(0)
# E_dbl(M)              returns the value (M + M)
# E_add(M, N)           returns the value (M + N)
# E_mul(M, k)           returns the value [k]M
# E_InputError          the Exception that can be thrown by these E functions

import p256

from P256GFp import (
        GFp, GFp_contains, GFp_from_bytes, GFp_to_bytes, GFp_eq, GFp_neg,
        GFp_add, GFp_inv, GFp_mul, GFp_sqrt, GFp_parity_of, GFp_Error)

p = p256.p
q = p256.q
a = GFp(p256.a)
b = GFp(p256.b)
G = GFp(p256.xG), GFp(p256.yG)
Z = GFp(0), GFp(0)

def _E_is_point_at_infinity(M):
    if not (type(M) is tuple and len(M) == 2):
        return False
    if not (GFp_contains(M[0]) and GFp_contains(M[1])):
        return False
    Mx, My = M
    Zx, Zy = Z
    return GFp_eq(Mx, Zx) and GFp_eq(My, Zy)

def _E_is_on_curve(M):
    if not (type(M) is tuple and len(M) == 2):
        return False
    if not (GFp_contains(M[0]) and GFp_contains(M[1])):
        return False
    x, y = M
    lhs = GFp_mul(y, y)
    rhs = GFp_add(GFp_add(GFp_mul(GFp_mul(x, x), x), GFp_mul(a, x)), b)
    return GFp_eq(lhs, rhs)

assert not _E_is_on_curve(Z)

def E(*args):
    if len(args) == 1 and type(args[0]) is bytes:
        return E_from_bytes(args[0])
    elif len(args) == 1 and args[0] == 0:
        return Z
    elif len(args) == 1 and args[0] == 1:
        return G
    elif len(args) == 2 and type(args[0]) is int and type(args[1]) is int:
        M = GFp(args[0]), GFp(args[1])
        if _E_is_on_curve(M):
            return M
        else:
            raise E_InputError('the point (x, y) is not on the curve')
    elif len(args) == 2 and GFp_contains(args[0]) and GFp_contains(args[1]):
        M = args[0], args[1]
        if _E_is_on_curve(M):
            return M
        else:
            raise E_InputError('the point (x, y) is not on the curve')
    else:
        raise E_InputError('E() can only accept either a `bytes` object, '
                           'an `int` object, or two `int` objects')

def E_from_bytes(stream):
    if type(stream) is not bytes:
        raise E_InputError('the provided input is not a `bytes` object')
    elif len(stream) == 1 and stream[0] == 0x00:
        return Z
    elif len(stream) == 1+32 and stream[0] == 0x02:
        return _E_import_compressed_elm_with_y_parity(stream[1:], y_parity=0)
    elif len(stream) == 1+32 and stream[0] == 0x03:
        return _E_import_compressed_elm_with_y_parity(stream[1:], y_parity=1)
    elif len(stream) == 1+32*2 and stream[0] == 0x04:
        return _E_import_uncompressed_elm(stream[1:])
    elif len(stream) == 1+32*2 and stream[0] == 0x06:
        return _E_import_uncompressed_elm_with_y_parity(stream[1:], y_parity=0)
    elif len(stream) == 1+32*2 and stream[0] == 0x07:
        return _E_import_uncompressed_elm_with_y_parity(stream[1:], y_parity=1)
    else:
        raise E_InputError('the provided input is in an invalid format')

def E_to_bytes(M, compressed=False):
    assert E_contains(M)
    if E_eq(M, Z):
        return b'\x00'
    elif compressed is False:
        Mx, My = M
        return b'\x04' + GFp_to_bytes(Mx) + GFp_to_bytes(My)
    elif compressed is True:
        Mx, My = M
        return bytes([0x02 ^ GFp_parity_of(My)]) + GFp_to_bytes(Mx)
    else:
        raise E_InputError('argument "compressed" must be True or False')

def E_contains(M):
    return _E_is_point_at_infinity(M) or _E_is_on_curve(M)

def E_take_x_mod_q(M):
    assert E_contains(M)
    if E_eq(M, Z):
        raise E_InputError('operand cannot be the point at infinity')
    else:
        x, y = M
        _, xval = x
        return xval % q

def E_eq(M, N):
    assert E_contains(M)
    assert E_contains(N)
    Mx, My = M
    Nx, Ny = N
    return GFp_eq(Mx, Nx) and GFp_eq(My, Ny)

def E_neg(M):
    assert E_contains(M)
    Mx, My = M
    return Mx, GFp_neg(My)

def E_dbl(M):
    assert E_contains(M)
    Mx, My = M
    if E_eq(M, Z):
        return Z
    elif GFp_eq(My, GFp(0)):
        return Z
    else:
        # s = (3 * Mx**2 + a) / (2 * My)
        # Rx = s**2 - 2 * Mx
        # Ry = s * (Mx - Rx) - My
        s = GFp_mul(GFp_add(GFp_mul(GFp(3), GFp_mul(Mx, Mx)), a),
                    GFp_inv(GFp_mul(GFp(2), My)))
        Rx = GFp_add(GFp_mul(s, s), GFp_neg(GFp_mul(GFp(2), Mx)))
        Ry = GFp_add(GFp_mul(s, GFp_add(Mx, GFp_neg(Rx))), GFp_neg(My))
        return Rx, Ry

def E_add(M, N):
    assert E_contains(M)
    assert E_contains(N)
    Mx, My = M
    Nx, Ny = N
    if E_eq(M, Z):
        return N
    elif E_eq(N, Z):
        return M
    elif E_eq(M, E_neg(N)):
        return Z
    elif E_eq(M, N):
        return E_dbl(M)
    else:
        # s = (My - Ny) / (Mx - Nx)
        # Rx = s**2 - Mx - Nx
        # Ry = s * (Mx - Rx) - My
        s = GFp_mul(GFp_add(My, GFp_neg(Ny)),
            GFp_inv(GFp_add(Mx, GFp_neg(Nx))))
        Rx = GFp_add(GFp_add(GFp_mul(s, s), GFp_neg(Mx)), GFp_neg(Nx))
        Ry = GFp_add(GFp_mul(s, GFp_add(Mx, GFp_neg(Rx))), GFp_neg(My))
        return Rx, Ry

def E_mul(M, k):
    assert type(k) is int
    assert E_contains(M)
    k = k % q
    if E_eq(M, Z) or k == 0:
        return Z
    else:
        klen = k.bit_length()
        R = Z
        for i in range(klen - 1, -1, -1):
            R = E_dbl(R)
            if (k >> i) & 1 == 1:
                R = E_add(R, M)
        return R

class E_InputError(Exception):
    pass

def _E_import_uncompressed_elm(s):
    assert len(s) == 32*2
    try:
        x = GFp_from_bytes(s[:32])
        y = GFp_from_bytes(s[32:])
    except GFp_Error:
        raise E_InputError('bad input octet string, not GFp elements')
    return E(x, y)

def _E_import_uncompressed_elm_with_y_parity(s, y_parity):
    assert len(s) == 32*2
    try:
        x = GFp_from_bytes(s[:32])
        y = GFp_from_bytes(s[32:])
    except GFp_Error:
        raise E_InputError('bad input octet string, not GFp elements')
    P = E(x, y)
    if GFp_parity_of(P) == y_parity & 1:
        return P
    else:
        raise E_InputError('bad input octet string, parity not matched')

def _E_import_compressed_elm_with_y_parity(s, y_parity):
    assert len(s) == 32
    try:
        x = GFp_from_bytes(s)
    except GFp_Error:
        raise E_InputError('bad input octet string, not GFp element')
    w = GFp_add(GFp_add(GFp_mul(GFp_mul(x, x), x), GFp_mul(a, x)), b)
    try:
        y = GFp_sqrt(w, y_parity)
    except GFp_Error:
        raise E_InputError('bad input octet string, point not on curve')
    return E(x, y)
