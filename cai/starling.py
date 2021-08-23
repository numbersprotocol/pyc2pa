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

import argparse
import os

from cai.core import CaiClaimBlock
from cai.core import CaiClaimCMSSignature
from cai.core import CaiStore
from cai.jumbf import App11Box

from cai.core import get_xmp_tag
from cai.core import insert_xmp_key
from cai.jumbf import create_codestream_superbox
from cai.jumbf import create_json_superbox
from cai.jumbf import get_app11_marker_segment_headers
from cai.jumbf import json_to_bytes

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12

'''Starling CLI tool to generate CAI metadata.
'''

class Starling(object):
    def __init__(self,
                 media_bytes,
                 media_name,
                 raw_assertions,
                 store_label,
                 recorder,
                 private_key='',
                 signature_standard='cms'):
        '''
        raw_bytes: media content in bytes.

        raw_assertions: dict of assertion JSON objects, and keys are labels.
            refer to create_assertions for the details.

        store_label: Example: cb.starling_1

        recorder: The recorder field in Claim.

        parent_claim: The parent_claim field in Claim. Example: self#jumbf=cai/cb.adobe/cai.claim

        private_key: private key bytes.

        signature_standard: CMS or CADES-B.
        '''
        self.raw_bytes = media_bytes
        self.media_name = media_name
        self.assertions = self.create_assertions(raw_assertions)
        self.store_label = store_label
        self.recorder = recorder
        self.private_key = private_key
        self.signature_standard = signature_standard
        # get the label of the last Claim
        self.parent_claim = get_xmp_tag(self.raw_bytes)
        # get App11 marker segment headers
        self.app11_headers = get_app11_marker_segment_headers(self.raw_bytes)
        self.has_app11_headers = True if len(self.app11_headers) > 0 else False

    def create_assertions(self, raw_assertions):
        '''
        raw_assertions: dict of assertion JSON objects, and keys are labels.
            Example:
                [
                    {
                        'cai.rights': {
                            'type': 'json',
                            'data_bytes': <data-bytes>
                        }
                    },
                    ...
                ]
        return: list of Assertion SuperBoxes
        '''
        assertions = []
        for k, v in raw_assertions.items():
            label = k
            data_bytes = v['data_bytes']
            assertion_type = v['type']

            if assertion_type == '.json':
                assertions.append(create_json_superbox(content=data_bytes, label=label))
            elif assertion_type == '.jpg':
                assertions.append(create_codestream_superbox(content=data_bytes, label=label))
            else:
                raise Exception(
                    'Unknown assertion type {0} from {1}'.format(assertion_type, label))
        return assertions

    def signel_claim_injection(self):
        # create a new Store
        cai_store = CaiStore(label=self.store_label,
                             assertions=self.assertions,
                             recorder=self.recorder,
                             parent_claim=self.parent_claim,
                             key=self.private_key,
                             sig=self.signature_standard)

        # create a new Claim Block Box
        cai_claim_block = CaiClaimBlock()
        cai_claim_block.content_boxes.append(cai_store)
        cai_segment = App11Box()
        cai_segment.payload = cai_claim_block.convert_bytes()

        # save CAI-injected media
        data_bytes = self.raw_bytes[0:2] + cai_segment.convert_bytes() + self.raw_bytes[2:]
        cai_data_bytes = insert_xmp_key(data_bytes, store_label=self.store_label)
        return cai_data_bytes

    def multiple_claims_injection(self):
        """Re-create a new Claim Block.
        The high-levle idea is to
        1. Re-construct current Claim Block by
           concatenating the payloads in the App11 segments.
        2. Append the new Store into the Claim Block.
        3. Re-create App11 segments based on the updated Claim Block.
        4. Replace the old App11 segments by the new App11 segments.
        """
        # generate acquisition assertion
        acquisition_assertion = {
            'dc:format': 'image/jpeg',
            'dc:title': self.media_name,
            'dcterms:provenance': self.parent_claim,
            'stRef:DocumentID': 'xmp:fakeid:39afb1d3-7f8c-44e6-b771-85e0d9adb377',
            'stRef:InstanceID': 'xmp:fakeid:10c04858-d3fd-4e2c-8947-7f1e29d62fbe',
            'thumbnail': 'self#jumbf=cai/{}/cai.assertions/cai.acquisition.thumbnail.jpeg'.format(self.store_label)
        }
        self.assertions.append(create_json_superbox(
            content=json_to_bytes(acquisition_assertion),
            label='cai.acquisition_1'))

        # create a new Store
        cai_store = CaiStore(label=self.store_label,
                             assertions=self.assertions,
                             recorder=self.recorder,
                             parent_claim=self.parent_claim,
                             key=self.private_key,
                             sig=self.signature_standard)

        # get last segment header information
        header_number = len(self.app11_headers)
        last_en = self.app11_headers[header_number]['en']
        last_lbox = self.app11_headers[header_number]['lbox']

        # re-construct Claim Block payload
        claim_block_payload = bytearray()
        ## App11 Length of Marker Segment (the Le parameter) value is 8 ~ 65535.
        ## App11 Packet Sequence number (the Z parameter) value is 1 ~ 2^32-1.
        ## The Claim Block maximum size will be ~= 2^48 B ~= 280 TB.
        for i in range(1, header_number + 1):
            payload_start = self.app11_headers[i]['offset'] + 20
            payload_end = payload_start + (self.app11_headers[i]['le'] - 18)
            payload = self.raw_bytes[payload_start : payload_end]
            claim_block_payload += payload
        store_bytes = cai_store.convert_bytes()

        # append new Store bytes
        updated_claim_block_payload = claim_block_payload + store_bytes
        updated_lbox = last_lbox + len(store_bytes)
        updated_claim_block_bytes = updated_lbox.to_bytes(4, byteorder='big') + b'jumb' + updated_claim_block_payload
        updated_app11_segment = App11Box(en=last_en)
        updated_app11_segment.payload = updated_claim_block_bytes

        ## Assuming that current CAI data consists of 3 App11 segments.
        ##
        ## +-- starting point
        ## v
        ## +-------+----+----+------+-----+------+------+-------------------------------+
        ## | APP11 | Le | CI | En=1 | Z=1 | LBox | TBox | Payload (Claim Block, part 1) |
        ## +-------+----+----+------+-----+------+------+-------------------------------+
        ## | APP11 | Le | CI | En=1 | Z=2 | LBox | TBox | Payload (Claim Block, part 2) |
        ## +-------+----+----+------+-----+------+------+-------------------------------+
        ## | APP11 | Le | CI | En=1 | Z=3 | LBox | TBox | Payload (Claim Block, part 3) |
        ## +-------+----+----+------+-----+------+------+-------------------------------+
        ##                                                                              ^
        ##                                                               ending point --+
        ##
        ## starting point of current CAI data
        update_range_s = self.app11_headers[1]['offset']
        ## ending point of current CAI data
        update_range_e = self.app11_headers[header_number]['offset'] + self.app11_headers[header_number]['le'] + 2

        # save CAI-injected media
        data_bytes = self.raw_bytes[:update_range_s] + updated_app11_segment.convert_bytes() + self.raw_bytes[update_range_e:]
        cai_data_bytes = insert_xmp_key(data_bytes, store_label=self.store_label)
        return cai_data_bytes

    def cai_injection(self):
        if self.has_app11_headers:
            cai_data_bytes = self.multiple_claims_injection()
        else:
            cai_data_bytes = self.signel_claim_injection()
        return cai_data_bytes


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-a', '--assertion',
        help=('Assertion filepath. '
              'Use multiple times for multiple Assertions.'
              'Assertion label will be filename.'),
        action='append',
        default=[])
    ap.add_argument(
        '--store-label',
        default='cb.starling_1',
        help='Store label. Default: cb.starling_1')
    ap.add_argument(
        '--recorder',
        default='Starling Capture',
        help='Claim recorder. Default: Starling Capture')
    ap.add_argument(
        '-k', '--key',
        default='',
        help='Private key filepath.')
    ap.add_argument(
        '-s', '--sig',
        default='cms',
        help='cms or endesive')
    ap.add_argument(
        '-i', '--inject',
        default='',
        help='Inject CAI metadata to the indicated file.')
    ap.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Debug mode toggle')
    return ap.parse_args()


