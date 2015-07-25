# GFp(i)                construct an element in GFp
# GFp_contains(e)       check if a Python object e is a valid element in GFp
# GFp_from_bytes(strm)  fixed-length-unsigned-MSB-first-decode the octets strm
# GFp_to_bytes(m)       fixed-length-unsigned-MSB-first-encode the integer m
# GFp_eq(m, n)          m == n
# GFp_neg(m)            -m
# GFp_add(m, n)         m + n
# GFp_inv(m)            m**(-1)
# GFp_mul(m, n)         m * n
# GFp_sqrt(m, parity)   m**(1/2)
# GFp_parity_of(m)      m & 1
# GFp_Error             can be thrown by GFp_from_bytes, GFp_inv, GFp_sqrt

from P256 import p

_TAG_ = 'GFp'

def GFp(i):
    assert type(i) is int
    return _TAG_, (i) % p

def GFp_contains(e):
    if type(e) is tuple and len(e) == 2:
        mtag, mval = e
        return mtag is _TAG_ and type(mval) is int
    else:
        return False

def GFp_from_bytes(strm):
    assert type(strm) is bytes
    if len(strm) != 32:
        raise GFp_Error('GFp element must be encoded as 32 octets exactly')
    mval = int.from_bytes(strm, byteorder='big', signed=False)
    if mval >= p:
        raise GFp_Error('GFp element must be an unsigned integer < p')
    return _TAG_, mval

def GFp_to_bytes(m):
    assert GFp_contains(m)
    _, mval = m
    mval = mval % p
    return mval.to_bytes(length=32, byteorder='big', signed=False)

def GFp_eq(m, n):
    assert GFp_contains(m)
    assert GFp_contains(n)
    _, mval = m
    _, nval = n
    return (mval - nval) % p == 0

def GFp_neg(m):
    assert GFp_contains(m)
    _, mval = m
    return _TAG_, (-mval) % p

def GFp_add(m, n):
    assert GFp_contains(m)
    assert GFp_contains(n)
    _, mval = m
    _, nval = n
    return _TAG_, (mval + nval) % p

def GFp_inv(m):
    assert GFp_contains(m)
    _, mval = m
    if (mval % p) == 0:
        raise GFp_Error('division by zero')
    return _TAG_, pow(mval, p - 2, p)

def GFp_mul(m, n):
    assert GFp_contains(m)
    assert GFp_contains(n)
    _, mval = m
    _, nval = n
    return _TAG_, (mval * nval) % p

def GFp_sqrt(m, parity):
    assert GFp_contains(m)
    assert type(parity) is int
    _, mval = m
    try:
        rval = _GFp_sqrt_modulo_p_(mval)
    except ArithmeticError:
        raise GFp_Error('no square root of the element exists')
    r = _TAG_, rval
    if GFp_parity_of(r) == parity & 1:
        return r
    else:
        return GFp_neg(r)

def GFp_parity_of(m):
    assert GFp_contains(m)
    _, mval = m
    return mval & 1

class GFp_Error(Exception):
    pass

def _GFp_sqrt_modulo_p_(n):
    # n^2 === n^( (p - 1) + 2 ) (mod p)
    # n^2 === n^(  p + 1      ) (mod p)
    # n   === n^( (p + 1) / 2 ) (mod p)
    # m^2 === n^( (p + 1) / 2 ) (mod p)
    # m   === n^( (p + 1) / 4 ) (mod p)
    assert type(n) is int
    assert type(p) is int
    assert p % 4 == 3
    m = pow(n, (p + 1) // 4, p)
    if (m * m - n) % p == 0:
        return m
    else:
        raise ArithmeticError('n=%d is not a square modulo p=%d' % (n, p))