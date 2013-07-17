from __future__ import absolute_import
from flask import make_response, current_app
try:
    from ujson import dumps
except ImportError:
    from json import dumps


# This dictionary contains any kwargs that are to be passed to the json.dumps
# function, used below.
settings = {}


def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""

    local_settings = settings.copy()

    dumped = dumps(data, **local_settings)

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp
