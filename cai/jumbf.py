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

import json

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


class Box(object):
    '''
    t_box: HEX string
    payload: bytes
    '''
    def __init__(self):
        self.t_box = ''
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
        l_box = self.get_size().to_bytes(4, byteorder='big')
        t_box = bytes.fromhex(self.t_box)

        return l_box + t_box + self.payload


class SuperBox(Box):
    def __init__(self):
        super(SuperBox, self).__init__()
        self.t_box = 'jumb'.encode('utf-8').hex()
        self.description_box = None
        self.content_boxes = []

    def set_payload(self):
        self.payload = self.description_box.convert_bytes()
        for content_box in self.content_boxes:
            self.payload += content_box.convert_bytes()

    def print_box(self):
        print('\nSuperboxBox')
        print('\tt_box:', self.t_box)
        print('\tbytes:', self.convert_bytes().hex())


class DescriptionBox(Box):
    '''
    db_type: HEX string
    db_toggle: integer
    db_label: string
    '''
    def __init__(self, content_type=Jumbf_content_types['json'], label=''):
        super(DescriptionBox, self).__init__()
        self.t_box = 'jumd'.encode('utf-8').hex()
        self.db_type = content_type
        # Spec A.3, Table A.2
        self.db_toggle = 3
        # Add 0 for CAI spec
        self.db_label = label

    def set_payload(self):
        db_type = bytes.fromhex(self.db_type)
        db_toggle = (self.db_toggle).to_bytes(1, byteorder='big')
        db_label = self.db_label.encode('utf-8') + b'\x00'
        self.payload = db_type + db_toggle + db_label

    def print_box(self):
        print('\nDescriptionBox')
        print('\tt_box:', self.t_box)
        print('\tpayload:', self.payload.hex())
        print('\t\tdb_type:', self.db_type)
        print('\t\tdb_toggle:', self.db_toggle)
        print('\t\tdb_label:', self.db_label)
        print('\tbytes:', self.convert_bytes().hex())


class ContentBox(Box):
    def __init__(self, t_box_type='json'):
        super(ContentBox, self).__init__()
        self.t_box = t_box_type.encode('utf-8').hex()

    def print_box(self):
        print('\nContentBox')
        print('\tt_box:', self.t_box)
        print('\tpayload:', self.payload.hex())
        print('\tbytes:', self.convert_bytes().hex())


class App11Box(object):
    def __init__(self):
        self.marker = 'FFEB'
        self.ci = 'JP'.encode('utf-8').hex()
        self.en = 1
        self.z = 1
        self.payload = b''

    def get_size(self):
        return len(self.convert_bytes())

    def _split_payload(self):
        # Le (2B) + CI (2B) + En (4B) + Z (4B) + LBox (4B) + TBox (4B) = 18
        # Le_max = 65535
        # segment payload size = 65535 - 18 = 65517

        segment_payload_size = 65517

        # Preserve LBox and TBox
        # We will split original payload to multiple sub-payloads,
        # and add both LBox and TBox to each of the sub-payloads.
        lbox = self.payload[:4]
        tbox = self.payload[4:8]
        payload = self.payload[8:]

        segment_superboxes = []
        while len(payload) > segment_payload_size:
            segment_superboxes.append(lbox + tbox + payload[:segment_payload_size])
            payload = payload[segment_payload_size:]
        segment_superboxes.append(lbox + tbox + payload)
        return segment_superboxes

    def convert_bytes(self):
        # Reminder: Superbox = LBox + TBox + Payload
        segment_superboxes = self._split_payload()
        total_bytes = b''
        self.z = 1
        for superbox in segment_superboxes:
            marker = bytes.fromhex(self.marker)
            ci = bytes.fromhex(self.ci)
            en = self.en.to_bytes(2, byteorder='big')
            z = self.z.to_bytes(4, byteorder='big')

            # marker is not included
            length = 2 + len(ci) + len(en) + len(z) + len(superbox)
            le = length.to_bytes(2, byteorder='big')
            total_bytes += marker + le + ci + en + z + superbox
            self.z += 1
        return total_bytes


def create_single_content_superbox(content=b'',
                         t_box_type='',
                         content_type='',
                         label=''):
    c_box = ContentBox(t_box_type=t_box_type)
    c_box.payload = content
    d_box = DescriptionBox(content_type=content_type, label=label)
    s_box = SuperBox()
    s_box.description_box = d_box
    s_box.content_boxes.append(c_box)
    return s_box


def create_json_superbox(content=b'', label=''):
    return create_single_content_superbox(
        content=content,
        t_box_type='json',
        content_type=Jumbf_content_types['json'],
        label=label)


def create_codestream_superbox(content=b'', label=''):
    return create_single_content_superbox(
        content=content,
        t_box_type='jp2c',
        content_type=Jumbf_content_types['codestream'],
        label=label)


def json_to_bytes(json_object):
    return json.dumps(json_object, separators=(',',':')).encode('utf-8')