from P256 import q
from ECGroup import (E, E_from_bytes, E_to_bytes, E_contains, E_take_x_mod_q,
                     E_eq, E_neg, E_dbl, E_add, E_mul, E_InputError)

Z = E(0) # the point at infinity (additive identity) of group E
G = E(1) # the base point that generates the cyclic group E

def verify(publickey, signature, message):
    Q    = _decode_a_public_key_point_from_an_octet_string(publickey)
    r, s = _decode_a_signature_from_an_octet_string(signature)
    h    = _hash_encode_an_octet_string_into_an_integer_modulo_q(message)
    return _is_valid_Q_h_r_s_ecdsa_quadruple(Q, h, r, s)

def extract_an_ecdsa_public_key_octets_from_an_x509_certificate(stream):
    raise NotImplementedError # TODO

def _is_valid_Q_h_r_s_ecdsa_quadruple(Q, h, r, s):
    raise NotImplementedError # TODO

def _decode_a_public_key_point_from_an_octet_string(pk):
    raise NotImplementedError # TODO

def _decode_a_signature_from_an_octet_string(sig):
    raise NotImplementedError # TODO

def _hash_encode_an_octet_string_into_an_integer_modulo_q(msg):
    raise NotImplementedError # TODO
