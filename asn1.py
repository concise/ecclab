NOT_A_PYTHON_BYTES = 'not a Python bytes object'
NOT_AN_ASN1_ENCODED = 'not an ASN.1 encoded result'
BAD_ASN1_OR_TOO_LONG = ('the ASN.1 encoded object has a value longer than '
                        '16 MiB or is corrupted')

def asn1_parse_sequence(stream):
    t, l, v = _asn1_parse_tlv(stream)
    if t != 0x30:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    # TODO repeatedly parse the substream `v` until the end
    raise NotImplementedError

def asn1_parse_integer(stream):
    t, l, v = _asn1_parse_tlv(stream)
    if t != 0x02:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    if l == 0:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    if l >= 2 and v[0] == 0x00 and v[1] == 0x00:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    intval = int.from_bytes(v, byteorder='big', signed=True)
    return intval

def _length_of_asn1_length_field(l):
    if type(l) is not int:
        assert False
    elif 0 <= l < 0x80:
        return 1
    elif l < 0x0100:
        return 2
    elif l < 0x010000:
        return 3
    elif l < 0x01000000:
        return 4
    else:
        assert False

def _asn1_parse_tlv(tlv):
    t, l, v, x = _asn1_parse_tlvx(tlv)
    if len(x) != 0:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    else:
        assert type(t) is int and 0 <= t <= 255
        assert type(l) is int and l >= 0
        assert type(v) is bytes and len(v) == l
        assert len(tlv) == 1 + _length_of_asn1_length_field(l) + l
        return t, l, v

def _asn1_parse_tlvx(tlvx):
    if type(tlvx) is not bytes:
        raise TypeError(NOT_A_PYTHON_BYTES)
    if len(tlvx) < 2:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    if tlvx[1] == 128:
        raise ValueError(NOT_AN_ASN1_ENCODED)
    t = tlvx[0]
    lvx = tlvx[1:]
    if lvx[0] <= 127:
        l, v, x = _asn1_parse_lvx_with_short_l(lvx)
    else:
        l, v, x = _asn1_parse_lvx_with_long_l(lvx)
    return t, l, v, x

def _asn1_parse_lvx_with_short_l(lvx):
    assert type(lvx) is bytes
    assert lvx[0] <= 127
    l = lvx[0]
    vx = lvx[1:]
    if len(vx) >= l:
        v, x = vx[:l], vx[l:]
        return l, v, x
    else:
        raise ValueError(NOT_AN_ASN1_ENCODED)

def _asn1_parse_lvx_with_long_l(lvx):
    assert type(lvx) is bytes
    assert lvx[0] >= 129
    if lvx[0] - 0x80 == 1:
        return _asn1_parse_lvx_with_2_l_octets(lvx)
    elif lvx[0] - 0x80 == 2:
        return _asn1_parse_lvx_with_3_l_octets(lvx)
    elif lvx[0] - 0x80 == 3:
        return _asn1_parse_lvx_with_4_l_octets(lvx)
    else:
        #
        # A shortest valid ASN.1 L-V octet string in this case will be:
        #
        # +------+------+------+------+------+-------------------------+
        # | 0x84 | 0x01 | 0x00 | 0x00 | 0x00 | ??????????????????????? |
        # +------+------+------+------+------+-------------------------+
        #                                         0x01000000 octets
        if len(lvx) < 5 + 0x01000000:
            raise ValueError(NOT_AN_ASN1_ENCODED)
        else:
            raise ValueError(BAD_ASN1_OR_TOO_LONG)

def _asn1_parse_lvx_with_2_l_octets(lvx):
    assert type(lvx) is bytes
    assert lvx[0] - 0x80 == 1
    l = int.from_bytes(lvx[1:2], byteorder='big')
    vx = lvx[2:]
    if 0x80 <= l <= 0xff and len(vx) >= l:
        v, x = vx[:l], vx[l:]
        return l, v, x
    else:
        raise ValueError(NOT_AN_ASN1_ENCODED)

def _asn1_parse_lvx_with_3_l_octets(lvx):
    assert type(lvx) is bytes
    assert lvx[0] - 0x80 == 2
    l = int.from_bytes(lvx[1:3], byteorder='big')
    vx = lvx[3:]
    if 0x0100 <= l <= 0xffff and len(vx) >= l:
        v, x = vx[:l], vx[l:]
        return l, v, x
    else:
        raise ValueError(NOT_AN_ASN1_ENCODED)

def _asn1_parse_lvx_with_4_l_octets(lvx):
    assert type(lvx) is bytes
    assert lvx[0] - 0x80 == 3
    l = int.from_bytes(lvx[1:4], byteorder='big')
    vx = lvx[4:]
    if 0x010000 <= l <= 0xffffff and len(vx) == l:
        v, x = vx[:l], vx[l:]
        return l, v, x
    else:
        raise ValueError(NOT_AN_ASN1_ENCODED)
