def bitlen(*args):
    # bit length of a bit string, an octet string, or a non-negative integer
    if (len(args) == 2 and type(args[0]) == bytes and type(args[1]) == int and
        0 <= args[1] and args[1] <= 7 and (len(args[0]) > 0 or args[1] == 0)
       ):
        return 8 * len(args[0]) - args[1]
    elif len(args) == 1 and type(args[0]) == bytes:
        return 8 * len(args[0])
    elif len(args) == 1 and type(args[0]) == int and args[0] >= 0:
        return int.bit_length(args[0])
    else:
        raise Exception('bad input')

def bytelen(*args):
    z = bitlen(*args)
    return (z // 8) + (z % 8 > 0)

def bytelen_signed_integer(n):
    # return the two's complement byte length of an integer
    if n >= 0:
        return n.bit_length()//8 + 1
    else:
        return (-n-1).bit_length()//8 + 1

def bits2int(b, q, b_npb=0):
    blen = bitlen(b, b_npb)
    qlen = bitlen(q)
    x = octets2int(b) >> b_npb
    return (x >> (blen-qlen)) if (blen > qlen) else x

def int2octets(x, q):
    qLEN = bytelen(q)
    return x.to_bytes(length=qLEN, byteorder='big')

def octets2int(z):
    return int.from_bytes(z, byteorder='big')

def octets2int_signed(z):
    return int.from_bytes(z, byteorder='big', signed=True)

def asn1_encode_integer(n):
    if n < 0:
        raise NotImplementedError('encoding a negative integer '
                                  'is not implemented yet')
    LEN = bytelen_signed_integer(n)
    nn = n.to_bytes(length=LEN, byteorder='big', signed=True)
    return b'\x02' + bytes([LEN]) + nn

def asn1_encode_sequence(seq_value):
    value_length = len(seq_value)
    return b'\x30' + bytes([value_length]) + seq_value

def asn1_extract_sequence(stream):
    if not (type(stream) == bytes and len(stream) >= 2):
        raise ValueError('SEQUENCE must be at least two bytes long')
    T = stream[0]
    if T != 0x30:
        raise ValueError('SEQUENCE must have Tag value 0x30')
    L = stream[1]
    if L == 128:
        raise ValueError('the first byte of L can never be 0x80')
    if L >= 129:
        raise NotImplementedError('L >= 128 is not implemented yet')
    if L > len(stream)-2:
        raise ValueError('the provided octet string is too short')
    return stream[2:2+L], stream[2+L:]

def asn1_extract_integer(stream):
    if not (type(stream) == bytes and len(stream) >= 3):
        raise ValueError('INTEGER must be at least three bytes long')
    T = stream[0]
    if T != 0x02:
        raise ValueError('SEQUENCE must have Tag value 0x02')
    L = stream[1]
    if L == 128:
        raise ValueError('the first byte of L can never be 0x80')
    if L >= 129:
        raise NotImplementedError('L >= 128 is not implemented yet')
    if L == 0:
        raise ValueError('length of an ASN.1 INTEGER value cannot be 0')
    if L > len(stream)-2:
        raise ValueError('the provided octet string is too short')
    decoded_V = octets2int_signed(stream[2:2+L])
    return decoded_V, stream[2+L:]


#
# This function provides an implementation of E = <G>, a DLP-hard finite cyclic
# group of prime order q
#
def nistp256():

    # The elliptic curve named secp256r1 (or prime256v1 or P-256) is defined by
    # the sextuple (p, a, b, G, q, h).  The base point G generates a finite
    # group, of size prime q, on which the discrete logarithm problem is hard.
    p =  0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    a = -3
    b =  0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
         0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
    q =  0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    h =  1

    # Arithmetics in the underlying prime field Fp
    def add(x, y): return (x + y) % p
    def mul(x, y): return (x * y) % p
    def neg(x,  ): return (-x) % p
    def inv(x,  ): return pow(x, p - 2, p)

    # Here, an imaginary point at infinity, the additive identity (zero) in E,
    # is just a user-defined constant point selected from Fp x Fp that is not
    # being used to represent any other nonzero point in E.
    ZERO = (0, 0)

    # {P}, {Q} => {P} == {Q}
    def EQ(P, Q):
        xP, yP = P
        xQ, yQ = Q
        return add(xP, neg(xQ)) == 0 and add(yP, neg(yQ)) == 0

    # {P} => -{P}
    def NEG(P):
        xP, yP = P
        if EQ(P, ZERO):
            return ZERO
        else:
            return xP, neg(yP)

    # Given {P} where {P} != 0 and 2*{P} != 0, compute {R} = 2*{P} as:
    # (1) t  = (3 * xP^2 + a) / (2 * yP)
    # (2) xR = t^2 - 2 * xP
    # (3) yR = t * (xP - xR) - yP
    def DBL__(P):
        xP, yP = P
        t = mul(add(mul(3, mul(xP, xP)), a), inv(mul(2, yP)))
        xR = add(mul(t, t), neg(mul(2, xP)))
        yR = add(mul(t, add(xP, neg(xR))), neg(yP))
        return xR, yR

    # Given {P} and {Q} where {P} != 0 and {Q} != 0 and {P} != +-{Q}, compute
    # {R} = {P} + {Q} as:
    # (1) t  = (yP - yQ) / (xP - xQ)
    # (2) xR = t^2 - xP - xQ
    # (3) yR = t * (xP - xR) - yP
    def ADD__(P, Q):
        xP, yP = P
        xQ, yQ = Q
        t = mul(add(yP, neg(yQ)), inv(add(xP, neg(xQ))))
        xR = add(add(mul(t, t), neg(xP)), neg(xQ))
        yR = add(mul(t, add(xP, neg(xR))), neg(yP))
        return xR, yR

    # Given {P} and {Q}, compute {R} = {P} + {Q}
    def ADD(P, Q):
        if EQ(P, ZERO):
            return Q
        elif EQ(Q, ZERO):
            return P
        elif EQ(P, NEG(Q)):
            return ZERO
        elif EQ(P, Q):
            return DBL__(P)
        else:
            return ADD__(P, Q)

    def MUL(Q, k):
        k = k % q
        l = k.bit_length()
        T = Q
        R = ZERO
        for i in range(l):        # i = 0 ~ (l-1)
            if (k >> i) & 1 == 1: # if the i-th bit is 1
                R = ADD(R, T)
            T = ADD(T, T)
        return R

    def G_MUL(k):
        k = k % q
        l = k.bit_length()
        T = G
        R = ZERO
        for i in range(l):        # i = 0 ~ (l-1)
            if (k >> i) & 1 == 1: # if the i-th bit is 1
                R = (ADD__(R, T)
                     if not EQ(R, ZERO) else T)
            T = DBL__(T)
        return R

    def Fp_to_octetstring(w):
        return int2octets(w, p)

    # Encode a public key ECPoint as an octet string
    def ECPoint_to_octetstring(U):
        xU, yU = U
        if EQ(U, ZERO):
            return b'\x00'
        else:
            return b'\x04' + Fp_to_octetstring(xU) + Fp_to_octetstring(yU)

    def octetstring_to_Fp(v):
        return octets2int(v) % p

    def ECPoint_from_octetstring(u):
        pLEN = bytelen(p)
        if u == b'\x00':
            return ZERO
        elif len(u) == pLEN * 2 + 1 and u[0] == 0x04:
            xU = octetstring_to_Fp(u[ 1      : pLEN+1 ])
            yU = octetstring_to_Fp(u[ pLEN+1 :        ])
            return xU, yU
        else:
            raise Exception('bad input')

    # Convert an ECPoint into a Fq element for signature generation (for r)
    def ECPoint_to_Fq(R):
        xR, yR = R
        return xR % q

    return (q, G, ZERO, EQ, NEG, ADD, MUL, G_MUL,
            ECPoint_to_octetstring, ECPoint_from_octetstring, ECPoint_to_Fq)



#
# This function provides an implementation of H and HMAC which have output
# length of hLEN bytes
#
def sha256():

    import hashlib
    import hmac
    hLEN = hashlib.sha256().digest_size # 32 for SHA256

    def H(msg, msg_n_padbits=0):
        if msg_n_padbits != 0:
            raise NotImplementedError('nonzero padding bits not implemented')
        consumer = hashlib.sha256()
        consumer.update(msg)
        return consumer.digest()

    def HMAC(key, msg, key_n_padbits=0, msg_n_padbits=0):
        if (key_n_padbits != 0 or msg_n_padbits != 0):
            raise NotImplementedError('nonzero padding bits not implemented')
        hmac_signer = hmac.new(key, digestmod=hashlib.sha256)
        hmac_signer.update(msg)
        return hmac_signer.digest()

    return H, HMAC, hLEN



def rfc6979_k_prng(x, h, q, hLEN, HMAC):
    '''
    x       a non-negative integer modulo q
    h       an integer modulo q  (h == bits2int(h1, q) % q)
    q       a sufficiently large prime number
    hLEN    the byte length of the output for H and HMAC functions
    HMAC    the HMAC function matching the selected H function
    returns a non-negative integer modulo q  (randomly chosen from [1, q-1])
    '''

    V = b'\x01' * hLEN
    K = b'\x00' * hLEN
    K = HMAC(K, V + b'\x00' + int2octets(x, q) + int2octets(h, q))
    V = HMAC(K, V)
    K = HMAC(K, V + b'\x01' + int2octets(x, q) + int2octets(h, q))
    V = HMAC(K, V)

    while True:
        T = b''
        while bitlen(T) < bitlen(q):
            V = HMAC(K, V)
            T = T + V
        k = bits2int(T, q)
        if 1 <= k and k <= q - 1:
            yield k
        K = HMAC(K, V + b'\x00')
        V = HMAC(K, V)



def ecdsa(hashinfo, groupinfo):

    _, HMAC, hLEN = hashinfo

    (q, G, _, _, _, ADD, MUL, G_MUL,
     to_octetstring, from_octetstring, to_Fq) = groupinfo

    # Arithmetics in the prime field Fq
    def add(x, y): return (x + y) % q
    def mul(x, y): return (x * y) % q
    def neg(x,  ): return (-x) % q
    def inv(x,  ): return pow(x, q - 2, q)

    def __secret_x_to_public_Q(x):
        Q = G_MUL(x)
        return Q

    def __sign_h_with_x_and_k(h, x, k):
        r = to_Fq(G_MUL(k))
        s = mul(add(h, mul(x, r)), inv(k))
        return r, s

    def __verify_h_r_s_with_Q(h, r, s, Q):
        return r == to_Fq(ADD(G_MUL(mul(h, inv(s))), MUL(Q, mul(r, inv(s)))))

    def encode_sig(r, s):
        rr = asn1_encode_integer(r)
        ss = asn1_encode_integer(s)
        return asn1_encode_sequence(rr + ss)

    def decode_sig(sig):
        rrss, __ = asn1_extract_sequence(sig)
        if len(__) != 0:
            raise ValueError('there are additional trailing bytes')
        r, ss = asn1_extract_integer(rrss)
        s, __ = asn1_extract_integer(ss)
        if len(__) != 0:
            raise ValueError('there are additional trailing bytes')
        return r, s

    def ecdsa_sk2pk(sk):
        x = octets2int(sk)
        return to_octetstring(__secret_x_to_public_Q(x))

    def ecdsa_sign(sk, h1):
        x = octets2int(sk)
        h = bits2int(h1, q) % q
        k_prng = rfc6979_k_prng(x, h, q, hLEN, HMAC)
        counter = 0
        for k in k_prng:
            r, s = __sign_h_with_x_and_k(h, x, k)
            if r != 0 and s != 0:
                return encode_sig(r, s)
            counter = counter + 1
            if counter >= 4:
                raise Exception('Cannot generate a good k value under 4 times')

    def ecdsa_verify(pk, h1, sig):
        Q = from_octetstring(pk)
        h = bits2int(h1, q) % q
        r, s = decode_sig(sig)
        return __verify_h_r_s_with_Q(h, r, s, Q)

    return ecdsa_sk2pk, ecdsa_sign, ecdsa_verify


#
# Test vector from RFC 6979
#

# b'\x10\xfe\xdc\xba\x98' -> '10fedcba98'
def B2H(byte_sequence):
    import codecs
    return codecs.encode(byte_sequence, 'hex').decode()

# '10fedcba98' -> b'\x10\xfe\xdc\xba\x98'
def H2B(hexchar_sequence):
    import codecs
    return codecs.decode(hexchar_sequence, 'hex')
    #return bytes.fromhex(hexchar_sequence)

m     = b'sample'
h1 = H2B('af2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e9891562113d8a62add1bf')
h     = 0xaf2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e9891562113d8a62add1bf
x     = 0xc9afa9d845ba75166b5c215767b1d6934e50c3db36e89b127b8a622b120f6721
U     =(0x60fed4ba255a9d31c961eb74c6356d68c049b8923b61fa6ce669622e60f29fb6,
        0x7903fe1008b8bc99a41ae9e95628bc64f2f1b20c2d7e9f5177a3c294d4462299)
ans_k = 0xa6e3c57dd01abe90086538398355dd4c3b17aa873382b0f24d6129493d8aad60
ans_r = 0xefd48b2aacb6a8fd1140dd9cd45e81d69d2c877b56aaf991c34d0ea84eaf3716
ans_s = 0xf7cb1c942d657c41d436c7a1b6e29f65f3e900dbb9aff4064dc4ab2f843acda8

# from ecdsa import * ; ecdsa_sk2pk, ecdsa_sign, ecdsa_verify = ecdsa(sha256(), nistp256())
# ecdsa_sign(sk=H2B('c9afa9d845ba75166b5c215767b1d6934e50c3db36e89b127b8a622b120f6721'), h1=H2B('af2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e9891562113d8a62add1bf'))
# ecdsa_verify(pk=H2B('0460fed4ba255a9d31c961eb74c6356d68c049b8923b61fa6ce669622e60f29fb67903fe1008b8bc99a41ae9e95628bc64f2f1b20c2d7e9f5177a3c294d4462299'), h1=H2B('af2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e9891562113d8a62add1bf'), sig=H2B('3046022100efd48b2aacb6a8fd1140dd9cd45e81d69d2c877b56aaf991c34d0ea84eaf3716022100f7cb1c942d657c41d436c7a1b6e29f65f3e900dbb9aff4064dc4ab2f843acda8'))
