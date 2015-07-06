try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from werkzeug.http import HTTP_STATUS_CODES


def http_status_message(code):
    """Maps an HTTP status code to the textual status"""
    return HTTP_STATUS_CODES.get(code, '')


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}
