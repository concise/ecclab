"""
ecdsa_verify :: ((bytes, bytes, bytes) -> bool) throws EcdsaInputError

    Given a (publickey, message, signature) tuple, return a Boolean value
    indicating whether the signature is correctly generated or raise an
    EcdsaInputError exception when some provided argument is not in the
    correct format.

    publickey :: bytes

        the ECDSA public key to verify digital signatures, encoded using the
        rules specified in ANSI X9.62

    message :: bytes

        the original message getting signed by the ECDSA private key holder,
        represented as an octet string

    signature :: bytes

        the digital signature generated by the ECDSA private key holder,
        encoded using ASN.1 as a sequence of two signed integers

"""

__all__ = ['verify', 'SigVerifyInputError']

def verify(publickey, message, signature):
    Q = decode_a_public_key_point_from_an_octet_string(publickey)
    h = hash_encode_an_octet_string_into_an_integer_modulo_q(message)
    r, s = decode_a_signature_from_an_octet_string(signature)
    return is_valid_Q_h_r_s_ecdsa_quadruple(Q, h, r, s)

class SigVerifyInputError(Exception):
    """
    This exception is raised when a function receives an input argument of the
    wrong data type, or of the right type but with an inappropriate value
    """
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and type(args[0]) is str and len(kwargs) == 0:
            lines = [s.strip() for s in args[0].split('\n')
                    if s.strip() != '']
            long_err_msg = ' '.join(lines)
            Exception.__init__(self, long_err_msg)
        else:
            Exception.__init__(self, *args, **kwargs)

def decode_a_public_key_point_from_an_octet_string(pk):

    ERROR_MSG_TYPE_MISMATCH = '''
            an EC public key point is expected to be encoded as an octet
            string, which we represent as a Python bytes object, but the
            provided input argument is not
            '''
    ERROR_MSG_POINT_AT_INFINITY = '''
            the provided EC point is the point at infinity, which cannot be
            used as a public key
            '''
    ERROR_MSG_INVALID_FORMAT = '''
            the provided octet string cannot be decoded to an EC public key
            point according to the rules specified in ANSI X9.62
            '''
    ERROR_MSG_UNDERLYING_FIELD_DECODING = '''
            a substring of the provided octet string is not a correct encoding
            of an element in the underlying prime field for the EC group
            '''
    ERROR_MSG_POINT_NOT_ON_CURVE = '''
            the provided point is not an element of the EC group
            '''
    ERROR_MSG_BAD_YCOORD_PARITY = '''
            the parity bit of the Y coordinate of the provided EC public key
            point is incorrect
            '''

    # Some parameters for the secp256r1/prime256v1/P-256 curve defined on GFp
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    pLEN = 32
    a = -3
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b

    def octets2int(z):
        return int.from_bytes(z, byteorder='big')

    def octet_string_back_to_GFp(octetstr):
        the_integer = octets2int(octetstr)
        if 0 <= the_integer and the_integer <= p-1:
            return the_integer
        else:
            raise SigVerifyInputError(ERROR_MSG_UNDERLYING_FIELD_DECODING)

    def is_nonzero_point_on_curve(Q):
        X, Y = Q
        return (X**3 + a*X + b - Y**2) % p == 0

    def decode_uncompressed_ecpoint(pk):
        XQ = octet_string_back_to_GFp(pk[ 1      : 1+pLEN   ])
        YQ = octet_string_back_to_GFp(pk[ 1+pLEN : 1+pLEN*2 ])
        Q = XQ, YQ
        if is_nonzero_point_on_curve(Q):
            return Q
        else:
            raise SigVerifyInputError(ERROR_MSG_POINT_NOT_ON_CURVE)

    def decode_uncompressed_ecpoint_with_y_parity(pk, y_parity):
        Q = decode_uncompressed_ecpoint(pk)
        X, Y = Q
        if Y & 1 == y_parity & 1:
            return Q
        else:
            raise SigVerifyInputError(ERROR_MSG_BAD_YCOORD_PARITY)

    def decode_compressed_ecpoint_with_y_parity(pk, y_parity):
        X = octet_string_back_to_GFp(pk[ 1 : 1+pLEN ])
        W = (X**3 + a*X**2 + b) % p     # W is the square of Y in GFp
        Y = pow(W, (p+1)/4, p)          # Compute the square root of W
        Q = X, Y
        if is_nonzero_point_on_curve(Q):
            return Q if (Y & 1 == y_parity & 1) else (p - Q)
        else:
            raise SigVerifyInputError(ERROR_MSG_POINT_NOT_ON_CURVE)

    if type(pk) is not bytes:
        raise SigVerifyInputError(ERROR_MSG_TYPE_MISMATCH)
    elif len(pk) == 1 and pk[0] == 0x00:
        raise SigVerifyInputError(ERROR_MSG_POINT_AT_INFINITY)
    elif len(pk) == 1+pLEN and pk[0] == 0x02:
        return decode_compressed_ecpoint_with_y_parity(pk, y_parity=0)
    elif len(pk) == 1+pLEN and pk[0] == 0x03:
        return decode_compressed_ecpoint_with_y_parity(pk, y_parity=1)
    elif len(pk) == 1+pLEN*2 and pk[0] == 0x04:
        return decode_uncompressed_ecpoint(pk)
    elif len(pk) == 1+pLEN*2 and pk[0] == 0x06:
        return decode_uncompressed_ecpoint_with_y_parity(pk, y_parity=0)
    elif len(pk) == 1+pLEN*2 and pk[0] == 0x07:
        return decode_uncompressed_ecpoint_with_y_parity(pk, y_parity=1)
    else:
        raise SigVerifyInputError(ERROR_MSG_INVALID_FORMAT)

