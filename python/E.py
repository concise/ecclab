# q                     the order of the cyclic group generated by G
# Z == E(0)             the additive identity, aka the point at infinity
# G == E(1)             the selected base point generating the cyclic group
# E(..., ...)           the factory function for an element in the group E
# E_from_bytes(...)     construct an element in E from an X9.62 encoded stream
# E_contains(...)       check if a Python object is a valid element in E
# E_take_x_mod_q(M)     returns the value of x-coordinate of M modulo q
# E_eq(M, N)            returns whether or not M is equal to N
# E_neg(M)              returns the value N such that (M + N) == E(0)
# E_dbl(M)              returns the value (M + M)
# E_add(M, N)           returns the value (M + N)
# E_mul(M, k)           returns the value [k]M
# E_InputError          the Exception that can be thrown by these E functions

from GFp import (p, GFp, GFp_contains, GFp_eq, GFp_neg, GFp_add,
                 GFp_inv, GFp_mul, GFp_sqrt_if_exists)

q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
a  = GFp(0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc)
b  = GFp(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
Gx = GFp(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296)
Gy = GFp(0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
G  = Gx, Gy
Z  = GFp(0), GFp(0)

def _is_a_two_tuple(obj):
    return type(obj) is tuple and len(obj) == 2

def _is_point_at_infinity(M):
    if _is_a_two_tuple(M) and GFp_contains(M[0]) and GFp_contains(M[1]):
        Mx, My = M
        Zx, Zy = Z
        return GFp_eq(Mx, Zx) and GFp_eq(My, Zy)
    else:
        return False

def _is_on_curve(M):
    if _is_a_two_tuple(M) and GFp_contains(M[0]) and GFp_contains(M[1]):
        x, y = M
        lhs = GFp_mul(y, y)
        rhs = GFp_add(GFp_add(GFp_mul(GFp_mul(x, x), x), GFp_mul(a, x)), b)
        return GFp_eq(lhs, rhs)
    else:
        return False

assert not _is_on_curve(Z)

def E(*args):
    if len(args) == 1 and type(args[0]) is bytes:
        return E_from_bytes(args[0])
    elif len(args) == 1 and args[0] == 0:
        return Z
    elif len(args) == 1 and args[0] == 1:
        return G
    elif len(args) == 2 and type(args[0]) is int and type(args[1]) is int:
        x, y = args
        M = GFp(x), GFp(y)
        if _is_on_curve(M):
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
        return _import_compressed_elm_with_y_parity(stream[1:], y_parity=0)
    elif len(stream) == 1+32 and stream[0] == 0x03:
        return _import_compressed_elm_with_y_parity(stream[1:], y_parity=1)
    elif len(stream) == 1+32*2 and stream[0] == 0x04:
        return _import_uncompressed_elm(stream[1:])
    elif len(stream) == 1+32*2 and stream[0] == 0x06:
        return _import_uncompressed_elm_with_y_parity(stream[1:], y_parity=0)
    elif len(stream) == 1+32*2 and stream[0] == 0x07:
        return _import_uncompressed_elm_with_y_parity(stream[1:], y_parity=1)
    else:
        raise E_InputError('the provided input is in an invalid format')

def E_contains(M):
    return _is_point_at_infinity(M) or _is_on_curve(M)

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

def _octet_string_to_unsigned_integer_less_than_p_(octetstr):
    intval = int.from_bytes(octetstr, byteorder='big', signed=False)
    if 0 <= intval and intval <= p-1:
        return intval
    else:
        raise E_InputError('bad input octet string')

def _import_uncompressed_elm(s):
    assert len(s) == 32*2
    x_int = _octet_string_to_unsigned_integer_less_than_p_(s[:32])
    y_int = _octet_string_to_unsigned_integer_less_than_p_(s[32:])
    return E(x_int, y_int)

def _import_uncompressed_elm_with_y_parity(s, y_parity):
    assert len(s) == 32*2
    x_int = _octet_string_to_unsigned_integer_less_than_p_(s[:32])
    y_int = _octet_string_to_unsigned_integer_less_than_p_(s[32:])
    P = E(x_int, y_int)
    if y_int & 1 == y_parity & 1:
        return P
    else:
        raise E_InputError('bad input octet string')

def _import_compressed_elm_with_y_parity(s, y_parity):
    assert len(s) == 32
    x_int = _octet_string_to_unsigned_integer_less_than_p_(s)
    x = GFp(x_int)
    w = GFp_add(GFp_add(GFp_mul(GFp_mul(x, x), x), GFp_mul(a, x)), b)
    y = GFp_sqrt_if_exists(w, y_parity)
    R = x, y
    if _is_on_curve(R):
        return x, y
    else:
        raise E_InputError('bad input octet string')
