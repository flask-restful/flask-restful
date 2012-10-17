from functools import wraps
from collections import OrderedDict
from flask import request, Response
from flask import abort as original_flask_abort
from flask.views import MethodView
from werkzeug.exceptions import HTTPException
from flask.ext.restful.utils import unauthorized, error_data, unpack
from flask.ext.restful.representations.json import output_json

__all__ = ('Api', 'Resource', 'marshal', 'marshal_with', 'abort')


def abort(http_status_code, **kwargs):
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.
    """
    #noinspection PyUnresolvedReferences
    try:
        original_flask_abort(http_status_code)
    except HTTPException as e:
        e.data = kwargs
        raise e

DEFAULT_REPRESENTATIONS = {'application/json': output_json}


class Api(object):
    """
    The main entry point for the application.
    You need to initialize it with a Flask Application :
    >>> app = Flask(__name__)
    >>> api = restful.Api(app)
    """

    def __init__(self, app, prefix='', default_mediatype='application/json',
                 decorators=None):
        self.representations = dict(DEFAULT_REPRESENTATIONS)
        self.urls = {}
        self.prefix = prefix
        self.app = app
        self.default_mediatype = default_mediatype
        self.decorators = decorators if decorators else []
        app.handle_exception = self.handle_error
        app.handle_user_exception = self.handle_error

    def handle_error(self, e):
        """Error handler for the API transforms a raised exception into a Flask
        response, with the appropriate HTTP status code and body.

        :param e: the raised Exception object
        :type e: Exception
        """
        code = getattr(e, 'code', 500)
        data = getattr(e, 'data', error_data(code))

        if code >= 500:
            self.app.logger.exception("Internal Error")

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
        :type resource: Resource
        :param urls: one or more url routes to match for the resource, standard
                     flask routing rules apply.  Any url variables will be
                     passed to the resource
        method as args.
        :type urls: str

        :param endpoint: endpoint name (defaults to Resource.__name__.lower()
                         can be used to reference this route in Url fields
                         see: Fields
        :type endpoint: str


        Examples:
            api.add_resource(HelloWorld, '/', '/hello')

            api.add_resource(Foo, '/foo', endpoint="foo")
            api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

        """
        endpoint = kwargs.get('endpoint') or resource.__name__.lower()

        resource.mediatypes = self.mediatypes_method()  # Hacky
        resource_func = self.output(resource.as_view(endpoint))

        for decorator in self.decorators:
            resource_func = decorator(resource_func)

        for url in urls:
            self.app.add_url_rule(self.prefix + url, view_func=resource_func)

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

        Ex:

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
    response with status 405 Method Not Alowed. Otherwise the appropriate
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
            return marshal(f(*args, **kwargs), self.fields)
        return wrapper
