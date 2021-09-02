# PyC2PA

![c2pa-concept-full](https://user-images.githubusercontent.com/292790/131808157-0ca62a79-c2f4-4e1d-b8b9-ef027476f4b0.jpg)
(photo source: C2PA)

PyC2PA is Python implementation of [C2PA](https://c2pa.org/) (Coalition for Content Provenance and Authenticity) addressing the prevalence of misleading information online through the development of technical standards for certifying the source and history (or provenance) of media content.

## Quick Trial

1. Download the testing photo: [meimei-fried-chicken-cai-cai-cai.jpg](https://user-images.githubusercontent.com/292790/131797706-937ac2ef-e57c-4fe6-9842-2941deba6cec.jpg)
1. Go to the [CAI verification website](https://verify.contentauthenticity.org/) and upload the photo.
1. You should see the C2PA information (3 injections) like this:

    ![cai-verify-example](https://user-images.githubusercontent.com/292790/131798257-21159c2a-a958-431b-aaea-1649b27aaaaf.png)

## Installation

```
$ python3 -m pip install pyc2pa
```

## C2PA CLI

In command line run:

```
$ c2pa [-a ASSERTION] [--store-label STORE_LABEL] [--recorder RECORDER] [-k KEY] [-s SIG] [-o OUTPUT] [-i INJECT]
```

Example: generate meimei-fried-chicken-cai.jpg containing single C2PA injection.

```
$ c2pa \
    -a cai.location.broad.json \
    -a cai.rights.json \
    -a cai.claim.thumbnail.jpg.jpg \
    -a cai.acquisition.thumbnail.jpg.jpg \
    -a adobe.asset.info.json \
    -a starling.integrity.json \
    --recorder "Starling Capture using Numbers Protocol" \
    --store-label "cb.starling_1" \
    -k certificate.p12 \
    -s endesive \
    -i meimei-fried-chicken.jpg
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

1. Currently, the `main` branch is based on C2PA spec draft v0.5 (compatible with the [latest C2PA spec draft](https://c2pa.org/public-draft/)).
2. The `feature-support-c2pa-photo` branch follows the latest C2PA spec implementation.
3. `pyc2pa/utils/` contains examples of single injection and multiple injection.
4. `pyc2pa/utils/digital-signature/` contains detailed documents and example codes how to create and verify a C2PA signature.
