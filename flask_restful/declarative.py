import difflib
from functools import wraps
from flask import url_for
from flask.ext.restful.utils import rest_url_for
from flask_restful import marshal, LinkedResource, abort
from reqparse import RequestParser

def parameters(*args, **kwargs):
    """Helper to specify the parameters section of the Verb decorator.
    You can use it with kwargs directly with types or with the Argument class supported by RequestParser.
    Can be used also for the output itself.
    """
    parser = RequestParser()
    for key, value in kwargs.iteritems():
        if isinstance(value, parser.argument_class):
            value.name = key
            parser.args.append(value)
        else:
            parser.add_argument(key, type=value)

    return parser


def output(*args, **kwargs):
    """Specify the output section of the Verb decorator.
    Can be used also for the output itself.
    """
    return kwargs


def link(*args, **kwargs):
    """Specify the linking section of the Verb decorator.
    """
    return kwargs


class Verb(object):
    """A decorator that describes the input and outputs of your REST action.
    You can specifies relations with other resources by setting links.

    >>> from flask.ext.restful import fields, marshal_with
    >>> mfields = { 'a': fields.Raw }
    >>> @Verb(parameters(one = int, two = str), output(a = fields.Integer, b = fields.String))
    ... def get(parameters):
    ...     return { 'a': 100, 'b': 'foo' }
    ...
    ...
    >>> get()
    OrderedDict([('a', 100)])

    see :meth:`flask.ext.restful.marshal`
    """

    def __init__(self, parser, fields, links=None):
        """:param fields: a dict of whose keys will make up the final
                          serialized response output"""
        self.parser = parser
        self.fields = fields
        self.links = links

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            # check for unexpected arguments
            weird_parameters, possible_parameters = self.parser.undeclared_args()
            if weird_parameters:
                close_matches = sum([difflib.get_close_matches(weird_parameter, possible_parameters) for weird_parameter in weird_parameters], [])
                message = 'Unknown parameter(s) [%s].' % ', '.join(weird_parameters)
                if close_matches:
                    message += ' Did you mean ' + ' or '.join((match for match in close_matches)) + ' ?'
                abort(400, message=message)

            # injects the parameters as kwargs
            resource_self = args[0]
            hal_context = dict(kwargs.items() + self.parser.parse_args().items())
            result = f(*args, **hal_context)

            if isinstance(resource_self, LinkedResource):
                links = {'self': {'href': rest_url_for(resource_self._endpoint, **hal_context)}}
                result['_links'] = links

            return marshal(result, self.fields, links=self.links, hal_context = hal_context)

        wrapper._parser = self.parser
        wrapper._fields = self.fields
        wrapper._links = self.links
        return wrapper
