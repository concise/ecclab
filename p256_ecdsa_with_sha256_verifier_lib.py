# verify
# extract_an_ecdsa_public_key_octets_from_an_x509_certificate
# SignatureVerifierError

from P256 import q
from P256ECC import (
        E, E_from_bytes, E_to_bytes, E_contains, E_take_x_mod_q, E_eq, E_neg,
        E_dbl, E_add, E_mul, E_InputError)

Z = E(0) # the point at infinity (additive identity) of group E
G = E(1) # the base point that generates the cyclic group E

def verify(publickey, signature, message):
    Q    = _decode_a_public_key_point_from_an_octet_string(publickey)
    r, s = _decode_a_signature_from_an_octet_string(signature)
    h    = _hash_encode_an_octet_string_into_an_integer_modulo_q(message)
    return _is_valid_Q_h_r_s_ecdsa_quadruple(Q, h, r, s)

def extract_an_ecdsa_public_key_octets_from_an_x509_certificate(stream):
    raise NotImplementedError # TODO

class SignatureVerifierError(Exception):
    pass

def _is_valid_Q_h_r_s_ecdsa_quadruple(Q, h, r, s):
    assert E_contains(Q) and not E_eq(Q, Z)
    assert 0 <= h and h <= q-1
    assert 1 <= r and r <= q-1
    assert 1 <= s and s <= q-1
    r2 = E_take_x_mod_q(E_add(E_mul(G, _div_(h, s)),
                              E_mul(Q, _div_(r, s))))
    return (r - r2) % q == 0

def _div_(a, b):
    return (a * pow(b, q - 2, q)) % q

def _decode_a_public_key_point_from_an_octet_string(pk):
    if type(pk) is not bytes:
        raise SignatureVerifierError('a public key MUST be a bytes')
    try:
        Q = E_from_bytes(pk)
    except E_InputError:
        raise SignatureVerifierError('the bytes is not a valid public key')
    if E_eq(Q, Z):
        raise SignatureVerifierError('the bytes is not a valid public key')
    else:
        return Q

def _decode_a_signature_from_an_octet_string(sig):
    seqbody, tail = _parse_an_asn1_sequence(sig)
    if len(tail) != 0:
        raise SignatureVerifierError('bad signature input')
    r, tail = parse_asn1_integer(sequence_body)
    s, tail = parse_asn1_integer(tail)
    if len(tail) != 0:
        raise SignatureVerifierError('bad signature input')
    if 0 < r and r < q and 0 < s and s < q:
        return r, s
    else:
        raise SignatureVerifierError('bad signature input')

def _hash_encode_an_octet_string_into_an_integer_modulo_q(msg):
    return _rfc6979_bits2int(_sha256(msg)) % q

def _parse_an_asn1_sequence(stream):
    if len(stream) < 2:
        raise SignatureVerifierError('bad signature input')
    T, L = stream[0], stream[1]
    if T != 0x30:
        raise SignatureVerifierError('bad signature input')
    if L > 127:
        raise SignatureVerifierError('bad signature input')
    if L > len(stream)-2:
        raise SignatureVerifierError('bad signature input')
    V = stream[2:2+L]
    trailing_octets = stream[2+L:]
    return V, trailing_octets

def _parse_an_asn1_signed_integer(stream):
    if len(stream) < 3:
        raise SignatureVerifierError('bad signature input')
    T, L = stream[0], stream[1]
    if T != 0x02:
        raise SignatureVerifierError('bad signature input')
    if L > 127:
        raise SignatureVerifierError('bad signature input')
    if L == 0 or L > len(stream)-2:
        raise SignatureVerifierError('bad signature input')
    V = int.from_bytes(stream[2:2+L], byteorder='big', signed=True)
    trailing_octets = stream[2+L:]
    return V, trailing_octets

def _sha256(msg_to_hash):
    import hashlib
    sha256_digester = hashlib.sha256()
    sha256_digester.update(msg_to_hash)
    return sha256_digester.digest()

def _octets2int(z):
    return int.from_bytes(z, byteorder='big')

def _rfc6979_bits2int(octetstr):
    blen = len(octetstr) * 8
    qlen = 256
    x = _octets2int(octetstr)
    return (x >> (blen-qlen)) if (blen > qlen) else x
