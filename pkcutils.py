# Public-Key Cryptography Utilities
#
#   Boolean :: Primitive  (Python bool)
#
#       TRUE and FALSE
#
#   OctetString :: Primitive  (Python bytes)
#
#       arbitrary octet strings
#
#   X509CertError :: Primitive  (Python ValueError)
#
#       "the provided OctetString is not an X509Cert"
#
#   PublicKeyError :: Primitive  (Python ValueError)
#
#       "the provided OctetString is not a PublicKey"
#
#   X509Cert :: OctetString  (X.509 v3 certificates)
#
#       A well-formed value of type X509Cert is an ASN.1 sequence of many
#       nested structures as defined by X.509 v3, including a well-formed
#       value of type PublicKey.
#
#   PublicKey :: OctetString  (X9.62 prime256v1 public keys)
#
#       A well-formed value of type PublicKey can be converted into an element
#       of the elliptic curve group prime256v1 using the rules defined in
#       X9.62, and the result MUST NOT be the point at infinity.  The
#       OctetString value is in the "uncompressed", "compressed", or "hybrid"
#       form, and its length should be 33 == (1 + 32) or 65 == (1 + 32 + 32).
#
#   Signature :: OctetString  (X9.62 prime256v1 ecdsa-with-SHA256 signatures)
#
#       A well-formed value of type Signature is an ASN.1 sequence of two
#       integers r and s, where both of them MUST be a positive integer less
#       than q.  Please note that an ill-formed value of such type passed into
#       the procedure verify_signature() does not cause an exception, because
#       an ill-formed digital signature is just considered invalid without
#       further processing.
#
#   Message :: OctetString  (arbitrary octet strings)
#
#       Any arbitrary octet string is a well-formed value of type Message.
#       The value will be hashed into an integer modulo q in a well-defined
#       way to perform the signature verification process.
#
#   extract_publickey_from_certificate : X509Cert -> PublicKey
#                                        except X509CertError
#
#       Return the "BIT STRING" value (the length of which shall be a multiple
#       of eight, so it is actually an octet string) from the nested field
#       tbsCertificate -> subjectPublicKeyInfo -> subjectPublicKey if such
#       field exists and the value is a valid PublicKey.  If the provided
#       X.509 certificate input is not well-formed, the X509CertError
#       exception will be raised.
#
#   compress_publickey : PublicKey -> PublicKey
#                        except PublicKeyError
#
#       If the provided PublicKey is already in the compressed form, return it
#       without any modification.  If the provided is in the uncompressed form
#       or the hybrid form as specified in X9.62, the compressed equivalent is
#       returned.  If the provided PublicKey is not in a correct format, the
#       PublicKeyError exception will be raised.
#
#   verify_signature : (PublicKey, Signature, Message) -> Boolean
#                      except PublicKeyError
#
#       Check if the provided Signature is valid for the Message under the
#       PublicKey.  The PublicKeyError exception is raised if and only if the
#       provided PublicKey is not in a correct format.
#
# If any value of the wrong type is passed into the above functions, a Python
# exception TypeError will be raised.

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
    if type(stream) is not bytes:
        raise SignatureVerifierError('bad input')
    seqbody, tail = _parse_an_asn1_sequence(stream)
    if len(tail) != 0:
        raise SignatureVerifierError('bad input')
    #
    # TODO: Need improvement later
    #
    # Because I'm too lazy to actually parse the whole X.509 certificate
    # structure, for now I am going to make a shortcut here...
    #
    splitted = seqbody.split(bytes.fromhex(
            '301306072a8648ce3d020106082a8648ce3d030107034200'))
    if len(splitted) == 1:
        raise SignatureVerifierError('bad input')
    elif len(splitted) >= 3:
        raise SignatureVerifierError('case not implemented yet')
    else:
        stream2 = splitted[1]
        if len(stream2) < 1:
            raise SignatureVerifierError('bad input')
        elif stream2[0] in {0x02, 0x03} and len(stream2) >= 33:
            octets = stream2[:33]
            try:
                Q = E_from_bytes(octets)
            except E_InputError:
                raise SignatureVerifierError('bad input')
            else:
                return octets
        elif stream2[0] in {0x04, 0x06, 0x07} and len(stream2) >= 65:
            octets = stream2[:65]
            try:
                Q = E_from_bytes(octets)
            except E_InputError:
                raise SignatureVerifierError('bad input')
            return octets
        else:
            raise SignatureVerifierError('bad input')

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
        raise SignatureVerifierError('bad input')
    r, tail = parse_asn1_integer(sequence_body)
    s, tail = parse_asn1_integer(tail)
    if len(tail) != 0:
        raise SignatureVerifierError('bad input')
    if 0 < r and r < q and 0 < s and s < q:
        return r, s
    else:
        raise SignatureVerifierError('bad input')

def _hash_encode_an_octet_string_into_an_integer_modulo_q(msg):
    return _rfc6979_bits2int(_sha256(msg)) % q

def _parse_an_asn1_sequence(stream):
    if len(stream) < 2:
        raise SignatureVerifierError('bad input')
    T, L = stream[0], stream[1]
    if T != 0x30:
        raise SignatureVerifierError('bad input')
    if L > 127:
        if L == 128:
            raise SignatureVerifierError('bad input')
        length_of_the_L_field = L - 128
        if len(stream) < 1 + 1 + length_of_the_L_field:
            raise SignatureVerifierError('bad input')
        octets_L_field = stream[2:2+length_of_the_L_field]
        L = int.from_bytes(octets_L_field, byteorder='big', signed=False)
        if len(stream) < 1 + 1 + length_of_the_L_field + L:
            raise SignatureVerifierError('bad input')
        V = stream[1+1+length_of_the_L_field:1+1+length_of_the_L_field+L]
        trailing_octets = stream[1+1+length_of_the_L_field+L:]
        return V, trailing_octets
    else:
        if L > len(stream)-2:
            raise SignatureVerifierError('bad input')
        V = stream[2:2+L]
        trailing_octets = stream[2+L:]
        return V, trailing_octets

def _parse_an_asn1_signed_integer(stream):
    if len(stream) < 3:
        raise SignatureVerifierError('bad input')
    T, L = stream[0], stream[1]
    if T != 0x02:
        raise SignatureVerifierError('bad input')
    if L > 127:
        raise SignatureVerifierError('case not implemented yet')
    if L == 0 or L > len(stream)-2:
        raise SignatureVerifierError('bad input')
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
