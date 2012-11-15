from functools import wraps
from flask.ext.restful import marshal, Resource
from reqparse import RequestParser

def parameters(*args, **kwargs):
    parser = RequestParser()
    for key, value in kwargs.iteritems():
        if isinstance(value, parser.argument_class):
            value.name = key
            parser.args.append(value)
        else:
            parser.add_argument(key, type = value)

    return parser

def output(*args, **kwargs):
    return kwargs

class Verb(object):
    """A decorator that describes the input and outputs of your REST action.

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
    def __init__(self, parser, fields):
        """:param fields: a dict of whose keys will make up the final
                          serialized response output"""
        self.parser = parser
        self.fields = fields

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # injects the parameters as kwargs
            kwargs = dict(kwargs.items() + self.parser.parse_args().items())
            return marshal(f(*args, **kwargs), self.fields)
        wrapper._parser = self.parser
        wrapper._fields = self.fields
        return wrapper