def hash_encode_an_octet_string_into_an_integer_modulo_q(msg):

    # Some parameters for the secp256r1/prime256v1/P-256 curve defined on GFp
    q = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    qLEN = 32

    def sha256(msg_to_hash):
        import hashlib
        sha256_digester = hashlib.sha256()
        sha256_digester.update(msg_to_hash)
        return sha256_digester.digest()

    def octets2int(z):
        return int.from_bytes(z, byteorder='big')

    def rfc6979_bits2int(octetstr):
        blen = len(octetstr) * 8
        qlen = qLEN * 8
        x = octets2int(octetstr)
        return (x >> (blen-qlen)) if (blen > qlen) else x

    return rfc6979_bits2int(sha256(msg)) % q

def decode_a_signature_from_an_octet_string(sig):

    ERROR_MSG_NOT_AN_ASN1_ECDSA_SIGNATURE = '''
            the provided octet string, which should represent an ECDSA
            signature, is not a valid ASN.1 sequence of two integers r and s
            with 0 < r < q and 0 < s < q
            '''

    q = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

    # :: (OctetString -> (OctetString, OctetString)) throws ValueError
    def parse_asn1_sequence(octetstr):
        if len(octetstr) < 2:
            raise ValueError('A SEQUENCE must be at least two bytes long')
        TAG, LEN = octetstr[0], octetstr[1]
        if TAG != 0x30:
            raise ValueError('A SEQUENCE must have TAG value 0x30')
        if LEN > 127:
            raise ValueError('LEN >= 128 should never happen')
        if LEN > len(octetstr)-2:
            raise ValueError('The length of the SEQUENCE is incorrect')
        return octetstr[ 2 : 2+LEN ], octetstr[ 2+LEN : ]

    # :: (OctetString -> (Integer, OctetString)) throws ValueError
    def parse_asn1_integer(octetstr):
        if len(octetstr) < 3:
            raise ValueError('An INTEGER must be at least three bytes long')
        TAG, LEN = octetstr[0], octetstr[1]
        if TAG != 0x02:
            raise ValueError('An INTEGER must have TAG value 0x02')
        if LEN > 127:
            raise ValueError('LEN >= 128 should never happen')
        if LEN == 0 or LEN > len(octetstr)-2:
            raise ValueError('The length of the INTEGER is incorrect')
        return octets2int_signed(octetstr[ 2 : 2+LEN ]), octetstr[ 2+LEN : ]

    # :: OctetString -> Integer
    def octets2int_signed(z):
        return int.from_bytes(z, byteorder='big', signed=True)

    try:
        sequence_body, tail = parse_asn1_sequence(sig)
        if len(tail) != 0:
            raise SigVerifyInputError(ERROR_MSG_NOT_AN_ASN1_ECDSA_SIGNATURE)
        r, tail = parse_asn1_integer(sequence_body)
        s, tail = parse_asn1_integer(tail)
        if len(tail) != 0:
            raise SigVerifyInputError(ERROR_MSG_NOT_AN_ASN1_ECDSA_SIGNATURE)
        if 0 < r and r < q and 0 < s and s < q:
            return r, s
        else:
            raise SigVerifyInputError(ERROR_MSG_NOT_AN_ASN1_ECDSA_SIGNATURE)
    except ValueError:
        raise SigVerifyInputError(ERROR_MSG_NOT_AN_ASN1_ECDSA_SIGNATURE)

