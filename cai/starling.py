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
    print('parent_claim: ', parent_claim)

    # get App11 marker segment headers
    app11_headers = get_app11_marker_segment_headers(raw_bytes)
    has_app11_headers = True if len(app11_headers) > 0 else False
    if has_app11_headers:
        print('Find App11 marker segments')
        for i in range(1, len(app11_headers) + 1):
            print('\t{0}'.format(app11_headers[i]))
    else:
        print('No existing App11 marker segment.')

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

    # create a new Store
    cai_store = CaiStore(label=store_label,
                         assertions=assertions,
                         recorder=recorder,
                         parent_claim=parent_claim,
                         key=key)
    if has_app11_headers:
        # get last segment header information
        header_number = len(app11_headers)
        last_le = app11_headers[header_number]['le']
        last_en = app11_headers[header_number]['en']
        last_z = app11_headers[header_number]['z']
        last_lbox = app11_headers[header_number]['lbox']
        last_tbox = app11_headers[header_number]['tbox']
        last_offset = app11_headers[header_number]['offset']
        print('Last Le: {0}, En: {1}, Z: {2}, LBox: {3}, TBox: {4}, offset: {5}'.format(
            last_le, last_en, last_z, last_lbox, last_tbox, last_offset))

        # re-construct Claim Block payload
        claim_block_payload = bytearray()
        for i in range(1, header_number + 1):
            payload_start = app11_headers[i]['offset'] + 20
            payload_end = payload_start + (app11_headers[i]['le'] - 18)
            payload = raw_bytes[payload_start : payload_end]
            claim_block_payload += payload
        print('Claim Block payload size (Description/Content Boxes): {}'.format(len(claim_block_payload)))

        print('Claim Block')
        print('\tSuperbox')
        print('\t\tLBox: {0}, TBox: {1}'.format(last_lbox, last_tbox))

        print('\tDescription Box')
        offset_d = 0
        lbox_d = int.from_bytes(claim_block_payload[offset_d: offset_d + 4], byteorder='big')
        tbox_d = claim_block_payload[offset_d + 4 : offset_d + 8].decode('utf-8')
        print('\t\toffset: {}'.format(offset_d))
        print('\t\tLBox: {0}, TBox: {1}'.format(lbox_d, tbox_d))
        print('\t\tType: {}'.format(claim_block_payload[offset_d + 8 : offset_d + 24].hex()))
        print('\t\tToggles: {}'.format(claim_block_payload[offset_d + 24 : offset_d + 25].hex()))
        print('\t\tLabel: {}'.format(claim_block_payload[offset_d + 25 : lbox_d].decode('utf-8')))

        print('\tContent Box (Stores)')
        print('\t\tStore #1')
        print('\t\tSuperbox')
        offset_s = lbox_d
        lbox_s = int.from_bytes(claim_block_payload[offset_s: offset_s + 4], byteorder='big')
        tbox_s = claim_block_payload[offset_s + 4 : offset_s + 8].decode('utf-8')
        print('\t\t\toffset: {}'.format(offset_s))
        print('\t\t\tLBox: {0}, TBox: {1}'.format(lbox_s, tbox_s))
        print('\t\tDescription Box')
        offset_d = offset_s + 8
        lbox_d = int.from_bytes(claim_block_payload[offset_d: offset_d + 4], byteorder='big')
        tbox_d = claim_block_payload[offset_d + 4 : offset_d + 8].decode('utf-8')
        print('\t\t\toffset: {}'.format(offset_d))
        print('\t\t\tLBox: {0}, TBox: {1}'.format(lbox_d, tbox_d))
        print('\t\t\tType: {}'.format(claim_block_payload[offset_d + 8 : offset_d + 24].hex()))
        print('\t\t\tToggles: {}'.format(claim_block_payload[offset_d + 24 : offset_d + 25].hex()))
        print('\t\t\tLabel: {}'.format(claim_block_payload[offset_d + 25 : offset_d + lbox_d].decode('utf-8')))
        print('\t\tContent Box')
        offset_c = offset_d + lbox_d
        lbox_c = int.from_bytes(claim_block_payload[offset_c: offset_c + 4], byteorder='big')
        tbox_c = claim_block_payload[offset_c + 4 : offset_c + 8].decode('utf-8')
        print('\t\t\toffset: {}'.format(offset_c))
        print('\t\t\tLBox: {0}, TBox: {1}'.format(lbox_c, tbox_c))
        print('\t\t\tType: {}'.format(claim_block_payload[offset_c + 8 : offset_c + 24].hex()))

        print('\t\tStore #2')
        print('\t\tSuperbox')
        offset_s = offset_s + lbox_s
        lbox_s = int.from_bytes(claim_block_payload[offset_s: offset_s + 4], byteorder='big')
        tbox_s = claim_block_payload[offset_s + 4 : offset_s + 8].decode('utf-8')
        print('\t\t\toffset: {}'.format(offset_s))
        print('\t\t\tLBox: {0}, TBox: {1}'.format(lbox_s, tbox_s))
        print('\t\tDescription Box')
        offset_d = offset_s + 8
        lbox_d = int.from_bytes(claim_block_payload[offset_d: offset_d + 4], byteorder='big')
        tbox_d = claim_block_payload[offset_d + 4 : offset_d + 8].decode('utf-8')
        print('\t\t\toffset: {}'.format(offset_d))
        print('\t\t\tLBox: {0}, TBox: {1}'.format(lbox_d, tbox_d))
        print('\t\t\tType: {}'.format(claim_block_payload[offset_d + 8 : offset_d + 24].hex()))
        print('\t\t\tToggles: {}'.format(claim_block_payload[offset_d + 24 : offset_d + 25].hex()))
        print('\t\t\tLabel: {}'.format(claim_block_payload[offset_d + 25 : offset_d + lbox_d].decode('utf-8')))

        print('\t\tStore #3 (newly created)')
        print('\t\tSuperbox')
        store_bytes = cai_store.convert_bytes()
        offset_s = 0
        lbox_s = int.from_bytes(store_bytes[offset_s: offset_s + 4], byteorder='big')
        tbox_s = store_bytes[offset_s + 4 : offset_s + 8].decode('utf-8')
        print('\t\t\toffset: {}'.format(offset_s))
        print('\t\t\tLBox: {0}, TBox: {1}'.format(lbox_s, tbox_s))
        print('\t\tDescription Box')
        offset_d = offset_s + 8
        lbox_d = int.from_bytes(store_bytes[offset_d: offset_d + 4], byteorder='big')
        tbox_d = store_bytes[offset_d + 4 : offset_d + 8].decode('utf-8')
        print('\t\t\tLBox: {0}, TBox: {1}'.format(lbox_d, tbox_d))
        print('\t\t\tType: {}'.format(store_bytes[offset_d + 8 : offset_d + 24].hex()))
        print('\t\t\tToggles: {}'.format(store_bytes[offset_d + 24 : offset_d + 25].hex()))
        print('\t\t\tLabel: {}'.format(store_bytes[offset_d + 25 : offset_d + lbox_d].decode('utf-8')))

        # append new Store bytes
        updated_claim_block_payload = claim_block_payload + store_bytes
        updated_lbox = last_lbox + len(store_bytes)
        #updated_tbox = last_tbox
        updated_claim_block_bytes = updated_lbox.to_bytes(4, byteorder='big') + b'jumb' + updated_claim_block_payload
        updated_app11_segment = App11Box(en=last_en)
        updated_app11_segment.payload = updated_claim_block_bytes

        update_range_s = app11_headers[1]['offset']
        update_range_e = app11_headers[1]['offset'] + last_lbox + 16
        print('Update range: {0} - {1}'.format(update_range_s, update_range_e))

        if len(args.inject) > 0:
            fname, fext = os.path.splitext(args.inject)
            fpath = fname + '-cai' + fext
            with open(fpath, 'wb') as f:
                data_bytes = raw_bytes[:update_range_s] + updated_app11_segment.convert_bytes() + raw_bytes[update_range_e:]
                cai_data_bytes = insert_xmp_key(data_bytes, store_label=store_label)
                f.write(cai_data_bytes)
    else:
        # create a new Claim Block Box
        cai_claim_block = CaiClaimBlock()
        cai_claim_block.content_boxes.append(cai_store)
        cai_segment = App11Box()
        cai_segment.payload = cai_claim_block.convert_bytes()

        # inject CAI metadata
        if len(args.inject) > 0:
            fname, fext = os.path.splitext(args.inject)
            fpath = fname + '-cai' + fext
            with open(fpath, 'wb') as f:
                data_bytes = raw_bytes[0:2] + cai_segment.convert_bytes() + raw_bytes[2:]
                cai_data_bytes = insert_xmp_key(data_bytes, store_label=store_label)
                f.write(cai_data_bytes)

    # output CAI metadata
    #if len(args.output) == 0:
    #    print(cai_segment.convert_bytes().hex())
    #else:
    #    with open(args.output, 'w') as f:
    #        f.write(cai_segment.convert_bytes().hex())


if __name__ == "__main__":
    main()   