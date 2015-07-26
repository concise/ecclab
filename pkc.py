import asn1
import p256

class PkcError(BaseException):
    pass

class PkcTypeError(PkcError, TypeError):
    pass

class PkcCertificateError(PkcError, ValueError):
    pass

class PkcPublickeyError(PkcError, ValueError):
    pass

def pkc_extract_publickey_from_certificate(certificate):
    if type(certificate) is not bytes:
        raise PkcTypeError
    return _pkc_extract_publickey_from_certificate(certificate)

def pkc_compress_publickey(publickey):
    if type(publickey) is not bytes:
        raise PkcTypeError
    return _pkc_compress_publickey(publickey)

def pkc_verify_signature(publickey, message, signature):
    if (type(publickey) is not bytes or type(message) is not bytes
    or type(signature) is not bytes):
        raise PkcTypeError
    return _pkc_verify_signature(publickey, message, signature)





def _pkc_ensure_good_subject_public_key_algorithm(alg):
    if alg == bytes.fromhex('301306072a8648ce3d020106082a8648ce3d030107'):
        return
    raise ValueError

def _pkc_ensure_good_subject_public_key(pk):
    try:
        p256.E_from_bytes(pk)
        return
    except p256.P256Error:
        pass
    raise ValueError

def _pkc_extract_publickey_from_certificate(cert):
    try:
        tbscert, *_                     = asn1.asn1_parse_sequence(cert)
        _, _, _, _, _, _, pkinfo, *_    = asn1.asn1_parse_sequence(tbscert)
        alg, pkbits                     = asn1.asn1_parse_sequence(pkinfo)
        publickey       = asn1.asn1_parse_bitstring_as_octet_string(pkbits)
        _pkc_ensure_good_subject_public_key_algorithm(alg)
        _pkc_ensure_good_subject_public_key(publickey)
        return publickey
    except asn1.Asn1Error:
        pass
    except ValueError:
        pass
    raise PkcCertificateError

def _pkc_compress_publickey(publickey_bytes):
    try:
        Q = p256.E_from_bytes(publickey_bytes)
        return p256.E_to_bytes(Q, compressed=True)
    except p256.P256Error:
        pass
    raise PkcPublickeyError

def _pkc_verify_signature(publickey_bytes, message_bytes, signature_bytes):
    try:
        rr, ss = asn1.asn1_parse_sequence(signature_bytes)
        r = asn1.asn1_parse_integer(rr)
        s = asn1.asn1_parse_integer(ss)
    except asn1.Asn1Error:
        return False
    h = _hash_encode_an_octet_string_into_an_integer_modulo_q(message_bytes)
    Q = _decode_an_elliptic_curve_group_element(publickey_bytes)
    return p256.p256_validate_ecdsa_Q_h_r_s_quadruple(Q, h, r, s)

def _decode_an_elliptic_curve_group_element(pk):
    try:
        Q = p256.E_from_bytes(pk)
        return Q
    except p256.P256Error:
        pass
    raise PkcPublickeyError

def _hash_encode_an_octet_string_into_an_integer_modulo_q(msg):
    return _rfc6979_bits2int(_sha256(msg)) % p256.q

def _rfc6979_bits2int(octetstr):
    blen = len(octetstr) * 8
    qlen = 256
    x = _octets2int(octetstr)
    return (x >> (blen-qlen)) if (blen > qlen) else x

def _octets2int(z):
    return int.from_bytes(z, byteorder='big', signed=False)

def _sha256(msg_to_hash):
    import hashlib
    sha256_digester = hashlib.sha256()
    sha256_digester.update(msg_to_hash)
    return sha256_digester.digest()
