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
    # n^( -1 ) === n^( (p - 1) -1 ) (mod p)
    # n^( -1 ) === n^(  p - 2     ) (mod p)
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
    # n^2 === n^( (p - 1) + 2 ) (mod p)
    # n^2 === n^(  p + 1      ) (mod p)
    # n   === n^( (p + 1) / 2 ) (mod p)
    # m^2 === n^( (p + 1) / 2 ) (mod p)
    # m   === n^( (p + 1) / 4 ) (mod p)
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

def fq_inv(elm):
    assert _is_an_fq_representation_(elm)
    if elm[1] == 0:
        raise fq_Error
    return _FqTAG_, pow(elm[1], _q_ - 2, _q_)

def fq_mul(elm1, elm2):
    assert _is_an_fq_representation_(elm1)
    assert _is_an_fq_representation_(elm2)
    return _FqTAG_, (elm1[1] * elm2[1]) % _q_

def fq_div(elm1, elm2):
    return fq_mul(elm1, fq_inv(elm2))

def fq_to_lsb_first_bit_sequence_generator(elm):
    assert _is_an_fq_representation_(elm)
    _, value = elm
    vlen = value.bit_length()
    for i in range(vlen):
        yield (value >> i) & 1

def fq_to_msb_first_bit_sequence(elm):
    return reversed(tuple(fq_to_lsb_first_bit_sequence_generator(elm)))










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

def _is_on_e_curve_(x, y):
    lhs = fp_square(y)
    rhs = fp_add(fp_add(fp_cube(x), fp_mul(_a_, x)), _b_)
    return fp_eq(lhs, rhs)

def _is_a_2d_fp_space_point_for_e_(obj):
    return (type(obj) is tuple and len(obj) == 3 and obj[0] is _ETAG_
            and _is_an_fp_representation_(obj[1])
            and _is_an_fp_representation_(obj[2]))

def _is_an_e_representation_(obj):
    if _is_a_2d_fp_space_point_for_e_(obj):
        _, x, y = obj
        if _is_on_e_curve_(x, y):
            return True
        else:
            return obj == _Z_
    else:
        return False

assert not _is_on_e_curve_(_xZ_, _yZ_)
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

def e_nonzero_from_octetstring(octetstring):
    if len(octetstring) == 1 and octetstring[0] == 0x00:
        raise e_Error
    return e_from_octetstring(octetstring)

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
    return fp_to_integer(x)

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
    # slope = (3 * xP**2 + _a_) / (2 * yP)
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










class asn1_Error(BaseException):
    pass

def asn1_parse_integer(octetstring):
    """
    return an signed integer encoded in this ASN.1 INTEGER
    """
    assert type(octetstring) is bytes
    T, L, V, X = _asn1_extract_T_L_V_X_from_(octetstring)
    assert _asn1_L_value_(L) == len(V)
    if len(X) != 0:
        raise asn1_Error
    if T != b'\x02':
        raise asn1_Error
    if len(V) >= 2 and V[0] == 0x00 and V[1] <= 0x7f:
        raise asn1_Error
    return int.from_bytes(V, byteorder='big', signed=True)

def asn1_parse_bitstring_as_octet_string(octetstring):
    """
    return an octet string encoded in this ASN.1 BIT STRING
    """
    assert type(octetstring) is bytes
    T, L, V, X = _asn1_extract_T_L_V_X_from_(octetstring)
    assert _asn1_L_value_(L) == len(V)
    if len(X) != 0:
        raise asn1_Error
    if T != b'\x03':
        raise asn1_Error
    if V[0] != 0x00:
        raise asn1_Error
    return V[1:]

def asn1_parse_sequence(octetstring):
    """
    return a sequence of octet strings encoded in this ASN.1 SEQUENCE
    """
    assert type(octetstring) is bytes
    T, L, V, X = _asn1_extract_T_L_V_X_from_(octetstring)
    assert _asn1_L_value_(L) == len(V)
    if len(X) != 0:
        raise asn1_Error
    if T != b'\x30':
        raise asn1_Error
    items = ()
    X = V
    while len(X) != 0:
        T, L, V, X = _asn1_extract_T_L_V_X_from_(X)
        items += (T + L + V,)
    return items

