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

'''Starling CLI tool to generate CAI metadata.
'''

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
        '-o', '--output',
        default='',
        help='Save CAI metadata to the filepath.')
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

    if args.debug:
        print(args)
        print(assertion_filepaths)
        print(assertion_labels)
        print(store_label)

    # read media content if injection is enabled
    with open(args.inject, 'rb') as f:
        raw_bytes = f.read()

    # get the label of the last Claim
    parent_claim = get_xmp_tag(raw_bytes)

    # get App11 marker segment headers
    app11_headers = get_app11_marker_segment_headers(raw_bytes)
    has_app11_headers = True if len(app11_headers) > 0 else False

    # create CAI metadata
    assertions = []
    for filepath, label in zip(assertion_filepaths, assertion_labels):
        with open(filepath, 'rb') as f:
            data_bytes = f.read().strip()
        fileext = os.path.splitext(filepath)[1]
        if fileext == '.json':
            assertions.append(create_json_superbox(content=data_bytes, label=label))
        elif fileext == '.jpg':
            assertions.append(create_codestream_superbox(content=data_bytes, label=label))
        else:
            raise Exception(
                'Unknown assertion type {0} from {1}'.format(fileext, filepath))

    # private key for signature
    if key_filepath != '':
        with open(key_filepath, 'rb') as f:
            key = f.read()
    else:
        key = []

    if has_app11_headers:
        # generate acquisition assertion
        acquisition_assertion = {
            'dc:format': 'image/jpeg',
            'dc:title': os.path.basename(args.inject),
            'dcterms:provenance': parent_claim,
            'stRef:DocumentID': 'xmp:fakeid:39afb1d3-7f8c-44e6-b771-85e0d9adb377',
            'stRef:InstanceID': 'xmp:fakeid:10c04858-d3fd-4e2c-8947-7f1e29d62fbe',
            'thumbnail': 'self#jumbf=cai/{}/cai.assertions/cai.acquisition.thumbnail.jpeg'.format(store_label)
        }
        assertions.append(create_json_superbox(
            content=json_to_bytes(acquisition_assertion),
            label='cai.acquisition_1'))

        # create a new Store
        cai_store = CaiStore(label=store_label,
                             assertions=assertions,
                             recorder=recorder,
                             parent_claim=parent_claim,
                             key=key)

        # get last segment header information
        header_number = len(app11_headers)
        last_en = app11_headers[header_number]['en']
        last_lbox = app11_headers[header_number]['lbox']

        # re-construct Claim Block payload
        claim_block_payload = bytearray()
        for i in range(1, header_number + 1):
            payload_start = app11_headers[i]['offset'] + 20
            payload_end = payload_start + (app11_headers[i]['le'] - 18)
            payload = raw_bytes[payload_start : payload_end]
            claim_block_payload += payload
        store_bytes = cai_store.convert_bytes()

        # append new Store bytes
        updated_claim_block_payload = claim_block_payload + store_bytes
        updated_lbox = last_lbox + len(store_bytes)
        updated_claim_block_bytes = updated_lbox.to_bytes(4, byteorder='big') + b'jumb' + updated_claim_block_payload
        updated_app11_segment = App11Box(en=last_en)
        updated_app11_segment.payload = updated_claim_block_bytes

        update_range_s = app11_headers[1]['offset']
        update_range_e = app11_headers[1]['offset'] + last_lbox + 16

        # save CAI-injected media
        if len(args.inject) > 0:
            fname, fext = os.path.splitext(args.inject)
            fpath = fname + '-cai' + fext
            with open(fpath, 'wb') as f:
                data_bytes = raw_bytes[:update_range_s] + updated_app11_segment.convert_bytes() + raw_bytes[update_range_e:]
                cai_data_bytes = insert_xmp_key(data_bytes, store_label=store_label)
                f.write(cai_data_bytes)
    else:
        # create a new Store
        cai_store = CaiStore(label=store_label,
                             assertions=assertions,
                             recorder=recorder,
                             parent_claim=parent_claim,
                             key=key)

        # create a new Claim Block Box
        cai_claim_block = CaiClaimBlock()
        cai_claim_block.content_boxes.append(cai_store)
        cai_segment = App11Box()
        cai_segment.payload = cai_claim_block.convert_bytes()

        # save CAI-injected media
        if len(args.inject) > 0:
            fname, fext = os.path.splitext(args.inject)
            fpath = fname + '-cai' + fext
            with open(fpath, 'wb') as f:
                data_bytes = raw_bytes[0:2] + cai_segment.convert_bytes() + raw_bytes[2:]
                cai_data_bytes = insert_xmp_key(data_bytes, store_label=store_label)
                f.write(cai_data_bytes)

    # save CAI metadata
    if len(args.output) > 0:
        with open(args.output, 'w') as f:
            f.write(cai_segment.convert_bytes().hex())


if __name__ == "__main__":
    main()   