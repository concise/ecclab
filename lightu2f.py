#!/usr/bin/env python3

class U2FException(BaseException):
    pass

# Request
# construct_registration_request(
#   Token[] registered_tokens // only need key handles
#   ) throws U2FException;
def construct_registration_request():
    pass

# Pair<Token, TokenAttestationCertificate>
# process_registration_response(
#   Request req,
#   Response res
#   ) throws U2FException;
def process_registration_response():
    pass

# Request
# construct_authentication_request(
#   Token[] registered_tokens // only need key handles
#   ) throws U2FException;
def construct_authentication_request():
    pass

# Pair<ListIndex, TokenAuthenticationCounter>[]
# process_authentication_response(
#   Token[] registered_tokens, // need key handles and public keys
#   Request req,
#   Response res
#   ) throws U2FException:
def process_authentication_response():
    pass

######################################################################

def get_cmdline_args():
    import sys
    return sys.argv[1:]

def read_from_stdin():
    import sys
    octets = sys.stdin.buffer.read()
    return octets

def write_to_stdout(octets):
    import sys
    sys.stdout.buffer.write(octets)

def reg_init(input_data):
    pass # TODO

def reg_end(input_data):
    pass # TODO

def auth_init(input_data):
    pass # TODO

def auth_end(input_data):
    pass # TODO

def choose_task_by_args(args):
    if args == ['reg_init']:
        return reg_init
    elif args == ['reg_end']:
        return reg_end
    elif args == ['auth_init']:
        return auth_init
    elif args == ['auth_end']:
        return auth_end
    else:
        return lambda _: b'{"error":"invalid cmdline argument","result":null}'

def main():
    args = get_cmdline_args()
    input_data = read_from_stdin()
    output_data = choose_task_by_args(args)(input_data)
    return output_data

if __name__ == '__main__':
    main()

'''

./lightu2f.py reg_init

    INPUT: a list of token key handles
    OUTPUT: a request dictionary for u2f client javascript api
    EXCEPTIONS:

        1.  input type checking

            * check if the input is in a correct format
            * here the input should be a list of octet strings
            * if the input is in an incorrect format, raise an error

        2.  input validation

            * check if the input data is well formed
            * here, each element in the list should be an octet string that
              consists of two parts, one for the public key and another for
              the key hadnle
            * if the input is ill-formed, raise an error

        3.  construct a request dictionary for the u2f client javascript api

            *

./lightu2f.py reg_end

    INPUT: a request dictionary for u2f client javascript api
           a response dictionary from u2f client javascript api
    OUTPUT: a key handle and a public key
            a u2f token attestation certificate
    EXCEPTIONS:

./lightu2f.py auth_init

    INPUT: a list of token key handles
    OUTPUT: a request dictionary for u2f client javascript api
    EXCEPTIONS:

./lightu2f.py auth_end

    INPUT: a list of token key handles and public keys
           a request dictionary for u2f client javascript api
           a response dictionary from u2f client javascript api
    OUTPUT: a list index indicating which token in the provided list is used
            a 4-byte authentication counter
    EXCEPTIONS:

'''