def _asn1_extract_T_L_V_X_from_(stream):
    X = stream
    T, X = _asn1_extract_T_from_(X)
    L, X = _asn1_extract_L_from_(X)
    V, X = _asn1_extract_V_from_(X, length=_asn1_L_value_(L))
    return T, L, V, X

def _asn1_L_value_(L):
    if len(L) == 0:
        raise asn1_Error
    elif len(L) == 1 and L[0] <= 0x7f:
        return L[0]
    elif len(L) == 2 and L[0] == 0x81 and L[1] >= 0x80:
        return L[1]
    elif len(L) == L[0] - 0x7f and L[0] >= 0x82 and L[1] != 0x00:
        return int.from_bytes(L[1:], byteorder='big', signed=False)
    else:
        raise asn1_Error

def _asn1_extract_T_from_(stream):
    if len(stream) == 0:
        raise asn1_Error
    return stream[:1], stream[1:]

def _asn1_extract_L_from_(stream):
    if len(stream) == 0:
        raise asn1_Error
    if stream[0] == 0x80:
        raise asn1_Error
    elif stream[0] <= 0x7f:
        return stream[:1], stream[1:]
    else:
        return _asn1_extract_long_L_from_(stream)

def _asn1_extract_long_L_from_(stream):
    length = stream[0] - 0x7f
    if len(stream) < length:
        raise asn1_Error
    L, _ = stream[:length], stream[length:]
    if (length == 2 and L[1] >= 0x80) or L[1] != 0x00:
        return L, _
    else:
        raise asn1_Error

def _asn1_extract_V_from_(stream, length):
    if len(stream) < length:
        raise asn1_Error
    return stream[:length], stream[length:]

def _asn1_parse_a_sequence_of_two_signed_integers_(octetstring):
    seq = asn1_parse_sequence(octetstring)
    if len(seq) != 2:
        raise asn1_Error
    octets1, octets2 = seq
    int1 = asn1_parse_integer(octets1)
    int2 = asn1_parse_integer(octets2)
    return int1, int2










__q__ = q

class ecdsa_Error(BaseException):
    pass

def _ecdsa_signature_base_octetstring_to_integer_mod_q_(octetstring):
    # h <- mod_q(bitstring_to_integer(truncate_to_q_length(hash( ... ))))
    assert type(octetstring) is bytes
    import hashlib
    sha256_digester = hashlib.sha256()
    sha256_digester.update(octetstring)
    digest = sha256_digester.digest()
    return int.from_bytes(digest, byteorder='big', signed=False) % __q__

def _ecdsa_is_valid_Qhrs_quadruple_(Q, h, r, s):
    assert _is_an_e_representation_(Q) and not e_eq(Q, e(0))
    assert type(h) is int and (0 <= h <= __q__ - 1)
    assert type(r) is int
    assert type(s) is int
    if not (1 <= r <= __q__ - 1):
        return False
    if not (1 <= s <= __q__ - 1):
        return False
    R = e_add(e_mul(e(1), fq_div(fq(h), fq(s))),
              e_mul(Q,    fq_div(fq(r), fq(s))))
    rr = e_to_integer(R) % __q__
    return rr == r

def ecdsa_verify_signature(publickey, message, signature):
    assert type(publickey) is bytes
    assert type(message) is bytes
    assert type(signature) is bytes
    try:
        Q    = e_nonzero_from_octetstring(publickey)
        h    = _ecdsa_signature_base_octetstring_to_integer_mod_q_(message)
        r, s = _asn1_parse_a_sequence_of_two_signed_integers_(signature)
        return _ecdsa_is_valid_Qhrs_quadruple_(Q, h, r, s)
    except e_Error:
        pass
    except asn1_Error:
        pass
    raise ecdsa_Error

def ecdsa_compress_publickey(publickey):
    assert type(publickey) is bytes
    try:
        Q = e_nonzero_from_octetstring(publickey)
        return e_to_octetstring(Q, compressed=True)
    except e_Error:
        pass
    raise ecdsa_Error

def ecdsa_decompress_publickey(publickey):
    assert type(publickey) is bytes
    try:
        Q = e_nonzero_from_octetstring(publickey)
        return e_to_octetstring(Q, compressed=False)
    except e_Error:
        pass
    raise ecdsa_Error

