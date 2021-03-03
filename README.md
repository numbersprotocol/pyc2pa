# Starling CAI

## CAI-Tool use

### Running CAI-Tool

In command line run: 

`python cai/starling.py [-a ASSERTION] [--store-label STORE_LABEL] [--recorder RECORDER] [-k KEY] [-s SIG] [-o OUTPUT] [-i INJECT]`

## Signature Verification

Current version of CAI-Tool has two signature implementations `cms` and `endesive`. 

`cms` signature implementation outputs a 256-byte binary blob that is a raw style SHA-style signature. It is advised to not use `cms` for cai signature.

`endesive` signature implementation is a CADES-B signature with DER encoding. It is currently advised to use `endesive` to sign CAI injected images.

### Generating Certificate and Private Key

Please run the following to generate certificate and private key for `endesive` signature.

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

Generate pkcs12

```
openssl pkcs12 -export -out certificate.p12 -inkey key.pem -in cert.pem 
```

For the current implementation please set password/pin to `1234`