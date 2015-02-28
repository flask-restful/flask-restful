from flask_restful.utils.crypto import encrypt, decrypt


class TestCrypto(object):
    def test_encrypt_decrypt(self):
        key = '0123456789abcdef0123456789abcdef'
        seed = 'deadbeefcafebabe'
        message = 'It should go through'
        assert decrypt(encrypt(message, key, seed), key, seed) == message
