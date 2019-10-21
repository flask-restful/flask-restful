from datetime import datetime
from decimal import Decimal
from functools import partial
import unittest

import pytest
from flask import Blueprint
from mock import Mock
import pytz

from flask_restful.fields import MarshallingException
from flask_restful.utils import OrderedDict
from flask_restful import fields


class Foo(object):
    def __init__(self):
        self.hey = 3


class Bar(object):
    def __marshallable__(self):
        return {"hey": 3}


def check_field(expected, field, value):
    assert expected == field.output('a', {'a': value})


@pytest.mark.parametrize('value,object,expected', [
    (True, fields.Boolean(), True),
    (False, fields.Boolean(), False),
    ({}, fields.Boolean(), False),
    ("false", fields.Boolean(), True),  # These are different from php
    ("0", fields.Boolean(), True),      # Will this be a problem?
    ("-3.13", fields.Float(), -3.13),
    (str(-3.13), fields.Float(), -3.13),
    (3, fields.Float(), 3.0),
])
def test_fields(value, object, expected):
    check_field(expected, object, value)


@pytest.mark.parametrize('date,expected', [
    (datetime(2011, 1, 1), "Sat, 01 Jan 2011 00:00:00 -0000"),
    (datetime(2011, 1, 1, 23, 59, 59),
     "Sat, 01 Jan 2011 23:59:59 -0000"),
    (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc),
     "Sat, 01 Jan 2011 23:59:59 -0000"),
    (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.timezone('CET')),
     "Sat, 01 Jan 2011 22:59:59 -0000")
])
def test_rfc822_datetime_formatters(date, expected):
    assert fields._rfc822(date) == expected


@pytest.mark.parametrize('date,expected', [
    (datetime(2011, 1, 1), "2011-01-01T00:00:00"),
    (datetime(2011, 1, 1, 23, 59, 59),
     "2011-01-01T23:59:59"),
    (datetime(2011, 1, 1, 23, 59, 59, 1000),
     "2011-01-01T23:59:59.001000"),
    (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc),
     "2011-01-01T23:59:59+00:00"),
    (datetime(2011, 1, 1, 23, 59, 59, 1000, tzinfo=pytz.utc),
     "2011-01-01T23:59:59.001000+00:00"),
    (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.timezone('CET')),
     "2011-01-01T23:59:59+01:00")
])
def test_iso8601_datetime_formatters(date, expected):
    assert fields._iso8601(date) == expected


@pytest.fixture()
def fields_app(app):
    app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
    bp = Blueprint("foo", __name__, url_prefix="/foo")
    bp.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
    app.register_blueprint(bp)
    
    return app


def test_decimal_trash():
    with pytest.raises(MarshallingException):
        fields.Float().output('a', {'a': 'Foo'})


def test_basic_dictionary():
    obj = {"foo": 3}
    field = fields.String()
    assert field.output("foo", obj) == "3"


def test_no_attribute():
    obj = {"bar": 3}
    field = fields.String()
    assert field.output("foo", obj) is None


def test_date_field_invalid():
    obj = {"bar": 3}
    field = fields.DateTime()
    with pytest.raises(MarshallingException):
        field.output("bar", obj)


def test_attribute():
    obj = {"bar": 3}
    field = fields.String(attribute="bar")
    assert field.output("foo", obj) == "3"


def test_formatting_field_none():
    obj = {}
    field = fields.FormattedString("/foo/{0[account_sid]}/{0[sid]}/")
    with pytest.raises(MarshallingException):
        field.output("foo", obj)


def test_formatting_field_tuple():
    obj = (3, 4)
    field = fields.FormattedString("/foo/{0[account_sid]}/{0[sid]}/")
    with pytest.raises(MarshallingException):
        field.output("foo", obj)


def test_formatting_field_dict():
    obj = {
        "sid": 3,
        "account_sid": 4,
    }
    field = fields.FormattedString("/foo/{account_sid}/{sid}/")
    assert field.output("foo", obj) == "/foo/4/3/"


