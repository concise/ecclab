class Asn1Error(BaseException):
    pass

class Asn1NotImplementedError(Asn1Error, NotImplementedError):
    pass

class Asn1TypeError(Asn1Error, TypeError):
    pass

class Asn1ValueError(Asn1Error, ValueError):
    pass

def asn1_parse_integer(octetstring):
    """
    return an signed integer encoded in this ASN.1 INTEGER
    """
    if type(octetstring) is not bytes:
        raise Asn1TypeError
    return _asn1_parse_integer(octetstring)

def asn1_parse_bitstring(octetstring, as_octet_string=True):
    """
    return an octet string encoded in this ASN.1 BIT STRING
    """
    if as_octet_string is True:
        if type(octetstring) is not bytes:
            raise Asn1TypeError
        return _asn1_parse_bitstring(octetstring)
    else:
        raise Asn1NotImplementedError

def asn1_parse_sequence(octetstring):
    """
    return a sequence of octet strings encoded in this ASN.1 SEQUENCE
    """
    if type(octetstring) is not bytes:
        raise Asn1TypeError
    return _asn1_parse_sequence(octetstring)

def _asn1_parse_integer(octetstring_bytes):
    T, L, V, X = _asn1_extract_T_L_V_X_from(octetstring_bytes)
    assert _asn1_L_value(L) == len(V)
    if len(X) != 0:
        raise Asn1ValueError
    if T != b'\x02':
        raise Asn1ValueError
    if L >= 2 and V[0] == 0x00 and V[1] <= 0x7f:
        raise Asn1ValueError
    return int.from_bytes(V, byteorder='big', signed=True)

def _asn1_parse_bitstring(octetstring_bytes):
    T, L, V, X = _asn1_extract_T_L_V_X_from(octetstring_bytes)
    assert _asn1_L_value(L) == len(V)
    if len(X) != 0:
        raise Asn1ValueError
    if T != b'\x03':
        raise Asn1ValueError
    if V[0] != 0x00:
        raise Asn1ValueError
    return V[1:]

def _asn1_parse_sequence(octetstring_bytes):
    T, L, V, X = _asn1_extract_T_L_V_X_from(octetstring_bytes)
    assert _asn1_L_value(L) == len(V)
    if len(X) != 0:
        raise Asn1ValueError
    if T != b'\x30':
        raise Asn1ValueError
    items = ()
    X = V
    while len(X) != 0:
        T, L, V, X = _asn1_extract_T_L_V_X_from(X)
        items += (T + L + V,)
    return items

def _asn1_extract_T_L_V_X_from(stream):
    X = stream
    T, X = _asn1_extract_T_from(X)
    L, X = _asn1_extract_L_from(X)
    V, X = _asn1_extract_V_from(X, length=_asn1_L_value(L))
    return T, L, V, X

def _asn1_L_value(L):
    if len(L) == 0:
        raise Asn1ValueError
    elif len(L) == 1 and L[0] <= 0x7f:
        return L[0]
    elif len(L) == 2 and L[0] == 0x81 and L[1] >= 0x80:
        return L[1]
    elif len(L) == L[0] - 0x7f and L[0] >= 0x82 and L[1] != 0x00:
        return int.from_bytes(L[1:], byteorder='big', signed=False)
    else:
        raise Asn1ValueError

def _asn1_extract_T_from(stream):
    if len(stream) == 0:
        raise Asn1ValueError
    return stream[:1], stream[1:]

def _asn1_extract_L_from(stream):
    if len(stream) == 0:
        raise Asn1ValueError
    if stream[0] == 0x80:
        raise Asn1ValueError
    elif stream[0] <= 0x7f:
        return stream[:1], stream[1:]
    else:
        return _asn1_extract_long_L_from(stream)

def _asn1_extract_long_L_from(stream):
    length = stream[0] - 0x7f
    if len(stream) < length:
        raise Asn1ValueError
    L, _ = stream[:length], stream[length:]
    if (length == 2 and L[1] >= 0x80) or L[1] != 0x00:
        return L, _
    else:
        raise Asn1ValueError

def _asn1_extract_V_from(stream, length):
    if len(stream) < length:
        raise Asn1ValueError
    return stream[:length], stream[length:]
