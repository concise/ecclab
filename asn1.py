NOT_A_PYTHON_BYTES = 'not a Python bytes object'
NOT_AN_ASN1_ENCODED = 'not an ASN.1 encoded result'
BAD_ASN1_OR_TOO_LONG = ('the ASN.1 encoded object has a value longer than '
                        '16 MiB or is corrupted')

def parse_asn1_sequence(stream):
    """
    parse_asn1_sequence parses an octet string as an ASN.1 encoded T-L-V
    triple just as what parse_asn1_anything does, but the V will be replaced
    with a tuple of bytes representing the ordered sequence in the provided
    ASN.1 SEQUENCE value.
    """
    raise NotImplementedError # TODO

def parse_asn1_integer(stream):
    """
    parse_asn1_integer parses an octet string as an ASN.1 encoded T-L-V triple
    just as what parse_asn1_anything does, but the V will be replaced with an
    int representing the signed integer value of the provided ASN.1 INTEGER.
    """
    raise NotImplementedError # TODO

def parse_asn1_anything(tlv):
    """
    parse_asn1_anything parses an octet string as an ASN.1 encoded T-L-V
    triple.

    Input data type:    tlv should be a bytes
    Output data types:  a tuple of three objects T, L, and V,
                        where T and L is an int and V is a bytes
    """
    if type(tlv) is not bytes:
        raise TypeError(NOT_A_PYTHON_BYTES)
    if len(tlv) < 2:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    if tlv[1] == 128:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    t = tlv[0]
    lv = tlv[1:]
    if lv[0] <= 127:
        l, v = parse_asn1_length_value_pair_with_short_length(lv)
    else:
        l, v = parse_asn1_length_value_pair_with_long_length(lv)
    return t, l, v

def parse_asn1_length_value_pair_with_short_length(lv):
    assert type(lv) is bytes
    assert lv[0] <= 127
    l = lv[0]
    v = lv[1:]
    if len(v) == l:
        return l, v
    else
        raise ValueError(NOT_AN_ASN1_ENCODED)

def parse_asn1_length_value_pair_with_long_length(lv):
    assert type(lv) is bytes
    assert lv[0] >= 129
    if lv[0] - 0x80 == 1:
        return parse_asn1_length_value_pair_with_2_length_octets(lv)
    elif lv[0] - 0x80 == 2:
        return parse_asn1_length_value_pair_with_3_length_octets(lv)
    elif lv[0] - 0x80 == 3:
        return parse_asn1_length_value_pair_with_4_length_octets(lv)
    else:
        #
        # A shortest valid ASN.1 L-V octet string in this case will be:
        #
        # +------+------+------+------+------+-------------------------+
        # | 0x84 | 0x01 | 0x00 | 0x00 | 0x00 | ??????????????????????? |
        # +------+------+------+------+------+-------------------------+
        #                                         0x01000000 octets
        if len(lv) < 5 + 0x01000000:
            raise ValueError(NOT_AN_ASN1_ENCODED)
        else:
            raise ValueError(BAD_ASN1_OR_TOO_LONG)

def parse_asn1_length_value_pair_with_2_length_octets(lv):
    assert type(lv) is bytes
    assert lv[0] - 0x80 = 1
    l = int.from_bytes(lv[1:2], byteorder='big')
    v = lv[2:]
    if 0x80 <= l <= 0xff and len(v) == l:
        return l, v
    else:
        raise ValueError(NOT_AN_ASN1_ENCODED)

def parse_asn1_length_value_pair_with_3_length_octets(lv):
    assert type(lv) is bytes
    assert lv[0] - 0x80 = 2
    l = int.from_bytes(lv[1:3], byteorder='big')
    v = lv[3:]
    if 0x0100 <= l <= 0xffff and len(v) == l:
        return l, v
    else:
        raise ValueError(NOT_AN_ASN1_ENCODED)

def parse_asn1_length_value_pair_with_4_length_octets(lv):
    assert type(lv) is bytes
    assert lv[0] - 0x80 = 3
    l = int.from_bytes(lv[1:4], byteorder='big')
    v = lv[4:]
    if 0x010000 <= l <= 0xffffff and len(v) == l:
        return l, v
    else:
        raise ValueError(NOT_AN_ASN1_ENCODED)
