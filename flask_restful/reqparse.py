from flask import request
from werkzeug.datastructures import MultiDict, FileStorage
import flask_restful
import inspect
import six

class Namespace(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    def __setattr__(self, name, value):
        self[name] = value

_friendly_location = {
    u'form': u'the post body',
    u'args': u'the query string',
    u'values': u'the post body or the query string',
    u'headers': u'the HTTP headers',
    u'cookies': u'the request\'s cookies',
    u'files': u'an uploaded file',
}

text_type = lambda x: six.text_type(x)

class Argument(object):

    def __init__(self, name, default=None, dest=None, required=False,
                 ignore=False, type=text_type, location=('json', 'values',),
                 choices=(), action='store', help=None, operators=('=',),
                 case_sensitive=True):
        """
        :param name: Either a name or a list of option strings, e.g. foo or
                        -f, --foo.
        :param default: The value produced if the argument is absent from the
            request.
        :param dest: The name of the attribute to be added to the object
            returned by parse_args(req).
        :param bool required: Whether or not the argument may be omitted (optionals
            only).
        :param action: The basic type of action to be taken when this argument
            is encountered in the request.
        :param ignore: Whether to ignore cases where the argument fails type
            conversion
        :param type: The type to which the request argument should be
            converted. If a type raises a ValidationError, the message in the
            error will be returned in the response.
        :param location: Where to source the arguments from the Flask request
            (ex: headers, args, etc.), can be an iterator
        :param choices: A container of the allowable values for the argument.
        :param help: A brief description of the argument, returned in the
            response when the argument is invalid. This takes precedence over
            the message passed to a ValidationError raised by a type converter.
        :param bool case_sensitive: Whether the arguments in the request are
            case sensitive or not
        """

        self.name = name
        self.default = default
        self.dest = dest
        self.required = required
        self.ignore = ignore
        self.location = location
        self.type = type
        self.choices = choices
        self.action = action
        self.help = help
        self.case_sensitive = case_sensitive
        self.operators = operators

    def source(self, request):
        """Pulls values off the request in the provided location
        :param request: The flask request object to parse arguments from
        """
        if isinstance(self.location, six.string_types):
            value = getattr(request, self.location, MultiDict())
            if callable(value):
                value = value()
            if value is not None:
                return value
        else:
            for l in self.location:
                value = getattr(request, l, None)
                if callable(value):
                    value = value()
                if value is not None:
                    return value

        return MultiDict()

    def convert(self, value, op):
        # check if we're expecting a string and the value is `None`
        if value is None and inspect.isclass(self.type) and issubclass(self.type, six.string_types):
            return None

        try:
            return self.type(value, self.name, op)
        except TypeError:
            try:
                return self.type(value, self.name)
            except TypeError:
                return self.type(value)

    def handle_validation_error(self, error):
        """Called when an error is raised while parsing. Aborts the request
        with a 400 status and an error message

        :param error: the error that was raised
        """
        msg = self.help if self.help is not None else str(error)
        flask_restful.abort(400, message=msg)

    def parse(self, request):
        """Parses argument value(s) from the request, converting according to
        the argument's type.

        :param request: The flask request object to parse arguments from
        """
        source = self.source(request)

        results = []

        for operator in self.operators:
            name = self.name + operator.replace("=", "", 1)
            if name in source:
                # Account for MultiDict and regular dict
                if hasattr(source, "getlist"):
                    values = source.getlist(name)
                else:
                    values = [source.get(name)]

                for value in values:
                    _is_file = isinstance(value, FileStorage)
                    if not (self.case_sensitive or _is_file):
                        value = value.lower()
                    if self.choices and value not in self.choices:
                        self.handle_validation_error(ValueError(
                            u"{0} is not a valid choice".format(value)))
                    if not _is_file:
                        try:
                            value = self.convert(value, operator)
                        except Exception as error:
                            if self.ignore:
                                continue

                            self.handle_validation_error(error)

                    results.append(value)

        if not results and self.required:
            if isinstance(self.location, six.string_types):
                error_msg = u"Missing required parameter {0} in {1}".format(
                    self.name,
                    _friendly_location.get(self.location, self.location)
                )
            else:
                friendly_locations = [_friendly_location.get(loc, loc) \
                                      for loc in self.location]
                error_msg = u"Missing required parameter {0} in {1}".format(
                    self.name,
                    ' or '.join(friendly_locations)
                )
            self.handle_validation_error(ValueError(error_msg))

        if not results:
            if callable(self.default):
                return self.default()
            else:
                return self.default

        if self.action == 'append':
            return results

        if self.action == 'store' or len(results) == 1:
            return results[0]
        return results


class RequestParser(object):
    """Enables adding and parsing of multiple arguments in the context of a
    single request. Ex::

        from flask import request

        parser = RequestParser()
        parser.add_argument('foo')
        parser.add_argument('int_bar', type=int)
        args = parser.parse_args()
    """

    def __init__(self, argument_class=Argument, namespace_class=Namespace):
        self.args = []
        self.argument_class = argument_class
        self.namespace_class = namespace_class

    def add_argument(self, *args, **kwargs):
        """Adds an argument to be parsed. See :class:`Argument`'s constructor
        for documentation on the available options.
        """

        self.args.append(self.argument_class(*args, **kwargs))
        return self

    def parse_args(self, req=None):
        """Parse all arguments from the provided request and return the results
        as a Namespace
        """
        if req is None:
            req = request

        namespace = self.namespace_class()

        for arg in self.args:
            namespace[arg.dest or arg.name] = arg.parse(req)

        return namespace
