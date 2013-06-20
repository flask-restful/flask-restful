from decimal import Decimal as MyDecimal, ROUND_HALF_EVEN
import urlparse
from flask_restful import types, marshal
from flask import url_for

__all__ = ["String", "FormattedString", "Url", "DateTime", "Float",
           "Integer", "Arbitrary", "Nested", "List", "Raw"]


class MarshallingException(Exception):
    """
    This is an encapsulating Exception in case of marshalling error.
    """

    def __init__(self, underlying_exception):
        # just put the contextual representation of the error to hint on what
        # went wrong without exposing internals
        super(MarshallingException, self).__init__(unicode(underlying_exception))


def is_indexable_but_not_string(obj):
    return not hasattr(obj, "strip") and hasattr(obj, "__getitem__")


def get_value(key, obj, default=None):
    """Helper for pulling a keyed value off various types of objects"""
    if is_indexable_but_not_string(obj):
        try:
            return obj[key]
        except KeyError:
            return default
    if hasattr(obj, key):
        return getattr(obj, key)
    return default


def to_marshallable_type(obj):
    """Helper for converting an object to a dictionary only if it is not
    dictionary already or an indexable object nor a simple type"""
    if obj is None:
        return None  # make it idempotent for None

    if hasattr(obj, '__getitem__'):
        return obj  # it is indexable it is ok

    if hasattr(obj, '__marshallable__'):
        return obj.__marshallable__()

    return dict(obj.__dict__)


class Raw(object):
    """Raw provides a base field class from which others should extend. It
    applies no formatting by default, and should only be used in cases where
    data does not need to be formatted before being serialized. Fields should
    throw a MarshallingException in case of parsing problem.
    """

    def __init__(self, default=None, attribute=None):
        self.attribute = attribute
        self.default = default

    def format(self, value):
        """Formats a field's value. No-op by default, concrete fields should
        override this and apply the appropriate formatting.

        :param value: The value to format
        :exception MarshallingException: In case of formatting problem

        Ex::

            class TitleCase(Raw):
                def format(self, value):
                    return unicode(value).title()
        """
        return value

    def output(self, key, obj):
        """Pulls the value for the given key from the object, applies the
        field's formatting and returns the result.
        :exception MarshallingException: In case of formatting problem
        """

        value = get_value(key if self.attribute is None else self.attribute, obj)

        if value is None:
            return self.default

        return self.format(value)


class Nested(Raw):
    """Allows you to nest one set of fields inside another.
    See :ref:`nested-field` for more information

    :param dict nested: The dictionary to nest
    :param bool allow_null: Whether to return None instead of a dictionary
        with null keys, if a nested dictionary has all-null keys
    """

    def __init__(self, nested, allow_null=False, **kwargs):
        self.nested = nested
        self.allow_null = allow_null
        super(Nested, self).__init__(**kwargs)

    def output(self, key, obj):
        value = get_value(key if self.attribute is None else self.attribute, obj)
        if self.allow_null and value is None:
            return None

        return marshal(value, self.nested)

class List(Raw):
    def __init__(self, cls_or_instance):
        super(List, self).__init__()
        if isinstance(cls_or_instance, type):
            if not issubclass(cls_or_instance, Raw):
                raise MarshallingException("The type of the list elements "
                                           "must be a subclass of "
                                           "flask_restful.fields.Raw")
            self.container = cls_or_instance()
        else:
            if not isinstance(cls_or_instance, Raw):
                raise MarshallingException("The instances of the list "
                                           "elements must be of type "
                                           "flask_restful.fields.Raw")
            self.container = cls_or_instance

    def output(self, key, data):
        value = get_value(key if self.attribute is None else self.attribute, data)
        # we cannot really test for external dict behavior
        if is_indexable_but_not_string(value) and not isinstance(value, dict):
            # Convert all instances in typed list to container type
            return [self.container.output(idx, value) for idx, val
                    in enumerate(value)]

        return [marshal(value, self.container.nested)]


class String(Raw):
    def format(self, value):
        try:
            return unicode(value)
        except ValueError as ve:
            raise MarshallingException(ve)


class Integer(Raw):
    def __init__(self, default=0, attribute=None):
        super(Integer, self).__init__(default, attribute)

    def format(self, value):
        try:
            if value is None:
                return self.default
            return int(value)
        except ValueError as ve:
            raise MarshallingException(ve)


class Boolean(Raw):
    def format(self, value):
        return bool(value)


class FormattedString(Raw):
    def __init__(self, src_str):
        super(FormattedString, self).__init__()
        self.src_str = unicode(src_str)

    def output(self, key, obj):
        try:
            data = to_marshallable_type(obj)
            return self.src_str.format(**data)
        except (TypeError, IndexError) as error:
            raise MarshallingException(error)


class Url(Raw):
    """
    A string representation of a Url
    """
    def __init__(self, endpoint):
        super(Url, self).__init__()
        self.endpoint = endpoint

    def output(self, key, obj):
        try:
            data = to_marshallable_type(obj)
            o = urlparse.urlparse(url_for(self.endpoint, **data))
            return urlparse.urlunparse(("", "", o.path, "", "", ""))
        except TypeError as te:
            raise MarshallingException(te)


class Float(Raw):
    """
    A double as IEEE-754 double precision.
    ex : 3.141592653589793 3.1415926535897933e-06 3.141592653589793e+24 nan inf -inf
    """

    def format(self, value):
        try:
            return repr(float(value))
        except ValueError as ve:
            raise MarshallingException(ve)


class Arbitrary(Raw):
    """
        A floating point number with an arbitrary precision
          ex: 634271127864378216478362784632784678324.23432
    """

    def format(self, value):
        return unicode(MyDecimal(value))


class DateTime(Raw):
    """Return a RFC822-formatted datetime string in UTC"""

    def format(self, value):
        try:
            return types.rfc822(value)
        except AttributeError as ae:
            raise MarshallingException(ae)

ZERO = MyDecimal()

class Fixed(Raw):
    def __init__(self, decimals=5):
        super(Fixed, self).__init__()
        self.precision = MyDecimal('0.' + '0' * (decimals - 1) + '1')

    def format(self, value):
        dvalue = MyDecimal(value)
        if not dvalue.is_normal() and dvalue != ZERO:
            raise MarshallingException('Invalid Fixed precision number.')
        return unicode(dvalue.quantize(self.precision, rounding=ROUND_HALF_EVEN))

Price = Fixed
