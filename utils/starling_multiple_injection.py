#!/usr/bin/python3
#
# Starling Hello World Example for multi-injection.
#
# This program will inject 3 CAI Stores.
#
# Usage
#     $ python3 starling_multiple_injection.py <image-filepath>
#
# Verify
#     1. Go to https://verify.contentauthenticity.org/inspect
#     2. Drag and drop the generated image.
#     3. The webpage will show the CAI information.

import os
import sys

from cai.jumbf import json_to_bytes, json_to_cbor_bytes
from cai.starling import Starling


photo_filename = sys.argv[1]
thumbnail_filename = sys.argv[1].replace('.jpg', '-thumbnail.jpg')

photo_bytes = open(photo_filename, 'rb').read()
thumbnail_bytes = open(thumbnail_filename, 'rb').read()

metadata = [
    {
        'claim': {
            'store_label': 'cb.Authmedia_1',
            'recorder': '851b7b53-a987-4a2c-af3f-f3221028cca9',
            'photo_filename': photo_filename,
        },
        'assertions': {
            'adobe.asset.info': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'title': photo_filename
                })
            },
            'cai.location.broad': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'location': 'Okura Garden Hotel, Shanghai'
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
                            "name": "Wing Shya"
                        }
                    ]
                })
            },
            'c2pa.thumbnail.claim.jpeg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
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
    },
    {
        'claim': {
            'store_label': 'cb.IOTAIntegrityChain_2',
            'recorder': 'AYYCXSXJTQOWBUKKORA9NOGMINILMDLMI9UKHWOPYVUOAEJGOMH9CEOONDVADMVABZVKINBBXBQLA9999',
            'photo_filename': photo_filename.replace('.jpg', '-cai.jpg')
        },
        'assertions': {
            'adobe.asset.info': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'title': photo_filename.replace('.jpg', '-cai.jpg')
                })
            },
            'cai.location.broad': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'location': 'Okura Garden Hotel, Shanghai'
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
                            "name": "Wing Shya"
                        }
                    ]
                })
            },
            'c2pa.thumbnail.claim.jpeg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
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
    },
    {
        'claim': {
            'store_label': 'cb.ThunderCoreNFTChain_3',
            'recorder': '0xc363852e13d5cd0df8a4a12bfe0e2f3b23e504ff:39',
            'photo_filename': photo_filename.replace('.jpg', '-cai-cai.jpg')
        },
        'assertions': {
            'adobe.asset.info': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'title': photo_filename.replace('.jpg', '-cai-cai.jpg')
                })
            },
            'cai.location.broad': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'location': 'Okura Garden Hotel, Shanghai'
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
                            "name": "Wing Shya"
                        }
                    ]
                })
            },
            'c2pa.thumbnail.claim.jpeg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
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
    },
]

key = open('key.pem', 'rb').read()
cert = open('cert.pem', 'rb').read()

# 1st CAI injection: Authmedia
# 2nd CAI injection: IOTA
# 3rd CAI injection: ThunderCore
for i in range(3):
    starling = Starling(photo_bytes,
                        metadata[i]['claim']['photo_filename'],
                        metadata[i]['assertions'],
                        metadata[i]['claim']['store_label'],
                        metadata[i]['claim']['recorder'],
                        key,
                        cert)
    photo_bytes = starling.c2pa_injection()

# Save to file
fname, fext = os.path.splitext(photo_filename)
fpath = fname + '-cai-cai-cai' + fext
with open(fpath, 'wb') as f:
    f.write(photo_bytes)
