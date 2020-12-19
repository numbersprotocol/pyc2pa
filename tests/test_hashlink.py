import unittest

from caitools.cai_tool import encode_hashlink


class TestEncodeHashlink(unittest.TestCase):
    def test_hashlink(self):
        testing_data = b'Hello World!'
        mh = encode_hashlink(testing_data)
        self.assertEqual(mh, b'zQmWvQxTqbG2Z9HPJgG57jjwR154cKhbtJenbyYTWkjgF3e')


if __name__ == '__main__':
    unittest.main()
