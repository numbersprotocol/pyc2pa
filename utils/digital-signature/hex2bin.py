#!/usr/bin/python3

import sys


def hex2bin(hexstr):
    data_bytes = bytes.fromhex(hexstr)
    return data_bytes


def main():
    hex_filepath = sys.argv[1]
    bin_filepath = sys.argv[2]

    with open(hex_filepath, 'r') as f:
        data_hex = f.read()

    with open(bin_filepath, 'wb') as f:
        f.write(hex2bin(data_hex))

    print('Convert HEX string to file', bin_filepath)


if __name__ == '__main__':
    main()
