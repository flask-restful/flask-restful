import difflib
from functools import wraps
import inspect
import logging
import os
import re
from flask import request, Response, render_template, send_from_directory
from flask import abort as original_flask_abort
from flask.views import MethodView, MethodViewType
from werkzeug.exceptions import HTTPException
from flask.ext.restful.links import Link, Embed
from flask.ext.restful.utils import unauthorized, error_data, unpack, hal
from flask.ext.restful.representations.json import output_json

try:
    #noinspection PyUnresolvedReferences
    from collections import OrderedDict
except ImportError:
    from utils.ordereddict import OrderedDict

__all__ = ('Api', 'Resource', 'LinkedResource', 'marshal', 'marshal_with', 'abort')


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
                 decorators=None, output_errors=True):
        self.representations = dict(DEFAULT_REPRESENTATIONS)
        self.urls = {}
        self.prefix = prefix
        self.app = app
        self.default_mediatype = default_mediatype
        self.decorators = decorators if decorators else []
        if output_errors and hasattr(app, 'handle_exception'):
            self.original_handle_exception, app.handle_exception = app.handle_exception, self.handle_exception
            self.original_handle_user_exception, app.handle_user_exception = app.handle_user_exception, self.handle_user_exception

        # FIXME, just hacked my way around Flask
        thisdir = os.path.dirname(__file__)

        from jinja2 import FileSystemLoader

        if isinstance(app.jinja_loader, FileSystemLoader):
            app.jinja_loader.searchpath += [thisdir + os.sep + 'templates']

        @app.route('/apiexplorer/<path:filename>')
        def ae_static(filename):
            return send_from_directory(thisdir + os.sep + 'static', filename)

        # register the url processing for HAL
        @app.context_processor
        def utility_processor():
            return dict(hal=hal)


    def handle_exception(self, e):
        self.original_handle_exception(e) # hijack the handler but at least play nice by calling it
        return self.handle_error(e) # but return the JSON

    def handle_user_exception(self, e):
        self.original_handle_user_exception(e) # hijack the handler but at least play nice by calling it
        return self.handle_error(e) # but return the JSON

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

        if code == 404:
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

        :param resource: the class of your resource
        :type resource: Resource
        :param urls: one or more url routes to match for the resource, standard
                     flask routing rules apply.  Any url variables will be
                     passed to the resource method as args.
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

        if endpoint in self.app.view_functions.keys():
            previous_view_class = self.app.view_functions[endpoint].func_dict['view_class']
            if previous_view_class != resource: # if you override with a different class the endpoint, avoid the collision by raising an exception
                raise ValueError('This endpoint (%s) is already set to the class %s.' % (endpoint, previous_view_class.__name__))

        resource.mediatypes = self.mediatypes_method()  # Hacky
        resource_func = self.output(resource.as_view(endpoint))

        # patch the resource_func for at least "GET" for the API explorer
        if 'GET' not in resource_func.methods:
            resource_func.methods.append('GET')
            # End of hacks for the API explorer

        for decorator in self.decorators:
            resource_func = decorator(resource_func)

        for url in urls:
            self.app.add_url_rule(self.prefix + url, view_func=resource_func)

    def recurse_add(self, resource_class, **kwargs):

        if resource_class not in self.registered_resources:
            logging.info("Registering: %s" % resource_class)
            uri = resource_class._self
            uri = uri.replace('{', '<').replace('}', '>') # hack to transform url conventions, FIXME
            self.add_resource(resource_class, uri, **kwargs)
            self.registered_resources.append(resource_class)
        for name, method in inspect.getmembers(resource_class, predicate=inspect.ismethod):
            if hasattr(method, '_links') and method._links is not None:
                links = method._links
                for value in links.values():
                    if isinstance(value, list):
                        self.recurse_add(value[0])
                    else:
                        self.recurse_add(value)
            if hasattr(method, '_fields'):
                fields = method._fields
                for value in fields.values():
                    if isinstance(value, list) and inspect.isclass(value[0]) and issubclass(value[0], LinkedResource):
                        self.recurse_add(value[0])
                    elif inspect.isclass(value) and issubclass(value, LinkedResource):
                        self.recurse_add(value)

    def add_root(self, resource_class, **kwargs):
        self.registered_resources = []
        self.recurse_add(resource_class, **kwargs)
        del self.registered_resources


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

    def explore(self, *args, **kwargs):
        for clazz in LinkedResource.__subclasses__():
            if clazz == self.__class__:
                methods = {}
                class_dict = clazz.__dict__
                for verb in ('get', 'put', 'post', 'head', 'delete'):
                    f = class_dict.get(verb, None)
                    if f:
                        methods[verb] = f
                return Response(render_template('apiexplorer.html', clazz=clazz, url=clazz._self, resource_params=kwargs, methods=methods, mimetype='text/html'))

    def dispatch_request(self, *args, **kwargs):
        for mime, _ in request.accept_mimetypes:
            if mime.find('html') != -1:
                return self.explore(self, *args, **kwargs)

        # Taken from flask
        #noinspection PyUnresolvedReferences
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        for decorator in self.method_decorators:
            meth = decorator(meth)
        try:
            resp = meth(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            raise e

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


class LinkedResource(Resource):
    # override that for your own linked resource
    _self = 'undefined'

    @classmethod
    def output(cls, k, data):
        """
        This is ducktyping the Resource as a Field so you can specify links between resources.

        :param k: the key of the link
        :param data: the class of the targetted resource
        :return:
        """
        return data[k]._self


def marshal(data, fields, links=None, hal_context = None):
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

    # handle the magic JSON HAL sections
    items = []
    embedded = []
    for k, v in fields.items():
        if inspect.isclass(v) and issubclass(v, LinkedResource): # this is the special case of embedded resources
            embedded.append((k, data[k].to_dict()))
        elif isinstance(v, list) and inspect.isclass(v[0]) and issubclass(v[0], LinkedResource): # an array of resources
            embedded.append((k, [resource.to_dict() for resource in data[k]]))
        elif isinstance(v, dict):
            items.append((k, marshal(data, v))) # recursively go down the dictionaries
        else:
            items.append((k, make(v).output(k, data))) # normal field output

    if data.has_key('_links') and links is not None:
        ls = data['_links'].items() # preset links like self
        for link_key, link_value in links.items():
            if inspect.isclass(link_value) and issubclass(link_value, LinkedResource): # simple straigh linked resource
                ls.append((link_key, {'href': hal(link_value._self, hal_context)}))
            elif isinstance(link_value, list): # an array of resources
                list_of_links = [link_obj.to_dict()  for link_obj in data[link_key]]
                ls.append((link_key, list_of_links))

        items = [('_links', dict(ls))] + items

    if embedded:
        items.append(('_embedded', OrderedDict(embedded)))

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
