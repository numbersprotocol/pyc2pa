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
import hashlib
import json
import os
import sys

import multibase
import multihash


def encode_hashlink(binary_content, codec='base58btc', to_hexstr=False):
    mh = multihash.Multihash(multihash.Func.sha2_256,
                             hashlib.sha256(binary_content).digest())
    mb = multibase.encode(codec, mh.encode())
    if to_hexstr:
        # return hex string
        return mb.hex()
    else:
        # return bytes
        return mb


def parse_json(fname):
    '''Parse json
    '''
    with open(fname) as f:
        data = json.load(f)

    output = json.dumps(data)

    return output


def convert_to_hex(label, indent = 0, sec_indent = -1):
    '''Convert label into hexadecimals
    '''
    if sec_indent == -1:
        sec_indent = indent
    result = []
    for i in range(len(label)):
        if i % 16 == 0:
            if i != 0:
                indent = sec_indent
        result.append(("%2x" % (ord(label[i]))))

    return result


def format_label_hex(label):
    '''Format to appropriate label hex
    Label hex has 00 at the end signifying \0
    '''
    label_hex = convert_to_hex(label)
    label_hex.append('00')
    return label_hex


def calc_label_hex_size(label):
    '''Calculate label_hex size
    Important for LBox Description Calculations
    '''
    size = len(format_label_hex(label))
    return size


