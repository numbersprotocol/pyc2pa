from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from endesive import plain


def main():
    with open('demo2_user1.p12', 'rb') as fp:
        p12 = pkcs12.load_key_and_certificates(fp.read(), b'1234', backends.default_backend())
    unsigned = open('plain-unsigned.txt', 'rb').read()
    signed = plain.sign(unsigned,
        p12[0], p12[1], p12[2],
        'sha256',
        attrs=True
    )
    open('plain-signed-attr.txt', 'wb').write(signed)


main()