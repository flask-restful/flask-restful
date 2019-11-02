# import pytest
#
# from flask_restful.utils import crypto
#
#
# @pytest.mark.parametrize('input,expected', [
#     (b'test', b'test\0\1\1\1\1\1\1\1\1\1\1\1'),
#     (b'filledto16nopad', b'filledto16nopad\0'),
#     (b'biggerthan16ispaddedtomultipleof16', b'biggerthan16ispaddedtomultipleof16\0\1\1\1\1\1\1\1\1\1\1\1\1\1'),
# ])
# def test_pad(input, expected):
#     assert crypto.pad(input) == expected
#
#
# @pytest.mark.parametrize('input,expected', [
#     (b'test\0\1\1\1\1\1\1', b'test'),
#     (b'another\0\1\1\1\1', b'another'),
#     (b'\1\0wrongway\0\1', b'\1\0wrongway'),
# ])
# def test_strip(input, expected):
#     assert crypto.pad(input) == expected
