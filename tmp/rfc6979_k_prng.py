#!/usr/bin/env python3
"""

uint        "Unsigned Integer"  <--- int

            An "Unsigned Integer" is represented as an object of the native
            Python type "int" with a value always greater than or equal to 0.

bits        "Bit Sequence"      <--- ('BitSequence', bytes, int)

            A "Bit Sequence" is represented as an object of the native Python
            type "tuple".  Such a tuple must have length equal to 3.  The
            first element must be an object of the native Python type "str"
            with string value "BitSequence".  The second element must be an
            object of the native Python type "bytes" representing an octet
            sequence.  The third element must be an object of the native
            Python type "int" with an integer value 0, 1, 2, 3, 4, 5, 6, or 7.
            The third element indicates the number of trailing padding bits in
            the last octet in the second element.  If the second element is an
            empty sequence, the third element must have value 0.

octets      "Octet Sequence"    <--- ('BitSequence', bytes, 0)

            An "Octet Sequence" is represented in the same way as a "Bit
            Sequence", but the third element is always 0.

"""

def _is_uint(uint):
    return type(uint) is int and uint >= 0

def _is_bits(bits):
    return (type(bits) is tuple
            and type(bits[0]) is str and bits[0] == 'BitSequence'
            and type(bits[1]) is bytes
            and type(bits[2]) is int and bits[2] in {0,1,2,3,4,5,6,7}
            and not (len(bits[1]) == 0 and bits[2] != 0))

def _is_octets(octets):
    return _is_bits(octets) and octets[2] == 0

def bit_length_of_uint(uint):
    assert _is_uint(uint)
    return int.bit_length(uint)

def bit_length_of_bits(bits):
    assert _is_bits(bits)
    _, octets, num_padding_bits = bits
    return len(octets) * 8 - num_padding_bits

def bit_length_of(uint_or_bits):
    if _is_uint(uint_or_bits):
        return bit_length_of_uint(uint_or_bits)
    elif _is_bits(uint_or_bits):
        return bit_length_of_bits(uint_or_bits)
    else:
        assert False

def octet_length_of_(uint_or_bits):
    z = bit_length_of(uint_or_bits)
    return (z // 8) + (1 if (z % 8 > 0) else 0)

def bits_to_uint(bits):
    assert _is_bits(bits)
    _, octets, num_padding_bits = bits
    tmp = int.from_bytes(octets, byteorder='big', signed=False)
    ret = tmp >> num_padding_bits
    assert _is_uint(ret)
    return ret

def bits_to_uint_of_same_length_as_uint(b, q):
    assert _is_bits(b)
    assert _is_uint(q)
    blen = bit_length_of(b)
    qlen = bit_length_of(q)
    c = bits_to_uint(b)
    if blen > qlen:
        return c >> (blen - qlen)
    else:
        return c

def uint_to_octets_of_same_length_as_uint(uint, q):
    assert _is_uint(uint)
    assert _is_uint(q)
    qlen = octet_length_of_(q)
    octets = int.to_bytes(uint, length=qlen, byteorder='big', signed=False)
    ret = 'BitSequence', octets, 0
    assert _is_octets(ret)
    return ret





def rfc6979_k_prng(x, h, q, hLEN, HMAC):
    '''
    generate pseudo-random integers in the inclusive range [1, q - 1]
    '''
    assert type(x) is int and 1 <= x <= q - 1   # private key
    assert type(h) is int and 0 <= h <= q - 1   # message hashed into Fq
    assert type(q) is int                       # group order
    assert type(hLEN) is int                    # H output byte-length
    assert type(HMAC(b'', b'')) is bytes        # HMAC function
    assert len(HMAC(b'', b'')) == hLEN          # HMAC output byte-length

    def bitlen(obj):
        assert (type(obj) is int and obj > 0) or type(obj) is bytes
        if type(obj) is int:
            return obj.bit_length()
        else:
            return len(obj) * 8

    def bytelen(obj):
        z = bitlen(obj)
        return (z // 8) + (1 if (z % 8 > 0) else 0)

    def int2octets(x, q):
        qLEN = bytelen(q)
        return x.to_bytes(length=qLEN, byteorder='big')

    def octets2int(z):
        return int.from_bytes(z, byteorder='big')

    def bits2int(b, q):
        blen = bitlen(b)
        qlen = bitlen(q)
        x = octets2int(b)
        return (x >> (blen-qlen)) if (blen > qlen) else x

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
        if 1 <= k <= q - 1:
            yield k
        K = HMAC(K, V + b'\x00')
        V = HMAC(K, V)


if __name__ == '__main__':

    # test vector from https://tools.ietf.org/html/rfc6979#appendix-A.2.5
    testx = 0xc9afa9d845ba75166b5c215767b1d6934e50c3db36e89b127b8a622b120f6721
    testh = 0xaf2bdbe1aa9b6ec1e2ade1d694f41fc71a831d0268e9891562113d8a62add1bf
    testq = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    asn_k = 0xa6e3c57dd01abe90086538398355dd4c3b17aa873382b0f24d6129493d8aad60
    testhLEN = 32
    def testHMAC(hmac_key, hmac_msg):
        import hashlib
        import hmac
        hmac_signer = hmac.new(hmac_key, digestmod=hashlib.sha256)
        hmac_signer.update(hmac_msg)
        return hmac_signer.digest()

    for gen_k in rfc6979_k_prng(testx, testh, testq, testhLEN, testHMAC):
        print('asn_k =', hex(asn_k))
        print('gen_k =', hex(gen_k))
        break