def type(label):
    '''Setting hex for different types
    Description box has type attribute
    '''
    if label == 'assertion':
        type = ['6A', '73', '6F', '6E', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'claim':
        type = ['63', '61', '63', '6c', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'signature':
        type = ['63', '61', '73', '67', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'store':
        type = ['63', '61', '73', '74', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'cai':
        type = ['63', '61', '63', '62', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)
    if label == 'cai.assertion':
        type = ['63', '61', '61', '73', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
        size = len(type)

    return type, size


def toggle():
    '''Set toggle box method
    '''
    type = ['03']
    size = len(type)
    return type, size


def format_hex(hex):
    '''Format l_box hex
    '''
    # remove 0x
    return_hex = hex[2:]
    return return_hex


def get_content_lbox(fname):
    '''Generate l_box hex and size for content box

    @return: (LBox, box size)
    '''
    data = parse_json(fname)

    t_box_size = len(convert_to_hex('json'))
    
    payload_size = len(convert_to_hex(data))

    total_size = 4 + t_box_size + payload_size

    l_box = format_l_box(total_size)

    return l_box, total_size


def get_uuid_content_box():
    '''Generate l_box for size for uuid content
    '''
    t_box_size = len(convert_to_hex('uuid'))
    
    data_hex = ['63', '61', '73', '67', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
    data_hex_size = len(data_hex)

    # signature 1: placeholder signature data as mockup
    # payload_data = ['73', '69', '67', '6e', '61', '74', '75', '72', '65', '20', '70', '6c', '61', '63', '65', '68', '6f', '6c', '64', '65', '72', '3a', '63', '62', '2e', '73', '74', '61', '72', '6c', '69', '6e', '67', '5f', '31', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20']
    # signature 2: real example signature
    payload_data = ['00', '87', '65', '0C', '94', '6D', 'EE', '53', '05', 'B2', 'D8', '87', '19', 'AD', '30', 'A9',
                    '9C', 'AB', 'CF', '3D', 'A2', '00', 'C2', '3D', '61', '71', '0B', 'EB', 'E7', '24', 'D0', 'CD',
                    'B1', 'CC', 'E5', '0C', '3A', '74', '26', '71', '5A', '86', '04', 'DB', '36', '55', 'C5', '30',
                    '62', '7D', 'F1', '6F', 'C0', '33', 'A9', '1A', 'BF', '72', 'E2', '41', 'FD', 'BC', 'D1', '2C',
                    '14', 'F2', 'AB', 'BD', '93', '2B', '20', '52', '86', '7B', '3F', '73', '14', '18', 'C9', '3E',
                    '2A', '5B', 'B9', 'B1', 'E0', '8A', '82', 'E0', '1F', 'B3', 'FA', '69', '6C', '25', 'E0', '40',
                    'D7', 'B3', '5A', '96', '6A', 'D0', '09', '55', 'A4', 'CA', '04', '36', '0C', '13', '00', '2A',
                    'BD', '79', '62', '1C', '95', '17', '9D', '26', '04', '91', 'E4', '94', '7C', '5C', 'DF', 'A7',
                    '90', 'A0', 'A9', '2E', 'F6', '34', '2D', 'EB', 'B4', '7C', 'E5', '9C', '12', 'DD', 'C5', '5F',
                    '74', 'CF', 'BB', '6C', 'FB', 'C5', 'D8', '8C', 'EA', 'A5', 'DF', '7A', '53', '18', '15', '19',
                    'A3', '67', '5D', '38', '33', '85', '8B', 'BF', '8C', 'EE', '3E', '33', '30', '86', '12', '92',
                    'E4', 'A8', 'BF', '76', 'F3', 'C5', 'F3', 'A4', 'D1', '6E', '4B', 'CB', 'C0', 'F1', '35', '80',
                    '5F', 'E7', 'AB', '59', '18', '90', '3F', '2F', 'DC', 'DE', 'CC', '2E', 'D0', '59', '32', 'F8',
                    'E0', '84', 'E0', 'B8', 'BB', '7A', 'CF', '3E', '9E', 'F1', '91', '19', '13', '39', '33', 'CF',
                    '6D', '99', 'C2', 'CA', '6C', 'F9', 'CA', 'A6', '7F', '41', 'BB', '96', 'B4', '8D', 'E4', '50',
                    '81', 'BB', 'E4', '96', 'C4', 'ED', '91', '31', 'AA', '17', 'C1', '45', '07', '1F', '59', '11']
    payload_size = len(payload_data)

    total_size = 4 + t_box_size + data_hex_size + payload_size

    l_box = format_l_box(total_size)

    return l_box, total_size


def get_description_l_box(label, block):
    '''Generate l_box hex and size for description box
    '''
    t_box_size = len(convert_to_hex('jumd'))
    type_size = type(block)[1]
    toggle_size = toggle()[1]
    label_size = calc_label_hex_size(label)

    total_size = 4 + t_box_size + type_size + toggle_size + label_size
    l_box = format_l_box(total_size)

    return l_box, total_size


def get_superbox_l_box(description_size, content_size):
    '''Generate l_box hex and size for superbox
    '''
    t_box_size = len(convert_to_hex('jumb'))

    total_size = 4 + t_box_size + description_size + content_size
    l_box = format_l_box(total_size)

    return l_box, total_size


def cai_store_payload_size(assertion, claim, signature):
    '''Calculate payload size
    '''
    total_size = assertion + claim + signature
    return total_size


def get_l_box_super_cai_store(description_size, payload_size):
    '''Create cai_store l_box hex and size for superbox
    '''
    t_box_size = len(convert_to_hex('jumb'))
    total = 4 + t_box_size + description_size + payload_size

    l_box = format_l_box(total)

    return l_box, total


def create_super_box(l_box):
    '''Create super_box (l_box & t_box)
    '''
    t_box = convert_to_hex('jumb')
    block = l_box + t_box
    return block


def create_description_box(l_box, type_label, label):
    '''Create description_box (l_box, t_box, type, toggle, label)
    '''
    t_box = convert_to_hex('jumd')
    label_hex = format_label_hex(label)
    type_box = type(type_label)[0]

    block = l_box + t_box + type_box + toggle()[0] + label_hex

    return block


def create_content_box(l_box, fname):
    ''' Create content_box (l_box, t_box, data)
    '''
    data = parse_json(fname)
    data_hex = convert_to_hex(data)

    t_box = convert_to_hex('json')
    block = l_box + t_box + data_hex

    return block


def create_uuid_box(l_box):
    '''Create uuid content_box
    '''
    t_box = convert_to_hex('uuid')
    data_hex = ['63', '61', '73', '67', '00', '11', '00', '10', '80', '00', '00', 'aa', '00', '38', '9b', '71']
    # payload_data = ['73', '69', '67', '6e', '61', '74', '75', '72', '65', '20', '70', '6c', '61', '63', '65', '68', '6f', '6c', '64', '65', '72', '3a', '63', '62', '2e', '73', '74', '61', '72', '6c', '69', '6e', '67', '5f', '31', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20']
    payload_data = ['00', '87', '65', '0C', '94', '6D', 'EE', '53', '05', 'B2', 'D8', '87', '19', 'AD', '30', 'A9',
                    '9C', 'AB', 'CF', '3D', 'A2', '00', 'C2', '3D', '61', '71', '0B', 'EB', 'E7', '24', 'D0', 'CD',
                    'B1', 'CC', 'E5', '0C', '3A', '74', '26', '71', '5A', '86', '04', 'DB', '36', '55', 'C5', '30',
                    '62', '7D', 'F1', '6F', 'C0', '33', 'A9', '1A', 'BF', '72', 'E2', '41', 'FD', 'BC', 'D1', '2C',
                    '14', 'F2', 'AB', 'BD', '93', '2B', '20', '52', '86', '7B', '3F', '73', '14', '18', 'C9', '3E',
                    '2A', '5B', 'B9', 'B1', 'E0', '8A', '82', 'E0', '1F', 'B3', 'FA', '69', '6C', '25', 'E0', '40',
                    'D7', 'B3', '5A', '96', '6A', 'D0', '09', '55', 'A4', 'CA', '04', '36', '0C', '13', '00', '2A',
                    'BD', '79', '62', '1C', '95', '17', '9D', '26', '04', '91', 'E4', '94', '7C', '5C', 'DF', 'A7',
                    '90', 'A0', 'A9', '2E', 'F6', '34', '2D', 'EB', 'B4', '7C', 'E5', '9C', '12', 'DD', 'C5', '5F',
                    '74', 'CF', 'BB', '6C', 'FB', 'C5', 'D8', '8C', 'EA', 'A5', 'DF', '7A', '53', '18', '15', '19',
                    'A3', '67', '5D', '38', '33', '85', '8B', 'BF', '8C', 'EE', '3E', '33', '30', '86', '12', '92',
                    'E4', 'A8', 'BF', '76', 'F3', 'C5', 'F3', 'A4', 'D1', '6E', '4B', 'CB', 'C0', 'F1', '35', '80',
                    '5F', 'E7', 'AB', '59', '18', '90', '3F', '2F', 'DC', 'DE', 'CC', '2E', 'D0', '59', '32', 'F8',
                    'E0', '84', 'E0', 'B8', 'BB', '7A', 'CF', '3E', '9E', 'F1', '91', '19', '13', '39', '33', 'CF',
                    '6D', '99', 'C2', 'CA', '6C', 'F9', 'CA', 'A6', '7F', '41', 'BB', '96', 'B4', '8D', 'E4', '50',
                    '81', 'BB', 'E4', '96', 'C4', 'ED', '91', '31', 'AA', '17', 'C1', '45', '07', '1F', '59', '11']
    block = l_box + t_box + data_hex + payload_data

    return block


def make_block(super, description, content):
    '''Create full JUMBF box (super + description + content)
    '''
    block = super + description + content
    return block


def make_store_block(super, desciption):
    '''Create partial JUMBF blox (for cai, cai_store, assertion_store)
    '''
    block = super + desciption
    return block


def create_injection_block(cai_block, store_block, assertion_store, assertion, claim, signature, size):
    '''Create block injections
    '''
    l_box = ['00']
    total_size = 10 + size
    total_size_hex = format_hex(hex(total_size))
    l_box.append(total_size_hex)

    header = ['FF', 'EB']
    c_box = convert_to_hex('JP')
    box_remain = ['00', '01', '00', '00', '00','01']

    block = header + l_box + c_box + box_remain + cai_block + store_block + assertion_store + assertion + claim + signature

    return block


def run_assertion(number_assertions):
    list = []
    label = []

    for i in range(number_assertions):
        fname = input('Assertion JSON: ')
        label_name = input('Assertion Label: ')

        list.append(fname)
        label.append(label_name)

    return list, label


def create_assertions(list, label):
    assertion_blocks = []
    super_l_box_list = []
    superbox_block_list = []
    total = 0

    content_list = []
    desc_list = []

    content_l_list = []
    desc_l_list = []

    for i in list:
        # create content l_box & content block
        content_lbox = get_content_lbox(i)
        content_lbox_block = create_content_box(content_lbox[0], i)
        content_l_list.append(content_lbox)
        content_list.append(content_lbox_block)

    for j in label:
        # create description 1_box & description block
        description_lbox = get_description_l_box(j, 'assertion')
        description_block = create_description_box(description_lbox[0], 'assertion', j)
        desc_l_list.append(description_lbox)
        desc_list.append(description_block)

    for x in range(len(content_l_list)):
        # create superbox 1_box and superbox block
        superbox_lbox = get_superbox_l_box(desc_l_list[x][1], content_l_list[x][1])
        superbox_block = create_super_box(superbox_lbox[0])
        superbox_block_list.append(superbox_block)
        super_l_box_list.append(superbox_lbox[1])

    for a in range(len(content_list)):
        # create complete assertion box
        block = make_block(superbox_block_list[a], desc_list[a], content_list[a])
        assertion_blocks.append(block)

    for i in super_l_box_list:
        total = total + i

    return assertion_blocks, total


def run_claim():
    fname = input("Claim JSON: ")
    return fname


def create_claim(fname):
    # create content l_box & content block
    content_lbox = get_content_lbox(fname)
    content_lbox_block = create_content_box(content_lbox[0], fname)

    # create description 1_box & description block
    description_lbox = get_description_l_box('cai.claim', 'claim')
    description_block = create_description_box(description_lbox[0], 'claim', 'cai.claim')

    # create superbox 1_box and superbox block
    superbox_lbox = get_superbox_l_box(description_lbox[1], content_lbox[1])
    superbox_block = create_super_box(superbox_lbox[0])

    # create complete assertion box
    block = make_block(superbox_block, description_block, content_lbox_block)

    return block, superbox_lbox[1]


def create_signature():
    # create content l_box & content block
    content_lbox = get_uuid_content_box()
    content_lbox_block = create_uuid_box(content_lbox[0])

    # create description 1_box & description block
    description_lbox = get_description_l_box('cai.signature', 'signature')
    description_block = create_description_box(description_lbox[0], 'signature', 'cai.signature')

    # create superbox 1_box and superbox block
    superbox_lbox = get_superbox_l_box(description_lbox[1], content_lbox[1])
    superbox_block = create_super_box(superbox_lbox[0])

    # create complete assertion box
    block = make_block(superbox_block, description_block, content_lbox_block)

    return block, superbox_lbox[1]


def run_store():
    label = input("Store label: ")
    return label


def create_complete(cai_l_box, cai_block, store_block, assertion_block, assertions, claim_block, signature_block):
    size = 10 + cai_l_box
    l_box = format_header_l_box(size)

    header = ['FF', 'EB']
    c_box = convert_to_hex('JP')
    box_remain = ['00', '01', '00', '00', '00','01']

    final_cai_block = header + l_box + c_box + box_remain + cai_block + store_block + assertion_block + assertions + claim_block + signature_block

    return final_cai_block


def format_l_box(total_size):
    '''Create a LBox.
    Meaning: Box length (LBox + TBox + Payload)
    Size: 4 bytes

    @return: a list of strings, every 2-char string shows a byte in Hex.
    '''
    size_hex = format_hex(hex(total_size))

    if len(size_hex) == 2:
        l_box = ['00', '00', '00', size_hex]
    if len(size_hex) == 3:
        l_box = ['00', '00', '0' + size_hex[0], size_hex[1:]]
    if len(size_hex) == 4:
        l_box = ['00', '00', size_hex[0:2], size_hex[2:]]
    if len(size_hex) == 5:
        l_box = ['00', '0' + size_hex[0], size_hex[1:3], size_hex[3:]]
    if len(size_hex) == 6:
        l_box = ['00', size_hex[0:2], size_hex[2:4], size_hex[4:]]
    if len(size_hex) == 7:
        l_box = ['0' + size_hex[0], size_hex[1:3], size_hex[3:5], size_hex[5:]]
    if len(size_hex) == 8:
        l_box = [size_hex[0:2], size_hex[2:4], size_hex[4:6], size_hex[6:]]

    return l_box


def format_header_l_box(total_size):
    size_hex = format_hex(hex(total_size))
    if len(size_hex) == 2:
        l_box = ['00', size_hex]
    if len(size_hex) == 3:
        l_box = ['0' + size_hex[0], size_hex[1:]]
    if len(size_hex) == 4:
        l_box = [size_hex[0:2], size_hex[2:]]

    return l_box


def process(assertions, claim, store_label):
    ass = assertions

    assertions = []
    for i in ass[0]:
        assertions = assertions + i

    claim = claim

    signature = create_signature()

    # create assertion block
    ass_desc = get_description_l_box('cai.assertions', 'cai.assertion')
    ass_desc_block = create_description_box(ass_desc[0], 'cai.assertion', 'cai.assertions')
    ass_super = get_superbox_l_box(ass_desc[1], ass[1])
    ass_super_block = create_super_box(ass_super[0])

    ass_block = make_store_block(ass_super_block, ass_desc_block)

    payload_size = cai_store_payload_size(ass_super[1], claim[1], signature[1])

    label = store_label
    store_desc = get_description_l_box(label, 'store')
    store_desc_block = create_description_box(store_desc[0], 'store', label)
    store_super = get_l_box_super_cai_store(store_desc[1], payload_size)
    store_super_block = create_super_box(store_super[0])
    store_block = make_store_block(store_super_block, store_desc_block)

    cai_payload = store_super[1]
    cai_desc = get_description_l_box('cai', 'cai')
    cai_desc_block = create_description_box(cai_desc[0], 'cai', 'cai')
    cai_super = get_l_box_super_cai_store(cai_desc[1], cai_payload)
    cai_super_block = create_super_box(cai_super[0])
    cai_block = make_store_block(cai_super_block, cai_desc_block)

    injection = create_complete(cai_super[1], cai_block, store_block, ass_block, assertions, claim[0], signature[0])
    print(injection)
    print(len(injection))


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
        '-c', '--claim',
        help='Claim filepath.')
    ap.add_argument(
        '--store-label',
        default='cb.starling_1',
        help='Store label. Default: cb.starling_1')
    ap.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Debug mode toggle')
    return ap.parse_args()


def main():
    args = parse_args()

    if len(args.assertion) > 0:
        assertion_filepaths = args.assertion
        assertion_labels = [os.path.splitext(os.path.basename(a))[0]
                            for a in assertion_filepaths]
        claim_filepath = args.claim
        store_label = args.store_label
    else:
        number_assertions = int(input('How many assertions? '))
        if number_assertions > 0:
            assertion_filepaths, assertion_labels = run_assertion(
                                                        number_assertions)
        else:
            print("Not a valid number of assertions")

        claim_filepath = run_claim()
        store_label = run_store()

    if args.debug:
        print(args)
        print(assertion_filepaths)
        print(assertion_labels)
        print(claim_filepath)
        print(store_label)

    assertions = create_assertions(assertion_filepaths, assertion_labels)
    claim = create_claim(claim_filepath)
    process(assertions, claim, store_label)


def main():
    script = sys.argv[0]
    process()


if __name__ == "__main__":
    main()
