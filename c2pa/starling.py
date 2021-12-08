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

import argparse
import os

from c2pa.core import C2paManifestBlock
from c2pa.core import C2paManifest
from c2pa.jumbf import App11Box, json_to_cbor_bytes

from c2pa.core import get_xmp_tag
from c2pa.core import insert_xmp_key
from c2pa.jumbf import create_codestream_superbox
from c2pa.jumbf import create_json_superbox
from c2pa.jumbf import create_cbor_superbox
from c2pa.jumbf import get_app11_marker_segment_headers

'''Starling CLI tool to generate CAI metadata.
'''


class Starling(object):
    def __init__(self,
                 media_bytes,
                 media_name,
                 raw_assertions,
                 provider,
                 recorder,
                 private_key='',
                 certificate=''):
        '''
        raw_bytes: media content in bytes.

        raw_assertions: dict of assertion JSON objects, and keys are labels.
            refer to create_assertions for the details.

        provider: Example: numbersprotocol

        recorder: The recorder field in Claim.

        private_key: private key bytes.

        certificate: certificate bytes.
        '''
        self.raw_bytes = media_bytes
        self.media_name = media_name
        self.assertions = self.create_assertions(raw_assertions)
        self.provider = provider
        self.recorder = recorder
        self.private_key = private_key
        self.certificate = certificate
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
            elif assertion_type == '.cbor':
                assertions.append(create_cbor_superbox(content=data_bytes, label=label))
            elif assertion_type == '.jpg' or assertion_type == '.jpeg':
                assertions.append(create_codestream_superbox(content=data_bytes, label=label))
            else:
                raise Exception(
                    'Unknown assertion type {0} from {1}'.format(assertion_type, label))
        return assertions

    def single_claim_injection(self):
        # create a new manifest
        c2pa_manifest = C2paManifest(provider=self.provider,
                                     assertions=self.assertions,
                                     recorder=self.recorder,
                                     key=self.private_key,
                                     media_name=self.media_name,
                                     certificate=self.certificate)

        # create a new Claim Block Box
        c2pa_manifest_block = C2paManifestBlock()
        c2pa_manifest_block.content_boxes.append(c2pa_manifest)
        c2pa_segment = App11Box()
        c2pa_segment.payload = c2pa_manifest_block.convert_bytes()

        # save CAI-injected media
        data_bytes = self.raw_bytes[0:2] + c2pa_segment.convert_bytes() + self.raw_bytes[2:]
        cai_data_bytes = insert_xmp_key(data_bytes, manifest_label=c2pa_manifest.manifest_label)
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
            'documentID': 'xmp:fakeid:39afb1d3-7f8c-44e6-b771-85e0d9adb377',
            'instanceID': 'xmp:fakeid:10c04858-d3fd-4e2c-8947-7f1e29d62fbe',
            'relationship': 'parentOf',
            'c2pa_manifest': {
                'url': self.parent_claim.replace('/c2pa.claim', ''),
                'alg': 'sha256',
                'hash': b'placeholder'
            },
            'thumbnail': {
                'url': self.parent_claim.replace('/c2pa.claim', '/c2pa.thumbnail.claim.jpeg'),
                'alg': 'sha256',
                'hash': b'placeholder'
            }
        }
        self.assertions.append(create_cbor_superbox(
            content=json_to_cbor_bytes(acquisition_assertion),
            label='c2pa.ingredient'))

        # create a new Store
        c2pa_manifest = C2paManifest(provider=self.provider,
                                     assertions=self.assertions,
                                     recorder=self.recorder,
                                     key=self.private_key,
                                     certificate=self.certificate,
                                     media_name=self.media_name)

        # get last segment header information
        header_number = len(self.app11_headers)
        last_en = self.app11_headers[header_number]['en']
        last_lbox = self.app11_headers[header_number]['lbox']

        # re-construct Claim Block payload
        claim_block_payload = bytearray()
        # App11 Length of Marker Segment (the Le parameter) value is 8 ~ 65535.
        # App11 Packet Sequence number (the Z parameter) value is 1 ~ 2^32-1.
        # The Claim Block maximum size will be ~= 2^48 B ~= 280 TB.
        for i in range(1, header_number + 1):
            payload_start = self.app11_headers[i]['offset'] + 20
            payload_end = payload_start + (self.app11_headers[i]['le'] - 18)
            payload = self.raw_bytes[payload_start: payload_end]
            claim_block_payload += payload
        store_bytes = c2pa_manifest.convert_bytes()

        # append new Store bytes
        updated_claim_block_payload = claim_block_payload + store_bytes
        updated_lbox = last_lbox + len(store_bytes)
        updated_claim_block_bytes = updated_lbox.to_bytes(4, byteorder='big') + b'jumb' + updated_claim_block_payload
        updated_app11_segment = App11Box(en=last_en)
        updated_app11_segment.payload = updated_claim_block_bytes

        # Assuming that current CAI data consists of 3 App11 segments.
        #
        # +-- starting point
        # v
        # +-------+----+----+------+-----+------+------+-------------------------------+
        # | APP11 | Le | CI | En=1 | Z=1 | LBox | TBox | Payload (Claim Block, part 1) |
        # +-------+----+----+------+-----+------+------+-------------------------------+
        # | APP11 | Le | CI | En=1 | Z=2 | LBox | TBox | Payload (Claim Block, part 2) |
        # +-------+----+----+------+-----+------+------+-------------------------------+
        # | APP11 | Le | CI | En=1 | Z=3 | LBox | TBox | Payload (Claim Block, part 3) |
        # +-------+----+----+------+-----+------+------+-------------------------------+
        #                                                                              ^
        #                                                               ending point --+
        #
        # starting point of current CAI data
        update_range_s = self.app11_headers[1]['offset']
        # ending point of current CAI data
        update_range_e = self.app11_headers[header_number]['offset'] + self.app11_headers[header_number]['le'] + 2

        # save CAI-injected media
        data_bytes = (
            self.raw_bytes[:update_range_s] +
            updated_app11_segment.convert_bytes() +
            self.raw_bytes[update_range_e:]
        )
        c2pa_data_bytes = insert_xmp_key(data_bytes, manifest_label=c2pa_manifest.manifest_label)
        return c2pa_data_bytes

    def c2pa_injection(self):
        if self.has_app11_headers:
            c2pa_data_bytes = self.multiple_claims_injection()
        else:
            c2pa_data_bytes = self.single_claim_injection()
        return c2pa_data_bytes


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
        '--provider',
        default='numbersprotocol',
        help='Manifest provider. Default: numbersprotocol')
    ap.add_argument(
        '--recorder',
        default='Starling Capture',
        help='Claim recorder. Default: Starling Capture')
    ap.add_argument(
        '-k', '--key',
        default='',
        help='Private key filepath.')
    ap.add_argument(
        '-c', '--cert',
        default='',
        help='Public certificate filepath.')
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
    provider = args.provider
    recorder = args.recorder
    key_filepath = args.key
    cert_filepath = args.cert

    if args.debug:
        print(args)
        print(assertion_filepaths)
        print(assertion_labels)
        print(provider)

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
            key = f.read()
    else:
        key = []

    # public certificate for the public key
    if cert_filepath != '':
        with open(cert_filepath, 'rb') as f:
            certificate = f.read()
    else:
        key = []

    # create CAI-injected media
    starling = Starling(raw_bytes,
                        os.path.basename(args.inject),
                        raw_assertions,
                        provider,
                        recorder,
                        key,
                        certificate)
    starling_cai_bytes = starling.c2pa_injection()

    # save CAI-injected media
    if len(args.inject) > 0:
        fname, fext = os.path.splitext(args.inject)
        fpath = fname + '-cai' + fext
        with open(fpath, 'wb') as f:
            f.write(starling_cai_bytes)


if __name__ == "__main__":
    main()
