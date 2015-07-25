#!/usr/bin/env python3

def try_secp256r1_ecdsa_verifier():

    import secp256r1_ecdsa_verifier

    msg = b'sample'
    key = bytes.fromhex('0460fed4ba255a9d31c961eb74c6356d68c049b8923b61fa6ce669622e60f29fb67903fe1008b8bc99a41ae9e95628bc64f2f1b20c2d7e9f5177a3c294d4462299')
    sig = bytes.fromhex('3046022100efd48b2aacb6a8fd1140dd9cd45e81d69d2c877b56aaf991c34d0ea84eaf3716022100f7cb1c942d657c41d436c7a1b6e29f65f3e900dbb9aff4064dc4ab2f843acda8')

    try:
        sig_is_valid = secp256r1_ecdsa_verifier.verify(publickey=key,
                                                       signature=sig,
                                                       message=msg)
    except secp256r1_ecdsa_verifier.SigVerifyInputError:
        print('ERROR: Some input value is in an incorrect format')
        return False

    if sig_is_valid is True:
        print('DONE: The signature is valid')
    elif sig_is_valid is False:
        print('DONE: The signature is invalid')
    else:
        print('ERROR: Unexpected output from the verify() function')

if __name__ == '__main__':
    try_secp256r1_ecdsa_verifier()

