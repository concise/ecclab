p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
xG = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
yG = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551










_p_     = p
_FpTAG_ = 'Fp'

class fp_Error(BaseException):
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
        raise fp_Error
    value = int.from_bytes(octetstring, byteorder='big', signed=False)
    if not (0 <= value <= _p_ - 1):
        raise fp_Error
    return fp(value)

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
        raise fp_Error
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
        raise fp_Error
    if parity is None or fp_parity_of(candidate) == parity & 1:
        return candidate
    else:
        return fp_neg(candidate)

def fp_parity_of(elm):
    assert _is_an_fp_representation_(elm)
    return elm[1] & 1










_q_     = q
_FqTAG_ = 'Fq'

class fq_Error(BaseException):
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










_a_    = fp(a)
_b_    = fp(b)
_xG_   = fp(xG)
_yG_   = fp(yG)
_xZ_   = fp(0)
_yZ_   = fp(0)
_ETAG_ = 'E'
_G_    = _ETAG_, _xG_, _yG_
_Z_    = _ETAG_, _xZ_, _yZ_

class e_Error(BaseException):
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
    assert type(octetstring) is bytes
    try:
        if len(octetstring) == 1 and octetstring[0] == 0x00:
            return _Z_
        elif len(octetstring) == 65 and octetstring[0] == 0x04:
            x = fp_from_octetstring(octetstring[1:33])
            y = fp_from_octetstring(octetstring[33:65])
            assert _is_an_e_representation_((_ETAG_, x, y))
            return _ETAG_, x, y
        elif len(octetstring) == 33 and octetstring[0] in {0x02, 0x03}:
            y_parity = octetstring[0] & 1
            x = fp_from_octetstring(octetstring[1:33])
            w = fp_add(fp_add(fp_cube(x), fp_mul(_a_, x)), _b_)
            y = fp_sqrt(w, parity=y_parity)
            assert _is_an_e_representation_((_ETAG_, x, y))
            return _ETAG_, x, y
    except fp_Error:
        pass
    raise e_Error

def e_to_octetstring(P, compressed=False):
    assert _is_an_e_representation_(P)
    _, x, y = P
    y_parity = fp_parity_of(y)
    assert y_parity in {0, 1}
    if not compressed:
        xx = fp_to_octetstring(x)
        yy = fp_to_octetstring(y)
        return b'\x04' + xx + yy
    else:
        xx = fp_to_octetstring(x)
        return bytes([0x02 ^ y_parity]) + xx

def e_to_integer(P):
    assert _is_an_e_representation_(P)
    _, x, y = P
    return fp_to_integer(y)

def e_eq(P, Q):
    assert _is_an_e_representation_(P)
    assert _is_an_e_representation_(Q)
    _, xP, yP = P
    _, xQ, yQ = Q
    return fp_eq(xP, xQ) and fp_eq(yP, yQ)

def e_neg(P):
    assert _is_an_e_representation_(P)
    _, x, y = P
    return _ETAG_, x, fp_neg(y)

def e_dbl(P):
    assert _is_an_e_representation_(P)
    _, xP, yP = P
    if e_eq(P, _Z_):
        return _Z_
    if fp_eq(yP, fp(0)):
        return _Z_
    # slope = (3 * xP**2 + a) / (2 * yP)
    # xR = slope**2 - 2 * xP
    # yR = slope * (xP - xR) - yP
    slope = fp_div(fp_add(fp_mul(fp(3), fp_square(xP)), _a_),
                   fp_mul(fp(2), yP))
    xR = fp_sub(fp_square(slope), fp_mul(fp(2), xP))
    yR = fp_sub(fp_mul(slope, fp_sub(xP, xR)), yP)
    return _ETAG_, xR, yR

def e_add(P, Q):
    assert _is_an_e_representation_(P)
    assert _is_an_e_representation_(Q)
    _, xP, yP = P
    _, xQ, yQ = Q
    if e_eq(P, _Z_):
        return Q
    if e_eq(Q, _Z_):
        return P
    if e_eq(P, e_neg(Q)):
        return _Z_
    if e_eq(P, Q):
        return e_dbl(P)
    # slope = (yP - yQ) / (xP - xQ)
    # xR = slope**2 - xP - xQ
    # yR = slope * (xP - xR) - yP
    slope = fp_div(fp_sub(yP, yQ), fp_sub(xP, xQ))
    xR = fp_sub(fp_sub(fp_square(slope), xP), xQ)
    yR = fp_sub(fp_mul(slope, fp_sub(xP, xR)), yP)
    return _ETAG_, xR, yR

def e_mul(P, k):
    assert _is_an_e_representation_(P)
    assert _is_an_fq_representation_(k)
    R = _Z_
    for bit in fq_to_msb_first_bit_sequence(k):
        R = e_dbl(R)
        if bit == 1:
            R = e_add(R, P)
    return R










def ecdsa_is_valid_Qhrs_quadruple(Q, h, r, s):
    # Q <- e_from_octetstring( key )    MUST NOT BE THE POINT AT INFINITY
    # h <- mod_q(bitstring_to_integer(truncate_to_q_length(hash( msg ))))
    # (r, s) <- asn1_parse_a_sequence_of_two_signed_integer( sig )
    assert _is_an_e_representation_(Q) and not e_eq(Q, e(0))
    assert type(h) is int and (0 <= h <= q - 1)
    assert type(r) is int
    assert type(s) is int
    if not (1 <= r <= q - 1):
        return False
    if not (1 <= s <= q - 1):
        return False
    # TODO
