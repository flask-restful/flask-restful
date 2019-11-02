# -*- coding: utf-8 -*-
import unittest

import pytest
from mock import Mock, patch
from flask import Flask
from werkzeug import exceptions
from werkzeug.datastructures import FileStorage, MultiDict
from werkzeug.wrappers import Request
from flask_restful.reqparse import Argument, RequestParser, Namespace
import six
import decimal

import json


def test_default_help():
    arg = Argument("foo")
    assert arg.help is None


@patch('flask_restful.abort')
def test_help_with_error_msg(abort, app):
    with app.app_context():
        parser = RequestParser()
        parser.add_argument('foo', choices=('one', 'two'), help='Bad choice: {error_msg}')
        req = Mock(['values'])
        req.values = MultiDict([('foo', 'three')])
        parser.parse_args(req)
        expected = {'foo': 'Bad choice: three is not a valid choice'}
        abort.assert_called_with(400, message=expected)


@patch('flask_restful.abort')
def test_help_with_unicode_error_msg(abort, app):
    with app.app_context():
        parser = RequestParser()
        parser.add_argument('foo', choices=('one', 'two'), help=u'Bad choice: {error_msg}')
        req = Mock(['values'])
        req.values = MultiDict([('foo', u'\xf0\x9f\x8d\x95')])
        parser.parse_args(req)
        expected = {'foo': u'Bad choice: \xf0\x9f\x8d\x95 is not a valid choice'}
        abort.assert_called_with(400, message=expected)


@patch('flask_restful.abort')
def test_help_no_error_msg(abort, app):
    with app.app_context():
        parser = RequestParser()
        parser.add_argument('foo', choices=['one', 'two'], help='Please select a valid choice')
        req = Mock(['values'])
        req.values = MultiDict([('foo', 'three')])
        parser.parse_args(req)
        expected = {'foo': 'Please select a valid choice'}
        abort.assert_called_with(400, message=expected)


@patch('flask_restful.abort', side_effect=exceptions.BadRequest('Bad Request'))
def test_no_help(abort, app):
    def bad_choice():
        parser = RequestParser()
        parser.add_argument('foo', choices=['one', 'two'])
        req = Mock(['values'])
        req.values = MultiDict([('foo', 'three')])
        parser.parse_args(req)
        abort.assert_called_with(400, message='three is not a valid choice')
    with app.app_context():
        with pytest.raises(exceptions.BadRequest):
            bad_choice()


def test_name():
    arg = Argument("foo")
    assert arg.name == "foo"


def test_dest():
    arg = Argument("foo", dest="foobar")
    assert arg.dest == "foobar"


def test_location_url():
    arg = Argument("foo", location="url")
    assert arg.location == "url"


def test_location_url_list():
    arg = Argument("foo", location=["url"])
    assert arg.location == ["url"]


def test_location_header():
    arg = Argument("foo", location="headers")
    assert arg.location == "headers"


def test_location_json():
    arg = Argument("foo", location="json")
    assert arg.location == "json"


def test_location_get_json():
    arg = Argument("foo", location="get_json")
    assert arg.location == "get_json"


def test_location_header_list():
    arg = Argument("foo", location=["headers"])
    assert arg.location == ["headers"]


def test_type():
    arg = Argument("foo", type=int)
    assert arg.type == int


def test_default():
    arg = Argument("foo", default=True)
    assert arg.default == True


def test_required():
    arg = Argument("foo", required=True)
    assert arg.required == True


def test_ignore():
    arg = Argument("foo", ignore=True)
    assert arg.ignore == True


def test_operator():
    arg = Argument("foo", operators=[">=", "<=", "="])
    assert arg.operators, [">=", "<=" == "="]


def test_action_filter():
    arg = Argument("foo", action="filter")
    assert arg.action == u"filter"


def test_action():
    arg = Argument("foo", action="append")
    assert arg.action == u"append"


def test_choices():
    arg = Argument("foo", choices=[1, 2])
    assert arg.choices, [1 == 2]


def test_default_dest():
    arg = Argument("foo")
    assert arg.dest is None


def test_default_operators():
    arg = Argument("foo")
    assert arg.operators[0] == "="
    assert len(arg.operators) == 1

@patch('flask_restful.reqparse.six')
def test_default_type(mock_six):
    arg = Argument("foo")
    sentinel = object()
    arg.type(sentinel)
    mock_six.text_type.assert_called_with(sentinel)


def test_default_default():
    arg = Argument("foo")
    assert arg.default is None


def test_required_default():
    arg = Argument("foo")
    assert arg.required == False


def test_ignore_default():
    arg = Argument("foo")
    assert arg.ignore == False


def test_action_default():
    arg = Argument("foo")
    assert arg.action == u"store"


def test_choices_default():
    arg = Argument("foo")
    assert len(arg.choices) == 0


def test_source():
    req = Mock(['args', 'headers', 'values'])
    req.args = {'foo': 'bar'}
    req.headers = {'baz': 'bat'}
    arg = Argument('foo', location=['args'])
    assert arg.source(req) == MultiDict(req.args)

    arg = Argument('foo', location=['headers'])
    assert arg.source(req) == MultiDict(req.headers)


def test_convert_default_type_with_null_input():
    arg = Argument('foo')
    assert arg.convert(None, None) is None


def test_convert_with_null_input_when_not_nullable():
    arg = Argument('foo', nullable=False)
    with pytest.raises(ValueError):
        arg.convert(None, None)


def test_source_bad_location():
    req = Mock(['values'])
    arg = Argument('foo', location=['foo'])
    assert len(arg.source(req)) == 0  # yes, basically you don't find it


def test_source_default_location():
    req = Mock(['values'])
    req._get_child_mock = lambda **kwargs: MultiDict()
    arg = Argument('foo')
    assert arg.source(req) == req.values


def test_option_case_sensitive():
    arg = Argument("foo", choices=["bar", "baz"], case_sensitive=True)
    assert True == arg.case_sensitive

    # Insensitive
    arg = Argument("foo", choices=["bar", "baz"], case_sensitive=False)
    assert False == arg.case_sensitive

    # Default
    arg = Argument("foo", choices=["bar", "baz"])
    assert True == arg.case_sensitive


def test_viewargs():
    req = Request.from_values()
    req.view_args = {"foo": "bar"}
    parser = RequestParser()
    parser.add_argument("foo", location=["view_args"])
    args = parser.parse_args(req)
    assert args['foo'] == "bar"

    req = Mock()
    req.values = ()
    req.json = None
    req.view_args = {"foo": "bar"}
    parser = RequestParser()
    parser.add_argument("foo", store_missing=True)
    args = parser.parse_args(req)
    assert args["foo"] is None


def test_parse_unicode():
    req = Request.from_values("/bubble?foo=barß")
    parser = RequestParser()
    parser.add_argument("foo")

    args = parser.parse_args(req)
    assert args['foo'] == u"barß"


def test_parse_unicode_app(app):
    parser = RequestParser()
    parser.add_argument("foo")

    with app.test_request_context('/bubble?foo=barß'):
        args = parser.parse_args()
        assert args['foo'] == u"barß"


def test_json_location(app):
    parser = RequestParser()
    parser.add_argument("foo", location="json", store_missing=True)

    with app.test_request_context('/bubble', method="post"):
        args = parser.parse_args()
        assert args['foo'] is None


