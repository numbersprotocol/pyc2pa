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
C2PA Hello World Example.

This program will download an photo from IPFS and run CAI injection.

Usage
    $ python3 c2pa_hello_world.py

Verify
    1. Go to https://verify.contentauthenticity.org/inspect
    2. Drag and drop the generated meimei-fried-chicken.jpg
    3. The webpage will show the CAI information
'''

import os

import requests

from c2pa.jumbf import json_to_bytes
from c2pa.starling import Starling


# single-claim injection
photo_url = 'https://ipfs.io/ipfs/QmaaqwP1p71b118uNnHCvQTtywu1tK1H5LEjT6wWi8c5o2'
photo_filename = 'meimei-fried-chicken.jpg'

# multi-claim injection
#photo_url = 'https://ipfs.io/ipfs/QmPa8Dokcjcouv1KYrXn1cYA6XLACDBPVmnaMZ4un8K54L'
#photo_filename = 'meimei-nbj.jpg'

photo_bytes = requests.get(photo_url).content

assertions = {
    'adobe.asset.info': {
        'type': '.json',
        'data_bytes': json_to_bytes({
            'title': 'meimei-nbj.jpg'
        })
    },
    'cai.location.broad': {
        'type': '.json',
        'data_bytes': json_to_bytes({
            'location': 'Dogworld, Taipei Taiwan'
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
        'data_bytes': photo_bytes
    },
    'cai.acquisition.thumbnail.jpg.jpg': {
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

starling = Starling(photo_bytes,
                    photo_filename,
                    assertions,
                    'cb.numbersprotocol_1',
                    'Capture App: 5c2cefaa-fb4e-4d77-991c-5046729b295f',
                    '',
                    '')
starling_cai_bytes = starling.cai_injection()

fname, fext = os.path.splitext(photo_filename)
fpath = fname + '-cai' + fext
with open(fpath, 'wb') as f:
    f.write(starling_cai_bytes)