def test_formatting_field():
    obj = Mock()
    obj.sid = 3
    obj.account_sid = 4
    field = fields.FormattedString("/foo/{account_sid}/{sid}/")
    assert field.output("foo", obj) == "/foo/4/3/"


def test_basic_field():
    obj = Mock()
    obj.foo = 3
    field = fields.Raw()
    assert field.output("foo", obj) == 3


def test_raw_field():
    obj = Mock()
    obj.foo = 3
    field = fields.Raw()
    assert field.output("foo", obj) == 3


def test_nested_raw_field():
    foo = Mock()
    bar = Mock()
    bar.value = 3
    foo.bar = bar
    field = fields.Raw()
    assert field.output("bar.value", foo) == 3


def test_formatted_string_invalid_obj():
    field = fields.FormattedString("{hey}")
    with pytest.raises(MarshallingException):
        field.output("hey", None)


def test_formatted_string():
    field = fields.FormattedString("{hey}")
    assert "3" == field.output("hey", Foo())


def test_string_with_attribute():
    field = fields.String(attribute="hey")
    assert "3" == field.output("foo", Foo())


def test_string_with_lambda():
    field = fields.String(attribute=lambda x: x.hey)
    assert "3" == field.output("foo", Foo())


def test_string_with_partial():
    def f(x, suffix):
        return "%s-%s" % (x.hey, suffix)

    p = partial(f, suffix="whatever")
    field = fields.String(attribute=p)
    assert "3-whatever" == field.output("foo", Foo())


def test_url_invalid_object(fields_app):
    field = fields.Url("foobar")
    with fields_app.test_request_context("/"):
        with pytest.raises(MarshallingException):
            field.output("hey", None)


def test_url(fields_app):
    field = fields.Url("foobar")
    with fields_app.test_request_context("/"):
        assert "/3" == field.output("hey", Foo())


def test_url_absolute(fields_app):
    field = fields.Url("foobar", absolute=True)

    with fields_app.test_request_context("/"):
        assert "http://localhost/3" == field.output("hey", Foo())


def test_url_absolute_scheme(fields_app):
    """Url.scheme should override current_request.scheme"""
    field = fields.Url("foobar", absolute=True, scheme='https')

    with fields_app.test_request_context("/", base_url="http://localhost"):

        assert "https://localhost/3" == field.output("hey", Foo())


def test_url_without_endpoint_invalid_object(fields_app):
    field = fields.Url()

    with fields_app.test_request_context("/hey"):
        with pytest.raises(MarshallingException):
            field.output("hey", None)


def test_url_without_endpoint(fields_app):
    field = fields.Url()

    with fields_app.test_request_context("/hey"):
        assert "/3" == field.output("hey", Foo())


def test_url_without_endpoint_absolute(fields_app):
    field = fields.Url(absolute=True)

    with fields_app.test_request_context("/hey"):
        assert "http://localhost/3" == field.output("hey", Foo())


def test_url_without_endpoint_absolute_scheme(fields_app):
    field = fields.Url(absolute=True, scheme='https')

    with fields_app.test_request_context("/hey", base_url="http://localhost"):
        assert "https://localhost/3" == field.output("hey", Foo())


def test_url_with_blueprint_invalid_object(fields_app):
    field = fields.Url()

    with fields_app.test_request_context("/foo/hey"):
        with pytest.raises(MarshallingException):
            field.output("hey", None)


def test_url_with_blueprint(fields_app):
    field = fields.Url()

    with fields_app.test_request_context("/foo/hey"):
        assert "/foo/3" == field.output("hey", Foo())


def test_url_with_blueprint_absolute(fields_app):
    field = fields.Url(absolute=True)

    with fields_app.test_request_context("/foo/hey"):
        assert "http://localhost/foo/3" == field.output("hey", Foo())


