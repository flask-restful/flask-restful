import unittest
from flask_restful.utils.crypto import encrypt, decrypt


class CryptoTestCase(unittest.TestCase):
    def test_encrypt_decrypt(self):
        key = '0123456789abcdef0123456789abcdef'
        seed = 'deadbeefcafebabe'
        message = 'It should go through'
        self.assertEqual(decrypt(encrypt(message, key, seed), key, seed), message)