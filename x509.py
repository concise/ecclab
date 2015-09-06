import asn1
import fast_secp256r1

class X509Error(BaseException):
    pass

def ecdsa_extract_publickey_octetstring_from_certificate(certificate):
    try:
        tbscert, _, _ = asn1.parse_ASN1_SEQUENCE(certificate)
        _, _, _, _, _, _, pk_info, *_ = asn1.parse_ASN1_SEQUENCE(tbscert)
        alg, pk_bits = asn1.parse_ASN1_SEQUENCE(pk_info)
        pk_octets = asn1.parse_ASN1_BITSTRING_as_octet_string(pk_bits)
        ensure_good_subjectpublickeyinfo_algorithm_field_(alg)
        ensure_good_ecdsa_publickey_(pk_octets)
        return pk_octets
    except asn1.ASN1Error:
        pass
    except ValueError:
        pass
    raise X509Error

def ensure_good_subjectpublickeyinfo_algorithm_field_(alg):
    if alg == bytes.fromhex('301306072a8648ce3d020106082a8648ce3d030107'):
        return
    raise X509Error

def ensure_good_ecdsa_publickey_(pk_octets):
    try:
        p = fast_secp256r1.point_from_octetstring(pk_octets)
        if p is not fast_secp256r1.O:
            return
    except ValueError:
        pass
    raise X509Error
