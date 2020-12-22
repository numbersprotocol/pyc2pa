import unittest

from caitools.jumbf import App11Box
from caitools.jumbf import Box
from caitools.jumbf import ContentBox
from caitools.jumbf import DescriptionBox
from caitools.jumbf import SuperBox

from caitools.jumbf import create_json_superbox


class TestBox(unittest.TestCase):
    def test_convert_bytes(self):
        testing_data = b'\x00\x00\x00\x08'

        box = Box()
        box_bytes = box.convert_bytes()
        print(box_bytes)

        self.assertEqual(box_bytes, testing_data)


class TestContentBox(unittest.TestCase):
    def test_convert_bytes(self):
        testing_data = b'\x00\x00\x00\x08json'

        box = ContentBox()
        box_bytes = box.convert_bytes()
        print(box_bytes)

        self.assertEqual(box_bytes, testing_data)

        box.payload = b'foobar'
        testing_data = b'\x00\x00\x00\x0ejson' + box.payload
        box_bytes = box.convert_bytes()
        print(box_bytes)

        self.assertEqual(box_bytes, testing_data)


class TestDescriptionBox(unittest.TestCase):
    def test_convert_bytes(self):
        testing_t_box = '6a756d64'

        box = DescriptionBox(label='starling')
        box_bytes = box.convert_bytes()
        print(box_bytes)
        box.print_box()

        self.assertEqual(box.t_box, testing_t_box)


class TestSuperBox(unittest.TestCase):
    def test_convert_bytes(self):
        testing_t_box = '6a756d62'

        d_box = DescriptionBox()
        d_box_bytes = d_box.convert_bytes()
        print('d_box:', d_box_bytes.hex())

        c_box = ContentBox()
        c_box_bytes = c_box.convert_bytes()
        print('c_box:', c_box_bytes.hex())

        s_box = SuperBox()
        s_box.description_box = d_box
        s_box.content_boxes.append(c_box)
        s_box_bytes = s_box.convert_bytes()
        print('s_box:', s_box_bytes.hex())

        self.assertEqual(s_box.t_box, testing_t_box)

    def test_json_superbox(self):
        s_box = create_json_superbox(b'foobar', 'starling')
        print(s_box.convert_bytes().hex())


class TestApp11Box(unittest.TestCase):
    def test_convert_bytes(self):
        s_box = create_json_superbox(b'foobar', 'starling')
        app11_box = App11Box()
        app11_box.payload = s_box.convert_bytes()
        box_bytes = app11_box.convert_bytes()

        self.assertEqual(box_bytes[0:2], b'\xff\xeb')
        self.assertEqual(box_bytes[4:6], b'\x4a\x50')
        self.assertEqual(box_bytes[6:8], b'\x00\x01')
        self.assertEqual(box_bytes[8:12], b'\x00\x00\x00\x01')


if __name__ == '__main__':
    unittest.main()
