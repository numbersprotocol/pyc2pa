# Copyright 2020 Numbers Co., Ltd.
#
# This file is part of starling-cai.
#
# starling-cai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# starling-cai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with starling-cai.  If not, see <http://www.gnu.org/licenses/>.

from cai.jumbf import Box
from cai.jumbf import ContentBox
from cai.jumbf import DescriptionBox
from cai.jumbf import SuperBox

from cai.jumbf import create_json_superbox
from cai.jumbf import json_to_bytes

'''Implementation of CAI Whitepaper
Content Authenticity Initiative
'''

Cai_content_types = {
    'claim_block'    : '6361636200110010800000aa00389b71',
    'store'          : '6361737400110010800000aa00389b71',
    'assertion_store': '6361617300110010800000aa00389b71',
    'claim'          : '6361636c00110010800000aa00389b71',
    'claim_signature': '6361736700110010800000aa00389b71',
}


Claim_mockup = {
    'recorder': 'Starling Capture',
    'signature': 'self#jumbf=cai/cb.starling_1/cai.signature',
    'assertions': [
        'self#jumbf=cai/cb.starling_1/cai.assertions/starling.location.precise?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMoBUAVbTEB7K',
        'self#jumbf=cai/cb.starling_1/cai.assertions/starling.sensors?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMvY4QFEN3973',
        'self#jumbf=cai/cb.starling_1/cai.assertions/starling.device?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMwEoBojZcUrZ',
        'self#jumbf=cai/cb.starling_1/cai.assertions/starling.integrity?hl=z26ycANRgtWbqYX9cdsWD4rsTqz8RYHQArrq4CZJwZn1cxX73kTP6x3rRcBsUfMo3SG72sZg13'
    ],
    'asset_hashes': [
        {
            'start': '0x0000000000000000',
            'length': '0x0000000000009959',
            'name': 'JFIF SOI-APP0',
            'url': '',
            'value': 'EiAuxjtmax46cC2N3Y9aFmBO9Jfay8LEwJWzBUtZ0sUM8gA='
        },
        {
            'start': '0x0000000000009959',
            'length': '0x000000000000027d',
            'name': 'JFIF APP1/XMP',
            'url': '',
            'value': 'EiDjZifCgG2iKxcYeChKTOcWlJ9I/UC9/c5XFiJREqJFpwA='
        },
        {
            'start': '0x000000000000a90c',
            'length': '0x00000000000215e6',
            'name': 'JFIF DQT-EOI',
            'url': '',
            'value': 'EiArx031oA0N5KOEG6n9R/bJJFYJvmGlDoLtuwbRipLTKAA='
        }
    ]
}


class CaiAssertionStore(SuperBox):
    def __init__(self, assertions):
        super(CaiAssertionStore, self).__init__()
        self.description_box = DescriptionBox(
                                   content_type=Cai_content_types['assertion_store'],
                                   label='cai.assertions')
        self.content_boxes = assertions


class CaiClaim(SuperBox):
    def __init__(self, assertion_store):
        super(CaiClaim, self).__init__()
        self.description_box = DescriptionBox(
                                   content_type=Cai_content_types['claim'],
                                   label='cai.claim')
        content_box = ContentBox()
        content_box.payload = json_to_bytes(self.create_claim(assertion_store))
        self.content_boxes.append(content_box)

    def create_claim(self, assertion_store):
        '''Create a Claim JSON object
        '''
        return Claim_mockup


class CaiClaimSignature(SuperBox):
    def __init__(self):
        super(CaiClaimSignature, self).__init__()
        self.description_box = DescriptionBox(
                                   content_type=Cai_content_types['claim_signature'],
                                   label='cai.signature')
        content_box = ContentBox(t_box_type='uuid')
        content_box.payload = self.create_signature()
        self.content_boxes.append(content_box)

    def create_signature(self):
        '''Create a Claim Signature payload in bytes.
        '''
        uuid = Cai_content_types['claim_signature']
        signature = 'signature placeholder:cb.starling_1'
        padding = b'\x20' * (100 - len(signature))
        payload = bytes.fromhex(uuid) + signature.encode('utf-8') + padding
        return payload


class CaiStore(SuperBox):
    def __init__(self, label='cb.starling_1', assertions=[]):
        super(CaiStore, self).__init__()
        self.description_box = DescriptionBox(
                                   content_type=Cai_content_types['store'],
                                   label=label)
        self.assertion_store = CaiAssertionStore(assertions)
        self.claim = CaiClaim(self.assertion_store)
        self.signature = CaiClaimSignature()
        self.content_boxes.append(self.assertion_store)
        self.content_boxes.append(self.claim)
        self.content_boxes.append(self.signature)


class CaiClaimBlock(SuperBox):
    def __init__(self):
        super(CaiClaimBlock, self).__init__()
        self.description_box = DescriptionBox(
                                   content_type=Cai_content_types['claim_block'],
                                   label='cai')