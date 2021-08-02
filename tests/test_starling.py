import unittest
import requests
import hashlib

from cai.jumbf import json_to_bytes
from cai.starling import Starling


class TestStarling(unittest.TestCase):
    def setUp(self):
        self.photo_url = 'https://http.cat/404'
        self.photo_filename = '404.jpg'
        self.photo_bytes = requests.get(self.photo_url).content
        self.assertions = {
            'adobe.asset.info': {
                'type': '.json',
                'data_bytes': json_to_bytes({'title': 'some-photo.jpg'})
            },
            'cai.location.broad': {
                'type': '.json',
                'data_bytes': json_to_bytes({'location': 'Somewhere'})
            },
            'cai.rights': {
                'type': '.json',
                'data_bytes': json_to_bytes({'copyright': 'Someone'})
            },
            'cai.claim.thumbnail.jpg.jpg': {
                'type': '.jpg',
                'data_bytes': self.photo_bytes
            },
            'cai.acquisition.thumbnail.jpg.jpg': {
                'type': '.jpg',
                'data_bytes': self.photo_bytes
            }
        }

    def test_single_claim_injection(self):
        testing_image_hash = ('afdff82350cbd714'
                              'ad5518de082187ce'
                              '973d060b4f267e7d'
                              '902e6c317de6ce4a')
        starling = Starling(
            self.photo_bytes, self.photo_filename, self.assertions,
            'cb.numbersprotocol_1',
            'Capture App: 5c2cefaa-fb4e-4d77-991c-5046729b295f', '', '')
        starling_cai_bytes = starling.cai_injection()

        m = hashlib.sha256()
        m.update(starling_cai_bytes)

        self.assertEqual(testing_image_hash, m.hexdigest())

    def test_multiple_claim_injection(self):
        testing_image_hash = ('79294181f1dba5f9'
                              '5e096a66ed04719e'
                              'b5e9ae76c1f5f0b7'
                              '6d4d2922e362ee75')

        # store label for each injection needs to be different
        # otherwise the multiple injection will not be recognized by verifier
        store_labels = [
            'cb.Authmedia_1',
            'cb.IOTAIntegrityChain_2',
            'cb.ThunderCoreNFTChain_3',
        ]

        starling_cai_bytes = self.photo_bytes
        for i in range(3):
            starling = Starling(
                starling_cai_bytes, self.photo_filename, self.assertions,
                store_labels[i],
                'Capture App: 5c2cefaa-fb4e-4d77-991c-5046729b295f', '', '')
            starling_cai_bytes = starling.cai_injection()

        m = hashlib.sha256()
        m.update(starling_cai_bytes)

        self.assertEqual(testing_image_hash, m.hexdigest())


if __name__ == '__main__':
    unittest.main()
