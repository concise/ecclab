class P256Error(BaseException):
    pass

class P256TypeError(P256Error, TypeError):
    pass

class P256ValueError(P256Error, ValueError):
    pass

def p256_validate_ecdsa_Q_h_r_s_quadruple(Q, h, r, s):
    if E_eq(Q, Z):
        return False
    r2 = E_take_x_mod_q(E_add(E_mul(G, _div_(h, s)), E_mul(Q, _div_(r, s))))
    return (r - r2) % q == 0

def _div_(a, b):
    return (a * pow(b, q - 2, q)) % q




# The elliptic curve named secp256r1 (or prime256v1 or P-256) is defined by
# the sextuple (p, a, b, G, q, h).  The base point G = (xG, yG) generates a
# cyclic group E of size prime q, which has some cryptographic properties
# suitable for constructing an asymmetric signature scheme.
p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
xG = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
yG = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
h  = 1




def GFp(m):
    if type(m) is not int:
        raise P256TypeError
    return m % p

def GFp_contains(val):
    if type(val) is not int:
        raise P256TypeError
    return 0 <= val <= p-1

def GFp_from_bytes(stream):
    if type(stream) is not bytes:
        raise P256TypeError
    if len(stream) != 32:
        raise P256ValueError
    m = int.from_bytes(stream, byteorder='big', signed=False)
    if 0 <= m <= p - 1:
        return m
    else:
        raise P256ValueError

def GFp_to_bytes(m):
    if type(m) is not int:
        raise P256TypeError
    m = m % p
    return m.to_bytes(length=32, byteorder='big', signed=False)

def GFp_eq(m, n):
    if type(m) is not int or type(n) is not int:
        raise P256TypeError
    return (m - n) % p == 0

def GFp_neg(m):
    if type(m) is not int:
        raise P256TypeError
    return -m % p

def GFp_add(m, n):
    if type(m) is not int or type(n) is not int:
        raise P256TypeError
    return (m + n) % p

def GFp_inv(m):
    if type(m) is not int:
        raise P256TypeError
    if m % p == 0:
        raise P256ValueError
    return pow(m, p - 2, p)

def GFp_mul(m, n):
    if type(m) is not int or type(n) is not int:
        raise P256TypeError
    return (m * n) % p

def GFp_sqrt(n, parity):
    if type(n) is not int or type(parity) is not int:
        raise P256TypeError
    m = pow(n, (p + 1) // 4, p)
    if (m * m - n) % p != 0:
        raise P256ValueError
    if GFp_parity_of(m) == parity & 1:
        return m
    else:
        return GFp_neg(m)

def GFp_parity_of(m):
    if type(n) is not int:
        raise P256TypeError
    return (m % p) & 1






Z = 0, 0

G = xG, yG

def E_is_point_at_infinity(M):
    if not (type(M) is tuple and len(M) == 2
    and GFp_contains(M[0]) and GFp_contains(M[1])):
        raise P256TypeError
    Mx, My = M
    Zx, Zy = Z
    return GFp_eq(Mx, Zx) and GFp_eq(My, Zy)

def E_is_on_curve(M):
    if not (type(M) is tuple and len(M) == 2
    and GFp_contains(M[0]) and GFp_contains(M[1])):
        raise P256TypeError
    x, y = M
    lhs = GFp_mul(y, y)
    rhs = GFp_add(GFp_add(GFp_mul(GFp_mul(x, x), x), GFp_mul(a, x)), b)
    return GFp_eq(lhs, rhs)

assert not E_is_on_curve(Z)

def E(*args):
    if len(args) == 1 and type(args[0]) is bytes:
        return E_from_bytes(args[0])
    elif len(args) == 1 and type(args) is int and args[0] == 0:
        return Z
    elif len(args) == 1 and type(args) is int and args[0] == 1:
        return G
    elif len(args) == 2 and type(args[0]) is int and type(args[1]) is int:
        M = GFp(args[0]), GFp(args[1])
        if E_is_on_curve(M):
            return M
        else:
            raise P256ValueError
    else:
        raise P256TypeError

def E_from_bytes(stream):
    if type(stream) is not bytes:
        raise P256TypeError
    elif len(stream) == 1 and stream[0] == 0x00:
        return Z
    elif len(stream) == 1+32 and stream[0] == 0x02:
        return E_import_compressed_elm_with_y_parity(stream[1:], parity=0)
    elif len(stream) == 1+32 and stream[0] == 0x03:
        return E_import_compressed_elm_with_y_parity(stream[1:], parity=1)
    elif len(stream) == 1+32*2 and stream[0] == 0x04:
        return E_import_uncompressed_elm(stream[1:])
    else:
        raise P256ValueError

def E_to_bytes(M, compressed=False):
    if not E_contains(M):
        raise P256ValueError
    if E_eq(M, Z):
        return b'\x00'
    if compressed is False:
        Mx, My = M
        return b'\x04' + GFp_to_bytes(Mx) + GFp_to_bytes(My)
    elif compressed is True:
        Mx, My = M
        return bytes([0x02 ^ GFp_parity_of(My)]) + GFp_to_bytes(Mx)
    else:
        raise P256TypeError

def E_contains(M):
    return E_is_point_at_infinity(M) or E_is_on_curve(M)

def E_take_x_mod_q(M):
    if not E_contains(M):
        raise P256ValueError
    if E_eq(M, Z):
        raise P256ValueError
    else:
        x, y = M
        return x % q

def E_eq(M, N):
    if not E_contains(M) or not E_contains(N):
        raise P256ValueError
    Mx, My = M
    Nx, Ny = N
    return GFp_eq(Mx, Nx) and GFp_eq(My, Ny)

def E_neg(M):
    if not E_contains(M):
        raise P256ValueError
    Mx, My = M
    return Mx, GFp_neg(My)

def E_dbl(M):
    if not E_contains(M):
        raise P256ValueError
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
    if not E_contains(M):
        raise P256ValueError
    if not E_contains(N):
        raise P256ValueError
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
    if type(k) is not int:
        raise P256TypeError
    if not E_contains(M):
        raise P256ValueError
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

def E_import_uncompressed_elm(s):
    x = GFp_from_bytes(s[:32])
    y = GFp_from_bytes(s[32:])
    return E(x, y)

def E_import_compressed_elm_with_y_parity(s, parity):
    x = GFp_from_bytes(s)
    w = GFp_add(GFp_add(GFp_mul(GFp_mul(x, x), x), GFp_mul(a, x)), b)
    y = GFp_sqrt(w, y_parity)
    return E(x, y)
