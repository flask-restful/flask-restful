from functools import wraps
from flask.ext.restful.paging import PAGER_ARG_NAME, PAGE_SIZE_ARG_NAME
from flask_restful import LinkedResource
from flask import request
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

    >>> from flask.ext.restful import fields
    >>> from flask.ext.restful.declarative import Verb
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

    def __init__(self, input_parser=None, output_fields=None, output_links=None, output_paging=False):
        """:param output_fields: a dict of whose keys will make up the final
                          serialized response output"""
        self.parser = input_parser if input_parser else parameters()
        if output_paging:
            self.parser.add_argument(PAGER_ARG_NAME, location='args')
            self.parser.add_argument(PAGE_SIZE_ARG_NAME, location='args', type=int)

        self.fields = output_fields if output_fields else output()
        self.links = output_links
        self.paging = output_paging

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            accept = str(request.accept_mimetypes)
            transform, _ = LinkedResource.representations.get(accept, LinkedResource.representations['application/hal+json'])
            hal_context = dict(kwargs.items() + self.parser.parse_args().items())
            return transform(args[0], self, f(*args, **hal_context), hal_context)

        wrapper._parser = self.parser
        wrapper._fields = self.fields
        wrapper._links = self.links
        wrapper._paging = self.paging
        return wrapper
