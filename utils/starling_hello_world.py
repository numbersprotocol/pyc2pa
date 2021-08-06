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

from cai.jumbf import json_to_bytes
from cai.starling import Starling


# single-claim injection
# photo_url = 'https://ipfs.io/ipfs/QmaaqwP1p71b118uNnHCvQTtywu1tK1H5LEjT6wWi8c5o2'
# photo_filename = 'meimei-fried-chicken.jpg'
photo_url = 'https://http.cat/404'
photo_filename = '404.jpg'

# multi-claim injection
# photo_url = 'https://ipfs.io/ipfs/QmPa8Dokcjcouv1KYrXn1cYA6XLACDBPVmnaMZ4un8K54L'
# photo_filename = 'meimei-nbj.jpg'

photo_bytes = requests.get(photo_url).content

assertions = {
    'adobe.asset.info': {
        'type': '.json',
        'data_bytes': json_to_bytes({
            'title': '404-cat.jpg'
        })
    },
    'c2pa.location.broad.v1': {
        'type': '.json',
        'data_bytes': json_to_bytes({
            'location': 'Somewhere on the Internet'
        })
    },
    'c2pa.rights.v1': {
        'type': '.json',
        'data_bytes': json_to_bytes({
            'copyright': 'http.cat'
        })
    },
    'c2pa.claim.thumbnail.jpg.jpg': {
        'type': '.jpg',
        'data_bytes': photo_bytes
    },
    'c2pa.acquisition.thumbnail.jpg.jpg': {
        'type': '.jpg',
        'data_bytes': photo_bytes
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

with open('data/Keys/Privkey.out', 'r') as f:
    private_key = f.read()

# TODO: Change the name of recorder as the format:
# https://datatracker.ietf.org/doc/html/rfc7231#section-5.5.3
starling = Starling(photo_bytes,
                    photo_filename,
                    assertions,
                    'numbersprotocol',
                    'Capture App: 5c2cefaa-fb4e-4d77-991c-5046729b295f',
                    private_key,
                    'cms')
starling_cai_bytes = starling.c2pa_injection()

fname, fext = os.path.splitext(photo_filename)
fpath = fname + '-cai' + fext
with open(fpath, 'wb') as f:
    f.write(starling_cai_bytes)
