class PkcError(BaseException):
    pass

class PkcTypeError(TypeError, PkcError):
    pass

class PkcCertificateError(ValueError, PkcError):
    pass

class PkcPublickeyError(ValueError, PkcError):
    pass

def pkc_extract_publickey_from_certificate(certificate):
    if type(certificate) is bytes:
        return _pkc_extract_publickey_from_certificate(certificate)
    else:
        raise PkcTypeError

def pkc_compress_publickey(publickey):
    if type(publickey) is bytes:
        return _pkc_compress_publickey(publickey)
    else:
        raise PkcTypeError

def pkc_verify_signature(publickey, message, signatures):
    if (type(publickey) is bytes and type(message) is bytes
    and type(signatures) is bytes):
        return _pkc_verify_signature(publickey, message, signatures)
    else:
        raise PkcTypeError

def _pkc_extract_publickey_from_certificate(certificate_bytes):
    pass

def _pkc_compress_publickey(publickey_bytes):
    pass

def _pkc_verify_signature(publickey_bytes, message_bytes, signatures_bytes):
    pass
