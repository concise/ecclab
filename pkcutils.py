'''
Public-Key Cryptography Utilities

    Boolean :: Primitive  (Python bool)

        TRUE and FALSE

    OctetString :: Primitive  (Python bytes)

        arbitrary octet strings

    X509CertError :: Primitive  (Python ValueError)

        "the provided OctetString is not an X509Cert"

    PublicKeyError :: Primitive  (Python ValueError)

        "the provided OctetString is not a PublicKey"

    X509Cert :: OctetString  (X.509 v3 certificates)

        A well-formed value of type X509Cert is an ASN.1 sequence of many
        nested structures as defined by X.509 v3, including a well-formed
        value of type PublicKey.

        SubjectPublicKeyInfo  ::=  SEQUENCE  {
                algorithm           AlgorithmIdentifier,
                subjectPublicKey    BIT STRING  }

        AlgorithmIdentifier  ::=  SEQUENCE  {
                algorithm           OBJECT IDENTIFIER,
                parameters          ANY DEFINED BY algorithm OPTIONAL }

        The subjectPublicKeyInfo field in a TBSCertificate should be in one of
        the following three formats:

                        AlgorithmIdentifier                   BIT STRING
        ------------------------------------------------- -------------------
        30 13 06 07 2a8648ce3d0201 06 08 2a8648ce3d030107 03 42 00 04 {X} {Y}
        30 13 06 07 2a8648ce3d0201 06 08 2a8648ce3d030107 03 22 00 02 {X}
        30 13 06 07 2a8648ce3d0201 06 08 2a8648ce3d030107 03 22 00 03 {X}
              ^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^
                OBJECT IDENTIFIER     OBJECT IDENTIFIER
                 id-ecPublicKey          secp256r1
                1.2.840.10045.2.1    1.2.840.10045.3.1.7


        Simplified procedure to extract a public key from the certificate:

                [tbsCertificate, ...] = certificate

                [version, serialNumber, signature, issuer, validity, subject,
                        subjectPublicKeyInfo, ...] = tbsCertificate

                [algorithm, subjectPublicKey] = subjectPublicKeyInfo

                id_ecPublicKey_secp256r1 = AlgorithmIdentifier(
                        301306072a8648ce3d020106082a8648ce3d030107)

                REQUIRE: algorithm is equal to id_ecPublicKey_secp256r1

                REQUIRE: subjectPublicKey is a BIT STRING with no padding bit

                pk_candidate = bit_string_to_octet_string(subjectPublicKey)

                REQUIRE: pk_candidate is an EC public key point of secp256r1

                output pk_candidate

        Simplified procedure to extract a public key from the certificate #2:

                pattern = 301306072a8648ce3d020106082a8648ce3d030107

                REQUIRE: at least one pattern occurrence in certificate

                candidates = []

                forEach occurrence of pattern in certificate:

                        tail = the octet string right after the occurrence

                        if the first four bytes are 03420004:

                                c = {0x04} + the next 64 bytes

                                if c is checked to be a valid EC point:

                                        candidates.append(c)

                        elif the first four bytes are 03220002 or 03220003:

                                c = {0x02 OR 0x03} + the next 32 bytes

                                if c is checked to be a valid EC point:

                                        candidates.append(c)

                ERROR if len(candidates) == 0

                ERROR if len(candidates) >= 2 SHOULD RARELY HAPPEN UNLESS...

                output candidates[0]

                ERROR message:

                        the provided octet string is not a valid X.509 version
                        3 certificate with a secp256r1 elliptic curve subject
                        public key



    PublicKey :: OctetString  (secp256r1 public keys)

        A well-formed value of type PublicKey can be converted into an element
        of the elliptic curve group secp256r1 using the rules defined in SEC1,
        and the result MUST NOT be the point at infinity.  The octet string is
        either in the "uncompressed" or in the "compressed" form, and its
        length should be either 33 == (1 + 32) or 65 == (1 + 32 + 32), and its
        first octet MUST.

        +------+--------------------------+--------------------------+
        | 0x04 | an octet string X for xQ | an octet string Y for yQ |
        +------+--------------------------+--------------------------+

        +------+--------------------------+
        | 0x02 | an octet string X for xQ |  yQ == 0  (mod 2)
        +------+--------------------------+

        +------+--------------------------+
        | 0x03 | an octet string X for xQ |  yQ == 1  (mod 2)
        +------+--------------------------+

        The field elements (xQ, yQ) MUST satisfy the elliptic curve equation.



    Signature :: OctetString  (secp256r1 ecdsa-with-SHA256 signatures)

        A well-formed value of type Signature is an ASN.1 sequence of two
        integers r and s, where both of them MUST be a positive integer less
        than q.  Please note that an ill-formed value of such type passed into
        the procedure verify_signature() does not cause an exception, because
        an ill-formed digital signature is just considered invalid without
        further processing.

        +------+------+------------------------------------------------------+
        |      |      | +----+------+-----------+  +----+------+-----------+ |
        | 0x30 |  L1  | |0x02|  L2  |     r     |  |0x02|  L3  |     s     | |
        |      |      | +----+------+-----------+  +----+------+-----------+ |
        +------+------+------------------------------------------------------+

        The integers (r, s) MUST satisfy:  1 <= r <= q-1  and  1 <= s <= q-1.



    Message :: OctetString  (arbitrary octet strings)

        Any arbitrary octet string is a well-formed value of type Message.
        The value will be hashed into an integer modulo q in a well-defined
        way to perform the signature verification process.



    extract_publickey_from_certificate : X509Cert -> PublicKey
                                         except X509CertError

        Return the "BIT STRING" value (the length of which shall be a multiple
        of eight, so it is actually an octet string) from the nested field
        tbsCertificate -> subjectPublicKeyInfo -> subjectPublicKey if such
        field exists and the value is a valid PublicKey.  If the provided
        X.509 certificate input is not well-formed, an X509CertError exception
        will be raised.

    compress_publickey : PublicKey -> PublicKey
                         except PublicKeyError

        If the provided PublicKey is already in the compressed form, return it
        without any modification.  If the provided is in the uncompressed form
        or the hybrid form as specified in X9.62, the compressed equivalent is
        returned.  If the provided PublicKey is not in a correct format, a
        PublicKeyError exception will be raised.

    decompress_publickey : PublicKey -> PublicKey
                           except PublicKeyError

        Decompress the provided PublicKey if possible and return the result.
        If the provided PublicKey is not in a correct format, a PublicKeyError
        exception will be raised.

    verify_signature : (PublicKey, Signature, Message) -> Boolean
                       except PublicKeyError

        Check if the provided Signature is valid for the Message under the
        PublicKey.  A PublicKeyError exception is raised if and only if the
        provided PublicKey is not in a correct format.

If any value of the wrong type is passed into the above functions, a Python
exception TypeError will be raised.

'''

