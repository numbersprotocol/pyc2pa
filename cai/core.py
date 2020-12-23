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
        self.content_boxes.append(ContentBox())
        self.content_boxes[0].payload = json_to_bytes(self.create_claim(assertion_store))

    def create_claim(self, assertion_store):
        '''Create a Claim JSON object
        '''
        return {'foo': 'bar'}


class CaiClaimSignature(SuperBox):
    def __init__(self):
        super(CaiClaimSignature, self).__init__()
        self.description_box = DescriptionBox(
                                   content_type=Cai_content_types['claim_signature'],
                                   label='cai.signature')
        self.content_boxes.append(ContentBox(t_box_type='uuid'))
        self.content_boxes[0].payload = self.create_signature()

    def create_signature(self):
        '''Create a Claim Signature payload in bytes.
        '''
        uuid = Cai_content_types['claim_signature']
        signature = 'signature placeholder:cb.starling_1'
        #padding = bytes.fromhex('20') * (100 - len(signature))
        #payload = bytes.fromhex(uuid) + signature.encode('utf-8') + padding
        payload = bytes.fromhex(uuid) + signature.encode('utf-8')
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