def test_url_with_blueprint_absolute_scheme(fields_app):
    field = fields.Url(absolute=True, scheme='https')

    with fields_app.test_request_context("/foo/hey", base_url="http://localhost"):
        assert "https://localhost/foo/3" == field.output("hey", Foo())


def test_url_superclass_kwargs(fields_app):
    field = fields.Url(absolute=True, attribute='hey')

    with fields_app.test_request_context("/hey"):
        assert "http://localhost/3" == field.output("hey", Foo())


def test_int():
    field = fields.Integer()
    assert 3 == field.output("hey", {'hey': 3})


def test_int_default():
    field = fields.Integer(default=1)
    assert 1 == field.output("hey", {'hey': None})


def test_no_int():
    field = fields.Integer()
    assert 0 == field.output("hey", {'hey': None})


def test_int_decode_error():
    field = fields.Integer()
    with pytest.raises(MarshallingException):
        field.output("hey", {'hey': 'Explode please I am nowhere looking like an int'})


def test_float():
    field = fields.Float()
    assert 3.0 == field.output("hey", {'hey': 3.0})


def test_float_decode_error():
    field = fields.Float()
    with pytest.raises(MarshallingException):
        field.output("hey", {'hey': 'Explode!'})

PI_STR = u'3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861'
PI = Decimal(PI_STR)


def test_arbitrary():
    field = fields.Arbitrary()
    assert PI_STR, field.output("hey" == {'hey': PI})


def test_fixed():
    field5 = fields.Fixed(5)
    field4 = fields.Fixed(4)

    assert '3.14159' == field5.output("hey", {'hey': PI})
    assert '3.1416' == field4.output("hey", {'hey': PI})
    assert '3.0000' == field4.output("hey", {'hey': '3'})
    assert '3.0000' == field4.output("hey", {'hey': '03'})
    assert '3.0000' == field4.output("hey", {'hey': '03.0'})


def test_zero_fixed():
    field = fields.Fixed()
    assert '0.00000' == field.output('hey', {'hey': 0})


def test_infinite_fixed():
    field = fields.Fixed()
    with pytest.raises(MarshallingException):
        field.output("hey", {'hey': '+inf'})

    with pytest.raises(MarshallingException):
        field.output("hey", {'hey': '-inf'})


def test_advanced_fixed():
    field = fields.Fixed()
    with pytest.raises(MarshallingException):
        field.output("hey", {'hey': 'NaN'})


def test_fixed_with_attribute():
    field = fields.Fixed(4, attribute="bar")
    assert '3.0000' == field.output("foo", {'bar': '3'})


def test_string():
    field = fields.String()
    assert "3" == field.output("hey", Foo())


def test_string_no_value():
    field = fields.String()
    assert field.output("bar", Foo()) is None


def test_string_none():
    field = fields.String()
    assert field.output("empty", {'empty': None}) is None


def test_rfc822_date_field_without_offset():
    obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
    field = fields.DateTime()
    assert "Mon, 22 Aug 2011 20:58:45 -0000", field.output("bar", obj)


def test_rfc822_date_field_with_offset():
    obj = {"bar": datetime(2011, 8, 22, 20, 58, 45, tzinfo=pytz.timezone('CET'))}
    field = fields.DateTime()
    assert "Mon, 22 Aug 2011 19:58:45 -0000" == field.output("bar", obj)


def test_iso8601_date_field_without_offset():
    obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
    field = fields.DateTime(dt_format='iso8601')
    assert "2011-08-22T20:58:45" == field.output("bar", obj)


def test_iso8601_date_field_with_offset():
    obj = {"bar": datetime(2011, 8, 22, 20, 58, 45, tzinfo=pytz.timezone('CET'))}
    field = fields.DateTime(dt_format='iso8601')
    assert "2011-08-22T20:58:45+01:00" == field.output("bar", obj)


def test_unsupported_datetime_format():
    obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
    field = fields.DateTime(dt_format='raw')
    with pytest.raises(MarshallingException):
        field.output('bar', obj)


