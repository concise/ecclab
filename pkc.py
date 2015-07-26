class PkcError(BaseException):
    pass

class PkcTypeError(PkcError, TypeError):
    pass

class PkcCertificateError(PkcError, ValueError):
    pass

class PkcPublickeyError(PkcError, ValueError):
    pass

def pkc_extract_publickey_from_certificate(certificate):
    if type(certificate) is not bytes:
        raise PkcTypeError
    return _pkc_extract_publickey_from_certificate(certificate)

def pkc_compress_publickey(publickey):
    if type(publickey) is not bytes:
        raise PkcTypeError
    return _pkc_compress_publickey(publickey)

def pkc_verify_signature(publickey, message, signature):
    if (type(publickey) is not bytes or type(message) is not bytes
    or type(signature) is not bytes):
        raise PkcTypeError
    return _pkc_verify_signature(publickey, message, signature)

def _pkc_extract_publickey_from_certificate(certificate_bytes):
    pass # TODO

def _pkc_compress_publickey(publickey_bytes):
    pass # TODO

def _pkc_verify_signature(publickey_bytes, message_bytes, signature_bytes):
    pass # TODO
