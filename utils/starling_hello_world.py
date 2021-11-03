#!/usr/bin/python3
#
# Starling Hello World Example.
#
# This program will download an photo from IPFS and run CAI injection.
#
# Usage
#     $ python3 starling_hello_world.py
#
# Verify
#     1. Go to https://verify.contentauthenticity.org/inspect
#     2. Drag and drop the generated meimei-fried-chicken.jpg
#     3. The webpage will show the CAI information

import os

import requests

from cai.jumbf import json_to_bytes, json_to_cbor_bytes
from cai.starling import Starling


# single-claim injection
photo_url = 'https://ipfs.io/ipfs/QmaaqwP1p71b118uNnHCvQTtywu1tK1H5LEjT6wWi8c5o2'
photo_filename = 'meimei-fried-chicken.jpg'

# multi-claim injection
# photo_url = 'https://ipfs.io/ipfs/QmPa8Dokcjcouv1KYrXn1cYA6XLACDBPVmnaMZ4un8K54L'
# photo_filename = 'meimei-nbj.jpg'

photo_bytes = requests.get(photo_url).content

assertions = {
    'c2pa.thumbnail.claim.jpeg': {
        'type': '.jpg',
        'data_bytes': photo_bytes
    },
    'c2pa.actions': {
        'type': '.cbor',
        'data_bytes': json_to_cbor_bytes({
            "actions": [
                {
                    "action": "c2pa.edited",
                    "parameters": "gradient"
                }
            ]
        })
    },
    'adobe.dictionary': {
        'type': '.cbor',
        'data_bytes': json_to_cbor_bytes({
            "url": "https://cai-assertions.adobe.com/photoshop/dictionary.json"
        })
    },
    'adobe.beta': {
        'type': '.cbor',
        'data_bytes': json_to_cbor_bytes({
            'version': '0.7.0'
        })
    },
    'stds.schema-org.CreativeWork': {
        'type': '.json',
        'data_bytes': json_to_bytes({
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "author": [
                {
                    "@type": "Person",
                    "credential": [],
                    "name": "Tammy Yang"
                }
            ]
        })
    },
    # other unused keys
    #     starling:FileconCID
    #     starling:FilecoinCID_Explorer
    #     starling:IPFSCID
    #     starling:IPFSCID_Explorer
    #     starling:HederaHx
    #     starling:HederaHx_Explorer
    #     starling:GUNNetwork
    #     starling:GUNNetwork_Explorer
    'starling.integrity.json': {
        'type': '.json',
        'data_bytes': json_to_bytes({
            'starling:PublicKey': 'fake-public-key',
            'starling:MediaHash': 'd3554e727696c9c0a116491b4dc2006752361ad478d2fa742158ec2cd823b56e',
            'starling:MediaKey': 'd3554e7276_1608464410000',
            'starling:CaptureTimestamp': '2020-12-20T11:40:10Z'
        })
    }
}

key = open('key.pem', 'rb').read()
cert = open('cert.pem', 'rb').read()

starling = Starling(photo_bytes,
                    photo_filename,
                    assertions,
                    'numbersprotocol',
                    'Capture App: 5c2cefaa-fb4e-4d77-991c-5046729b295f',
                    key,
                    cert)
starling_cai_bytes = starling.c2pa_injection()

fname, fext = os.path.splitext(photo_filename)
fpath = fname + '-cai' + fext
with open(fpath, 'wb') as f:
    f.write(starling_cai_bytes)
