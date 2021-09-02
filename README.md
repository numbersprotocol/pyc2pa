# PyC2PA

![c2pa-concept-full](https://user-images.githubusercontent.com/292790/131794471-411556ae-3186-4a85-a62a-e30cc0a77764.jpg)
(photo source: C2PA)

PyC2PA is Python implementation of [C2PA](https://c2pa.org/) (Coalition for Content Provenance and Authenticity) addressing the prevalence of misleading information online through the development of technical standards for certifying the source and history (or provenance) of media content.

## Quick Trial

1. Download the testing photo: [meimei-fried-chicken-cai-cai-cai.jpg](![c2pa-concept-full](https://user-images.githubusercontent.com/292790/131794471-411556ae-3186-4a85-a62a-e30cc0a77764.jpg))
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

## For Developer

1. Currently, the `main` branch is based on C2PA spec draft v0.5 (compatible with the [latest C2PA spec draft](https://c2pa.org/public-draft/)).
2. The `feature-support-c2pa-photo` branch follows the latest C2PA spec implementation.
3. `pyc2pa/utils/` contains examples of single injection and multiple injection.
4. `pyc2pa/utils/digital-signature/` contains detailed documents and example codes how to create and verify a C2PA signature.
