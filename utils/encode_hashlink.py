import argparse
import hashlib
import os

import multibase
import multihash


'''
Example
    input: {"copyright":"Starling Labs"} (29)
    output: mEiBChBVd8onGt71mftnzv4e9C6m67kAeHCK1K8TDtuKfDA
'''


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


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '-i', '--input',
        help=('Input filepath. '
              'Creating the hashlink parameter for the input file.'),
        )
    return ap.parse_args()


if __name__ == '__main__':
    args = parse_args()
    filepath = args.input
    with open(filepath, 'rb') as f:
        # remove potential newline '0x0a' added by text editor
        data_bytes = f.read().strip()

        print('Input file: {0}\nhashlink param: {1}'.format(
            os.path.basename(filepath),
            encode_hashlink(data_bytes, to_hexstr=True)
        ))