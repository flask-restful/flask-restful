from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.routing import BuildError
from werkzeug.urls import url_quote


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

from flask.globals import _request_ctx_stack, _app_ctx_stack, request

def rest_url_for(endpoint, **values):
    """A variation of the standard Flask url_for as we don't want the appending of unknown parameters to URLs
    """
    appctx = _app_ctx_stack.top
    reqctx = _request_ctx_stack.top
    if appctx is None:
        raise RuntimeError('Attempted to generate a URL with the application '
                           'context being pushed.  This has to be executed ')

    # If request specific information is available we have some extra
    # features that support "relative" urls.
    if reqctx is not None:
        url_adapter = reqctx.url_adapter
        blueprint_name = request.blueprint
        if not reqctx.request._is_old_module:
            if endpoint[:1] == '.':
                if blueprint_name is not None:
                    endpoint = blueprint_name + endpoint
                else:
                    endpoint = endpoint[1:]
        else:
            # TODO: get rid of this deprecated functionality in 1.0
            if '.' not in endpoint:
                if blueprint_name is not None:
                    endpoint = blueprint_name + '.' + endpoint
            elif endpoint.startswith('.'):
                endpoint = endpoint[1:]
        external = values.pop('_external', False)

    # Otherwise go with the url adapter from the appctx and make
    # the urls external by default.
    else:
        url_adapter = appctx.url_adapter
        if url_adapter is None:
            raise RuntimeError('Application was not able to create a URL '
                               'adapter for request independent URL generation. '
                               'You might be able to fix this by setting '
                               'the SERVER_NAME config variable.')
        external = values.pop('_external', True)

    anchor = values.pop('_anchor', None)
    method = values.pop('_method', None)
    appctx.app.inject_url_defaults(endpoint, values)
    try:
        rv = url_adapter.build(endpoint, values, method=method,
                               force_external=external, append_unknown=False) # <-- This is the change append_unknown=False
    except BuildError, error:
        # We need to inject the values again so that the app callback can
        # deal with that sort of stuff.
        values['_external'] = external
        values['_anchor'] = anchor
        values['_method'] = method
        return appctx.app.handle_url_build_error(error, endpoint, values)

    if anchor is not None:
        rv += '#' + url_quote(anchor)
    return rv
