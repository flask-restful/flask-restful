from decimal import Decimal
import unittest
from mock import Mock
from flask.ext.restful.fields import MarshallingException
from flask_restful import fields
from datetime import datetime
from flask import Flask
#noinspection PyUnresolvedReferences
from nose.tools import assert_equals # you need it for tests in form of continuations


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
        ("-3.13", "-3.13"),
        (str(-3.13), "-3.13"),
        (3, "3"),
    ]
    for value, expected in values:
        yield check_field, expected, fields.Arbitrary(), value


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


class FieldsTestCase(unittest.TestCase):

    def test_decimal_trash(self):
        self.assertRaises(MarshallingException, lambda: fields.Float().output('a', {'a': 'Foo'}))

    def test_basic_dictionary(self):
        obj = {"foo": 3}
        field = fields.String()
        self.assertEquals(field.output("foo", obj), "3")


    def test_no_attribute(self):
        obj = {"bar": 3}
        field = fields.String()
        self.assertEquals(field.output("foo", obj), None)


    def test_date_field_invalid(self):
        obj = {"bar": 3}
        field = fields.DateTime()
        self.assertRaises(MarshallingException, lambda: field.output("bar", obj))


    def test_attribute(self):
        obj = {"bar": 3}
        field = fields.String(attribute="bar")
        self.assertEquals(field.output("foo", obj), "3")


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
        self.assertEquals(field.output("foo", obj), "/foo/4/3/")


    def test_formatting_field(self):
        obj = Mock()
        obj.sid = 3
        obj.account_sid = 4
        field = fields.FormattedString("/foo/{account_sid}/{sid}/")
        self.assertEquals(field.output("foo", obj), "/foo/4/3/")


    def test_basic_field(self):
        obj = Mock()
        obj.foo = 3
        field = fields.Raw()
        self.assertEquals(field.output("foo", obj), 3)


    def test_raw_field(self):
        obj = Mock()
        obj.foo = 3
        field = fields.Raw()
        self.assertEquals(field.output("foo", obj), 3)


    def test_nested_raw_field(self):
        foo = Mock()
        bar = Mock()
        bar.value = 3
        foo.bar = bar
        field = fields.Raw()
        self.assertEquals(field.output("bar.value", foo), 3)


    def test_formatted_string_invalid_obj(self):
        field = fields.FormattedString("{hey}")
        self.assertRaises(MarshallingException, lambda: field.output("hey", None))


    def test_formatted_string(self):
        field = fields.FormattedString("{hey}")
        self.assertEquals("3", field.output("hey", Foo()))


    def test_string_with_attribute(self):
        field = fields.String(attribute="hey")
        self.assertEquals("3", field.output("foo", Foo()))


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
            self.assertEquals("/3", field.output("hey", Foo()))

    def test_int(self):
        field = fields.Integer()
        self.assertEquals(3, field.output("hey", {'hey': 3}))


    def test_int_default(self):
        field = fields.Integer(default=1)
        self.assertEquals(1, field.output("hey", {'hey': None}))


    def test_no_int(self):
        field = fields.Integer()
        self.assertEquals(0, field.output("hey", {'hey': None}))

    def test_int_decode_error(self):
        field = fields.Integer()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': 'Explode please I am nowhere looking like an int'}))

    def test_float(self):
        field = fields.Float()
        self.assertEquals('3.0', field.output("hey", {'hey': 3.0}))

    def test_float_decode_error(self):
        field = fields.Float()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': 'Explode!'}))

    PI_STR = u'3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861'
    PI = Decimal(PI_STR)

    def test_arbitrary(self):
        field = fields.Arbitrary()
        self.assertEquals(self.PI_STR, field.output("hey", {'hey': self.PI}))

    def test_fixed(self):
        field5 = fields.Fixed(5)
        field4 = fields.Fixed(4)

        self.assertEquals('3.14159', field5.output("hey", {'hey': self.PI}))
        self.assertEquals('3.1416', field4.output("hey", {'hey': self.PI}))
        self.assertEquals('3.0000', field4.output("hey", {'hey': '3'}))
        self.assertEquals('3.0000', field4.output("hey", {'hey': '03'}))
        self.assertEquals('3.0000', field4.output("hey", {'hey': '03.0'}))

    def test_zero_fixed(self):
        field = fields.Fixed()
        self.assertEquals('0.00000', field.output('hey', {'hey': 0}))

    def test_infinite_fixed(self):
        field = fields.Fixed()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': '+inf'}))
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': '-inf'}))


    def test_advanced_fixed(self):
        field = fields.Fixed()
        self.assertRaises(MarshallingException, lambda: field.output("hey", {'hey': 'NaN'}))

    def test_fixed_with_attribute(self):
        field = fields.Fixed(4, attribute="bar")
        self.assertEquals('3.0000', field.output("foo", {'bar': '3'}))


    def test_string(self):
        field = fields.String()
        self.assertEquals("3", field.output("hey", Foo()))


    def test_string_no_value(self):
        field = fields.String()
        self.assertEquals(None, field.output("bar", Foo()))


    def test_string_none(self):
        field = fields.String()
        self.assertEquals(None, field.output("empty", {'empty': None}))


    def test_date_field_with_offset(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
        field = fields.DateTime()
        self.assertEquals("Mon, 22 Aug 2011 20:58:45 -0000", field.output("bar", obj))


    def test_to_dict(self):
        obj = {"hey": 3}
        self.assertEquals(obj, fields.to_marshallable_type(obj))


    def test_to_dict_obj(self):
        obj = {"hey": 3}
        self.assertEquals(obj, fields.to_marshallable_type(Foo()))

    def test_to_dict_custom_marshal(self):
        obj = {"hey": 3}
        self.assertEquals(obj, fields.to_marshallable_type(Bar()))

    def test_get_value(self):
        self.assertEquals(3, fields.get_value("hey", {"hey": 3}))


    def test_get_value_no_value(self):
        self.assertEquals(None, fields.get_value("foo", {"hey": 3}))


    def test_get_value_obj(self):
        self.assertEquals(3, fields.get_value("hey", Foo()))

    def test_list(self):
        obj = {'list': ['a', 'b', 'c']}
        field = fields.List(fields.String)
        self.assertEquals(['a', 'b', 'c'], field.output('list', obj))

    def test_list_from_object(self):
        class TestObject(object):
            def __init__(self, list):
                self.list = list
        obj = TestObject(['a', 'b', 'c'])
        field = fields.List(fields.String)
        self.assertEquals(['a', 'b', 'c'], field.output('list', obj))

    def test_list_with_attribute(self):
        class TestObject(object):
            def __init__(self, list):
                self.foo = list
        obj = TestObject(['a', 'b', 'c'])
        field = fields.List(fields.String, attribute='foo')
        self.assertEquals(['a', 'b', 'c'], field.output('list', obj))

    def test_null_list(self):
        class TestObject(object):
            def __init__(self, list):
                self.list = list
        obj = TestObject(None)
        field = fields.List(fields.String)
        self.assertEquals(None, field.output('list', obj))

if __name__ == '__main__':
    unittest.main()
