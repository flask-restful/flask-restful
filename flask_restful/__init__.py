import difflib
from functools import wraps, partial
import re
from flask import request, Response, url_for
from flask import abort as original_flask_abort
from flask.views import MethodView
from flask.signals import got_request_exception
from werkzeug.exceptions import HTTPException, MethodNotAllowed, NotFound
from werkzeug.http import HTTP_STATUS_CODES
from flask.ext.restful.utils import unauthorized, error_data, unpack
from flask.ext.restful.representations.json import output_json
import sys

try:
    #noinspection PyUnresolvedReferences
    from collections import OrderedDict
except ImportError:
    from .utils.ordereddict import OrderedDict

__all__ = ('Api', 'Resource', 'marshal', 'marshal_with', 'abort')


def abort(http_status_code, **kwargs):
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.
    """
    #noinspection PyUnresolvedReferences
    try:
        original_flask_abort(http_status_code)
    except HTTPException as e:
        if len(kwargs):
            e.data = kwargs
        raise e

DEFAULT_REPRESENTATIONS = {'application/json': output_json}


class Api(object):
    """
    The main entry point for the application.
    You need to initialize it with a Flask Application: ::

    >>> app = Flask(__name__)
    >>> api = restful.Api(app)

    Alternatively, you can use :meth:`init_app` to set the Flask application
    after it has been constructed.

    :param app: the Flask application object
    :type app: flask.Flask
    :param prefix: Prefix all routes with a value, eg v1 or 2010-04-01
    :type prefix: str
    :param default_mediatype: The default media type to return
    :type default_mediatype: str
    :param decorators: Decorators to attach to every resource
    :type decorators: list
    :param catch_all_404s: Use :meth:`handle_error`
        to handle 404 errors throughout your app
    :type catch_all_404s: bool

    """

    def __init__(self, app=None, prefix='',
                 default_mediatype='application/json', decorators=None,
                 catch_all_404s=False):
        self.representations = dict(DEFAULT_REPRESENTATIONS)
        self.urls = {}
        self.prefix = prefix
        self.default_mediatype = default_mediatype
        self.decorators = decorators if decorators else []
        self.catch_all_404s = catch_all_404s

        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        """Initialize this class with the given :class:`flask.Flask`
        application object.

        :param app: the Flask application object
        :type app: flask.Flask

        Examples::

            api = Api()
            api.init_app(app)
            api.add_resource(...)

        """
        self.app = app
        self.endpoints = set()
        app.handle_exception = partial(self.error_router, app.handle_exception)
        app.handle_user_exception = partial(self.error_router, app.handle_user_exception)


    def _should_use_fr_error_handler(self):
        """ Determine if error should be handled with FR or default Flask

        The goal is to return Flask error handlers for non-FR-related routes,
        and FR errors (with the correct media type) for FR endpoints. This
        method currently handles 404 and 405 errors.

        :return: bool
        """
        adapter = self.app.create_url_adapter(request)

        try:
            adapter.match()
        except MethodNotAllowed as e:
            # Check if the other HTTP methods at this url would hit the Api
            valid_route_method = e.valid_methods[0]
            rule, _ = adapter.match(method=valid_route_method, return_rule=True)
            return rule.endpoint in self.endpoints
        except NotFound:
            return self.catch_all_404s
        except:
            # Werkzeug throws other kinds of exceptions, such as Redirect
            pass


    def _has_fr_route(self):
        """Encapsulating the rules for whether the request was to a Flask endpoint"""
        # 404's, 405's, which might not have a url_rule
        if self._should_use_fr_error_handler():
            return True
        # for all other errors, just check if FR dispatched the route
        return request.url_rule and request.url_rule.endpoint in self.endpoints

    def error_router(self, original_handler, e):
        """This function decides whether the error occured in a flask-restful
        endpoint or not. If it happened in a flask-restful endpoint, our
        handler will be dispatched. If it happened in an unrelated view, the
        app's original error handler will be dispatched.

        :param original_handler: the original Flask error handler for the app
        :type original_handler: function
        :param e: the exception raised while handling the request
        :type e: Exception

        """
        if self._has_fr_route():
            return self.handle_error(e)
        return original_handler(e)

    def handle_error(self, e):
        """Error handler for the API transforms a raised exception into a Flask
        response, with the appropriate HTTP status code and body.

        :param e: the raised Exception object
        :type e: Exception

        """
        got_request_exception.send(self.app, exception=e)

        if not hasattr(e, 'code') and self.app.propagate_exceptions:
            exc_type, exc_value, tb = sys.exc_info()
            if exc_value is e:
                exc = exc_type(exc_value)
                exc.__traceback__ = tb
                raise exc
            else:
                raise e

        code = getattr(e, 'code', 500)
        data = getattr(e, 'data', error_data(code))

        if code >= 500:

            # There's currently a bug in Python3 that disallows calling
            # logging.exception() when an exception hasn't actually be raised
            if sys.exc_info() == (None, None, None):
                self.app.logger.error("Internal Error")
            else:
                self.app.logger.exception("Internal Error")

        if code == 404 and ('message' not in data or
                            data['message'] == HTTP_STATUS_CODES[404]):
            rules = dict([(re.sub('(<.*>)', '', rule.rule), rule.rule)
                          for rule in self.app.url_map.iter_rules()])
            close_matches = difflib.get_close_matches(request.path, rules.keys())
            if close_matches:
                # If we already have a message, add punctuation and continue it.
                if "message" in data:
                    data["message"] += ". "
                else:
                    data["message"] = ""

                data['message'] += 'You have requested this URI [' + request.path + \
                        '] but did you mean ' + \
                        ' or '.join((rules[match]
                                     for match in close_matches)) + ' ?'

        resp = self.make_response(data, code)

        if code == 401:
            resp = unauthorized(resp,
                self.app.config.get("HTTP_BASIC_AUTH_REALM", "flask-restful"))

        return resp

    def mediatypes_method(self):
        """Return a method that returns a list of mediatypes
        """
        return lambda resource_cls: self.mediatypes() + [self.default_mediatype]

    def add_resource(self, resource, *urls, **kwargs):
        """Adds a resource to the api.

        :param resource: the class name of your resource
        :type resource: :class:`Resource`
        :param urls: one or more url routes to match for the resource, standard
                     flask routing rules apply.  Any url variables will be
                     passed to the resource method as args.
        :type urls: str

        :param endpoint: endpoint name (defaults to :meth:`Resource.__name__.lower`
            Can be used to reference this route in :class:`fields.Url` fields
        :type endpoint: str

        Additional keyword arguments not specified above will be passed as-is
        to :meth:`flask.Flask.add_url_rule`.

        Examples::

            api.add_resource(HelloWorld, '/', '/hello')
            api.add_resource(Foo, '/foo', endpoint="foo")
            api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

        """
        endpoint = kwargs.pop('endpoint', None) or resource.__name__.lower()
        self.endpoints.add(endpoint)

        if endpoint in self.app.view_functions.keys():
            previous_view_class = self.app.view_functions[endpoint].__dict__['view_class']

            # if you override the endpoint with a different class, avoid the collision by raising an exception
            if previous_view_class != resource:
                raise ValueError('This endpoint (%s) is already set to the class %s.' % (endpoint, previous_view_class.__name__))

        resource.mediatypes = self.mediatypes_method()  # Hacky
        resource.endpoint = endpoint
        resource_func = self.output(resource.as_view(endpoint))

        for decorator in self.decorators:
            resource_func = decorator(resource_func)


        for url in urls:
            self.app.add_url_rule(self.prefix + url, view_func=resource_func, **kwargs)

    def output(self, resource):
        """Wraps a resource (as a flask view function), for cases where the
        resource does not directly return a response object

        :param resource: The resource as a flask view function
        """
        @wraps(resource)
        def wrapper(*args, **kwargs):
            resp = resource(*args, **kwargs)
            if isinstance(resp, Response):  # There may be a better way to test
                return resp
            data, code, headers = unpack(resp)
            return self.make_response(data, code, headers=headers)
        return wrapper

    def url_for(self, resource, **values):
        """Generates a URL to the given resource."""
        return url_for(resource.endpoint, **values)
        
    def make_response(self, data, *args, **kwargs):
        """Looks up the representation transformer for the requested media
        type, invoking the transformer to create a response object. This
        defaults to (application/json) if no transformer is found for the
        requested mediatype.

        :param data: Python object containing response data to be transformed
        """
        for mediatype in self.mediatypes() + [self.default_mediatype]:
            if mediatype in self.representations:
                resp = self.representations[mediatype](data, *args, **kwargs)
                resp.headers['Content-Type'] = mediatype
                return resp

    def mediatypes(self):
        """Returns a list of requested mediatypes sent in the Accept header"""
        return [h for h, q in request.accept_mimetypes]

    def representation(self, mediatype):
        """Allows additional representation transformers to be declared for the
        api. Transformers are functions that must be decorated with this
        method, passing the mediatype the transformer represents. Three
        arguments are passed to the transformer:

        * The data to be represented in the response body
        * The http status code
        * A dictionary of headers

        The transformer should convert the data appropriately for the mediatype
        and return a Flask response object.

        Ex::

            @api.representation('application/xml')
            def xml(data, code, headers):
                resp = make_response(convert_data_to_xml(data), code)
                resp.headers.extend(headers)
                return resp
        """
        def wrapper(func):
            self.representations[mediatype] = func
            return func
        return wrapper


class Resource(MethodView):
    """
    Represents an abstract RESTful resource. Concrete resources should extend
    from this class and expose methods for each supported HTTP method. If a
    resource is invoked with an unsupported HTTP method, the API will return a
    response with status 405 Method Not Allowed. Otherwise the appropriate
    method is called and passed all arguments from the url rule used when
    adding the resource to an Api instance. See Api.add_resource for details.
    """
    representations = None
    method_decorators = []

    def dispatch_request(self, *args, **kwargs):

        # Taken from flask
        #noinspection PyUnresolvedReferences
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        for decorator in self.method_decorators:
            meth = decorator(meth)

        resp = meth(*args, **kwargs)

        if isinstance(resp, Response):  # There may be a better way to test
            return resp

        representations = self.representations or {}

        #noinspection PyUnresolvedReferences
        for mediatype in self.mediatypes():
            if mediatype in representations:
                data, code, headers = unpack(resp)
                resp = representations[mediatype](data, code, headers)
                resp.headers['Content-Type'] = mediatype
                return resp

        return resp


def marshal(data, fields):
    """Takes raw data (in the form of a dict, list, object) and a dict of
    fields to output and filters the data based on those fields.

    :param fields: a dict of whose keys will make up the final serialized
                   response output
    :param data: the actual object(s) from which the fields are taken from


    >>> from flask.ext.restful import fields, marshal
    >>> data = { 'a': 100, 'b': 'foo' }
    >>> mfields = { 'a': fields.Raw }

    >>> marshal(data, mfields)
    OrderedDict([('a', 100)])

    """
    def make(cls):
        if isinstance(cls, type):
            return cls()
        return cls

    if isinstance(data, (list, tuple)):
        return [marshal(d, fields) for d in data]

    items = ((k, marshal(data, v) if isinstance(v, dict)
                                  else make(v).output(k, data))
                                  for k, v in fields.items())
    return OrderedDict(items)


class marshal_with(object):
    """A decorator that apply marshalling to the return values of your methods.

    >>> from flask.ext.restful import fields, marshal_with
    >>> mfields = { 'a': fields.Raw }
    >>> @marshal_with(mfields)
    ... def get():
    ...     return { 'a': 100, 'b': 'foo' }
    ...
    ...
    >>> get()
    OrderedDict([('a', 100)])

    see :meth:`flask.ext.restful.marshal`
    """
    def __init__(self, fields):
        """:param fields: a dict of whose keys will make up the final
                          serialized response output"""
        self.fields = fields

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            if isinstance(resp, tuple):
                data, code, headers = unpack(resp)
                return marshal(data, self.fields), code, headers
            else:
                return marshal(resp, self.fields)
        return wrapper