def test_to_dict():
    obj = {"hey": 3}
    assert obj == fields.to_marshallable_type(obj)


def test_to_dict_obj():
    obj = {"hey": 3}
    assert obj == fields.to_marshallable_type(Foo())


def test_to_dict_custom_marshal():
    obj = {"hey": 3}
    assert obj == fields.to_marshallable_type(Bar())


def test_get_value():
    assert 3 == fields.get_value("hey", {"hey": 3})


def test_get_value_no_value():
    assert fields.get_value("foo", {"hey": 3}) is None


def test_get_value_obj():
    assert 3 == fields.get_value("hey", Foo())


def test_list():
    obj = {'list': ['a', 'b', 'c']}
    field = fields.List(fields.String)
    assert ['a', 'b', 'c'] == field.output('list', obj)


def test_list_from_set():
    obj = {'list': {'a', 'b', 'c'}}
    field = fields.List(fields.String)
    assert {'a', 'b', 'c'} == set(field.output('list', obj))


def test_list_from_object():
    class TestObject(object):
        def __init__(self, list):
            self.list = list
    obj = TestObject(['a', 'b', 'c'])
    field = fields.List(fields.String)
    assert ['a', 'b', 'c'] == field.output('list', obj)


def test_list_with_attribute():
    class TestObject(object):
        def __init__(self, list):
            self.foo = list
    obj = TestObject(['a', 'b', 'c'])
    field = fields.List(fields.String, attribute='foo')
    assert ['a', 'b', 'c'] == field.output('list', obj)


def test_list_with_scoped_attribute_on_dict_or_obj():
    class TestObject(object):
        def __init__(self, list_):
            self.bar = list_

    class TestEgg(object):
        def __init__(self, val):
            self.attrib = val

    eggs = [TestEgg(i) for i in ['a', 'b', 'c']]
    test_obj = TestObject(eggs)
    test_dict = {'bar': [{'attrib': 'a'}, {'attrib': 'b'}, {'attrib': 'c'}]}

    field = fields.List(fields.String(attribute='attrib'), attribute='bar')
    assert ['a', 'b', 'c'] == field.output('bar', test_obj)
    assert ['a', 'b', 'c'] == field.output('bar', test_dict)


def test_null_list():
    class TestObject(object):
        def __init__(self, list):
            self.list = list
    obj = TestObject(None)
    field = fields.List(fields.String)
    assert field.output('list', obj) is None


def test_indexable_object():
    class TestObject(object):
        def __init__(self, foo):
            self.foo = foo

        def __getitem__(self, n):
            if type(n) is int:
                if n < 3:
                    return n
                raise IndexError
            raise TypeError

    obj = TestObject("hi")
    field = fields.String(attribute="foo")
    assert "hi" == field.output("foo", obj)


def test_list_from_dict_with_attribute():
    obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
    field = fields.List(fields.Integer(attribute='a'))
    assert [1, 2, 3] == field.output('list', obj)


def test_list_of_nested():
    obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
    field = fields.List(fields.Nested({'a': fields.Integer}))
    assert [
        OrderedDict([('a', 1)]),
        OrderedDict([('a', 2)]),
        OrderedDict([('a', 3)])
    ] == field.output('list', obj)


def test_nested_with_default():
    obj = None
    field = fields.Nested({'a': fields.Integer, 'b': fields.String}, default={})
    assert {} == field.output('a', obj)


def test_list_of_raw():
    obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
    field = fields.List(fields.Raw)
    assert [
        OrderedDict([('a', 1), ('b', 1), ]),
        OrderedDict([('a', 2), ('b', 1), ]),
        OrderedDict([('a', 3), ('b', 1), ]),
    ] == field.output('list', obj)

    obj = {'list': [1, 2, 'a']}
    field = fields.List(fields.Raw)
    assert [1, 2, 'a'], field.output('list' == obj)


if __name__ == '__main__':
    unittest.main()