import asn1
from P256 import q
from P256ECC import (
        E, E_from_bytes, E_to_bytes, E_contains, E_take_x_mod_q, E_eq, E_neg,
        E_dbl, E_add, E_mul, E_InputError)

def ensure_good_subject_public_key_algorithm(alg):
    if alg != bytes.fromhex('301306072a8648ce3d020106082a8648ce3d030107'):
        raise ValueError

def ensure_good_subject_public_key(pk):
    E_from_bytes(pk)

def extract_publickey_from_certificate(x509v3cert):
    try:
        tbscert, *_                     = asn1.parse_one_SEQUENCE(x509v3cert)
        _, _, _, _, _, _, pkinfo, *_    = asn1.parse_one_SEQUENCE(tbscert)
        alg, pkbits                     = asn1.parse_one_SEQUENCE(pkinfo)
        publickey = asn1.parse_one_BITSTRING_to_an_octet_string(pkbits)
        ensure_good_subject_public_key_algorithm(alg)
        ensure_good_subject_public_key(publickey)
        return publickey
    except ValueError:
        # 1. cannot parse the octet string as some value encoded using ASN.1
        # 2. cannot unpack the sequence; not enough number of values
        # 3. alg is not { id-ecPublicKey secp256r1 }
        pass
    except E_InputError:
        # 4. the octet string cannot be converted back into a public key point
        pass
    raise ValueError


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
    # TODO: Might need improvement later
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
    r, tail = _parse_an_asn1_signed_integer(sequence_body)
    s, tail = _parse_an_asn1_signed_integer(tail)
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

'''

[RFC5280]       Cooper, D., Santesson, S., Farrell, S., Boeyen, S.,
                Housley, R., and W. Polk, "Internet X.509 Public Key
                Infrastructure Certificate and Certificate Revocation
                List (CRL) Profile", RFC 5280, May 2008.
                https://tools.ietf.org/html/rfc5280

                4.1.    Basic Certificate Fields

[RFC5480]       Turner, S., Brown, D., Yiu, K., Housley, R., and T. Polk,
                "Elliptic Curve Cryptography Subject Public Key Information",
                RFC 5480, March 2009. https://tools.ietf.org/html/rfc5480

                2.2.    Subject Public Key

[SEC1]          Standards for Efficient Cryptography Group (SECG), "SEC 1:
                Elliptic Curve Cryptography", Version 2.0, May 2009.
                http://www.secg.org/sec1-v2.pdf

                2.3.1   Bit-String-to-Octet-String Conversion
                2.3.4   Octet-String-to-Elliptic-Curve-Point Conversion
                3.2.2   Validation of Elliptic Curve Public Keys
                3.2.3   Partial Validation of Elliptic Curve Public Keys
                C.3     Syntax for Elliptic Curve Public Keys
                C.5     Syntax for Signature and Key Establishment Schemes

[SEC2]          Standards for Efficient Cryptography Group (SECG), "SEC 2:
                Recommended Elliptic Curve Domain Parameters", Version 2.0,
                January 2010. http://www.secg.org/sec2-v2.pdf

                2.1     Properties of Elliptic Curve Domain Parameters over Fp
                2.4.2   Recommended Parameters secp256r1

Note that "secp256r1" means:

        sec     standards for efficient cryptography
        p256    elliptic curve over a prime field Fp; bit length of p is 256
        r       verifiably random parameters (non-Koblitz)
        1       the sequence number

'''
