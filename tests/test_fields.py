from decimal import Decimal
from functools import partial
import pytz
import unittest
from mock import Mock
from flask_restful.fields import MarshallingException
from flask_restful.utils import OrderedDict
from flask_restful import fields
from datetime import datetime, timedelta, tzinfo
from flask import Flask, Blueprint
#noinspection PyUnresolvedReferences
from nose.tools import assert_equals  # you need it for tests in form of continuations


class Foo(object):
    def __init__(self):
        self.hey = 3


class Bar(object):
    def __marshallable__(self):
        return {"hey": 3}


def check_field(expected, field, value):
    assert_equals(expected, field.output('a', {'a': value}))


def test_float():
    values = [
        ("-3.13", -3.13),
        (str(-3.13), -3.13),
        (3, 3.0),
    ]
    for value, expected in values:
        yield check_field, expected, fields.Float(), value


def test_boolean():
    values = [
        (True, True),
        (False, False),
        ({}, False),
        ("false", True),  # These are different from php
        ("0", True),      # Will this be a problem?
    ]
    for value, expected in values:
        yield check_field, expected, fields.Boolean(), value


def test_rfc822_datetime_formatters():
    dates = [
        (datetime(2011, 1, 1), "Sat, 01 Jan 2011 00:00:00 -0000"),
        (datetime(2011, 1, 1, 23, 59, 59),
         "Sat, 01 Jan 2011 23:59:59 -0000"),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc),
         "Sat, 01 Jan 2011 23:59:59 -0000"),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.timezone('CET')),
         "Sat, 01 Jan 2011 22:59:59 -0000")
    ]
    for date_obj, expected in dates:
        yield assert_equals, fields._rfc822(date_obj), expected


def test_iso8601_datetime_formatters():
    dates = [
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
    ]
    for date_obj, expected in dates:
        yield assert_equals, fields._iso8601(date_obj), expected


