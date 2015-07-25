# GFp(i)                construct an element in GFp from the integer i
# GFp_contains(X)       check if a Python object X is a valid element in GFp
# GFp_eq(m, n)          returns whether or not m is equal to n
# GFp_neg(m)            returns the value n such that (m + n) == GFp(0)
# GFp_add(m, n)         returns the value (m + n)
# GFp_inv(m)            returns the value n such that (m * n) == GFp(1)
# GFp_mul(m, n)         returns the value (m * n)
# GFp_sqrt_if_exists(m) returns the value n such that (n * n) == m

_TAG_ = 'GFp'

_PRIME_ = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff

def _is_a_two_tuple(obj):
    return type(obj) is tuple and len(obj) == 2

def GFp(some_integer):
    assert type(some_integer) is int
    return _TAG_, (some_integer) % _PRIME_

def GFp_contains(m):
    if _is_a_two_tuple(m):
        mtag, mval = m
        return mtag is _TAG_ and type(mval) is int
    else:
        return False

def GFp_eq(m, n):
    assert GFp_contains(m)
    assert GFp_contains(n)
    _, mval = m
    _, nval = n
    return (mval - nval) % _PRIME_ == 0

def GFp_neg(m):
    assert GFp_contains(m)
    _, mval = m
    return _TAG_, (-mval) % _PRIME_

def GFp_add(m, n):
    assert GFp_contains(m)
    assert GFp_contains(n)
    _, mval = m
    _, nval = n
    return _TAG_, (mval + nval) % _PRIME_

def GFp_inv(m):
    assert GFp_contains(m)
    _, mval = m
    if (mval % _PRIME_) == 0:
        raise ZeroDivisionError
    return _TAG_, pow(mval, _PRIME_ - 2, _PRIME_)

def GFp_mul(m, n):
    assert GFp_contains(m)
    assert GFp_contains(n)
    _, mval = m
    _, nval = n
    return _TAG_, (mval * nval) % _PRIME_

def GFp_sqrt_if_exists(m, parity):
    assert GFp_contains(m)
    _, mval = m
    rval = pow(mval, (_PRIME_+1)//4, _PRIME_)
    if rval & 1 != parity:
        rval = (-rval) % _PRIME_
    return _TAG_, rval
