#!/usr/bin/python3

# Copyright 2020 Numbers Co., Ltd.
#
# This file is part of pyc2pa.
#
# pyc2pa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyc2pa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyc2pa.  If not, see <http://www.gnu.org/licenses/>.

'''
C2PA Hello World Example for multi-injection.

This program will inject 3 CAI Stores.

Usage
    $ python3 c2pa_multiple_injection.py <image-filepath>

Verify
    1. Go to https://verify.contentauthenticity.org/inspect
    2. Drag and drop the generated image.
    3. The webpage will show the CAI information.
'''

import os
import sys

from c2pa.jumbf import json_to_bytes
from c2pa.starling import Starling


photo_filename = sys.argv[1]
thumbnail_filename = sys.argv[1].replace('.jpg', '-thumbnail.jpg')

photo_bytes = open(photo_filename, 'rb').read()
thumbnail_bytes = open(thumbnail_filename, 'rb').read()

metadata = [
    {
        'claim': {
            'store_label': 'cb.Authmedia_1',
            'recorder': '851b7b53-a987-4a2c-af3f-f3221028cca9',
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
                    'location': 'Taipei, Taiwan'
                })
            },
            'cai.rights': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'copyright': 'Tammy Yang'
                })
            },
            'cai.claim.thumbnail.jpg.jpg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
            'cai.acquisition.thumbnail.jpg.jpg': {
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
                    'location': 'Taipei, Taiwan'
                })
            },
            'cai.rights': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'copyright': 'Tammy Yang'
                })
            },
            'cai.claim.thumbnail.jpg.jpg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
            'cai.acquisition.thumbnail.jpg.jpg': {
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
                    'location': 'Taipei, Taiwan'
                })
            },
            'cai.rights': {
                'type': '.json',
                'data_bytes': json_to_bytes({
                    'copyright': 'Tammy Yang'
                })
            },
            'cai.claim.thumbnail.jpg.jpg': {
                'type': '.jpg',
                'data_bytes': thumbnail_bytes
            },
            'cai.acquisition.thumbnail.jpg.jpg': {
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

# 1st CAI injection: Authmedia
# 2nd CAI injection: IOTA
# 3rd CAI injection: ThunderCore
for i in range(3):
    starling = Starling(photo_bytes,
                        photo_filename,
                        metadata[i]['assertions'],
                        metadata[i]['claim']['store_label'],
                        metadata[i]['claim']['recorder'],
                        '',
                        '')
    photo_bytes = starling.cai_injection()

# Save to file
fname, fext = os.path.splitext(photo_filename)
fpath = fname + '-cai-cai-cai' + fext
with open(fpath, 'wb') as f:
    f.write(photo_bytes)
