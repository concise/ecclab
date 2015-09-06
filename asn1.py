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
    return int.from_bytes(V, byteorder='big', signed=True)

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
        return int.from_bytes(L[1:], byteorder='big', signed=False)
    else:
        raise ASN1Error
