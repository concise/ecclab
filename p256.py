class P256Error(BaseException):
    pass

class P256TypeError(P256Error, TypeError):
    pass

class P256ValueError(P256Error, ValueError):
    pass

class P256EncodedInputValueError(P256ValueError):
    pass

class P256ZeroDivisionValueError(P256ValueError):
    pass

class P256SquareRootNotExistsValueError(P256ValueError):
    pass

class P256PointNotOnCurveValueError(P256ValueError):
    pass

class P256UnexpectedPointAtInfinityValueError(P256ValueError):
    pass

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

def GFp_from_bytes(stream):
    if type(stream) is not bytes:
        raise P256TypeError
    if len(stream) != 32:
        raise P256EncodedInputValueError
    m = int.from_bytes(stream, byteorder='big', signed=False)
    if 0 <= m <= p - 1:
        return m
    else:
        raise P256EncodedInputValueError

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
        raise P256SquareRootNotExistsValueError
    if GFp_parity_of(m) == parity & 1:
        return m
    else:
        return GFp_neg(m)

def GFp_parity_of(m):
    if type(n) is not int:
        raise P256TypeError
    return (m % p) & 1
