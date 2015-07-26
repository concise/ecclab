def asn1_parse_one_SEQUENCE(stream):
    T, L, V, X = extract_T_L_V_X_from(stream)
    assert value_of_L(L) == len(V)
    if len(X) != 0:
        raise ValueError
    if T != b'\x30':
        raise ValueError

    items = ()
    X = V
    while len(X) != 0:
        T, L, V, X = extract_T_L_V_X_from(X)
        items += (T + L + V,)
    return items

def asn1_parse_one_INTEGER(stream):
    T, L, V, X = extract_T_L_V_X_from(stream)
    assert value_of_L(L) == len(V)
    if len(X) != 0:
        raise ValueError
    if T != b'\x02':
        raise ValueError
    if L >= 2 and V[0] == 0x00 and V[1] <= 0x7f:
        raise ValueError
    return int.from_bytes(V, byteorder='big', signed=True)

# ----------------------------------------------------------------------------

def extract_T_L_V_X_from(stream):
    X = stream
    T, X = extract_T_from(X)
    L, X = extract_L_from(X)
    V, X = extract_V_from(X, length=value_of_L(L))
    return T, L, V, X

def extract_T_from(stream):
    if type(stream) is bytes:
        if len(stream) >= 1:
            T, _ = stream[:1], stream[1:]
            return T, _
        else:
            raise ValueError
    else:
        raise TypeError

def extract_L_from(stream):
    if type(stream) is bytes:
        if len(stream) >= 1:
            leading_octet_value = stream[0]
            if leading_octet_value <= 0x7f:
                L, _ = stream[:1], stream[1:]
                return L, _
            elif leading_octet_value == 0x80:
                raise ValueError
            else:
                return extract_long_L_from(stream)
        else:
            raise ValueError
    else:
        raise TypeError

def extract_V_from(stream, length):
    if type(stream) is bytes:
        if len(stream) >= length:
            V, _ = stream[:length], stream[length:]
            return V, _
        else:
            raise TypeError
    else:
        raise TypeError

def value_of_L(L):
    if type(L) is not bytes:
        raise TypeError
    if len(L) == 0:
        raise ValueError
    if L[0] <= 0x7f and len(L) == 1:
        return L[0]
    elif L[0] == 0x81 and len(L) == 2 and L[1] >= 0x80:
        return L[1]
    elif L[0] >= 0x82 and len(L) == L[0] - 0x7f and L[1] != 0x00:
        return int.from_bytes(L[1:], byteorder='big', signed=False)
    else:
        raise ValueError

# ----------------------------------------------------------------------------

def extract_long_L_from(stream):
    assert type(stream) is bytes
    assert len(stream) >= 1
    assert stream[0] >= 0x81
    length_of_L = stream[0] - 0x7f
    if len(stream) < length_of_L:
        raise ValueError
    L, _ = stream[:length_of_L], stream[length_of_L:]
    if (length_of_L == 2 and L[1] >= 0x80) or L[1] >= 0x00:
        value_of_L(L) # MUST NOT raise any exception here
        return L, _
    else:
        raise ValueError