def main():
    args = parse_args()

    assertion_filepaths = args.assertion
    assertion_labels = [os.path.splitext(os.path.basename(a))[0]
                        for a in assertion_filepaths]
    store_label = args.store_label
    recorder = args.recorder
    key_filepath = args.key
    type_sig = args.sig

    if args.debug:
        print(args)
        print(assertion_filepaths)
        print(assertion_labels)
        print(store_label)
        print(type_sig)

    # read media content if injection is enabled
    with open(args.inject, 'rb') as f:
        raw_bytes = f.read()

    # create CAI metadata
    raw_assertions = {}
    for filepath, label in zip(assertion_filepaths, assertion_labels):
        with open(filepath, 'rb') as f:
            data_bytes = f.read().strip()
        fileext = os.path.splitext(filepath)[1]

        raw_assertions[label] = {
            'type': fileext,
            'data_bytes': data_bytes
        }

    # private key for signature
    if key_filepath != '':
        with open(key_filepath, 'rb') as f:
            if type_sig=='cms':
                key = f.read()
            elif type_sig=='endesive':
                # load_key_and_certificates second parameter is password to decrypt the data. Can be set to None of PKCS12 is not encrypted
                # https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization.html
                key = pkcs12.load_key_and_certificates(f.read(), b'', backends.default_backend())
            else:
                raise Exception(
                    'Unknown signature type {0}'.format(type_sig))
    else:
        key = []

    # create CAI-injected media
    starling = Starling(raw_bytes,
                        os.path.basename(args.inject),
                        raw_assertions,
                        store_label,
                        recorder,
                        key,
                        type_sig)
    starling_cai_bytes = starling.cai_injection()

    # save CAI-injected media
    if len(args.inject) > 0:
        fname, fext = os.path.splitext(args.inject)
        fpath = fname + '-cai' + fext
        with open(fpath, 'wb') as f:
            f.write(starling_cai_bytes)


if __name__ == "__main__":
    main()   