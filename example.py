#!/usr/bin/env python3

def bytes_tohex(i):
    import codecs
    return codecs.encode(i, 'hex').decode()

def test_get_pk_from_cert():
    print('----- test_get_pk_from_cert() starts -----')
    import secp256r1
    cert = bytes.fromhex('3082013c3081e4a003020102020a47901280001155957352300a06082a8648ce3d0403023017311530130603550403130c476e756262792050696c6f74301e170d3132303831343138323933325a170d3133303831343138323933325a3031312f302d0603550403132650696c6f74476e756262792d302e342e312d34373930313238303030313135353935373335323059301306072a8648ce3d020106082a8648ce3d030107034200048d617e65c9508e64bcc5673ac82a6799da3c1446682c258c463fffdf58dfd2fa3e6c378b53d795c4a4dffb4199edd7862f23abaf0203b4b8911ba0569994e101300a06082a8648ce3d0403020347003044022060cdb6061e9c22262d1aac1d96d8c70829b2366531dda268832cb836bcd30dfa0220631b1459f09e6330055722c8d89b7f48883b9089b88d60d1d9795902b30410df')
    try:
        pk = secp256r1.ecdsa_extract_publickey_octetstring_from_certificate(cert)
        pk_uncompressed = secp256r1.ecdsa_decompress_publickey(pk)
        pk_compressed   = secp256r1.ecdsa_compress_publickey(pk)
        print('An secp256r1 ECDSA public key is extracted from the certificate:')
        print('in the uncompressed form:')
        print(bytes_tohex(pk_uncompressed))
        print('in the compressed form:')
        print(bytes_tohex(pk_compressed))
        print('----- test_get_pk_from_cert() done -----')
    except secp256r1.ecdsa_Error:
        print('ERROR: the input is not a valid X.509 version 3 certificate with a secp256r1 public key')
        print('----- test_get_pk_from_cert() failed -----')

def test_perform_signature_verification():
    print('----- test_perform_signature_verification() starts -----')
    import secp256r1
    key = bytes.fromhex('0460fed4ba255a9d31c961eb74c6356d68c049b8923b61fa6ce669622e60f29fb67903fe1008b8bc99a41ae9e95628bc64f2f1b20c2d7e9f5177a3c294d4462299')
    msg = bytes.fromhex('73616d706c65')
    sig = bytes.fromhex('3046022100efd48b2aacb6a8fd1140dd9cd45e81d69d2c877b56aaf991c34d0ea84eaf3716022100f7cb1c942d657c41d436c7a1b6e29f65f3e900dbb9aff4064dc4ab2f843acda8')
    try:
        sig_is_valid = secp256r1.ecdsa_verify_signature(key, msg, sig)
        if sig_is_valid is True:
            print('The signature is valid')
        else:
            print('The signature is invalid')
        print('----- test_perform_signature_verification() done -----')
    except secp256r1.ecdsa_Error:
        print('ERROR: the input cannot be recognized as a valid secp256r1 public key EC point')
        print('----- test_perform_signature_verification() failed -----')

if __name__ == '__main__':
    test_get_pk_from_cert()
    test_perform_signature_verification()
