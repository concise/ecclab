p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
xG = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
yG = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551










_p_     = p
_FpTAG_ = 'Fp'

class FpError(BaseException):
    pass

def _is_an_fp_representation_(obj):
    return (type(obj) is tuple and len(obj) == 2 and obj[0] is _FpTAG_
            and type(obj[1]) is int and 0 <= obj[1] <= _p_ - 1)

def fp(integer):
    return fp_from_integer(integer)

def fp_from_integer(integer):
    assert type(integer) is int
    return _FpTAG_, integer % _p_

def fp_to_integer(elm):
    assert _is_an_fp_representation_(elm)
    return elm[1]

def fp_from_octetstring(octetstring):
    assert type(octetstring) is bytes
    if len(octetstring) != 32:
        raise FpError
    value = int.from_bytes(octetstring, byteorder='big', signed=False)
    if not (0 <= value <= _p_ - 1):
        raise FpError
    return fp_from_integer(value)

def fp_to_octetstring(elm):
    assert _is_an_fp_representation_(elm)
    return elm[1].to_bytes(length=32, byteorder='big', signed=False)

def fp_eq(elm1, elm2):
    assert _is_an_fp_representation_(elm1)
    assert _is_an_fp_representation_(elm2)
    return elm1[1] == elm2[1]

def fp_neq(elm1, elm2):
    return not fp_eq(elm1, elm2)

def fp_neg(elm):
    assert _is_an_fp_representation_(elm)
    return _FpTAG_, -elm[1] % _p_

def fp_add(elm1, elm2):
    assert _is_an_fp_representation_(elm1)
    assert _is_an_fp_representation_(elm2)
    return _FpTAG_, (elm1[1] + elm2[1]) % _p_

def fp_sub(elm1, elm2):
    return fp_add(elm1, fp_neg(elm2))

def fp_inv(elm):
    assert _is_an_fp_representation_(elm)
    if elm[1] == 0:
        raise FpError
    return _FpTAG_, pow(elm[1], _p_ - 2, _p_)

def fp_mul(elm1, elm2):
    assert _is_an_fp_representation_(elm1)
    assert _is_an_fp_representation_(elm2)
    return _FpTAG_, (elm1[1] * elm2[1]) % _p_

def fp_div(elm1, elm2):
    return fp_mul(elm1, fp_inv(elm2))

def fp_square(elm):
    return fp_mul(elm, elm)

def fp_cube(elm):
    return fp_mul(fp_mul(elm, elm), elm)

def fp_sqrt(elm, parity=None):
    assert _is_an_fp_representation_(elm)
    assert parity is None or type(parity) is int
    candidate = _FpTAG_, pow(elm[1], (_p_ + 1) // 4, _p_)
    if fp_neq(fp_square(candidate), elm):
        raise FpError
    if parity is None or fp_parity_of(candidate) == parity & 1:
        return candidate
    else:
        return fp_neg(candidate)

def fp_parity_of(elm):
    assert _is_an_fp_representation_(elm)
    return elm[1] & 1










_q_     = q
_FqTAG_ = 'Fp'

class FqError(BaseException):
    pass

def _is_an_fq_representation_(obj):
    return (type(obj) is tuple and len(obj) == 2 and obj[0] is _FqTAG_
            and type(obj[1]) is int and 0 <= obj[1] <= _q_ - 1)

def fq(integer):
    return fq_from_integer(integer)

def fq_from_integer(integer):
    assert type(integer) is int
    return _FqTAG_, integer % _q_

def fq_to_integer(elm):
    assert _is_an_fq_representation_(elm)
    return elm[1]

def fq_to_msb_first_bit_sequence(elm):
    assert _is_an_fq_representation_(elm)
    _, value = elm
    vlen = value.bit_length()
    for i in range(vlen - 1, -1, -1):
        yield (value >> i) & 1










_a_    = fp_from_integer(a)
_b_    = fp_from_integer(b)
_xG_   = fp_from_integer(xG)
_yG_   = fp_from_integer(yG)
_xZ_   = fp_from_integer(0)
_yZ_   = fp_from_integer(0)
_ETAG_ = 'E'
_G_    = _ETAG_, _xG_, _yG_
_Z_    = _ETAG_, _xZ_, _yZ_

class EError(BaseException):
    pass

def _is_a_2d_fp_space_point_(obj):
    return (type(obj) is tuple and len(obj) == 3 and obj[0] is _ETAG_
            and _is_an_fp_representation_(obj[1])
            and _is_an_fp_representation_(obj[2]))

def _is_on_curve_(x, y):
    lhs = fp_square(y)
    rhs = fp_add(fp_add(fp_cube(x), fp_mul(_a_, x)), _b_)
    return fp_eq(lhs, rhs)

def _is_an_e_representation_(obj):
    if _is_a_2d_fp_space_point_(obj):
        _, x, y = obj
        if _is_on_curve_(x, y):
            return True
        else:
            return obj == _Z_
    else:
        return False

assert not _is_on_curve_(_xZ_, _yZ_)
assert _is_an_e_representation_(_G_)
assert _is_an_e_representation_(_Z_)

def e(spec):
    assert type(spec) is int and spec == 0 or spec == 1
    if spec == 0:
        return _Z_
    elif spec == 1:
        return _G_
    else:
        assert False

def e_from_octetstring(octetstring):
    pass
    # TODO
    # 0x04       uncompressed
    # 0x02, 0x03 compressed with one parity bit

def e_to_octetstring(P, compressed=False):
    pass
    # TODO

def e_to_integer_modulo_q(P):
    pass
    # TODO

def e_eq(P, Q):
    pass
    # TODO

def e_neg(P):
    pass
    # TODO

def e_dbl(P):
    pass
    # TODO

def e_add(P, Q):
    pass
    # TODO

def e_mul(P, k):
    pass
    # TODO use fq_ function
