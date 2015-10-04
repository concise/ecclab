import sys
#__all__ = ('G', 'n', 'O', 'add', 'mul', 'point_from_octetstring')

G = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296 \
  , 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

O = None

def neg(P):
    assert is_valid_point(P)
    if P is None:
        return None
    else:
        return P[0], -P[1] % p

def add(P1, P2):
    assert is_valid_point(P1)
    assert is_valid_point(P2)
    if P1 is None:
        return P2
    elif P2 is None:
        return P1
    elif P1[0] != P2[0]:
        return AFFINE_POINT_ADDITION(P1, P2)
    elif P1[1] == P2[1] != 0:
        return AFFINE_POINT_DOUBLING(P1)
    else:
        return None

def mul(k, P):
    assert type(k) is int
    assert is_valid_point(P)
    k = k % n
    if k == 0 or P is None:
        return None
    elif k == 1:
        return P
    elif k == n - 1:
        return P[0], -P[1] % p
    else:
        return MontgomeryLadderScalarMultiply_ver2(k, P)

def point_from_octetstring(octetstring):
    if type(octetstring) is not bytes:
        raise ValueError
    elif len(octetstring) == 1 and octetstring[0] == 0x00:
        return None
    elif len(octetstring) == 65 and octetstring[0] == 0x04:
        x = int.from_bytes(octetstring[1:33], byteorder='big', signed=False)
        y = int.from_bytes(octetstring[33:65], byteorder='big', signed=False)
        assert is_valid_point((x, y))
        return x, y
    elif len(octetstring) == 33 and octetstring[0] in {0x02, 0x03}:
        y_parity = octetstring[0] & 1
        x = int.from_bytes(octetstring[1:33], byteorder='big', signed=False)
        y = y_candidates_from_x(x)[y_parity]
        return x, y
    else:
        raise ValueError

#-----------------------------------------------------------------------------

def ecdsa_double_scalar_multiplication(t, u, Q):
    assert type(t) is int and 0 <= t <= n - 1
    assert type(u) is int and 1 <= u <= n - 1
    assert is_valid_point(Q) and Q is not None
    tG = mul(t, G)
    uQ = mul(u, Q)
    R = add(tG, uQ)
    return R

