from endesive import plain

def main():
    trusted_cert_pems = (open('demo2_ca.crt.pem', 'rt').read(),)
    unsigned = open('plain-unsigned.txt', 'rb').read()

    fname = 'plain-signed-attr.txt'
    signed = open(fname, 'rb').read()

    (hashok, signatureok, certok) = plain.verify(signed, unsigned, trusted_cert_pems)

    print('signature ok?', signatureok)
    print('hash ok?', hashok)

if __name__ == "__main__":
    main()