import io
import json
import unittest

from c2pa.core import CaiAssertionStore
from c2pa.core import CaiClaim
from c2pa.core import CaiClaimBlock
from c2pa.core import CaiClaimSignature
from c2pa.core import CaiStore
from c2pa.jumbf import App11Box
from c2pa.jumbf import create_json_superbox
from c2pa.jumbf import json_to_bytes


class TestCaiBox(unittest.TestCase):
    def test_cai_assertion_store(self):
        testing_assertion = (
            '000000466a756d62000000296a756d646a736f6e00110010800000aa00389b71'
            '03737461726c696e672e6d6f636b757000000000156a736f6e7b22666f6f223a'
            '22626172227d'
        )

        testing_assertion_store = (
            '000000766a756d62000000286a756d646361617300110010800000aa00389b71'
            '036361692e617373657274696f6e7300000000466a756d62000000296a756d64'
            '6a736f6e00110010800000aa00389b7103737461726c696e672e6d6f636b7570'
            '00000000156a736f6e7b22666f6f223a22626172227d'
        )

        data = {'foo': 'bar'}
        data_bytes = json_to_bytes(data)

        assertions = []
        assertions.append(create_json_superbox(data_bytes, 'starling.mockup'))

        cai_assertion_store = CaiAssertionStore(assertions)

        print('\n[ CAI Assertion ]')
        assertion = cai_assertion_store.content_boxes[0]
        for content_box in assertion.content_boxes:
            content_box.print_box()
        assertion.description_box.print_box()
        assertion.print_box()

        self.assertEqual(assertion.convert_bytes(),
                         bytes.fromhex(testing_assertion))

        print('\n[ CAI Assertion Store ]')
        cai_assertion_store.description_box.print_box()
        cai_assertion_store.print_box()

        self.assertEqual(cai_assertion_store.convert_bytes(),
                         bytes.fromhex(testing_assertion_store))

    def test_cai_claim(self):
        testing_claim = (
            '000000406a756d62000000236a756d646361636c00110010800000aa00389b71'
            '036361692e636c61696d00000000156a736f6e7b22666f6f223a22626172227d'
        )

        data = {'foo': 'bar'}
        data_bytes = json_to_bytes(data)

        assertions = []
        assertions.append(create_json_superbox(data_bytes, 'starling.mockup'))

        cai_claim = CaiClaim(assertions)

        print('\n[ CAI Claim ]')
        for content_box in cai_claim.content_boxes:
            content_box.print_box()
        cai_claim.description_box.print_box()
        cai_claim.print_box()

        self.assertEqual(cai_claim.convert_bytes(),
                         bytes.fromhex(testing_claim))

    def test_cai_claim_signature(self):
        testing_claim_signature = (
            '000000446a756d62000000276a756d646361736700110010800000aa00389b71'
            '036361692e7369676e617475726500000000156a736f6e7b22666f6f223a2262'
            '6172227d'
        )

        cai_claim_signature = CaiClaimSignature()

        print('\n[ CAI Claim Signature ]')
        for content_box in cai_claim_signature.content_boxes:
            content_box.print_box()
        cai_claim_signature.description_box.print_box()
        cai_claim_signature.print_box()

        #self.assertEqual(cai_claim_signature.convert_bytes(),
        #                 bytes.fromhex(testing_claim_signature))

    def test_cai_store(self):
        testing_store = (
            '000001296a756d62000000276a756d646361737400110010800000aa00389b71'
            '0363622e737461726c696e675f3100000000766a756d62000000286a756d6463'
            '61617300110010800000aa00389b71036361692e617373657274696f6e730000'
            '0000466a756d62000000296a756d646a736f6e00110010800000aa00389b7103'
            '737461726c696e672e6d6f636b757000000000156a736f6e7b22666f6f223a22'
            '626172227d000000406a756d62000000236a756d646361636c00110010800000'
            'aa00389b71036361692e636c61696d00000000156a736f6e7b22666f6f223a22'
            '626172227d000000446a756d62000000276a756d646361736700110010800000'
            'aa00389b71036361692e7369676e617475726500000000156a736f6e7b22666f'
            '6f223a22626172227d'
        )

        data = {'foo': 'bar'}
        data_bytes = json_to_bytes(data)

        assertions = []
        assertions.append(create_json_superbox(data_bytes, 'starling.mockup'))

        cai_store = CaiStore(assertions=assertions)

        print('\n[ CAI Store ]')
        for content_box in cai_store.content_boxes:
            content_box.description_box.print_box()
            content_box.print_box()
        cai_store.description_box.print_box()
        cai_store.print_box()

        #self.assertEqual(cai_store.convert_bytes(),
        #                 bytes.fromhex(testing_store))

    def test_cai_claim_block(self):
        testing_claim_block = (
            '0000014e6a756d620000001d6a756d646361636200110010800000aa00389b71'
            '0363616900000001296a756d62000000276a756d646361737400110010800000'
            'aa00389b710363622e737461726c696e675f3100000000766a756d6200000028'
            '6a756d646361617300110010800000aa00389b71036361692e61737365727469'
            '6f6e7300000000466a756d62000000296a756d646a736f6e00110010800000aa'
            '00389b7103737461726c696e672e6d6f636b757000000000156a736f6e7b2266'
            '6f6f223a22626172227d000000406a756d62000000236a756d646361636c0011'
            '0010800000aa00389b71036361692e636c61696d00000000156a736f6e7b2266'
            '6f6f223a22626172227d000000446a756d62000000276a756d64636173670011'
            '0010800000aa00389b71036361692e7369676e617475726500000000156a736f'
            '6e7b22666f6f223a22626172227d'
        )

        data = {'foo': 'bar'}
        data_bytes = json_to_bytes(data)

        assertions = []
        assertions.append(create_json_superbox(data_bytes, 'starling.mockup'))

        cai_store = CaiStore(assertions=assertions)
        cai_claim_block = CaiClaimBlock()
        cai_claim_block.content_boxes.append(cai_store)

        print('\n[ CAI Claim Block ]')
        for content_box in cai_claim_block.content_boxes:
            content_box.description_box.print_box()
            content_box.print_box()
        cai_claim_block.description_box.print_box()
        cai_claim_block.print_box()

        #self.assertEqual(cai_claim_block.convert_bytes(),
        #                 bytes.fromhex(testing_claim_block))

    def test_app11_segment(self):
        testing_app11_segment = (
            'ffeb01584a500001000000010000014e6a756d620000001d6a756d6463616362'
            '00110010800000aa00389b710363616900000001296a756d62000000276a756d'
            '646361737400110010800000aa00389b710363622e737461726c696e675f3100'
            '000000766a756d62000000286a756d646361617300110010800000aa00389b71'
            '036361692e617373657274696f6e7300000000466a756d62000000296a756d64'
            '6a736f6e00110010800000aa00389b7103737461726c696e672e6d6f636b7570'
            '00000000156a736f6e7b22666f6f223a22626172227d000000406a756d620000'
            '00236a756d646361636c00110010800000aa00389b71036361692e636c61696d'
            '00000000156a736f6e7b22666f6f223a22626172227d000000446a756d620000'
            '00276a756d646361736700110010800000aa00389b71036361692e7369676e61'
            '7475726500000000156a736f6e7b22666f6f223a22626172227d'
        )

        data = {'foo': 'bar'}
        data_bytes = json_to_bytes(data)

        assertions = []
        assertions.append(create_json_superbox(data_bytes, 'starling.mockup'))

        cai_store = CaiStore(assertions=assertions)
        cai_claim_block = CaiClaimBlock()
        cai_claim_block.content_boxes.append(cai_store)

        print('\n[ App11 Segment ]')
        cai_claim_block.print_box()
        app11_segment = App11Box()
        app11_segment.payload = cai_claim_block.convert_bytes()
        print('\tbytes:', app11_segment.convert_bytes().hex())

        #self.assertEqual(app11_segment.convert_bytes(),
        #                 bytes.fromhex(testing_app11_segment))


if __name__ == '__main__':
    unittest.main()
