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

import hashlib
import uuid

import multibase
import multihash
import pyexiv2
import cbor

from cai.jumbf import ContentBox
from cai.jumbf import DescriptionBox
from cai.jumbf import SuperBox
from cai.jumbf import json_to_bytes, json_to_cbor_bytes

'''Implementation of C2PA Whitepaper
Content Provenance and Authenticity
'''

Cai_content_types = {
    'manifest_block'    : '6332706100110010800000aa00389b71',
    'manifest'          : '63326D6100110010800000aa00389b71',
    'assertion_store'   : '6332617300110010800000aa00389b71',
    'claim'             : '6332636C00110010800000aa00389b71',
    'claim_signature'   : '6332637300110010800000aa00389b71',
}


Claim_asset_hashes_mockup = [
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


def encode_hashlink(binary_content, codec='base64', to_hexstr=False):
    mh = multihash.Multihash(multihash.Func.sha2_256,
                             hashlib.sha256(binary_content).digest())
    mb = multibase.encode(codec, mh.encode())
    if to_hexstr:
        # return hex string
        return mb.decode('utf-8')
    else:
        # return bytes
        return mb


def compute_hash(binary_content):
    m = hashlib.sha256(binary_content)
    return m.digest()


def insert_xmp_key(data_bytes, manifest_label):
    metadata = pyexiv2.ImageMetadata.from_buffer(data_bytes)
    metadata.read()
    metadata['Xmp.dcterms.provenance'] = pyexiv2.XmpTag(
        'Xmp.dcterms.provenance', 'self#jumbf=c2pa/{}/c2pa.claim'.format(manifest_label))
    metadata.write()
    return metadata.buffer


def get_xmp_tag(data_bytes, tag='Xmp.dcterms.provenance'):
    metadata = pyexiv2.ImageMetadata.from_buffer(data_bytes)
    metadata.read()
    if tag in metadata.xmp_keys:
        return metadata[tag].raw_value
    else:
        return ''


class C2paAssertionStore(SuperBox):
    def __init__(self, assertions):
        super(C2paAssertionStore, self).__init__()
        self.description_box = DescriptionBox(
            content_type=Cai_content_types['assertion_store'],
            label='c2pa.assertions')
        self.content_boxes = assertions


class C2paClaim(SuperBox):
    def __init__(self,
                 assertion_store,
                 manifest_label,
                 media_name,
                 recorder='Starling Capture using Numbers Protocol',
                 parent_claim='',):
        super(C2paClaim, self).__init__()
        self.description_box = DescriptionBox(
            content_type=Cai_content_types['claim'], label='c2pa.claim')
        content_box = ContentBox(t_box_type='cbor')
        content_box.payload = json_to_cbor_bytes(
            self.create_claim(assertion_store,
                              manifest_label,
                              recorder=recorder,
                              parent_claim=parent_claim,
                              media_name=media_name))
        self.content_boxes.append(content_box)

    def create_claim(self,
                     assertion_store,
                     manifest_label,
                     media_name,
                     recorder='Starling Capture',
                     parent_claim=''):
        '''Create a Claim JSON object
        '''
        claim = {}
        claim['dc:title'] = media_name
        claim['dc:format'] = 'image/jpeg'
        claim['instanceID'] = 'xmp:iid:4124fae1-1da7-4a3f-95c8-d8ae071bd048'
        claim['claim_generator'] = recorder
        claim['signature'] = 'self#jumbf=c2pa/{}/c2pa.signature'.format(
            manifest_label)
        claim['assertions'] = [{
            'url': 'self#jumbf=c2pa/{manifest_label}/c2pa.assertions/{assertion_label}'
            .format(
                manifest_label=manifest_label,
                assertion_label=assertion.description_box.db_label,
            ),
            'alg': 'sha256',
            'hash': compute_hash(assertion.content_boxes[0].convert_bytes()[8:]),
        } for assertion in assertion_store.content_boxes]
        claim['alg'] = 'sha256'
        if parent_claim != '':
            claim['parent_claim'] = parent_claim
        return claim


class C2paClaimSignature(SuperBox):
    def __init__(self, claim, key):
        super(C2paClaimSignature, self).__init__()
        self.description_box = DescriptionBox(
            content_type=Cai_content_types['claim_signature'],
            label='c2pa.signature')
        content_box = ContentBox(t_box_type='cbor')
        content_box.payload = self.create_signature(claim, key)
        self.content_boxes.append(content_box)

    def create_signature(self, claim, key):
        '''Create a Claim Signature payload in bytes.
        '''
        phdr = b''
        uhdr = {'x5chain': b''}
        payload = None
        signature = b''

        message = [phdr, uhdr, payload, signature]
        tag = cbor.Tag(18, message)
        cose_tag = cbor.dumps(tag)

        pad = b'\x20' * (4096 - len(cose_tag))
        payload = cose_tag + pad
        return payload


class C2paManifest(SuperBox):
    def __init__(self,
                 media_name,
                 provider='numbersprotocol',
                 assertions=[],
                 recorder='Starling Capture',
                 parent_claim='',
                 key='',
                 sig='cms'):
        super(C2paManifest, self).__init__()
        self.manifest_label = '{}:urn:uuid:{}'.format(provider, uuid.uuid4())
        self.description_box = DescriptionBox(
            content_type=Cai_content_types['manifest'],
            label=self.manifest_label)
        self.assertion_store = C2paAssertionStore(assertions)
        self.claim = C2paClaim(self.assertion_store,
                               self.manifest_label,
                               media_name,
                               recorder=recorder,
                               parent_claim=parent_claim)
        self.signature = C2paClaimSignature(self.claim.content_boxes[0].payload, key=key)
        
        self.content_boxes.append(self.assertion_store)
        self.content_boxes.append(self.claim)
        self.content_boxes.append(self.signature)


class C2paManifestBlock(SuperBox):
    def __init__(self):
        super(C2paManifestBlock, self).__init__()
        self.description_box = DescriptionBox(
            content_type=Cai_content_types['manifest_block'], label='c2pa')
