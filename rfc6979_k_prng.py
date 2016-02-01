#!/usr/bin/env python3

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

    # the test uses SHA-256
    testhLEN = 32
    def testHMAC(hmac_key, hmac_msg):
        import hashlib
        import hmac
        hmac_signer = hmac.new(hmac_key, digestmod=hashlib.sha256)
        hmac_signer.update(hmac_msg)
        return hmac_signer.digest()

    gen_k = next(rfc6979_k_prng(testx, testh, testq, testhLEN, testHMAC))
    print('generated k =', hex(gen_k))
    print('answer of k =', hex(asn_k))
