# Starling CAI

## CAI-Tool use

### Running CAI-Tool

In command line run: 

```
python cai/starling.py [-a ASSERTION] [--store-label STORE_LABEL] [--recorder RECORDER] [-k KEY] [-s SIG] [-o OUTPUT] [-i INJECT]
```

## Signature Verification

Current version of CAI-Tool has two signature implementations `cms` and `endesive`. 

`cms` signature implementation outputs a 256-byte binary blob that is a raw style SHA-style signature. It is advised to not use `cms` for cai signature.

`endesive` signature implementation is a CADES-B signature with DER encoding. It is currently advised to use `endesive` to sign CAI injected images.

### Generating Certificate and Private Key

Please run the following to generate certificate and private key for `endesive` signature.

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 7
```

Generate pkcs12

```
openssl pkcs12 -export -out <filename>.p12 -inkey key.pem -in cert.pem 
```

Remove password for pkcs12

```
# Export to temporary pem file
openssl pkcs12 -in protected.p12 -nodes -out temp.pem
#  -> Enter password

# Convert pem back to p12
openssl pkcs12 -export -in temp.pem  -out unprotected.p12
# -> Just press [return] twice for no password

# Remove temporary certificate
rm temp.pem

```

Generate crt.pem for verification purposes

```
openssl pkcs12 -in <filename>.p12 -out <filename>crt.pem -clcerts -nokeys
```