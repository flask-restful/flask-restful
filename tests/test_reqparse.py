# -*- coding: utf-8 -*-
import unittest
from mock import Mock, patch
from flask import Flask
from werkzeug import exceptions
from werkzeug.wrappers import Request
from werkzeug.datastructures import FileStorage, MultiDict
from flask_restful.reqparse import Argument, RequestParser, Namespace
import six
import decimal

import json


class ReqParseTestCase(unittest.TestCase):
    def test_default_help(self):
        arg = Argument("foo")
        self.assertEqual(arg.help, None)

    @patch('flask_restful.abort')
    def test_help_with_error_msg(self, abort):
        app = Flask(__name__)
        with app.app_context():
            parser = RequestParser()
            parser.add_argument('foo', choices=('one', 'two'), help='Bad choice: {error_msg}')
            req = Mock(['values'])
            req.values = MultiDict([('foo', 'three')])
            parser.parse_args(req)
            expected = {'foo': 'Bad choice: three is not a valid choice'}
            abort.assert_called_with(400, message=expected)

    @patch('flask_restful.abort')
    def test_help_with_unicode_error_msg(self, abort):
        app = Flask(__name__)
        with app.app_context():
            parser = RequestParser()
            parser.add_argument('foo', choices=('one', 'two'), help=u'Bad choice: {error_msg}')
            req = Mock(['values'])
            req.values = MultiDict([('foo', u'\xf0\x9f\x8d\x95')])
            parser.parse_args(req)
            expected = {'foo': u'Bad choice: \xf0\x9f\x8d\x95 is not a valid choice'}
            abort.assert_called_with(400, message=expected)

    @patch('flask_restful.abort')
    def test_help_no_error_msg(self, abort):
        app = Flask(__name__)
        with app.app_context():
            parser = RequestParser()
            parser.add_argument('foo', choices=['one', 'two'], help='Please select a valid choice')
            req = Mock(['values'])
            req.values = MultiDict([('foo', 'three')])
            parser.parse_args(req)
            expected = {'foo': 'Please select a valid choice'}
            abort.assert_called_with(400, message=expected)

    @patch('flask_restful.abort', side_effect=exceptions.BadRequest('Bad Request'))
    def test_no_help(self, abort):
        def bad_choice():
            parser = RequestParser()
            parser.add_argument('foo', choices=['one', 'two'])
            req = Mock(['values'])
            req.values = MultiDict([('foo', 'three')])
            parser.parse_args(req)
            abort.assert_called_with(400, message='three is not a valid choice')
        app = Flask(__name__)
        with app.app_context():
            self.assertRaises(exceptions.BadRequest, bad_choice)

    def test_name(self):
        arg = Argument("foo")
        self.assertEqual(arg.name, "foo")

    def test_dest(self):
        arg = Argument("foo", dest="foobar")
        self.assertEqual(arg.dest, "foobar")

    def test_location_url(self):
        arg = Argument("foo", location="url")
        self.assertEqual(arg.location, "url")

    def test_location_url_list(self):
        arg = Argument("foo", location=["url"])
        self.assertEqual(arg.location, ["url"])

    def test_location_header(self):
        arg = Argument("foo", location="headers")
        self.assertEqual(arg.location, "headers")

    def test_location_json(self):
        arg = Argument("foo", location="json")
        self.assertEqual(arg.location, "json")

    def test_location_get_json(self):
        arg = Argument("foo", location="get_json")
        self.assertEqual(arg.location, "get_json")

    def test_location_header_list(self):
        arg = Argument("foo", location=["headers"])
        self.assertEqual(arg.location, ["headers"])

    def test_type(self):
        arg = Argument("foo", type=int)
        self.assertEqual(arg.type, int)

    def test_default(self):
        arg = Argument("foo", default=True)
        self.assertEqual(arg.default, True)

    def test_required(self):
        arg = Argument("foo", required=True)
        self.assertEqual(arg.required, True)

    def test_ignore(self):
        arg = Argument("foo", ignore=True)
        self.assertEqual(arg.ignore, True)

    def test_operator(self):
        arg = Argument("foo", operators=[">=", "<=", "="])
        self.assertEqual(arg.operators, [">=", "<=", "="])

    def test_action_filter(self):
        arg = Argument("foo", action="filter")
        self.assertEqual(arg.action, u"filter")

    def test_action(self):
        arg = Argument("foo", action="append")
        self.assertEqual(arg.action, u"append")

    def test_choices(self):
        arg = Argument("foo", choices=[1, 2])
        self.assertEqual(arg.choices, [1, 2])

    def test_default_dest(self):
        arg = Argument("foo")
        self.assertEqual(arg.dest, None)

    def test_default_operators(self):
        arg = Argument("foo")
        self.assertEqual(arg.operators[0], "=")
        self.assertEqual(len(arg.operators), 1)

    @patch('flask_restful.reqparse.six')
    def test_default_type(self, mock_six):
        arg = Argument("foo")
        sentinel = object()
        arg.type(sentinel)
        mock_six.text_type.assert_called_with(sentinel)

    def test_default_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.default, None)

    def test_required_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.required, False)

    def test_ignore_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.ignore, False)

    def test_action_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.action, u"store")

    def test_choices_default(self):
        arg = Argument("foo")
        self.assertEqual(len(arg.choices), 0)

    def test_source(self):
        req = Mock(['args', 'headers', 'values'])
        req.args = {'foo': 'bar'}
        req.headers = {'baz': 'bat'}
        arg = Argument('foo', location=['args'])
        self.assertEqual(arg.source(req), MultiDict(req.args))

        arg = Argument('foo', location=['headers'])
        self.assertEqual(arg.source(req), MultiDict(req.headers))

    def test_convert_default_type_with_null_input(self):
        arg = Argument('foo')
        self.assertEqual(arg.convert(None, None), None)

    def test_convert_with_null_input_when_not_nullable(self):
        arg = Argument('foo', nullable=False)
        self.assertRaises(ValueError, lambda: arg.convert(None, None))

    def test_source_bad_location(self):
        req = Mock(['values'])
        arg = Argument('foo', location=['foo'])
        self.assertTrue(len(arg.source(req)) == 0)  # yes, basically you don't find it

    def test_source_default_location(self):
        req = Mock(['values'])
        req._get_child_mock = lambda **kwargs: MultiDict()
        arg = Argument('foo')
        self.assertEqual(arg.source(req), req.values)

    def test_option_case_sensitive(self):
        arg = Argument("foo", choices=["bar", "baz"], case_sensitive=True)
        self.assertEqual(True, arg.case_sensitive)

        # Insensitive
        arg = Argument("foo", choices=["bar", "baz"], case_sensitive=False)
        self.assertEqual(False, arg.case_sensitive)

        # Default
        arg = Argument("foo", choices=["bar", "baz"])
        self.assertEqual(True, arg.case_sensitive)

    def test_viewargs(self):
        req = Request.from_values()
        req.view_args = {"foo": "bar"}
        parser = RequestParser()
        parser.add_argument("foo", location=["view_args"])
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bar")

        req = Mock()
        req.values = ()
        req.json = None
        req.view_args = {"foo": "bar"}
        parser = RequestParser()
        parser.add_argument("foo", store_missing=True)
        args = parser.parse_args(req)
        self.assertEqual(args["foo"], None)

    def test_parse_unicode(self):
        req = Request.from_values("/bubble?foo=barß")
        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], u"barß")

    def test_parse_unicode_app(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo")

        with app.test_request_context('/bubble?foo=barß'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], u"barß")

    def test_json_location(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", location="json", store_missing=True)

        with app.test_request_context('/bubble', method="post"):
            args = parser.parse_args()
            self.assertEqual(args['foo'], None)

    def test_get_json_location(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", location="json")

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": "bar"}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], 'bar')

    def test_parse_append_ignore(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", ignore=True, type=int, action="append",
                            store_missing=True),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], None)

    def test_parse_append_default(self):
        req = Request.from_values("/bubble?")

        parser = RequestParser()
        parser.add_argument("foo", action="append", store_missing=True),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], None)

    def test_parse_append(self):
        req = Request.from_values("/bubble?foo=bar&foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], ["bar", "bat"])

    def test_parse_append_single(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], ["bar"])

    def test_parse_append_many(self):
        req = Request.from_values("/bubble?foo=bar&foo=bar2")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], ["bar", "bar2"])

    def test_parse_append_many_location_json(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", action='append', location="json")

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": ["bar", "bar2"]}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], ['bar', 'bar2'])

    def test_parse_dest(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", dest="bat")

        args = parser.parse_args(req)
        self.assertEqual(args['bat'], "bar")

    def test_parse_gte_lte_eq(self):
        req = Request.from_values("/bubble?foo>=bar&foo<=bat&foo=foo")

        parser = RequestParser()
        parser.add_argument("foo", operators=[">=", "<=", "="], action="append"),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], ["bar", "bat", "foo"])

    def test_parse_gte(self):
        req = Request.from_values("/bubble?foo>=bar")

        parser = RequestParser()
        parser.add_argument("foo", operators=[">="])

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bar")

    def test_parse_foo_operators_four_hunderd(self):
        app = Flask(__name__)
        with app.app_context():
            parser = RequestParser()
            parser.add_argument("foo", type=int),

            self.assertRaises(exceptions.BadRequest, lambda: parser.parse_args(Request.from_values("/bubble?foo=bar")))

    def test_parse_foo_operators_ignore(self):
        parser = RequestParser()
        parser.add_argument("foo", ignore=True, store_missing=True)

        args = parser.parse_args(Request.from_values("/bubble"))
        self.assertEqual(args['foo'], None)

    def test_parse_lte_gte_mock(self):
        mock_type = Mock()
        req = Request.from_values("/bubble?foo<=bar")

        parser = RequestParser()
        parser.add_argument("foo", type=mock_type, operators=["<="])

        parser.parse_args(req)
        mock_type.assert_called_with("bar", "foo", "<=")

    def test_parse_lte_gte_append(self):
        parser = RequestParser()
        parser.add_argument("foo", operators=["<=", "="], action="append")

        args = parser.parse_args(Request.from_values("/bubble?foo<=bar"))
        self.assertEqual(args['foo'], ["bar"])

    def test_parse_lte_gte_missing(self):
        parser = RequestParser()
        parser.add_argument("foo", operators=["<=", "="])
        args = parser.parse_args(Request.from_values("/bubble?foo<=bar"))
        self.assertEqual(args['foo'], "bar")

    def test_parse_eq_other(self):
        parser = RequestParser()
        parser.add_argument("foo"),
        args = parser.parse_args(Request.from_values("/bubble?foo=bar&foo=bat"))
        self.assertEqual(args['foo'], "bar")

    def test_parse_eq(self):
        req = Request.from_values("/bubble?foo=bar")
        parser = RequestParser()
        parser.add_argument("foo"),
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bar")

    def test_parse_lte(self):
        req = Request.from_values("/bubble?foo<=bar")
        parser = RequestParser()
        parser.add_argument("foo", operators=["<="])

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bar")

    def test_parse_required(self):
        app = Flask(__name__)
        with app.app_context():
            req = Request.from_values("/bubble")

            parser = RequestParser()
            parser.add_argument("foo", required=True, location='values')

            message = ''
            try:
                parser.parse_args(req)
            except exceptions.BadRequest as e:
                message = e.data['message']

            self.assertEqual(message, ({'foo': 'Missing required parameter in '
                                                'the post body or the query '
                                                'string'}))

            parser = RequestParser()
            parser.add_argument("bar", required=True, location=['values', 'cookies'])

            try:
                parser.parse_args(req)
            except exceptions.BadRequest as e:
                message = e.data['message']
            self.assertEqual(message, ({'bar': 'Missing required parameter in '
                                                'the post body or the query '
                                                'string or the request\'s '
                                                'cookies'}))

    def test_parse_error_bundling(self):
        app = Flask(__name__)
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
            self.assertEqual(message, error_message)

    def test_parse_error_bundling_w_parser_arg(self):
        app = Flask(__name__)
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
            self.assertEqual(message, error_message)

    def test_parse_default_append(self):
        req = Request.from_values("/bubble")
        parser = RequestParser()
        parser.add_argument("foo", default="bar", action="append",
                            store_missing=True)

        args = parser.parse_args(req)

        self.assertEqual(args['foo'], "bar")

    def test_parse_default(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", default="bar", store_missing=True)

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bar")

    def test_parse_callable_default(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", default=lambda: "bar", store_missing=True)

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bar")

    def test_parse(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo"),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bar")

    def test_parse_none(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], None)

    def test_parse_store_missing(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", store_missing=False)

        args = parser.parse_args(req)
        self.assertFalse('foo' in args)

    def test_parse_choices_correct(self):
        req = Request.from_values("/bubble?foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"]),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "bat")

    def test_parse_choices(self):
        app = Flask(__name__)
        with app.app_context():
            req = Request.from_values("/bubble?foo=bar")

            parser = RequestParser()
            parser.add_argument("foo", choices=["bat"]),

            self.assertRaises(exceptions.BadRequest, lambda: parser.parse_args(req))

    def test_parse_choices_sensitive(self):
        app = Flask(__name__)
        with app.app_context():
            req = Request.from_values("/bubble?foo=BAT")

            parser = RequestParser()
            parser.add_argument("foo", choices=["bat"], case_sensitive=True),

            self.assertRaises(exceptions.BadRequest, lambda: parser.parse_args(req))

    def test_parse_choices_insensitive(self):
        req = Request.from_values("/bubble?foo=BAT")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"], case_sensitive=False),

        args = parser.parse_args(req)
        self.assertEqual('bat', args.get('foo'))

        # both choices and args are case_insensitive
        req = Request.from_values("/bubble?foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", choices=["BAT"], case_sensitive=False),

        args = parser.parse_args(req)
        self.assertEqual('bat', args.get('foo'))

    def test_parse_ignore(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", type=int, ignore=True, store_missing=True),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], None)

    def test_chaining(self):
        parser = RequestParser()
        self.assertTrue(parser is parser.add_argument("foo"))

    def test_namespace_existence(self):
        namespace = Namespace()
        namespace.foo = 'bar'
        namespace['bar'] = 'baz'
        self.assertEqual(namespace['foo'], 'bar')
        self.assertEqual(namespace.bar, 'baz')

    def test_namespace_missing(self):
        namespace = Namespace()
        self.assertRaises(AttributeError, lambda: namespace.spam)
        self.assertRaises(KeyError, lambda: namespace['eggs'])

    def test_namespace_configurability(self):
        req = Request.from_values()
        self.assertTrue(isinstance(RequestParser().parse_args(req), Namespace))
        self.assertTrue(type(RequestParser(namespace_class=dict).parse_args(req)) is dict)

    def test_none_argument(self):

        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", location="json")
        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": None}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], None)

    def test_type_callable(self):
        req = Request.from_values("/bubble?foo=1")

        parser = RequestParser()
        parser.add_argument("foo", type=lambda x: x, required=False),

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "1")

    def test_type_callable_none(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", type=lambda x: x, location="json", required=False),

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": None}),
                                      content_type='application/json'):
            try:
                args = parser.parse_args()
                self.assertEqual(args['foo'], None)
            except exceptions.BadRequest:
                self.fail()

    def test_type_decimal(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", type=decimal.Decimal, location="json")

        with app.test_request_context('/bubble', method='post',
                                      data=json.dumps({"foo": "1.0025"}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], decimal.Decimal("1.0025"))


    def test_type_hard_decimal(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", type=decimal.Decimal, location="json")

        with app.test_request_context('/bubble', method='post',
                                      data=json.dumps({"foo": 89.92}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], decimal.Decimal("89.92"))

    def test_type_filestorage(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", type=FileStorage, location='files')

        fdata = six.b('foo bar baz qux')
        with app.test_request_context('/bubble', method='POST',
                                      data={'foo': (six.BytesIO(fdata), 'baz.txt')}):
            args = parser.parse_args()

            self.assertEqual(args['foo'].name, 'foo')
            self.assertEqual(args['foo'].filename, 'baz.txt')
            self.assertEqual(args['foo'].read(), fdata)

    def test_filestorage_custom_type(self):
        def _custom_type(f):
            return FileStorage(stream=f.stream,
                               filename="{0}aaaa".format(f.filename),
                               name="{0}aaaa".format(f.name))

        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", type=_custom_type, location='files')

        fdata = six.b('foo bar baz qux')
        with app.test_request_context('/bubble', method='POST',
                                      data={'foo': (six.BytesIO(fdata), 'baz.txt')}):
            args = parser.parse_args()

            self.assertEqual(args['foo'].name, 'fooaaaa')
            self.assertEqual(args['foo'].filename, 'baz.txtaaaa')
            self.assertEqual(args['foo'].read(), fdata)

    def test_passing_arguments_object(self):
        req = Request.from_values("/bubble?foo=bar")
        parser = RequestParser()
        parser.add_argument(Argument("foo"))

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], u"bar")

    def test_int_choice_types(self):
        app = Flask(__name__)
        parser = RequestParser()
        parser.add_argument("foo", type=int, choices=[1, 2, 3], location='json')

        with app.test_request_context(
                '/bubble', method='post',
                data=json.dumps({'foo': 5}),
                content_type='application/json'
        ):
            try:
                parser.parse_args()
                self.fail()
            except exceptions.BadRequest:
                pass

    def test_int_range_choice_types(self):
        app = Flask(__name__)
        parser = RequestParser()
        parser.add_argument("foo", type=int, choices=range(100), location='json')

        with app.test_request_context(
                '/bubble', method='post',
                data=json.dumps({'foo': 101}),
                content_type='application/json'
        ):
            try:
                parser.parse_args()
                self.fail()
            except exceptions.BadRequest:
                pass

    def test_request_parser_copy(self):
        req = Request.from_values("/bubble?foo=101&bar=baz")
        parser = RequestParser()
        foo_arg = Argument('foo', type=int)
        parser.args.append(foo_arg)
        parser_copy = parser.copy()

        # Deepcopy should create a clone of the argument object instead of
        # copying a reference to the new args list
        self.assertFalse(foo_arg in parser_copy.args)

        # Args added to new parser should not be added to the original
        bar_arg = Argument('bar')
        parser_copy.args.append(bar_arg)
        self.assertFalse(bar_arg in parser.args)

        args = parser_copy.parse_args(req)
        self.assertEqual(args['foo'], 101)
        self.assertEqual(args['bar'], u'baz')

    def test_request_parse_copy_including_settings(self):
        parser = RequestParser(trim=True, bundle_errors=True)
        parser_copy = parser.copy()

        self.assertEqual(parser.trim, parser_copy.trim)
        self.assertEqual(parser.bundle_errors, parser_copy.bundle_errors)

    def test_request_parser_replace_argument(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        parser_copy = parser.copy()
        parser_copy.replace_argument('foo')

        args = parser_copy.parse_args(req)
        self.assertEqual(args['foo'], u'baz')

    def test_both_json_and_values_location(self):

        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument('foo', type=int)
        parser.add_argument('baz', type=int)
        with app.test_request_context('/bubble?foo=1', method="post",
                                      data=json.dumps({"baz": 2}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], 1)
            self.assertEqual(args['baz'], 2)

    def test_not_json_location_and_content_type_json(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument('foo', location='args')

        with app.test_request_context('/bubble', method='get',
                                      content_type='application/json'):
            parser.parse_args()  # Should not raise a 400: BadRequest

    def test_request_parser_remove_argument(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        parser_copy = parser.copy()
        parser_copy.remove_argument('foo')

        args = parser_copy.parse_args(req)
        self.assertEqual(args, {})

    def test_strict_parsing_off(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        args = parser.parse_args(req)
        self.assertEqual(args, {})

    def test_strict_parsing_on(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        self.assertRaises(exceptions.BadRequest, parser.parse_args, req, strict=True)

    def test_strict_parsing_off_partial_hit(self):
        req = Request.from_values("/bubble?foo=1&bar=bees&n=22")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], 1)

    def test_strict_parsing_on_partial_hit(self):
        req = Request.from_values("/bubble?foo=1&bar=bees&n=22")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        self.assertRaises(exceptions.BadRequest, parser.parse_args, req, strict=True)

    def test_trim_argument(self):
        req = Request.from_values("/bubble?foo= 1 &bar=bees&n=22")
        parser = RequestParser()
        parser.add_argument('foo')
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], ' 1 ')

        parser = RequestParser()
        parser.add_argument('foo', trim=True)
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], '1')

        parser = RequestParser()
        parser.add_argument('foo', trim=True, type=int)
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], 1)

    def test_trim_request_parser(self):
        req = Request.from_values("/bubble?foo= 1 &bar=bees&n=22")
        parser = RequestParser(trim=False)
        parser.add_argument('foo')
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], ' 1 ')

        parser = RequestParser(trim=True)
        parser.add_argument('foo')
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], '1')

        parser = RequestParser(trim=True)
        parser.add_argument('foo', type=int)
        args = parser.parse_args(req)
        self.assertEqual(args['foo'], 1)

    def test_trim_request_parser_override_by_argument(self):
        parser = RequestParser(trim=True)
        parser.add_argument('foo', trim=False)

        self.assertFalse(parser.args[0].trim)

    def test_trim_request_parser_json(self):
        app = Flask(__name__)

        parser = RequestParser(trim=True)
        parser.add_argument("foo", location="json")
        parser.add_argument("int1", location="json", type=int)
        parser.add_argument("int2", location="json", type=int)

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": " bar ", "int1": 1, "int2": " 2 "}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['foo'], 'bar')
            self.assertEqual(args['int1'], 1)
            self.assertEqual(args['int2'], 2)

    def test_list_argument(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument('arg1', location='json', type=list)

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({'arg1': ['foo', 'bar']}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['arg1'], ['foo', 'bar'])

    def test_list_argument_dict(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument('arg1', location='json', type=list)

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({'arg1': [{'foo': 1, 'bar': 2}]}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEqual(args['arg1'], [{'foo': 1, 'bar': 2}])

    def test_argument_repr(self):
        arg = Argument('foo')
        try:  # Python 2.6 compatibility
            self.assertIn('foo', arg.__repr__())
        except AttributeError:
            self.assertTrue('foo' in arg.__repr__())
        self.assertTrue(arg.__repr__().startswith("Argument('foo'"))

    def test_argument_str(self):
        arg = Argument('foo', choices=[1, 2, 3, 4, 5])
        try:  # Python 2.6 compatibility
            self.assertIn('foo', str(arg))
        except AttributeError:
            self.assertTrue('foo' in str(arg))
        self.assertTrue(str(arg).startswith('Name: foo'))
        try:  # Python 2.6 compatibility
            self.assertIn('choices: [1, 2, 3, 4, 5]', str(arg))
        except AttributeError:
            self.assertTrue('choices: [1, 2, 3, 4, 5]' in str(arg))
        arg = Argument('foo', choices=[1, 2, 3, 4, 5, 6])
        try:  # Python 2.6 compatibility
            self.assertIn("choices: [1, 2, 3, '...', 6]", str(arg))
        except AttributeError:
            self.assertTrue("choices: [1, 2, 3, '...', 6]" in str(arg))


if __name__ == '__main__':
    unittest.main()
