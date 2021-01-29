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
    parent_claim = get_xmp_tag(raw_bytes)
    print('parent_claim: ', parent_claim)

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

    if key_filepath != '':
        with open(key_filepath, 'rb') as f:
            key = f.read()
    else:
        key = []

    cai_store = CaiStore(label=store_label,
                         assertions=assertions,
                         recorder=recorder,
                         parent_claim=parent_claim,
                         key=key)
    cai_claim_block = CaiClaimBlock()
    cai_claim_block.content_boxes.append(cai_store)
    cai_segment = App11Box()
    cai_segment.payload = cai_claim_block.convert_bytes()

    # output CAI metadata
    if len(args.output) == 0:
        print(cai_segment.convert_bytes().hex())
    else:
        with open(args.output, 'w') as f:
            f.write(cai_segment.convert_bytes().hex())

    # inject CAI metadata
    if len(args.inject) > 0:
        fname, fext = os.path.splitext(args.inject)
        fpath = fname + '-cai' + fext
        with open(fpath, 'wb') as f:
            data_bytes = raw_bytes[0:2] + cai_segment.convert_bytes() + raw_bytes[2:]
            cai_data_bytes = insert_xmp_key(data_bytes, store_label=store_label)
            f.write(cai_data_bytes)


if __name__ == "__main__":
    main()   