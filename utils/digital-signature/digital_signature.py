import sys
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5


def usage():
    print("Usage: \n"
            "digi-sig -s  <priv-key> <data> <signature-file> \n"
            "digi-sig -v  <PUB-key> <data> <signature-file> \n")


if (len(sys.argv) < 5):
    usage()
    quit()

op = sys.argv[1]
key_f = sys.argv[2]
data_f = sys.argv[3]
sig_f = sys.argv[4]


def generate_signature(key, data, sig_f):
    print("Generating Signature")
    h = SHA256.new(data)
    rsa = RSA.importKey(key)
    signer = PKCS1_v1_5.new(rsa)
    signature = signer.sign(h)
    with open(sig_f, 'wb') as f: f.write(signature)


def verify_signature(key, data, sig_f):
    print("Verifying Signature")
    h = SHA256.new(data)
    rsa = RSA.importKey(key)
    signer = PKCS1_v1_5.new(rsa)
    with open(sig_f, 'rb') as f: signature = f.read()

    if (signer.verify(h, signature)):
        rsp = 'Success'
    else:
        rsp = 'Failure'
    print(rsp)


def main():
    # Read all file contents
    with open(key_f, 'rb') as f: key = f.read()
    with open(data_f, 'rb') as f: data = f.read()

    if (op == "-s"):
        # Generate Signature
        generate_signature(key, data, sig_f)
    elif (op == "-v"):
        # Verify Signature
        verify_signature(key, data, sig_f)
    else:
        #Error
        usage()


if __name__ == "__main__":
    main()