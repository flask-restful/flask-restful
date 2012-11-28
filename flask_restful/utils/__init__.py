from werkzeug.http import HTTP_STATUS_CODES


def http_status_message(code):
    """Maps an HTTP status code to the textual status"""
    return HTTP_STATUS_CODES.get(code, '')


def challenge(authentication, realm):
    """Constructs the string to be sent in the WWW-Authenticate header"""
    return u"{0} realm=\"{1}\"".format(authentication, realm)


def unauthorized(response, realm):
    """ Given a response, change it to ask for credentials"""
    response.headers['WWW-Authenticate'] = challenge("Basic", realm)
    return response


def error_data(code):
    """Constructs a dictionary with status and message for returning in an
    error response"""
    error = {
        'status': code,
        'message': http_status_message(code),
    }
    return error


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

def hal(link, parameters):
    return link.format(**parameters) # FIXME improve that to be really HAL compliant for parsing URLs

def dynamic_import(name):
    """
    :param name: a fully qualified class name like 'a.b.c.klass'
    :return: the class
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
