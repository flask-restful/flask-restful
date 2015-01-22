# -*- coding: utf-8 -*-
import unittest
from mock import Mock, patch, NonCallableMock
from flask import Flask
from werkzeug import exceptions, MultiDict
from werkzeug.wrappers import Request
from werkzeug.datastructures import FileStorage
from flask_restful.reqparse import Argument, RequestParser, Namespace
import six
import decimal

import json


class ReqParseTestCase(unittest.TestCase):
    def test_default_help(self):
        arg = Argument("foo")
        self.assertEquals(arg.help, None)

    @patch('flask_restful.abort')
    def test_help(self, abort):
        from werkzeug.datastructures import MultiDict
        parser = RequestParser()
        parser.add_argument('foo', choices=['one', 'two'], help='Bad choice')
        req = Mock(['values'])
        req.values = MultiDict([('foo', 'three')])
        parser.parse_args(req)
        abort.assert_called_with(400, message='Bad choice')

    @patch('flask_restful.abort', side_effect=exceptions.BadRequest('Bad Request'))
    def test_no_help(self, abort):
        def bad_choice():
            from werkzeug.datastructures import MultiDict
            parser = RequestParser()
            parser.add_argument('foo', choices=['one', 'two'])
            req = Mock(['values'])
            req.values = MultiDict([('foo', 'three')])
            parser.parse_args(req)
            abort.assert_called_with(400, message='three is not a valid choice')

        self.assertRaises(exceptions.BadRequest, bad_choice)

    def test_name(self):
        arg = Argument("foo")
        self.assertEquals(arg.name, "foo")

    def test_dest(self):
        arg = Argument("foo", dest="foobar")
        self.assertEquals(arg.dest, "foobar")

    def test_location_url(self):
        arg = Argument("foo", location="url")
        self.assertEquals(arg.location, "url")

    def test_location_url_list(self):
        arg = Argument("foo", location=["url"])
        self.assertEquals(arg.location, ["url"])

    def test_location_header(self):
        arg = Argument("foo", location="headers")
        self.assertEquals(arg.location, "headers")

    def test_location_json(self):
        arg = Argument("foo", location="json")
        self.assertEquals(arg.location, "json")

    def test_location_get_json(self):
        arg = Argument("foo", location="get_json")
        self.assertEquals(arg.location, "get_json")

    def test_location_header_list(self):
        arg = Argument("foo", location=["headers"])
        self.assertEquals(arg.location, ["headers"])

    def test_type(self):
        arg = Argument("foo", type=int)
        self.assertEquals(arg.type, int)

    def test_default(self):
        arg = Argument("foo", default=True)
        self.assertEquals(arg.default, True)

    def test_required(self):
        arg = Argument("foo", required=True)
        self.assertEquals(arg.required, True)

    def test_ignore(self):
        arg = Argument("foo", ignore=True)
        self.assertEquals(arg.ignore, True)

    def test_operator(self):
        arg = Argument("foo", operators=[">=", "<=", "="])
        self.assertEquals(arg.operators, [">=", "<=", "="])

    def test_action_filter(self):
        arg = Argument("foo", action="filter")
        self.assertEquals(arg.action, u"filter")

    def test_action(self):
        arg = Argument("foo", action="append")
        self.assertEquals(arg.action, u"append")

    def test_choices(self):
        arg = Argument("foo", choices=[1, 2])
        self.assertEquals(arg.choices, [1, 2])

    def test_default_dest(self):
        arg = Argument("foo")
        self.assertEquals(arg.dest, None)

    def test_default_operators(self):
        arg = Argument("foo")
        self.assertEquals(arg.operators[0], "=")
        self.assertEquals(len(arg.operators), 1)

    @patch('flask_restful.reqparse.six')
    def test_default_type(self, mock_six):
        arg = Argument("foo")
        sentinel = object()
        arg.type(sentinel)
        mock_six.text_type.assert_called_with(sentinel)

    def test_default_default(self):
        arg = Argument("foo")
        self.assertEquals(arg.default, None)

    def test_required_default(self):
        arg = Argument("foo")
        self.assertEquals(arg.required, False)

    def test_ignore_default(self):
        arg = Argument("foo")
        self.assertEquals(arg.ignore, False)

    def test_action_default(self):
        arg = Argument("foo")
        self.assertEquals(arg.action, u"store")

    def test_choices_default(self):
        arg = Argument("foo")
        self.assertEquals(len(arg.choices), 0)

    def test_source(self):
        req = Mock(['args', 'headers', 'values'])
        req.args = {'foo': 'bar'}
        req.headers = {'baz': 'bat'}
        arg = Argument('foo', location=['args'])
        self.assertEquals(arg.source(req), MultiDict(req.args))

        arg = Argument('foo', location=['headers'])
        self.assertEquals(arg.source(req), MultiDict(req.headers))

    def test_source_bad_location(self):
        req = Mock(['values'])
        arg = Argument('foo', location=['foo'])
        self.assertTrue(len(arg.source(req)) == 0)  # yes, basically you don't find it

    def test_source_default_location(self):
        req = Mock(['values'])
        req._get_child_mock = lambda **kwargs: MultiDict()
        arg = Argument('foo')
        self.assertEquals(arg.source(req), req.values)

    def test_option_case_sensitive(self):
        arg = Argument("foo", choices=["bar", "baz"], case_sensitive=True)
        self.assertEquals(True, arg.case_sensitive)

        # Insensitive
        arg = Argument("foo", choices=["bar", "baz"], case_sensitive=False)
        self.assertEquals(False, arg.case_sensitive)

        # Default
        arg = Argument("foo", choices=["bar", "baz"])
        self.assertEquals(True, arg.case_sensitive)

    def test_viewargs(self):
        req = Request.from_values()
        req.view_args = {"foo": "bar"}
        parser = RequestParser()
        parser.add_argument("foo", location=["view_args"], type=str)
        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

        req = Mock()
        req.values = ()
        req.json = None
        req.view_args = {"foo": "bar"}
        parser = RequestParser()
        parser.add_argument("foo", type=str, store_missing=True)
        args = parser.parse_args(req)
        self.assertEquals(args["foo"], None)

    def test_parse_unicode(self):
        req = Request.from_values("/bubble?foo=barß")
        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], u"barß")

    def test_parse_unicode_app(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo")

        with app.test_request_context('/bubble?foo=barß'):
            args = parser.parse_args()
            self.assertEquals(args['foo'], u"barß")

    def test_json_location(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", location="json", store_missing=True)

        with app.test_request_context('/bubble', method="post"):
            args = parser.parse_args()
            self.assertEquals(args['foo'], None)

    def test_get_json_location(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", location="json")

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": "bar"}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEquals(args['foo'], 'bar')

    def test_parse_append_ignore(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", ignore=True, type=int, action="append",
                            store_missing=True),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

    def test_parse_append_default(self):
        req = Request.from_values("/bubble?")

        parser = RequestParser()
        parser.add_argument("foo", action="append", store_missing=True),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

    def test_parse_append(self):
        req = Request.from_values("/bubble?foo=bar&foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], ["bar", "bat"])

    def test_parse_append_single(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], ["bar"])

    def test_parse_dest(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", dest="bat")

        args = parser.parse_args(req)
        self.assertEquals(args['bat'], "bar")

    def test_parse_gte_lte_eq(self):
        req = Request.from_values("/bubble?foo>=bar&foo<=bat&foo=foo")

        parser = RequestParser()
        parser.add_argument("foo", operators=[">=", "<=", "="], action="append"),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], ["bar", "bat", "foo"])

    def test_parse_gte(self):
        req = Request.from_values("/bubble?foo>=bar")

        parser = RequestParser()
        parser.add_argument("foo", operators=[">="])

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def test_parse_foo_operators_four_hunderd(self):
        parser = RequestParser()
        parser.add_argument("foo", type=int),

        self.assertRaises(exceptions.BadRequest, lambda: parser.parse_args(Request.from_values("/bubble?foo=bar")))

    def test_parse_foo_operators_ignore(self):
        parser = RequestParser()
        parser.add_argument("foo", ignore=True, store_missing=True)

        args = parser.parse_args(Request.from_values("/bubble"))
        self.assertEquals(args['foo'], None)

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
        self.assertEquals(args['foo'], ["bar"])

    def test_parse_lte_gte_missing(self):
        parser = RequestParser()
        parser.add_argument("foo", operators=["<=", "="])
        args = parser.parse_args(Request.from_values("/bubble?foo<=bar"))
        self.assertEquals(args['foo'], "bar")

    def test_parse_eq_other(self):
        parser = RequestParser()
        parser.add_argument("foo"),
        args = parser.parse_args(Request.from_values("/bubble?foo=bar&foo=bat"))
        self.assertEquals(args['foo'], "bar")

    def test_parse_eq(self):
        req = Request.from_values("/bubble?foo=bar")
        parser = RequestParser()
        parser.add_argument("foo"),
        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def test_parse_lte(self):
        req = Request.from_values("/bubble?foo<=bar")
        parser = RequestParser()
        parser.add_argument("foo", operators=["<="])

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def test_parse_required(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", required=True, location='values')

        message = ''
        try:
            parser.parse_args(req)
        except exceptions.BadRequest as e:
            message = e.data['message']

        self.assertEquals(message, (u'Missing required parameter foo in the '
                                    'post body or the query string'))

        parser = RequestParser()
        parser.add_argument("bar", required=True, location=['values', 'cookies'])

        try:
            parser.parse_args(req)
        except exceptions.BadRequest as e:
            message = e.data['message']

        self.assertEquals(message, (u"Missing required parameter bar in the "
                                    "post body or the query string or the "
                                    "request's cookies"))

    def test_parse_default_append(self):
        req = Request.from_values("/bubble")
        parser = RequestParser()
        parser.add_argument("foo", default="bar", action="append",
                            store_missing=True)

        args = parser.parse_args(req)

        self.assertEquals(args['foo'], "bar")

    def test_parse_default(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", default="bar", store_missing=True)

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def test_parse_callable_default(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", default=lambda: "bar", store_missing=True)

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def test_parse(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo"),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def test_parse_none(self):
        req = Request.from_values("/bubble")

        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

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
        self.assertEquals(args['foo'], "bat")

    def test_parse_choices(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"]),

        self.assertRaises(exceptions.BadRequest, lambda: parser.parse_args(req))

    def test_parse_choices_sensitive(self):
        req = Request.from_values("/bubble?foo=BAT")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"], case_sensitive=True),

        self.assertRaises(exceptions.BadRequest, lambda: parser.parse_args(req))

    def test_parse_choices_insensitive(self):
        req = Request.from_values("/bubble?foo=BAT")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"], case_sensitive=False),

        args = parser.parse_args(req)
        self.assertEquals('bat', args.get('foo'))

        # both choices and args are case_insensitive
        req = Request.from_values("/bubble?foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", choices=["BAT"], case_sensitive=False),

        args = parser.parse_args(req)
        self.assertEquals('bat', args.get('foo'))

    def test_parse_ignore(self):
        req = Request.from_values("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", type=int, ignore=True, store_missing=True),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

    def test_chaining(self):
        parser = RequestParser()
        self.assertTrue(parser is parser.add_argument("foo"))

    def test_namespace_existence(self):
        namespace = Namespace()
        namespace.foo = 'bar'
        namespace['bar'] = 'baz'
        self.assertEquals(namespace['foo'], 'bar')
        self.assertEquals(namespace.bar, 'baz')

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
        parser.add_argument("foo", type=str, location="json")
        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": None}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEquals(args['foo'], None)

    def test_type_callable(self):
        req = Request.from_values("/bubble?foo=1")

        parser = RequestParser()
        parser.add_argument("foo", type=lambda x: x, required=False),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "1")

    def test_type_callable_none(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", type=lambda x: x, location="json", required=False),

        with app.test_request_context('/bubble', method="post",
                                      data=json.dumps({"foo": None}),
                                      content_type='application/json'):
            try:
                args = parser.parse_args()
                self.assertEquals(args['foo'], None)
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
            self.assertEquals(args['foo'], decimal.Decimal("1.0025"))

    def test_type_filestorage(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument("foo", type=FileStorage, location='files')

        fdata = six.b('foo bar baz qux')
        with app.test_request_context('/bubble', method='POST',
                                      data={'foo': (six.BytesIO(fdata), 'baz.txt')}):
            args = parser.parse_args()

            self.assertEquals(args['foo'].name, 'foo')
            self.assertEquals(args['foo'].filename, 'baz.txt')
            self.assertEquals(args['foo'].read(), fdata)

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

            self.assertEquals(args['foo'].name, 'fooaaaa')
            self.assertEquals(args['foo'].filename, 'baz.txtaaaa')
            self.assertEquals(args['foo'].read(), fdata)



    def test_passing_arguments_object(self):
        req = Request.from_values("/bubble?foo=bar")
        parser = RequestParser()
        parser.add_argument(Argument("foo", type=str))

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], u"bar")

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
        self.assertEquals(args['foo'], 101)
        self.assertEquals(args['bar'], u'baz')

    def test_request_parser_replace_argument(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        parser_copy = parser.copy()
        parser_copy.replace_argument('foo', type=str)

        args = parser_copy.parse_args(req)
        self.assertEquals(args['foo'], u'baz')

    def test_both_json_and_values_location(self):

        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument('foo', type=int)
        parser.add_argument('baz', type=int)
        with app.test_request_context('/bubble?foo=1', method="post",
                                      data=json.dumps({"baz": 2}),
                                      content_type='application/json'):
            args = parser.parse_args()
            self.assertEquals(args['foo'], 1)
            self.assertEquals(args['baz'], 2)

    def test_not_json_location_and_content_type_json(self):
        app = Flask(__name__)

        parser = RequestParser()
        parser.add_argument('foo', location='args')

        with app.test_request_context('/bubble', method='get',
                                      content_type='application/json'):
            parser.parse_args() # Should not raise a 400: BadRequest

    def test_request_parser_remove_argument(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        parser_copy = parser.copy()
        parser_copy.remove_argument('foo')

        args = parser_copy.parse_args(req)
        self.assertEquals(args, {})

    def test_strict_parsing_off(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        args = parser.parse_args(req)
        self.assertEquals(args, {})

    def test_strict_parsing_on(self):
        req = Request.from_values("/bubble?foo=baz")
        parser = RequestParser()
        self.assertRaises(exceptions.BadRequest, parser.parse_args, req, strict=True)

    def test_strict_parsing_off_partial_hit(self):
        req = Request.from_values("/bubble?foo=1&bar=bees&n=22")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        args = parser.parse_args(req)
        self.assertEquals(args['foo'], 1)

    def test_strict_parsing_on_partial_hit(self):
        req = Request.from_values("/bubble?foo=1&bar=bees&n=22")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        self.assertRaises(exceptions.BadRequest, parser.parse_args, req, strict=True)


if __name__ == '__main__':
    unittest.main()
