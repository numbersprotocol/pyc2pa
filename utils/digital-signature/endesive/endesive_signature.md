## Generating Endesive Signatures

 CAI Technical Spec mentions signing is done by hashing Claim JSON and doing CADES-B signature.

 ### General p12 and cert.pem

 1. Generate Public and Private Key with the following:
 
        openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 7
        openssl pkcs12 -export -out <filename>.p12 -inkey key.pem -in cert.pem

    Output will be the following:

    ```
    <filename>.p12
    ```

2. Generate certificate for verification with the following:

       openssl pkcs12 -in <filename>.p12 -out <filename>crt.pem -clcerts -nokeys

    Output will be the following:

        <filename>.crt.pem

3. Generate Signature with:

       python endesive-sign.py -s <p12> <claim JSON> <name of signature file.der>

4. Verify Signature with:

       python endesive-sign.py -v <crt.pem> <claim JSON> <signature file .der>

### Sample Usage:

```
# claim json : starling.claim.json

# Generate p12 
# Will output file certificate.p12 (will be used to generate signature). set pass to 1234
$ openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 7
$ openssl pkcs12 -export -out certificate.p12 -inkey key.pem -in cert.pem

# Generate crt.pem
# Will output file certificate.crt.pem (will be used to verify signed) 
$ openssl pkcs12 -in certificate.p12 -out certificate.crt.pem -clcerts -nokeys


# Usage:
# Generating Signature:
$ python endesive-sign.py -s certificate.p12 starling.claim.json starling.der
Generating Signature

# Verifying Signature:
$ python endesive-sign.py -v certificate.crt.pem starling.claim.json starling.der
Verifying Signature
signature ok? True
hash ok? True
cert ok? True
```

### Verifying using Adobe's Methodology

**Requirements**
- Extracted CMS signature to starling.der
- Extracted claim JSON to starling.claim.json (exact byte sequence inserted into image)

```
# Convert signature from DER to PEM encoding:
$ openssl pkcs7 -inform der -in starling.der -out starling.der.pkcs7

# Extract X.509 certificates from signature:
$ openssl pkcs7 -print_certs -in starling.der.pkcs7 -out starling.der.cert

# Verify CMS signature against detached data (claim):
$ openssl smime -verify -binary -inform der -in starling.der -content starling.claim.json -certfile starling.der.cert -noverify
{
    "assertions": [
        "self#jumbf=cai/cb.starling_1/cai.assertions/starling.location.precise?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMoBUAVbTEB7K",
        "self#jumbf=cai/cb.starling_1/cai.assertions/starling.sensors?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMvY4QFEN3973",
        "self#jumbf=cai/cb.starling_1/cai.assertions/starling.device?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMwEoBojZcUrZ",
        "self#jumbf=cai/cb.starling_1/cai.assertions/starling.integrity?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMo3SG72sZg13"
    ],
    "asset_hashes": [
        {
            "start": "0x0000000000000000",
            "length": "0x0000000000009959",
            "name": "JFIF SOI-APP0",
            "url": "",
            "value": "EiAuxjtmax46cC2N3Y9aFmBO9Jfay8LEwJWzBUtZ0sUM8gA="
        },
        {
            "start": "0x0000000000009959",
            "length": "0x000000000000027d",
            "name": "JFIF APP1/XMP",
            "url": "",
            "value": "EiDjZifCgG2iKxcYeChKTOcWlJ9I/UC9/c5XFiJREqJFpwA="
        },
        {
            "start": "0x000000000000a90c",
            "length": "0x00000000000215e6",
            "name": "JFIF DQT-EOI",
            "url": "",
            "value": "EiArx031oA0N5KOEG6n9R/bJJFYJvmGlDoLtuwbRipLTKAA="
        }
    ],
    "recorder": "Starling Capture",
    "signature": "self#jumbf=cai/cb.starling_1/cai.signature"
Verification successful

```

### Verifying signature from CAI file Tutorial

1. Prepare p12 certificate

    **with password**

       openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 7
       openssl pkcs12 -export -out <filename>.p12 -inkey key.pem -in cert.pem

    **remove password**

       ```
       # Export pkcs12 to pem
       $ openssl pkcs12 -in <filename>.p12 -nodes -out temp.pem
       Enter Import Password:
       MAC verified OK

       # convert pem back to p12 w/ no password (press space twice when prompted password)
       $ openssl pkcs12 -export -in temp.pem  -out <filename>.p12
       Enter Export Password:
       Verifying - Enter Export Password:

       #  remove temp certfiicate
       $ rm temp.pem
       ```

2. Generate Certificate for verification

       openssl pkcs12 -in <filename>.p12 -out <filename>crt.pem -clcerts -nokeys

3. Create CAI-Injected Photo

    Add `p12` & `crt.pem` and run script `./run.sh <jpg filename>`

    You will get CAI-injected photo `filename-cai.jpg>`

4. Get exact byte sequence of `claim JSON` and extract signature to `signature.der`

    The `Claim JSON` has to be compact format (`jq . -c <claim-json>`) without EOL (`0x0a`).
    
    You can check by `xxd <claim-json>`.

5. Run verification w/script

       python endesive-sign.py -v <filename>.crt.pem <claim json> signature.der

    Output

       Verifying Signature
       signature ok? True
       hash ok? True
       cert ok? True

6. Run verification (Adobe Method)

       openssl pkcs7 -inform der -in signature.der -out signature.der.pkcs7

       openssl pkcs7 -print_certs -in signature.der.pkcs7 -out signature.der.cert

       openssl smime -verify -binary -inform der -in signature.der -content <claim json> -certfile signature.der.cert -noverify