def test_get_json_location(app):
    parser = RequestParser()
    parser.add_argument("foo", location="json")

    with app.test_request_context('/bubble', method="post",
                                  data=json.dumps({"foo": "bar"}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['foo'] == 'bar'


def test_parse_append_ignore():
    req = Request.from_values("/bubble?foo=bar")

    parser = RequestParser()
    parser.add_argument("foo", ignore=True, type=int, action="append",
                        store_missing=True),

    args = parser.parse_args(req)
    assert args['foo'] is None


def test_parse_append_default():
    req = Request.from_values("/bubble?")

    parser = RequestParser()
    parser.add_argument("foo", action="append", store_missing=True),

    args = parser.parse_args(req)
    assert args['foo'] is None


def test_parse_append():
    req = Request.from_values("/bubble?foo=bar&foo=bat")

    parser = RequestParser()
    parser.add_argument("foo", action="append"),

    args = parser.parse_args(req)
    assert args['foo'], ["bar" == "bat"]


def test_parse_append_single():
    req = Request.from_values("/bubble?foo=bar")

    parser = RequestParser()
    parser.add_argument("foo", action="append"),

    args = parser.parse_args(req)
    assert args['foo'] == ["bar"]


def test_parse_append_many():
    req = Request.from_values("/bubble?foo=bar&foo=bar2")

    parser = RequestParser()
    parser.add_argument("foo", action="append"),

    args = parser.parse_args(req)
    assert args['foo'], ["bar" == "bar2"]


def test_parse_append_many_location_json(app):
    parser = RequestParser()
    parser.add_argument("foo", action='append', location="json")

    with app.test_request_context('/bubble', method="post",
                                  data=json.dumps({"foo": ["bar", "bar2"]}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['foo'], ['bar' == 'bar2']


def test_parse_dest():
    req = Request.from_values("/bubble?foo=bar")

    parser = RequestParser()
    parser.add_argument("foo", dest="bat")

    args = parser.parse_args(req)
    assert args['bat'] == "bar"


def test_parse_gte_lte_eq():
    req = Request.from_values("/bubble?foo>=bar&foo<=bat&foo=foo")

    parser = RequestParser()
    parser.add_argument("foo", operators=[">=", "<=", "="], action="append"),

    args = parser.parse_args(req)
    assert args['foo'], ["bar", "bat" == "foo"]


def test_parse_gte():
    req = Request.from_values("/bubble?foo>=bar")

    parser = RequestParser()
    parser.add_argument("foo", operators=[">="])

    args = parser.parse_args(req)
    assert args['foo'] == "bar"


def test_parse_foo_operators_four_hundred():
    app = Flask(__name__)
    with app.app_context():
        parser = RequestParser()
        parser.add_argument("foo", type=int),

        with pytest.raises(exceptions.BadRequest):
            parser.parse_args(Request.from_values("/bubble?foo=bar"))


def test_parse_foo_operators_ignore():
    parser = RequestParser()
    parser.add_argument("foo", ignore=True, store_missing=True)

    args = parser.parse_args(Request.from_values("/bubble"))
    assert args['foo'] is None


def test_parse_lte_gte_mock():
    mock_type = Mock()
    req = Request.from_values("/bubble?foo<=bar")

    parser = RequestParser()
    parser.add_argument("foo", type=mock_type, operators=["<="])

    parser.parse_args(req)
    mock_type.assert_called_with("bar", "foo", "<=")


def test_parse_lte_gte_append():
    parser = RequestParser()
    parser.add_argument("foo", operators=["<=", "="], action="append")

    args = parser.parse_args(Request.from_values("/bubble?foo<=bar"))
    assert args['foo'] == ["bar"]


def test_parse_lte_gte_missing():
    parser = RequestParser()
    parser.add_argument("foo", operators=["<=", "="])
    args = parser.parse_args(Request.from_values("/bubble?foo<=bar"))
    assert args['foo'] == "bar"


def test_parse_eq_other():
    parser = RequestParser()
    parser.add_argument("foo"),
    args = parser.parse_args(Request.from_values("/bubble?foo=bar&foo=bat"))
    assert args['foo'] == "bar"


def test_parse_eq():
    req = Request.from_values("/bubble?foo=bar")
    parser = RequestParser()
    parser.add_argument("foo"),
    args = parser.parse_args(req)
    assert args['foo'] == "bar"


def test_parse_lte():
    req = Request.from_values("/bubble?foo<=bar")
    parser = RequestParser()
    parser.add_argument("foo", operators=["<="])

    args = parser.parse_args(req)
    assert args['foo'] == "bar"


def test_parse_required(app):
    with app.app_context():
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", required=True, location='values')

        message = ''
        try:
            parser.parse_args(req)
        except exceptions.BadRequest as e:
            message = e.data['message']

        assert message == ({'foo': 'Missing required parameter in '
                                   'the post body or the query '
                                   'string'})

        parser = RequestParser()
        parser.add_argument("bar", required=True, location=['values', 'cookies'])

        try:
            parser.parse_args(req)
        except exceptions.BadRequest as e:
            message = e.data['message']
        assert message ==({'bar': 'Missing required parameter in '
                                  'the post body or the query '
                                  'string or the request\'s '
                                  'cookies'})


def test_parse_error_bundling(app):
    app.config['BUNDLE_ERRORS'] = True
    with app.app_context():
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", required=True, location='values')
        parser.add_argument("bar", required=True, location=['values', 'cookies'])

        message = ''
        try:
            parser.parse_args(req)
        except exceptions.BadRequest as e:
            message = e.data['message']
        error_message = {'foo': 'Missing required parameter in the post '
                                'body or the query string',
                         'bar': 'Missing required parameter in the post '
                                'body or the query string or the '
                                'request\'s cookies'}
        assert message == error_message

def test_parse_error_bundling_w_parser_arg(app):
    app.config['BUNDLE_ERRORS'] = False
    with app.app_context():
        req = Request.from_values("/bubble")

        parser = RequestParser(bundle_errors=True)
        parser.add_argument("foo", required=True, location='values')
        parser.add_argument("bar", required=True, location=['values', 'cookies'])

        message = ''
        try:
            parser.parse_args(req)
        except exceptions.BadRequest as e:
            message = e.data['message']
        error_message = {'foo': 'Missing required parameter in the post '
                                'body or the query string',
                         'bar': 'Missing required parameter in the post '
                         'body or the query string or the request\'s '
                         'cookies'}
        assert message == error_message


def test_parse_default_append():
    req = Request.from_values("/bubble")
    parser = RequestParser()
    parser.add_argument("foo", default="bar", action="append",
                        store_missing=True)

    args = parser.parse_args(req)

    assert args['foo'] == "bar"


def test_parse_default():
    req = Request.from_values("/bubble")

    parser = RequestParser()
    parser.add_argument("foo", default="bar", store_missing=True)

    args = parser.parse_args(req)
    assert args['foo'] == "bar"


def test_parse_callable_default():
    req = Request.from_values("/bubble")

    parser = RequestParser()
    parser.add_argument("foo", default=lambda: "bar", store_missing=True)

    args = parser.parse_args(req)
    assert args['foo'] == "bar"


def test_parse():
    req = Request.from_values("/bubble?foo=bar")

    parser = RequestParser()
    parser.add_argument("foo"),

    args = parser.parse_args(req)
    assert args['foo'] == "bar"


def test_parse_none():
    req = Request.from_values("/bubble")

    parser = RequestParser()
    parser.add_argument("foo")

    args = parser.parse_args(req)
    assert args['foo'] is None


def test_parse_store_missing():
    req = Request.from_values("/bubble")

    parser = RequestParser()
    parser.add_argument("foo", store_missing=False)

    args = parser.parse_args(req)
    assert 'foo' not in args


def test_parse_choices_correct():
    req = Request.from_values("/bubble?foo=bat")

    parser = RequestParser()
    parser.add_argument("foo", choices=["bat"]),

    args = parser.parse_args(req)
    assert args['foo'] == "bat"

def test_parse_choices(app):
    with app.app_context():
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"]),

        with pytest.raises(exceptions.BadRequest):
            parser.parse_args(req)


def test_parse_choices_sensitive():
    app = Flask(__name__)
    with app.app_context():
        req = Request.from_values("/bubble?foo=BAT")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"], case_sensitive=True),

        with pytest.raises(exceptions.BadRequest):
            parser.parse_args(req)


def test_parse_choices_insensitive():
    req = Request.from_values("/bubble?foo=BAT")

    parser = RequestParser()
    parser.add_argument("foo", choices=["bat"], case_sensitive=False),

    args = parser.parse_args(req)
    assert 'bat' == args.get('foo')

    # both choices and args are case_insensitive
    req = Request.from_values("/bubble?foo=bat")

    parser = RequestParser()
    parser.add_argument("foo", choices=["BAT"], case_sensitive=False),

    args = parser.parse_args(req)
    assert 'bat' == args.get('foo')


def test_parse_ignore():
    req = Request.from_values("/bubble?foo=bar")

    parser = RequestParser()
    parser.add_argument("foo", type=int, ignore=True, store_missing=True),

    args = parser.parse_args(req)
    assert args['foo'] is None


def test_chaining():
    parser = RequestParser()
    assert parser is parser.add_argument("foo")


def test_namespace_existence():
    namespace = Namespace()
    namespace.foo = 'bar'
    namespace['bar'] = 'baz'
    assert namespace['foo'] == 'bar'
    assert namespace.bar == 'baz'


def test_namespace_missing():
    namespace = Namespace()
    with pytest.raises(AttributeError):
        namespace.spam
    with pytest.raises(KeyError):
        namespace['eggs']


def test_namespace_configurability():
    req = Request.from_values()
    assert isinstance(RequestParser().parse_args(req), Namespace)
    assert type(RequestParser(namespace_class=dict).parse_args(req)) is dict


def test_none_argument(app):
    parser = RequestParser()
    parser.add_argument("foo", location="json")
    with app.test_request_context('/bubble', method="post",
                                  data=json.dumps({"foo": None}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['foo'] is None


def test_type_callable():
    req = Request.from_values("/bubble?foo=1")

    parser = RequestParser()
    parser.add_argument("foo", type=lambda x: x, required=False),

    args = parser.parse_args(req)
    assert args['foo'] == "1"


def test_type_callable_none(app):
    parser = RequestParser()
    parser.add_argument("foo", type=lambda x: x, location="json", required=False),

    with app.test_request_context('/bubble', method="post",
                                  data=json.dumps({"foo": None}),
                                  content_type='application/json'):
        try:
            args = parser.parse_args()
            assert args['foo'] is None
        except exceptions.BadRequest:
            assert False


def test_type_decimal(app):
    parser = RequestParser()
    parser.add_argument("foo", type=decimal.Decimal, location="json")

    with app.test_request_context('/bubble', method='post',
                                  data=json.dumps({"foo": "1.0025"}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['foo'] == decimal.Decimal("1.0025")


def test_type_filestorage(app):
    parser = RequestParser()
    parser.add_argument("foo", type=FileStorage, location='files')

    fdata = six.b('foo bar baz qux')
    with app.test_request_context('/bubble', method='POST',
                                  data={'foo': (six.BytesIO(fdata), 'baz.txt')}):
        args = parser.parse_args()

        assert args['foo'].name == 'foo'
        assert args['foo'].filename == 'baz.txt'
        assert args['foo'].read() == fdata


def test_filestorage_custom_type(app):
    def _custom_type(f):
        return FileStorage(stream=f.stream,
                           filename="{0}aaaa".format(f.filename),
                           name="{0}aaaa".format(f.name))

    parser = RequestParser()
    parser.add_argument("foo", type=_custom_type, location='files')

    fdata = six.b('foo bar baz qux')
    with app.test_request_context('/bubble', method='POST',
                                  data={'foo': (six.BytesIO(fdata), 'baz.txt')}):
        args = parser.parse_args()

        assert args['foo'].name == 'fooaaaa'
        assert args['foo'].filename == 'baz.txtaaaa'
        assert args['foo'].read() == fdata


def test_passing_arguments_object():
    req = Request.from_values("/bubble?foo=bar")
    parser = RequestParser()
    parser.add_argument(Argument("foo"))

    args = parser.parse_args(req)
    assert args['foo'] == u"bar"


def test_int_choice_types(app):
    parser = RequestParser()
    parser.add_argument("foo", type=int, choices=[1, 2, 3], location='json')

    with app.test_request_context(
            '/bubble', method='post',
            data=json.dumps({'foo': 5}),
            content_type='application/json'
    ):
        with pytest.raises(exceptions.BadRequest):
            parser.parse_args()

def test_int_range_choice_types(app):
    parser = RequestParser()
    parser.add_argument("foo", type=int, choices=range(100), location='json')

    with app.test_request_context(
            '/bubble', method='post',
            data=json.dumps({'foo': 101}),
            content_type='application/json'
    ):
        with pytest.raises(exceptions.BadRequest):
            parser.parse_args()

def test_request_parser_copy():
    req = Request.from_values("/bubble?foo=101&bar=baz")
    parser = RequestParser()
    foo_arg = Argument('foo', type=int)
    parser.args.append(foo_arg)
    parser_copy = parser.copy()

    # Deepcopy should create a clone of the argument object instead of
    # copying a reference to the new args list
    assert foo_arg not in parser_copy.args

    # Args added to new parser should not be added to the original
    bar_arg = Argument('bar')
    parser_copy.args.append(bar_arg)
    assert bar_arg not in parser.args

    args = parser_copy.parse_args(req)
    assert args['foo'] == 101
    assert args['bar'] == u'baz'


def test_request_parse_copy_including_settings():
    parser = RequestParser(trim=True, bundle_errors=True)
    parser_copy = parser.copy()

    assert parser.trim == parser_copy.trim
    assert parser.bundle_errors == parser_copy.bundle_errors


def test_request_parser_replace_argument():
    req = Request.from_values("/bubble?foo=baz")
    parser = RequestParser()
    parser.add_argument('foo', type=int)
    parser_copy = parser.copy()
    parser_copy.replace_argument('foo')

    args = parser_copy.parse_args(req)
    assert args['foo'] == u'baz'


def test_both_json_and_values_location(app):
    parser = RequestParser()
    parser.add_argument('foo', type=int)
    parser.add_argument('baz', type=int)
    with app.test_request_context('/bubble?foo=1', method="post",
                                  data=json.dumps({"baz": 2}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['foo'] == 1
        assert args['baz'] == 2


def test_not_json_location_and_content_type_json(app):
    parser = RequestParser()
    parser.add_argument('foo', location='args')

    with app.test_request_context('/bubble', method='get',
                                  content_type='application/json'):
        parser.parse_args()  # Should not raise a 400: BadRequest


def test_request_parser_remove_argument():
    req = Request.from_values("/bubble?foo=baz")
    parser = RequestParser()
    parser.add_argument('foo', type=int)
    parser_copy = parser.copy()
    parser_copy.remove_argument('foo')

    args = parser_copy.parse_args(req)
    assert args == {}


def test_strict_parsing_off():
    req = Request.from_values("/bubble?foo=baz")
    parser = RequestParser()
    args = parser.parse_args(req)
    assert args == {}


def test_strict_parsing_on():
    req = Request.from_values("/bubble?foo=baz")
    parser = RequestParser()
    with pytest.raises(exceptions.BadRequest):
        parser.parse_args(req, strict=True)


def test_strict_parsing_off_partial_hit():
    req = Request.from_values("/bubble?foo=1&bar=bees&n=22")
    parser = RequestParser()
    parser.add_argument('foo', type=int)
    args = parser.parse_args(req)
    assert args['foo'] == 1


def test_strict_parsing_on_partial_hit():
    req = Request.from_values("/bubble?foo=1&bar=bees&n=22")
    parser = RequestParser()
    parser.add_argument('foo', type=int)
    with pytest.raises(exceptions.BadRequest):
        parser.parse_args(req, strict=True)


def test_trim_argument():
    req = Request.from_values("/bubble?foo= 1 &bar=bees&n=22")
    parser = RequestParser()
    parser.add_argument('foo')
    args = parser.parse_args(req)
    assert args['foo'] == ' 1 '

    parser = RequestParser()
    parser.add_argument('foo', trim=True)
    args = parser.parse_args(req)
    assert args['foo'] == '1'

    parser = RequestParser()
    parser.add_argument('foo', trim=True, type=int)
    args = parser.parse_args(req)
    assert args['foo'] == 1


def test_trim_request_parser():
    req = Request.from_values("/bubble?foo= 1 &bar=bees&n=22")
    parser = RequestParser(trim=False)
    parser.add_argument('foo')
    args = parser.parse_args(req)
    assert args['foo'] == ' 1 '

    parser = RequestParser(trim=True)
    parser.add_argument('foo')
    args = parser.parse_args(req)
    assert args['foo'] == '1'

    parser = RequestParser(trim=True)
    parser.add_argument('foo', type=int)
    args = parser.parse_args(req)
    assert args['foo'] == 1


def test_trim_request_parser_override_by_argument():
    parser = RequestParser(trim=True)
    parser.add_argument('foo', trim=False)

    assert not parser.args[0].trim


def test_trim_request_parser_json(app):
    parser = RequestParser(trim=True)
    parser.add_argument("foo", location="json")
    parser.add_argument("int1", location="json", type=int)
    parser.add_argument("int2", location="json", type=int)

    with app.test_request_context('/bubble', method="post",
                                  data=json.dumps({"foo": " bar ", "int1": 1, "int2": " 2 "}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['foo'] == 'bar'
        assert args['int1'] == 1
        assert args['int2'] == 2


def test_list_argument(app):
    parser = RequestParser()
    parser.add_argument('arg1', location='json', type=list)

    with app.test_request_context('/bubble', method="post",
                                  data=json.dumps({'arg1': ['foo', 'bar']}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['arg1'] == ['foo', 'bar']


def test_list_argument_dict(app):
    parser = RequestParser()
    parser.add_argument('arg1', location='json', type=list)

    with app.test_request_context('/bubble', method="post",
                                  data=json.dumps({'arg1': [{'foo': 1, 'bar': 2}]}),
                                  content_type='application/json'):
        args = parser.parse_args()
        assert args['arg1'] == [{'foo': 1, 'bar': 2}]


def test_argument_repr():
    arg = Argument('foo')
    assert 'foo' in arg.__repr__()
    assert arg.__repr__().startswith("Argument('foo'")


def test_argument_str():
    arg = Argument('foo', choices=[1, 2, 3, 4, 5])
    assert 'foo' in str(arg)
    assert str(arg).startswith('Name: foo')
    assert 'choices: [1, 2, 3, 4, 5]' in str(arg)
    arg = Argument('foo', choices=[1, 2, 3, 4, 5, 6])
    assert "choices: [1, 2, 3, '...', 6]" in str(arg)


if __name__ == '__main__':
    unittest.main()