def is_valid_Q_h_r_s_ecdsa_quadruple(Q, h, r, s):

    def modinv(n, prime_modulo):
        assert n % prime_modulo != 0
        return pow(n, prime_modulo - 2, prime_modulo)

    #
    # GFq operations
    #

    q = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    def GFq_eq(m, n): return (m - n) % q == 0
    def GFq_mul(m, n): return (m * n) % q
    def GFq_inv(m): return modinv(m, q)

    #
    # The elliptic curve parameters
    #

    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    a = -3
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    def on_curve(Q):
        assert type(Q) is tuple and len(Q) == 2
        X, Y = Q
        return (X**3 + a*X + b - Y**2) % p == 0

    #
    # The selected base point G which generates an additive group of order q
    # and Z the point at infinity
    #

    XG = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    YG = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
    G  = XG, YG
    Z  = 0, 0
    assert on_curve(G)
    assert not on_curve(Z)

    #
    # ECGroup operations
    #

    def EQ(P, Q):
        X1, Y1 = P
        X2, Y2 = Q
        return (X1 - X2) % p == 0 and (Y1 - Y2) % p == 0

    def NEG(P):
        assert on_curve(P) or EQ(P, Z)
        if EQ(P, Z):
            return Z
        X, Y = P
        return X, -Y % p

    def DBL(P):
        assert on_curve(P) or EQ(P, Z)
        if EQ(P, Z):
            return Z
        XP, YP = P
        t = ((3*XP**2 + a) * modinv(2 * YP, p)) % p
        XR = (t**2 - 2*XP) % p
        YR = (t * (XP - XR) - YP) % p
        return XR, YR

    def ADD(P, Q):
        assert on_curve(P) or EQ(P, Z)
        assert on_curve(Q) or EQ(Q, Z)
        assert not EQ(P, Q)
        if EQ(P, Z):
            return Q
        if EQ(Q, Z):
            return P
        if EQ(P, NEG(Q)):
            return Z
        X1, Y1 = P
        X2, Y2 = Q
        t = ((Y1 - Y2) * modinv(X1 - X2, p)) % p
        X3 = (t**2 - X1 - X2) % p
        Y3 = (t * (X1 - X3) - Y1) % p
        return X3, Y3

    def ECGroup_to_GFq(M):
        assert on_curve(M)
        X, Y = M
        return X % q

    def ECGroup_ADD(P, Q):
        assert on_curve(P) or EQ(P, Z)
        assert on_curve(Q) or EQ(Q, Z)
        if EQ(P, Z):
            return Q
        elif EQ(Q, Z):
            return P
        elif EQ(P, NEG(Q)):
            return Z
        elif EQ(P, Q):
            return DBL(P)
        else:
            return ADD(P, Q)

    def ECGroup_MUL(Q, k):
        assert on_curve(Q) or EQ(Q, Z)
        if EQ(Q, Z):
            return Z
        k = k % q
        l = k.bit_length()
        T = Q
        R = Z
        for i in range(l):
            if (k >> i) & 1 == 1:
                R = ADD(R, T)
            T = DBL(T)
        return R

    #
    # (Q, h, r, s) is a valid ECDSA quadruple iff the equality holds:
    #
    #       r == ECGroup_to_GFq( G[h/s] + Q[r/s] )
    #

    assert on_curve(Q)
    assert 0 <= h <= q-1
    assert 1 <= r <= q-1
    assert 1 <= s <= q-1
    computed_r_to_be_checked = ECGroup_to_GFq(ECGroup_ADD(
            ECGroup_MUL(G, GFq_mul(h, GFq_inv(s))),
            ECGroup_MUL(Q, GFq_mul(r, GFq_inv(s)))))
    return GFq_eq(r, computed_r_to_be_checked)

def extract_ecdsa_publickey_from_an_x509_certificate(*_, **__):
    return NotImplementedError # TODO
