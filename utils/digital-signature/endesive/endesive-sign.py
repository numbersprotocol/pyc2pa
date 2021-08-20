import sys
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from endesive import plain

def usage():
    print("Usage: \n"
            "endesive-sig -s <p12> <unsigned claim> <signed> \n"
            "endesive-verify -v <crt.pem> <unsigned claim> <signed> \n")

if (len(sys.argv) < 5):
    usage()
    quit()

op = sys.argv[1]
key_f = sys.argv[2]
data_f = sys.argv[3]
sign_f = sys.argv[4]

def generate_signature(key, data, signed):
    print("Generating Signature")
    with open(key, 'rb') as fp:
        p12 = pkcs12.load_key_and_certificates(fp.read(), b'1234', backends.default_backend())
    datau = open(data, 'rb').read()
    datas = plain.sign(datau,
        p12[0], p12[1], p12[2],
        'sha256',
        attrs=True
    )
    open(signed, 'wb').write(datas)

def verfy_signature(key, data, signed):
    print("Verifying Signature")
    trusted_cert_pems = (open(key, 'rt').read(),)
    datau = open(data, 'rb').read()
    datas = open(signed, 'rb').read()
    (hashok, signatureok, certok) = plain.verify(datas, datau, trusted_cert_pems)
    print('signature ok?', signatureok)
    print('hash ok?', hashok)
    print('cert ok?', certok)

def main():
    
    if (op == '-s'):
        # Generate Signature
        generate_signature(key_f, data_f, sign_f)

    elif (op == '-v'):
        # Verify Signature
        verfy_signature(key_f, data_f, sign_f)
    else:
        usage()


if __name__ == "__main__":
    main()