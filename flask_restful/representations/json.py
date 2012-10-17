from __future__ import absolute_import
from flask import make_response
from json import dumps


def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""
    resp = make_response(dumps(data), code)
    resp.headers.extend(headers or {})
    return resp
