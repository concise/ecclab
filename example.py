#!/usr/bin/env python3

import secp256r1

key = bytes.fromhex('0460fed4ba255a9d31c961eb74c6356d68c049b8923b61fa6ce669622e60f29fb67903fe1008b8bc99a41ae9e95628bc64f2f1b20c2d7e9f5177a3c294d4462299')
msg = bytes.fromhex('73616d706c65')
sig = bytes.fromhex('3046022100efd48b2aacb6a8fd1140dd9cd45e81d69d2c877b56aaf991c34d0ea84eaf3716022100f7cb1c942d657c41d436c7a1b6e29f65f3e900dbb9aff4064dc4ab2f843acda8')

try:
    sig_is_valid = secp256r1.ecdsa_verify_signature(key, msg, sig)
    if sig_is_valid is True:
        print('the signature is valid')
    else:
        print('the signature is invalid')
except secp256r1.ecdsa_Error:
    print('ERROR: the provided public key is incorrect')
