from __future__ import absolute_import
from flask import make_response, current_app
from json import dumps


# This dictionary contains any kwargs that are to be passed to the json.dumps
# function, used below.
settings = {}


def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""

    # If we're in debug mode, and the indent is not set, we set it to a
    # reasonable value here.  Note that this won't override any existing value
    # that was set.  We also set the "sort_keys" value.
    local_settings = settings.copy()
    if current_app.debug:
        local_settings.setdefault('indent', 4)
        local_settings.setdefault('sort_keys', True)

    # We also add a trailing newline to the dumped JSON if the indent value is
    # set - this makes using `curl` on the command line much nicer.
    dumped = dumps(data, **local_settings)
    if 'indent' in local_settings:
        dumped += '\n'

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp
