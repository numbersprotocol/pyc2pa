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

'''Implementation of ISO/IEC 19566-5:2019(E)
Information technologies - JPEG systems
Part 5: JPEG universal metadata box format (JUMBF)
'''

# Spec B.1
Jumbf_content_types = {
    'codestream': '6579d6fbdba2446bb2ac1b82feeb89d1',
    'xml'       : '786d6c2000110010800000aa00389b71',
    'json'      : '6a736f6e00110010800000aa00389b71',
    'uuid'      : '7575696400110010800000aa00389b71',
}


Cai_content_types = {
    'claim_block'    : '6361636200110010800000aa00389b71',
    'store'          : '6361737400110010800000aa00389b71',
    'assertion_store': '6361617300110010800000aa00389b71',
    'claim'          : '6361636c00110010800000aa00389b71',
    'claim_signature': '6361736700110010800000aa00389b71',
}


class Box(object):
    def __init__(self):
        self.t_box = b'aaaaaaaa'
        self.payload = b''

    def get_size(self):
        # Calculate box size dynamically.
        # 8 is from l_box (4) + t_box (4)
        return 8 + len(self.payload)
    
    def set_payload(self):
        pass

    def convert_bytes(self):
        self.set_payload()

        # Calculate box size dynamically.
        # 8 is from l_box (4) + t_box (4)
        l_box = self.get_size()
        return (l_box).to_bytes(4, byteorder='big') + self.t_box + self.payload


class SuperBox(Box):
    def __init__(self):
        super(SuperBox, self).__init__()
        self.t_box = bytes.fromhex('6a756d62')
        self.description_box = None
        self.content_boxes = []

    def set_payload(self):
        self.payload = self.description_box.convert_bytes()
        for content_box in self.content_boxes:
            self.payload += content_box.convert_bytes()


class DescriptionBox(Box):
    def __init__(self, content_type='json', label=''):
        super(DescriptionBox, self).__init__()
        self.t_box = bytes.fromhex('6a756d64')
        self.db_type = bytes.fromhex(Jumbf_content_types[content_type])
        # Spec A.3, Table A.2
        self.db_toggle = b'\x03'
        # Add 0 for CAI spec
        self.db_label = label.encode('utf-8') + b'\x00'

    def set_payload(self):
        print(self.db_type)
        print(self.db_toggle)
        print(self.db_label)
        self.payload = self.db_type + self.db_toggle + self.db_label

    def print_box(self):
        print('t_box:', self.t_box)
        print('payload:', self.payload)
        print('\tdb_type:', self.db_type)
        print('\tdb_toggle:', self.db_toggle)
        print('\tdb_label:', self.db_label)


class ContentBox(Box):
    def __init__(self, content_type='json'):
        super(ContentBox, self).__init__()
        self.t_box = content_type.encode('utf-8')