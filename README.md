# PyC2PA

![c2pa-concept-full](https://user-images.githubusercontent.com/292790/131808157-0ca62a79-c2f4-4e1d-b8b9-ef027476f4b0.jpg)
(photo source: C2PA)

PyC2PA is Python implementation of [C2PA](https://c2pa.org/) (Coalition for Content Provenance and Authenticity) addressing the prevalence of misleading information online through the development of technical standards for certifying the source and history (or provenance) of media content.
The latest tool can be checked in [C2PA tool (Command Line Interface)](https://github.com/contentauth/c2patool).

## Quick Trial

1. Download the testing photo: [meimei-fried-chicken-cai-cai-cai.jpg](https://user-images.githubusercontent.com/17119193/145776913-cfe4de41-7f58-482e-b732-9aeb00c477bb.jpg)
1. Go to the [CAI beta verification website](https://verify-beta.contentauthenticity.org/inspect) and upload the photo.
1. You should see the C2PA information (3 injections) like this:

    ![cai-verify-example](https://user-images.githubusercontent.com/17119193/145777230-778ffff0-109d-470b-b0c3-6152bd63f8cb.png)

## Installation

```
$ sudo apt install swig
$ python3 -m pip install c2pa
```

## C2PA CLI

In command line run:

```
$ c2pa [-h] [-a ASSERTION] [--provider PROVIDER] [--recorder RECORDER] [-k KEY] [-c CERT] [-i INJECT] [-d]
```

### Example

Files used in the following examples are provided in [example.zip](https://github.com/numbersprotocol/pyc2pa/files/7702158/example.zip)

```
$ unzip example.zip
$ cd example
```

Generate private key and certificate.

```
$ openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Generate thumbnail image.

```
$ convert -resize 1024x768 meimei-fried-chicken.jpg c2pa.thumbnail.claim.jpeg.jpg
```

Generate meimei-fried-chicken-cai.jpg containing single C2PA injection.

```
$ c2pa \
    -a stds.schema-org.CreativeWork.json \
    -a c2pa.thumbnail.claim.jpeg.jpg \
    -a starling.integrity.json \
    --provider "numbersprotocol" \
    --recorder "Starling Capture using Numbers Protocol" \
    -k key.pem \
    -c cert.pem \
    -i meimei-fried-chicken.jpg
```

Generate meimei-fried-chicken-cai-cai.jpg containing 2 C2PA injections.

```
$ c2pa \
    -a stds.schema-org.CreativeWork.json \
    -a c2pa.thumbnail.claim.jpeg.jpg \
    -a starling.integrity.json \
    --provider "numbersprotocol" \
    --recorder "Starling Capture using Numbers Protocol" \
    -k key.pem \
    -c cert.pem \
    -i meimei-fried-chicken-cai.jpg
```

## Quick Start

In `pyc2pa/utils/`, there are two examples showing how to do single injection and multiple injection programmatically.

```
# Prepare testing input JPEG photo and its thumbnail.
# Assuming that testing input JPEG is ~/meimei-fried-chicken.jpg
$ cd pyc2pa/utils/
$ cp ~/meimei-fried-chicken.jpg .
$ convert -resize 50% meimei-fried-chicken.jpg meimei-fried-chicken-thumbnail.jpg

# Run single injection example
# (download meimei-fried-chicken-cai.jpg from IPFS)
# output: meimei-fried-chicken-cai.jpg
$ python3 c2pa_hello_world.py

# Run multiple injection example
# output: meimei-fried-chicken-cai-cai-cai.jpg
$ python3 c2pa_multiple_injection.py meimei-fried-chicken.jpg
```

## Development Tips

1. Currently, the `main` branch is based on C2PA spec draft v0.7 (compatible with the [latest C2PA spec draft](https://c2pa.org/public-draft/)).
2. The `feature-support-c2pa-photo` branch follows the latest C2PA spec implementation.
3. `pyc2pa/utils/` contains examples of single injection and multiple injection.
4. `pyc2pa/utils/digital-signature/` contains detailed documents and example codes how to create and verify a C2PA signature.