class FieldsTestCase(unittest.TestCase):

    def test_decimal_trash(self):
        self.assertRaises(MarshallingException, lambda: fields.Float().output('a', {'a': 'Foo'}))

    def test_basic_dictionary(self):
        obj = {"foo": 3}
        field = fields.String()
        self.assertEqual(field.output("foo", obj), "3")

    def test_no_attribute(self):
        obj = {"bar": 3}
        field = fields.String()
        self.assertEqual(field.output("foo", obj), None)

    def test_date_field_invalid(self):
        obj = {"bar": 3}
        field = fields.DateTime()
        self.assertRaises(MarshallingException, lambda: field.output("bar", obj))

    def test_attribute(self):
        obj = {"bar": 3}
        field = fields.String(attribute="bar")
        self.assertEqual(field.output("foo", obj), "3")

    def test_formatting_field_none(self):
        obj = {}
        field = fields.FormattedString("/foo/{0[account_sid]}/{0[sid]}/")
        self.assertRaises(MarshallingException, lambda: field.output("foo", obj))

    def test_formatting_field_tuple(self):
        obj = (3, 4)
        field = fields.FormattedString("/foo/{0[account_sid]}/{0[sid]}/")
        self.assertRaises(MarshallingException, lambda: field.output("foo", obj))

    def test_formatting_field_dict(self):
        obj = {
            "sid": 3,
            "account_sid": 4,
        }
        field = fields.FormattedString("/foo/{account_sid}/{sid}/")
        self.assertEqual(field.output("foo", obj), "/foo/4/3/")

    def test_formatting_field(self):
        obj = Mock()
        obj.sid = 3
        obj.account_sid = 4
        field = fields.FormattedString("/foo/{account_sid}/{sid}/")
        self.assertEqual(field.output("foo", obj), "/foo/4/3/")

    def test_basic_field(self):
        obj = Mock()
        obj.foo = 3
        field = fields.Raw()
        self.assertEqual(field.output("foo", obj), 3)

    def test_raw_field(self):
        obj = Mock()
        obj.foo = 3
        field = fields.Raw()
        self.assertEqual(field.output("foo", obj), 3)

    def test_nested_raw_field(self):
        foo = Mock()
        bar = Mock()
        bar.value = 3
        foo.bar = bar
        field = fields.Raw()
        self.assertEqual(field.output("bar.value", foo), 3)

    def test_formatted_string_invalid_obj(self):
        field = fields.FormattedString("{hey}")
        self.assertRaises(MarshallingException, lambda: field.output("hey", None))

    def test_formatted_string(self):
        field = fields.FormattedString("{hey}")
        self.assertEqual("3", field.output("hey", Foo()))

    def test_string_with_attribute(self):
        field = fields.String(attribute="hey")
        self.assertEqual("3", field.output("foo", Foo()))

    def test_string_with_lambda(self):
        field = fields.String(attribute=lambda x: x.hey)
        self.assertEqual("3", field.output("foo", Foo()))

    def test_string_with_partial(self):

        def f(x, suffix):
            return "%s-%s" % (x.hey, suffix)

        p = partial(f, suffix="whatever")
        field = fields.String(attribute=p)
        self.assertEqual("3-whatever", field.output("foo", Foo()))

    def test_url_invalid_object(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url("foobar")

        with app.test_request_context("/"):
            self.assertRaises(MarshallingException, lambda: field.output("hey", None))

    def test_url(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url("foobar")

        with app.test_request_context("/"):
            self.assertEqual("/3", field.output("hey", Foo()))

    def test_url_absolute(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url("foobar", absolute=True)

        with app.test_request_context("/"):
            self.assertEqual("http://localhost/3", field.output("hey", Foo()))

    def test_url_absolute_scheme(self):
        """Url.scheme should override current_request.scheme"""
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url("foobar", absolute=True, scheme='https')

        with app.test_request_context("/", base_url="http://localhost"):
            self.assertEqual("https://localhost/3", field.output("hey", Foo()))

    def test_url_without_endpoint_invalid_object(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url()

        with app.test_request_context("/hey"):
            self.assertRaises(MarshallingException, lambda: field.output("hey", None))

    def test_url_without_endpoint(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url()

        with app.test_request_context("/hey"):
            self.assertEqual("/3", field.output("hey", Foo()))

    def test_url_without_endpoint_absolute(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url(absolute=True)

        with app.test_request_context("/hey"):
            self.assertEqual("http://localhost/3", field.output("hey", Foo()))

    def test_url_without_endpoint_absolute_scheme(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url(absolute=True, scheme='https')

        with app.test_request_context("/hey", base_url="http://localhost"):
            self.assertEqual("https://localhost/3", field.output("hey", Foo()))

    def test_url_with_blueprint_invalid_object(self):
        app = Flask(__name__)
        bp = Blueprint("foo", __name__, url_prefix="/foo")
        bp.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        app.register_blueprint(bp)
        field = fields.Url()

        with app.test_request_context("/foo/hey"):
            self.assertRaises(MarshallingException, lambda: field.output("hey", None))

    def test_url_with_blueprint(self):
        app = Flask(__name__)
        bp = Blueprint("foo", __name__, url_prefix="/foo")
        bp.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        app.register_blueprint(bp)
        field = fields.Url()

        with app.test_request_context("/foo/hey"):
            self.assertEqual("/foo/3", field.output("hey", Foo()))

    def test_url_with_blueprint_absolute(self):
        app = Flask(__name__)
        bp = Blueprint("foo", __name__, url_prefix="/foo")
        bp.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        app.register_blueprint(bp)
        field = fields.Url(absolute=True)

        with app.test_request_context("/foo/hey"):
            self.assertEqual("http://localhost/foo/3", field.output("hey", Foo()))

    def test_url_with_blueprint_absolute_scheme(self):
        app = Flask(__name__)
        bp = Blueprint("foo", __name__, url_prefix="/foo")
        bp.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        app.register_blueprint(bp)
        field = fields.Url(absolute=True, scheme='https')

        with app.test_request_context("/foo/hey", base_url="http://localhost"):
            self.assertEqual("https://localhost/foo/3", field.output("hey", Foo()))

    def test_url_superclass_kwargs(self):
        app = Flask(__name__)
        app.add_url_rule("/<hey>", "foobar", view_func=lambda x: x)
        field = fields.Url(absolute=True, attribute='hey')

        with app.test_request_context("/hey"):
            self.assertEqual("http://localhost/3", field.output("hey", Foo()))

    def test_int(self):
        field = fields.Integer()
        self.assertEqual(3, field.output("hey", {'hey': 3}))

    def test_int_default(self):
        field = fields.Integer(default=1)
        self.assertEqual(1, field.output("hey", {'hey': None}))

    def test_no_int(self):
        field = fields.Integer()
        self.assertEqual(0, field.output("hey", {'hey': None}))

    def test_int_decode_error(self):
        field = fields.Integer()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': 'Explode please I am nowhere looking like an int'}))

    def test_float(self):
        field = fields.Float()
        self.assertEqual(3.0, field.output("hey", {'hey': 3.0}))

    def test_float_decode_error(self):
        field = fields.Float()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': 'Explode!'}))

    PI_STR = u'3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861'
    PI = Decimal(PI_STR)

    def test_arbitrary(self):
        field = fields.Arbitrary()
        self.assertEqual(self.PI_STR, field.output("hey", {'hey': self.PI}))

    def test_fixed(self):
        field5 = fields.Fixed(5)
        field4 = fields.Fixed(4)

        self.assertEqual('3.14159', field5.output("hey", {'hey': self.PI}))
        self.assertEqual('3.1416', field4.output("hey", {'hey': self.PI}))
        self.assertEqual('3.0000', field4.output("hey", {'hey': '3'}))
        self.assertEqual('3.0000', field4.output("hey", {'hey': '03'}))
        self.assertEqual('3.0000', field4.output("hey", {'hey': '03.0'}))

    def test_zero_fixed(self):
        field = fields.Fixed()
        self.assertEqual('0.00000', field.output('hey', {'hey': 0}))

    def test_infinite_fixed(self):
        field = fields.Fixed()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': '+inf'}))
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': '-inf'}))

    def test_advanced_fixed(self):
        field = fields.Fixed()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': 'NaN'}))

    def test_fixed_with_attribute(self):
        field = fields.Fixed(4, attribute="bar")
        self.assertEqual('3.0000', field.output("foo", {'bar': '3'}))

    def test_string(self):
        field = fields.String()
        self.assertEqual("3", field.output("hey", Foo()))

    def test_string_no_value(self):
        field = fields.String()
        self.assertEqual(None, field.output("bar", Foo()))

    def test_string_none(self):
        field = fields.String()
        self.assertEqual(None, field.output("empty", {'empty': None}))

    def test_rfc822_date_field_without_offset(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
        field = fields.DateTime()
        self.assertEqual("Mon, 22 Aug 2011 20:58:45 -0000", field.output("bar", obj))

    def test_rfc822_date_field_with_offset(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45, tzinfo=pytz.timezone('CET'))}
        field = fields.DateTime()
        self.assertEqual("Mon, 22 Aug 2011 19:58:45 -0000", field.output("bar", obj))

    def test_iso8601_date_field_without_offset(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
        field = fields.DateTime(dt_format='iso8601')
        self.assertEqual("2011-08-22T20:58:45", field.output("bar", obj))

    def test_iso8601_date_field_with_offset(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45, tzinfo=pytz.timezone('CET'))}
        field = fields.DateTime(dt_format='iso8601')
        self.assertEqual("2011-08-22T20:58:45+01:00", field.output("bar", obj))

    def test_unsupported_datetime_format(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
        field = fields.DateTime(dt_format='raw')
        self.assertRaises(MarshallingException, lambda: field.output('bar', obj))

    def test_to_dict(self):
        obj = {"hey": 3}
        self.assertEqual(obj, fields.to_marshallable_type(obj))

    def test_to_dict_obj(self):
        obj = {"hey": 3}
        self.assertEqual(obj, fields.to_marshallable_type(Foo()))

    def test_to_dict_custom_marshal(self):
        obj = {"hey": 3}
        self.assertEqual(obj, fields.to_marshallable_type(Bar()))

    def test_get_value(self):
        self.assertEqual(3, fields.get_value("hey", {"hey": 3}))

    def test_get_value_no_value(self):
        self.assertEqual(None, fields.get_value("foo", {"hey": 3}))

    def test_get_value_obj(self):
        self.assertEqual(3, fields.get_value("hey", Foo()))

    def test_list(self):
        obj = {'list': ['a', 'b', 'c']}
        field = fields.List(fields.String)
        self.assertEqual(['a', 'b', 'c'], field.output('list', obj))

    def test_list_from_set(self):
        obj = {'list': set(['a', 'b', 'c'])}
        field = fields.List(fields.String)
        self.assertEqual(set(['a', 'b', 'c']), set(field.output('list', obj)))

    def test_list_from_object(self):
        class TestObject(object):
            def __init__(self, list):
                self.list = list
        obj = TestObject(['a', 'b', 'c'])
        field = fields.List(fields.String)
        self.assertEqual(['a', 'b', 'c'], field.output('list', obj))

    def test_list_with_attribute(self):
        class TestObject(object):
            def __init__(self, list):
                self.foo = list
        obj = TestObject(['a', 'b', 'c'])
        field = fields.List(fields.String, attribute='foo')
        self.assertEqual(['a', 'b', 'c'], field.output('list', obj))

    def test_list_with_scoped_attribute_on_dict_or_obj(self):
        class TestObject(object):
            def __init__(self, list_):
                self.bar = list_

        class TestEgg(object):
            def __init__(self, val):
                self.attrib = val

        eggs = [TestEgg(i) for i in ['a', 'b', 'c']]
        test_obj = TestObject(eggs)
        test_dict = {'bar': [{'attrib': 'a'}, {'attrib':'b'}, {'attrib':'c'}]}

        field = fields.List(fields.String(attribute='attrib'), attribute='bar')
        self.assertEqual(['a', 'b', 'c'], field.output('bar', test_obj))
        self.assertEqual(['a', 'b', 'c'], field.output('bar', test_dict))

    def test_null_list(self):
        class TestObject(object):
            def __init__(self, list):
                self.list = list
        obj = TestObject(None)
        field = fields.List(fields.String)
        self.assertEqual(None, field.output('list', obj))

    def test_indexable_object(self):
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
        self.assertEqual("hi", field.output("foo", obj))

    def test_list_from_dict_with_attribute(self):
        obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
        field = fields.List(fields.Integer(attribute='a'))
        self.assertEqual([1, 2, 3], field.output('list', obj))

    def test_list_of_nested(self):
        obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
        field = fields.List(fields.Nested({'a': fields.Integer}))
        self.assertEqual([OrderedDict([('a', 1)]), OrderedDict([('a', 2)]), OrderedDict([('a', 3)])],
                          field.output('list', obj))

    def test_nested_with_default(self):
        obj = None
        field = fields.Nested({'a': fields.Integer, 'b': fields.String}, default={})
        self.assertEqual({}, field.output('a', obj))

    def test_list_of_raw(self):
        obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
        field = fields.List(fields.Raw)
        self.assertEqual([OrderedDict([('a', 1), ('b', 1), ]),
                           OrderedDict([('a', 2), ('b', 1), ]),
                           OrderedDict([('a', 3), ('b', 1), ])],
                          field.output('list', obj))

        obj = {'list': [1, 2, 'a']}
        field = fields.List(fields.Raw)
        self.assertEqual([1, 2, 'a'], field.output('list', obj))


if __name__ == '__main__':
    unittest.main()