def ecdsa_extract_publickey_octetstring_from_certificate(certificate):
    try:

        #
        # Certificate ::= SEQUENCE {
        #   tbsCertificate          TBSCertificate,
        #   signatureAlgorithm      AlgorithmIdentifier,
        #   signatureValue          BIT STRING
        # }
        #
        tbscert, _, _ = asn1_parse_sequence(certificate)

        #
        # TBSCertificate ::= SEQUENCE {
        #   version             [0] EXPLICIT Version DEFAULT v1,
        #   serialNumber            CertificateSerialNumber,
        #   signature               AlgorithmIdentifier,
        #   issuer                  Name,
        #   validity                Validity,
        #   subject                 Name,
        #   subjectPublicKeyInfo    SubjectPublicKeyInfo,
        #   issuerUniqueID      [1] IMPLICIT UniqueIdentifier OPTIONAL,
        #                           -- If present, version MUST be v2 or v3
        #   subjectUniqueID     [2] IMPLICIT UniqueIdentifier OPTIONAL,
        #                           -- If present, version MUST be v2 or v3
        #   extensions          [3] EXPLICIT Extensions OPTIONAL
        #                           -- If present, version MUST be v3
        # }
        #
        _, _, _, _, _, _, pk_info, *_ = asn1_parse_sequence(tbscert)

        #
        # SubjectPublicKeyInfo ::= SEQUENCE {
        #   algorithm               AlgorithmIdentifier,
        #   subjectPublicKey        BIT STRING
        # }
        #
        alg, pk_bits = asn1_parse_sequence(pk_info)

        #
        # From Section 2.1 of RFC5480:
        #
        #       The algorithm field in the SubjectPublicKeyInfo structure
        #       indicates the algorithm and any associated parameters for the
        #       ECC public key (see Section 2.2).
        #
        #       AlgorithmIdentifier ::= SEQUENCE {
        #         algorithm               OBJECT IDENTIFIER,
        #         parameters              ANY DEFINED BY algorithm OPTIONAL
        #       }
        #
        #       id-ecPublicKey indicates that the algorithms that can be used
        #       with the subject public key are unrestricted.  The key is only
        #       restricted by the values indicated in the key usage
        #       certificate extension (see Section 3).  id-ecPublicKey MUST be
        #       supported.  See Section 2.1.1.  This value is also included in
        #       certificates when a public key is used with ECDSA.
        #
        # From Section 2.1.1 of RFC5480:
        #
        #       id-ecPublicKey OBJECT IDENTIFIER ::= {
        #         iso(1) member-body(2) us(840) ansi-X9-62(10045)
        #         keyType(2) 1
        #       }
        #
        #       The parameter for id-ecPublicKey is as follows and MUST always
        #       be present:
        #
        #       ECParameters ::= CHOICE {
        #         namedCurve         OBJECT IDENTIFIER
        #         -- implicitCurve   NULL
        #         -- specifiedCurve  SpecifiedECDomain
        #       }
        #
        # From Section 2.1.1.1 of RFC5480:
        #
        #       secp256r1 OBJECT IDENTIFIER ::= {
        #         iso(1) member-body(2) us(840) ansi-X9-62(10045)
        #         curves(3) prime(1) 7
        #       }
        #
        _ecdsa_ensure_good_subjectpublickeyinfo_algorithm_field_(alg)

        #
        # ECPoint ::= OCTET STRING
        #
        pk_octets = asn1_parse_bitstring_as_octet_string(pk_bits)
        _ecdsa_ensure_good_ecdsa_publickey_(pk_octets)

        return pk_octets

    except asn1_Error:
        pass
    except ValueError:
        pass
    raise ecdsa_Error

def _ecdsa_ensure_good_subjectpublickeyinfo_algorithm_field_(alg):
    #
    #                   AlgorithmIdentifier
    #
    # 30 13   06 07 2a8648ce3d0201   06 08 2a8648ce3d030107
    #         ^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^
    #         the algorithm field      the parameter field
    #
    #          OBJECT IDENTIFIER        OBJECT IDENTIFIER
    #           id-ecPublicKey              secp256r1
    #          1.2.840.10045.2.1       1.2.840.10045.3.1.7
    #
    if alg != bytes.fromhex('301306072a8648ce3d020106082a8648ce3d030107'):
        raise ecdsa_Error

def _ecdsa_ensure_good_ecdsa_publickey_(pk_octets):
    try:
        Q = e_nonzero_from_octetstring(pk_octets)
        return
    except e_Error:
        pass
    raise ecdsa_Error
