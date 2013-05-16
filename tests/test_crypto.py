import unittest
from flask_restful.utils.crypto import encrypt, decrypt, create_cipher


class CryptoTestCase(unittest.TestCase):
    def test_encrypt_decrypt(self):
        key = '0123456789abcdef0123456789abcdef'
        seed = 'deadbeefcafebabe'
        message = 'It should go through'
        self.assertEqual(decrypt(encrypt(message, key, seed), key, seed), message)

    def test_parameters_error_case(self):
        key = '0123456789abcdef0123456789abcdef'
        seed = 'deadbeefcafebabe'
        create_cipher(key, seed)  # should pass ok

        self.assertRaises(ValueError, lambda: create_cipher(key, seed[:-1]))
        self.assertRaises(ValueError, lambda: create_cipher(key[:-1], seed))