def y_candidates_from_x(xP):
    assert type(xP) is int
    y_squared = (xP * xP * xP + a * xP + b) % p
    y = pow(y_squared, (p + 1) // 4, p)
    if y * y % p != y_squared:
        raise ValueError
    return (y, p - y) if (y & 1 == 0) else (p - y, y)

def is_valid_point(P):
    return (P is None or (type(P) is tuple and len(P) == 2 and
            type(P[0]) is int and 0 <= P[0] <= p - 1 and
            type(P[1]) is int and 0 <= P[1] <= p - 1 and
            (P[0] * P[0] * P[0] + a * P[0] + b - P[1] * P[1]) % p == 0))

#-----------------------------------------------------------------------------

p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = -3
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b

_4b_ = 4 * b % p

def inv_mod_p(n):
    return pow(n, p - 2, p)

def AFFINE_POINT_ADDITION(P1, P2):
    x1, y1 = P1
    x2, y2 = P2
    v = ((y2 - y1) * inv_mod_p(x2 - x1)) % p
    x3 = (v * v - x1 - x2) % p
    y3 = (v * (x1 - x3) - y1) % p
    return x3, y3

def AFFINE_POINT_DOUBLING(P1):
    x1, y1 = P1
    w = ((3 * x1 * x1 + a) * inv_mod_p(2 * y1)) % p
    x4 = (w * w - 2 * x1) % p
    y4 = (w * (x1 - x4) - y1) % p
    return x4, y4

def msb_first_bit_string(n):
    return tuple(map(int,bin(n)[2:]))

def MontgomeryLadderScalarMultiply(k, P):
    if k > n // 2:
        flipped = True
        k = n - k
    else:
        flipped = False
    xP, yP = P
    X1, X2, Z = CoZIdDbl(xP, yP)
    for bit in msb_first_bit_string(k)[1:]:
        if bit == 1:
            X1, X2, Z = CoZDiffAddDbl(X1, X2, Z, xD=xP)
        else:
            X2, X1, Z = CoZDiffAddDbl(X2, X1, Z, xD=xP)
    X, Y, Z = CoZRecover(X1, X2, Z, xD=xP, yD=yP)
    iZ = inv_mod_p(Z)
    return (X * iZ) % p, ((Y * iZ) % p if not flipped else (-Y * iZ) % p)

def MontgomeryLadderScalarMultiply_ver2(k, P):
    if k > n // 2:
        flipped = True
        k = n - k
    else:
        flipped = False
    xP, yP = P
    X1, X2, Z = CoZIdDbl(xP, yP)
    xD = xP
    TD = (xD * Z) % p
    Ta = (a * Z * Z) % p
    Tb = (4 * b * Z * Z * Z) % p
    for bit in msb_first_bit_string(k)[1:]:
        if bit == 1:
            X1, X2, TD, Ta, Tb = CoZDiffAddDbl_alg6(X1, X2, TD, Ta, Tb)
        else:
            X2, X1, TD, Ta, Tb = CoZDiffAddDbl_alg6(X2, X1, TD, Ta, Tb)
    X, Y, Z = CoZRecover_alg8(X1, X2, TD, Ta, Tb, xD=xP, yD=yP)
    iZ = inv_mod_p(Z)
    return (X * iZ) % p, ((Y * iZ) % p if not flipped else (-Y * iZ) % p)

def CoZIdDbl(x, y):
    Z  = ( 4 * y * y      ) % p
    X1 = ( Z * x          ) % p
    t  = ( 3 * x * x + a  ) % p
    X2 = ( t * t - 2 * X1 ) % p
    return X1, X2, Z

def CoZDiffAddDbl(X1, X2, Z, xD):
    R2 = ( Z * Z     ) % p
    R3 = ( a * R2    ) % p
    R1 = ( Z * R2    ) % p
    R2 = ( _4b_ * R1 ) % p
    R1 = ( X2 * X2   ) % p
    R5 = ( R1 - R3   ) % p
    R4 = ( R5 * R5   ) % p
    R1 = ( R1 + R3   ) % p
    R5 = ( X2 * R1   ) % p
    R5 = ( R5 + R5   ) % p
    R5 = ( R5 + R5   ) % p
    R5 = ( R5 + R2   ) % p
    R1 = ( R1 + R3   ) % p
    R3 = ( X1 * X1   ) % p
    R1 = ( R1 + R3   ) % p
    X1 = ( X1 - X2   ) % p
    X2 = ( X2 + X2   ) % p
    R3 = ( X2 * R2   ) % p
    R4 = ( R4 - R3   ) % p
    R3 = ( X1 * X1   ) % p
    R1 = ( R1 - R3   ) % p
    X1 = ( X1 + X2   ) % p
    X2 = ( X1 * R1   ) % p
    X2 = ( X2 + R2   ) % p
    R2 = ( Z * R3    ) % p
    Z  = ( xD * R2   ) % p
    X2 = ( X2 - Z    ) % p
    X1 = ( R5 * X2   ) % p
    X2 = ( R3 * R4   ) % p
    Z  = ( R2 * R5   ) % p
    return X1, X2, Z

def CoZRecover(X1, X2, Z, xD, yD):
    R1 = ( xD * Z    ) % p
    R2 = ( X1 - R1   ) % p
    R3 = ( R2 * R2   ) % p
    R4 = ( R3 * X2   ) % p
    R2 = ( R1 * X1   ) % p
    R1 = ( X1 + R1   ) % p
    X2 = ( Z * Z     ) % p
    R3 = ( a * X2    ) % p
    R2 = ( R2 + R3   ) % p
    R3 = ( R2 * R1   ) % p
    R3 = ( R3 - R4   ) % p
    R3 = ( R3 + R3   ) % p
    R1 = ( yD + yD   ) % p
    R1 = ( R1 + R1   ) % p
    R2 = ( R1 * X1   ) % p
    X1 = ( R2 * X2   ) % p
    R2 = ( X2 * Z    ) % p
    Z  = ( R2 * R1   ) % p
    R4 = ( _4b_ * R2 ) % p
    X2 = ( R4 + R3   ) % p
    return X1, X2, Z




def ecdsa_verify_signature(publickey, message, signature):
    assert type(publickey) is bytes
    assert type(message) is bytes
    assert type(signature) is bytes

    try:
        Q = point_from_octetstring(publickey)
    except ValueError:
        return False
    if Q is None:
        return False

    try:
        r, s = parse_signature(signature)
    except ASN1Error:
        return False
    except ValueError:
        return False

    e = message_preprocessing(message)

    # Compute si = (s^(-1) mod n) and then compute (t, u) = (e*si, r*si)
    si = pow(s, n - 2, n)
    t = (e * si) % n
    u = (r * si) % n

    # Compute R = (t*G + u*Q)
    R = ecdsa_double_scalar_multiplication(t, u, Q)
    if R is None:
        return False

    # Compute r2 = the x coordinate of R mode n
    r2 = R[0] % n
    return r == r2

def do_sha256_using_openssl(rawdata):
    import subprocess
    p1 = subprocess.Popen(('openssl', 'dgst', '-sha256'),
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE)
    p2 = subprocess.Popen(('awk', '{print $NF}'),
                          stdin=p1.stdout,
                          stdout=subprocess.PIPE)
    p1.stdin.write(rawdata)
    p1.stdin.close()
    result_bytes = p2.stdout.read().rstrip().decode()
    return bytes.fromhex(result_bytes)
    #
    # echo 00 | xxd -p -r | openssl dgst -sha256 | awk '{print $NF}'
    #

def mysha256(msg):
    return do_sha256_using_openssl(msg)
    #
    # hex readable string -> octets
    #   bytes.fromhex('0001') == b'\x00\x01'
    #
    # octets -> hex readable string
    #   import codecs
    #   codecs.encode(b'\x00\x01', 'hex') == '0001'
    #
    import hashlib
    digester = hashlib.sha256()
    digester.update(msg)
    digest = digester.digest()
    return digest

def message_preprocessing(msg):
    digest = mysha256(msg)
    return octet_string_to_unsigned_integer(digest)

def first_octet_num_value_in_an_octet_string(octet):
    return octet[0]

def octet_string_to_unsigned_integer(octet_string):
    import codecs
    return int.from_bytes(octet_string, byteorder='big')
    #return int(codecs.encode(octet_string, 'hex'), 16)


def parse_signature(sig):
    r, s = parse_ASN1_SEQUENCE_of_two_INTEGERs(sig)
    if (1 <= r <= n - 1) and (1 <= s <= n - 1):
        return r, s
    else:
        raise ValueError














class ASN1Error(BaseException):
    pass

def parse_ASN1_SEQUENCE_of_two_INTEGERs(octetstring):
    sequence_elements = parse_ASN1_SEQUENCE(octetstring)
    if len(sequence_elements) != 2:
        raise ASN1Error
    octets1, octets2 = sequence_elements
    int1 = parse_ASN1_INTEGER(octets1)
    int2 = parse_ASN1_INTEGER(octets2)
    return int1, int2

def parse_ASN1_SEQUENCE(octetstring):
    if type(octetstring) is not bytes:
        raise ASN1Error
    T, L, V, X = destruct_leading_TLV_octets_from(octetstring)
    if len(X) != 0:
        raise ASN1Error
    if T != b'\x30':
        raise ASN1Error
    sequence_elements = ()
    X = V
    while len(X) != 0:
        T, L, V, X = destruct_leading_TLV_octets_from(X)
        sequence_elements += (T + L + V,)
    return sequence_elements

def parse_ASN1_BITSTRING_as_octet_string(octetstring):
    if type(octetstring) is not bytes:
        raise ASN1Error
    T, L, V, X = destruct_leading_TLV_octets_from(octetstring)
    if len(X) != 0:
        raise ASN1Error
    if T != b'\x03':
        raise ASN1Error
    if V[0] != 0x00:
        raise ASN1Error
    return V[1:]

# ----------------------------------------------------------------------------

def parse_ASN1_INTEGER(octetstring):
    if type(octetstring) is not bytes:
        raise ASN1Error
    T, L, V, X = destruct_leading_TLV_octets_from(octetstring)
    if len(X) != 0:
        raise ASN1Error
    if T != b'\x02':
        raise ASN1Error
    if len(V) >= 2 and V[0] == 0x00 and V[1] <= 0x7f:
        raise ASN1Error
    return octet_string_to_signed_integer(V)

def octet_string_to_signed_integer(octet_string):
    assert type(octet_string) is bytes

    l = len(octet_string)
    if l == 0:
        return 0

    v = first_octet_num_value_in_an_octet_string(octet_string)
    if v <= 0x7f:
        return octet_string_to_unsigned_integer(octet_string)
    else:
        return octet_string_to_unsigned_integer(octet_string) - (1 << (8 * l))


def destruct_leading_TLV_octets_from(stream):
    X = stream
    T, X = destruct_leading_T_octet_from(X)
    L, X = destruct_leading_L_octets_from(X)
    V, X = destruct_leading_V_octets_from(X, L=L)
    return T, L, V, X

def destruct_leading_T_octet_from(stream):
    if len(stream) == 0:
        raise ASN1Error
    else:
        return stream[:1], stream[1:]

def destruct_leading_L_octets_from(stream):
    if len(stream) == 0:
        raise ASN1Error
    elif stream[0] < 0x80:
        return stream[:1], stream[1:]
    elif stream[0] == 0x80:
        raise ASN1Error
    elif stream[0] > 0x80:
        return destruct_leading_long_L_octets_from(stream)

def destruct_leading_long_L_octets_from(stream):
    length = stream[0] - 0x7f
    if len(stream) < length:
        raise ASN1Error
    L, _ = stream[:length], stream[length:]
    if (length == 2 and L[1] >= 0x80) or (length > 2 and L[1] != 0x00):
        return L, _
    else:
        raise ASN1Error

def destruct_leading_V_octets_from(stream, L):
    length = get_length_from_L_octets(L)
    if len(stream) < length:
        raise ASN1Error
    else:
        return stream[:length], stream[length:]

def get_length_from_L_octets(L):
    if len(L) == 0:
        raise ASN1Error
    elif len(L) == 1 and L[0] <= 0x7f:
        return L[0]
    elif len(L) == 2 and L[0] == 0x81 and L[1] >= 0x80:
        return L[1]
    elif len(L) == L[0] - 0x7f and L[0] >= 0x82 and L[1] != 0x00:
        return octet_string_to_unsigned_integer(L[1:])
    else:
        raise ASN1Error

def CoZDiffAddDbl_alg6(X1, X2, TD, Ta, Tb):
    R2 = (X1 - X2) % p
    R1 = (R2 * R2) % p
    R2 = (X2 * X2) % p
    R3 = (R2 - Ta) % p
    R4 = (R3 * R3) % p
    R5 = (X2 + X2) % p
    R3 = (R5 * Tb) % p
    R4 = (R4 - R3) % p
    R5 = (R5 + R5) % p
    R2 = (R2 + Ta) % p
    R3 = (R5 * R2) % p
    R3 = (R3 + Tb) % p
    R5 = (X1 + X2) % p
    R2 = (R2 + Ta) % p
    R2 = (R2 - R1) % p
    X2 = (X1 * X1) % p
    R2 = (R2 + X2) % p
    X2 = (R5 * R2) % p
    X2 = (X2 + Tb) % p
    X1 = (R3 * X2) % p
    X2 = (R1 * R4) % p
    R2 = (R1 * R3) % p
    R3 = (R2 * Tb) % p
    R4 = (R2 * R2) % p
    R1 = (TD * R2) % p
    R2 = (Ta * R4) % p
    Tb = (R3 * R4) % p
    X1 = (X1 - R1) % p
    TD = R1
    Ta = R2
    return X1, X2, TD, Ta, Tb

def CoZRecover_alg8(X1, X2, TD, Ta, Tb, xD, yD):
    R1 = (TD * X1) % p
    R2 = (R1 + Ta) % p
    R3 = (X1 + TD) % p
    R4 = (R2 * R3) % p
    R3 = (X1 - TD) % p
    R2 = (R3 * R3) % p
    R3 = (R2 * X2) % p
    R4 = (R4 - R3) % p
    R4 = (R4 + R4) % p
    R4 = (R4 + Tb) % p
    R2 = (TD * TD) % p
    R3 = (X1 * R2) % p
    R1 = (xD * R3) % p
    R3 = (yD + yD) % p
    R3 = (R3 + R3) % p
    X1 = (R3 * R1) % p
    R1 = (R2 * TD) % p
    Z  = (R3 * R1) % p
    R2 = (xD * xD) % p
    R3 = (R2 * xD) % p
    X2 = (R3 * R4) % p
    return X1, X2, Z

def main():
    if len(sys.argv) != 4:
        print('Please provide three octet strings:' +
              ' 1) public key, 2) message, and 3) signature ' +
              'all in hex format')
        return
    try:
        key = bytes.fromhex(sys.argv[1])
        msg = bytes.fromhex(sys.argv[2])
        sig = bytes.fromhex(sys.argv[3])
        import time
        a = time.time()
        for i in range(1000):
            sig_is_valid = ecdsa_verify_signature(key, msg, sig)
        print(time.time() - a)
        if sig_is_valid is True:
            print('true')
        else:
            print('false')
    except ValueError:
        print('false')


if __name__ == '__main__':
    main()
