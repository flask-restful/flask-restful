from functools import wraps
import urllib
from flask import url_for
from flask.ext.restful.links import PlainLink
from flask.ext.restful.paging import PAGER_ARG_NAME, PAGE_SIZE_ARG_NAME
from flask.ext.restful.utils import rest_url_for
from flask_restful import marshal, LinkedResource, Link
from reqparse import RequestParser
import re
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

    def __init__(self, parser, fields, links=None, paging=False):
        """:param fields: a dict of whose keys will make up the final
                          serialized response output"""
        self.parser = parser
        if paging:
            self.parser.add_argument(PAGER_ARG_NAME, location='args')
            self.parser.add_argument(PAGE_SIZE_ARG_NAME, location='args', type=int)

        self.fields = fields
        self.links = links
        self.paging = paging

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # injects the parameters as kwargs
            resource_self = args[0]
            hal_context = dict(kwargs.items() + self.parser.parse_args().items())
            base_url = rest_url_for(resource_self._endpoint, **hal_context)
            links = {'self': {'href': base_url}}
            if self.paging:
                result, paging_info, result_size = f(*args, **hal_context)
                for url_param in re.search(r"<([A-Za-z0-9_]+)>", resource_self._self).groups():  # FIXME this won't work with more complex flask descriptions
                    del(paging_info[url_param])
                for name, value in dict(paging_info).iteritems():
                    if value is None:
                        del(paging_info[name])
                links['next'] = PlainLink(base_url + '?' + urllib.urlencode(paging_info), "Next results")
                links_desc = dict(self.links.items() + [('next', resource_self.__class__)])
            else:
                result = f(*args, **hal_context)
                links_desc = self.links

            result['_links'] = links

            return marshal(result, self.fields, links=links_desc, hal_context=hal_context)

        wrapper._parser = self.parser
        wrapper._fields = self.fields
        wrapper._links = self.links
        wrapper._paging = self.links
        return wrapper
