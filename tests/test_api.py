import unittest
from flask import Flask, views
from flask.signals import got_request_exception, signals_available
try:
    from mock import Mock, patch
except:
    # python3
    from unittest.mock import Mock, patch
import flask
import werkzeug
from flask.ext.restful.utils import http_status_message, challenge, unauthorized, error_data, unpack
import flask_restful
import flask_restful.fields
from flask_restful import OrderedDict
from json import dumps, loads
#noinspection PyUnresolvedReferences
from nose.tools import assert_equals, assert_true # you need it for tests in form of continuations
import six

def check_unpack(expected, value):
    assert_equals(expected, value)

def test_unpack():
    yield check_unpack, ("hey", 200, {}), unpack("hey")
    yield check_unpack, (("hey",), 200, {}), unpack(("hey",))
    yield check_unpack, ("hey", 201, {}), unpack(("hey", 201))
    yield check_unpack, ("hey", 201, "foo"), unpack(("hey", 201, "foo"))
    yield check_unpack, (["hey", 201], 200, {}), unpack(["hey", 201])

# Add a dummy Resource to verify that the app is properly set.
class HelloWorld(flask_restful.Resource):
    def get(self):
        return {}

class APITestCase(unittest.TestCase):

    def test_http_code(self):
        self.assertEquals(http_status_message(200), 'OK')
        self.assertEquals(http_status_message(404), 'Not Found')


    def test_challenge(self):
        self.assertEquals(challenge('Basic', 'Foo'), 'Basic realm="Foo"')


    def test_unauthorized(self):
        response = Mock()
        response.headers = {}
        unauthorized(response, "flask-restful")
        self.assertEquals(response.headers['WWW-Authenticate'],
                      'Basic realm="flask-restful"')


    def test_unauthorized_custom_realm(self):
        response = Mock()
        response.headers = {}
        unauthorized(response, realm='Foo')
        self.assertEquals(response.headers['WWW-Authenticate'], 'Basic realm="Foo"')


    def test_handle_error_401_sends_challege_default_realm(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)
        exception = Mock()
        exception.code = 401
        exception.data = {'foo': 'bar'}

        with app.test_request_context('/foo'):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 401)
            self.assertEquals(resp.headers['WWW-Authenticate'],
                          'Basic realm="flask-restful"')


    def test_handle_error_401_sends_challege_configured_realm(self):
        app = Flask(__name__)
        app.config['HTTP_BASIC_AUTH_REALM'] = 'test-realm'
        api = flask_restful.Api(app)
        exception = Mock()
        exception.code = 401
        exception.data = {'foo': 'bar'}

        with app.test_request_context('/foo'):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 401)
            self.assertEquals(resp.headers['WWW-Authenticate'],
                          'Basic realm="test-realm"')


    def test_error_data(self):
        self.assertEquals(error_data(400), {
            'status': 400,
            'message': 'Bad Request',
            })


    def test_marshal(self):
        fields = OrderedDict([('foo', flask_restful.fields.Raw)])
        marshal_dict = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
        output = flask_restful.marshal(marshal_dict, fields)
        self.assertEquals(output, {'foo': 'bar'})

    def test_marshal_decorator(self):
        fields = OrderedDict([('foo', flask_restful.fields.Raw)])

        @flask_restful.marshal_with(fields)
        def try_me():
            return OrderedDict([('foo', 'bar'), ('bat', 'baz')])
        self.assertEquals(try_me(), {'foo': 'bar'})

    def test_marshal_decorator_tuple(self):
        fields = OrderedDict([('foo', flask_restful.fields.Raw)])

        @flask_restful.marshal_with(fields)
        def try_me():
            return OrderedDict([('foo', 'bar'), ('bat', 'baz')]), 200, {'X-test': 123}
        self.assertEquals(try_me(), ({'foo': 'bar'}, 200, {'X-test': 123}))

    def test_marshal_field(self):
        fields = OrderedDict({'foo': flask_restful.fields.Raw()})
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
        output = flask_restful.marshal(marshal_fields, fields)
        self.assertEquals(output, {'foo': 'bar'})


    def test_marshal_tuple(self):
        fields = OrderedDict({'foo': flask_restful.fields.Raw})
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
        output = flask_restful.marshal((marshal_fields,), fields)
        self.assertEquals(output, [{'foo': 'bar'}])


    def test_marshal_nested(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.Nested({
                'fye': flask_restful.fields.String,
            }))
        ])

        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'fye': 'fum'})])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', 'fum')]))])
        self.assertEquals(output, expected)

    def test_marshal_nested_with_non_null(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.Nested(
                OrderedDict([
                    ('fye', flask_restful.fields.String),
                    ('blah', flask_restful.fields.String)
                ]), allow_null=False))
        ])
        marshal_fields = [OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', None)])]
        output = flask_restful.marshal(marshal_fields, fields)
        expected = [OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', None)]))])]
        self.assertEquals(output, expected)

    def test_marshal_nested_with_null(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.Nested(
                OrderedDict([
                    ('fye', flask_restful.fields.String),
                    ('blah', flask_restful.fields.String)
                ]), allow_null=True))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', None)])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', None)])
        self.assertEquals(output, expected)


    def test_allow_null_presents_data(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.Nested(
                OrderedDict([
                    ('fye', flask_restful.fields.String),
                    ('blah', flask_restful.fields.String)
                ]), allow_null=True))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'blah': 'cool'})])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', 'cool')]))])
        self.assertEquals(output, expected)

    def test_marshal_nested_property(self):
        class TestObject(object):
            @property
            def fee(self):
                return {'blah': 'cool'}
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.Nested(
                OrderedDict([
                    ('fye', flask_restful.fields.String),
                    ('blah', flask_restful.fields.String)
                ]), allow_null=True))
        ])
        obj = TestObject()
        obj.foo = 'bar'
        obj.bat = 'baz'
        output = flask_restful.marshal([obj], fields)
        expected = [OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', 'cool')]))])]
        self.assertEquals(output, expected)

    def test_marshal_list(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.List(flask_restful.fields.String))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', ['fye', 'fum'])])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', (['fye', 'fum']))])
        self.assertEquals(output, expected)


    def test_marshal_list_of_nesteds(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.List(flask_restful.fields.Nested({
                'fye': flask_restful.fields.String
            })))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'fye': 'fum'})])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', [OrderedDict([('fye', 'fum')])])])
        self.assertEquals(output, expected)


    def test_marshal_list_of_lists(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('fee', flask_restful.fields.List(flask_restful.fields.List(
                flask_restful.fields.String)))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', [['fye'], ['fum']])])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', [['fye'], ['fum']])])
        self.assertEquals(output, expected)


    def test_marshal_nested_dict(self):
        fields = OrderedDict([
            ('foo', flask_restful.fields.Raw),
            ('bar', OrderedDict([
                ('a', flask_restful.fields.Raw),
                ('b', flask_restful.fields.Raw),
            ])),
        ])
        marshal_fields = OrderedDict([('foo', 'foo-val'), ('bar', 'bar-val'), ('bat', 'bat-val'),
                                      ('a', 1), ('b', 2), ('c', 3)])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'foo-val'), ('bar', OrderedDict([('a', 1), ('b', 2)]))])
        self.assertEquals(output, expected)


    def test_api_representation(self):
        app = Mock()
        api = flask_restful.Api(app)

        @api.representation('foo')
        def foo():
            pass

        self.assertEquals(api.representations['foo'], foo)


    def test_api_base(self):
        app = Mock()
        api = flask_restful.Api(app)
        self.assertEquals(api.urls, {})
        self.assertEquals(api.prefix, '')
        self.assertEquals(api.default_mediatype, 'application/json')


    def test_api_delayed_initialization(self):
        app = Flask(__name__)
        api = flask_restful.Api()
        api.init_app(app)

        api.add_resource(HelloWorld, '/', endpoint="hello")


    def test_api_prefix(self):
        app = Mock()
        api = flask_restful.Api(app, prefix='/foo')
        self.assertEquals(api.prefix, '/foo')


    def test_handle_server_error(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        exception = Mock()
        exception.code = 500
        exception.data = {'foo': 'bar'}

        with app.test_request_context("/foo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 500)
            self.assertEquals(resp.data.decode(), dumps({
                'foo': 'bar',
            }))


    def test_handle_auth(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        exception = Mock()
        exception.code = 401
        exception.data = {'foo': 'bar'}

        with app.test_request_context("/foo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 401)
            self.assertEquals(resp.data.decode(), dumps({'foo': 'bar',}))

            self.assertTrue('WWW-Authenticate' in resp.headers)


    def test_handle_api_error(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)
        class Test(flask_restful.Resource):
            def get(self):
                flask.abort(404)
        api.add_resource(Test(), '/api', endpoint='api')
        app = app.test_client()

        resp = app.get("/api")
        assert_equals(resp.status_code, 404)
        assert_equals('application/json', resp.headers['Content-Type'])
        data = loads(resp.data.decode())
        assert_equals(data.get('status'), 404)
        assert_true('message' in data)


    def test_handle_non_api_error(self):
        app = Flask(__name__)
        flask_restful.Api(app)
        app = app.test_client()

        resp = app.get("/foo")
        self.assertEquals(resp.status_code, 404)
        self.assertEquals('text/html', resp.headers['Content-Type'])

    def test_non_api_error_404_catchall(self):
        app = Flask(__name__)
        api = flask_restful.Api(app, catch_all_404s=True)
        app = app.test_client()

        resp = app.get("/foo")
        self.assertEquals(api.default_mediatype, resp.headers['Content-Type'])


    def test_handle_error_signal(self):
        if not signals_available:
            self.skipTest("Can't test signals without signal support")
        app = Flask(__name__)
        api = flask_restful.Api(app)

        exception = Mock()
        exception.code = 400
        exception.data = {'foo': 'bar'}

        recorded = []
        def record(sender, exception):
            recorded.append(exception)

        got_request_exception.connect(record, app)
        try:
            with app.test_request_context("/foo"):
                api.handle_error(exception)
                self.assertEquals(len(recorded), 1)
                self.assertTrue(exception is recorded[0])
        finally:
            got_request_exception.disconnect(record, app)

    def test_handle_error(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        exception = Mock()
        exception.code = 400
        exception.data = {'foo': 'bar'}

        with app.test_request_context("/foo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 400)
            self.assertEquals(resp.data.decode(), dumps({
                'foo': 'bar',
            }))

    def test_handle_smart_errors(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)
        view = flask_restful.Resource

        exception = Mock()
        exception.code = 404
        exception.data = {"status": 404, "message": "Not Found"}
        api.add_resource(view, '/foo', endpoint='bor')
        api.add_resource(view, '/fee', endpoint='bir')
        api.add_resource(view, '/fii', endpoint='ber')


        with app.test_request_context("/faaaaa"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 404)
            self.assertEquals(resp.data.decode(), dumps({
                "status": 404, "message": "Not Found",
            }))

        with app.test_request_context("/fOo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 404)
            self.assertEquals(resp.data.decode(), dumps({
                "status": 404, "message": "Not Found. You have requested this URI [/fOo] but did you mean /foo ?",
            }))

        with app.test_request_context("/fOo"):
            del exception.data["message"]
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 404)
            self.assertEquals(resp.data.decode(), dumps({
                "status": 404, "message": "You have requested this URI [/fOo] but did you mean /foo ?",
            }))


    def test_media_types(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo",
            headers={'Accept': 'application/json'}):
            self.assertEquals(api.mediatypes(), ['application/json'])


    def test_media_types_method(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo",
            headers={'Accept': 'application/xml; q=.5'}):
            self.assertEquals(api.mediatypes_method()(Mock()),
                ['application/xml', 'application/json'])


    def test_media_types_q(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo",
            headers={'Accept': 'application/json; q=1; application/xml; q=.5'}):
            self.assertEquals(api.mediatypes(),
                          ['application/json', 'application/xml'])


    def test_decorator(self):
        def return_zero(func):
            return 0

        app = Mock()
        app.view_functions = {}
        view = Mock()
        api = flask_restful.Api(app)
        api.decorators.append(return_zero)
        api.output = Mock()
        api.add_resource(view, '/foo', endpoint='bar')

        app.add_url_rule.assert_called_with('/foo', view_func=0)


    def test_add_resource_endpoint(self):
        app = Mock()
        app.view_functions = {}
        view = Mock()

        api = flask_restful.Api(app)
        api.output = Mock()
        api.add_resource(view, '/foo', endpoint='bar')

        view.as_view.assert_called_with('bar')

    def test_add_two_conflicting_resources_on_same_endpoint(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        class Foo1(flask_restful.Resource):
            def get(self):
                return 'foo1'

        class Foo2(flask_restful.Resource):
            def get(self):
                return 'foo2'

        api.add_resource(Foo1, '/foo', endpoint='bar')
        self.assertRaises(ValueError, api.add_resource, Foo2, '/foo/toto', endpoint='bar')

    def test_add_the_same_resource_on_same_endpoint(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        class Foo1(flask_restful.Resource):
            def get(self):
                return 'foo1'

        api.add_resource(Foo1, '/foo', endpoint='bar')
        api.add_resource(Foo1, '/foo/toto', endpoint='blah')

        with app.test_client() as client:
            foo1 = client.get('/foo')
            self.assertEquals(foo1.data, b'"foo1"')
            foo2 = client.get('/foo/toto')
            self.assertEquals(foo2.data, b'"foo1"')


    def test_add_resource(self):
        app = Mock()
        app.view_functions = {}
        api = flask_restful.Api(app)
        api.output = Mock()
        api.add_resource(views.MethodView, '/foo')

        app.add_url_rule.assert_called_with('/foo',
            view_func=api.output())

    def test_add_resource_kwargs(self):
        app = Mock()
        app.view_functions = {}
        api = flask_restful.Api(app)
        api.output = Mock()
        api.add_resource(views.MethodView, '/foo', defaults={"bar": "baz"})

        app.add_url_rule.assert_called_with('/foo',
            view_func=api.output(), defaults={"bar": "baz"})


    def test_output_unpack(self):

        def make_empty_response():
            return {'foo': 'bar'}

        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo"):
            wrapper = api.output(make_empty_response)
            resp = wrapper()
            self.assertEquals(resp.status_code, 200)
            self.assertEquals(resp.data.decode(), '{"foo": "bar"}')


    def test_output_func(self):

        def make_empty_resposne():
            return flask.make_response('')

        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo"):
            wrapper = api.output(make_empty_resposne)
            resp = wrapper()
            self.assertEquals(resp.status_code, 200)
            self.assertEquals(resp.data.decode(), '')


    def test_resource(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        resource.get = Mock()
        with app.test_request_context("/foo"):
            resource.dispatch_request()


    def test_resource_resp(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        resource.get = Mock()
        with app.test_request_context("/foo"):
            resource.get.return_value = flask.make_response('')
            resource.dispatch_request()


    def test_resource_text_plain(self):
        app = Flask(__name__)

        def text(data, code, headers=None):
            return flask.make_response(six.text_type(data))

        class Foo(flask_restful.Resource):

            representations = {
                'text/plain': text,
                }

            def get(self):
                return 'hello'

        with app.test_request_context("/foo", headers={'Accept': 'text/plain'}):
            resource = Foo()
            resp = resource.dispatch_request()
            self.assertEquals(resp.data.decode(), 'hello')


    def test_resource_error(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        with app.test_request_context("/foo"):
            self.assertRaises(AssertionError, lambda: resource.dispatch_request())


    def test_resource_head(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        with app.test_request_context("/foo", method="HEAD"):
            self.assertRaises(AssertionError, lambda: resource.dispatch_request())


    def test_abort_data(self):
        try:
            flask_restful.abort(404, foo='bar')
            assert False  # We should never get here
        except Exception as e:
            self.assertEquals(e.data, {'foo': 'bar'})


    def test_abort_no_data(self):
        try:
            flask_restful.abort(404)
            assert False  # We should never get here
        except Exception as e:
            self.assertEquals(False, hasattr(e, "data"))


    def test_abort_custom_message(self):
        try:
            flask_restful.abort(404, message="no user")
            assert False  # We should never get here
        except Exception as e:
            assert_equals(e.data['message'], "no user")


    def test_abort_type(self):
        self.assertRaises(werkzeug.exceptions.HTTPException, lambda: flask_restful.abort(404))


    def test_endpoints(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(HelloWorld, '/ids/<int:id>', endpoint="hello")
        with app.test_request_context('/foo'):
            self.assertFalse(api._has_fr_route())

        with app.test_request_context('/ids/3'):
            self.assertTrue(api._has_fr_route())

            
    def test_url_for(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(HelloWorld, '/ids/<int:id>')
        with app.test_request_context('/foo'):
            self.assertEqual(api.url_for(HelloWorld, id = 123), '/ids/123')

            
    def test_fr_405(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(HelloWorld, '/ids/<int:id>', endpoint="hello")
        app = app.test_client()
        resp = app.post('/ids/3')
        self.assertEquals(resp.status_code, 405)
        self.assertEquals(resp.content_type, api.default_mediatype)

    def test_will_prettyprint_json_in_debug_mode(self):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        api = flask_restful.Api(app)

        class Foo1(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar', 'baz': 'asdf'}

        api.add_resource(Foo1, '/foo', endpoint='bar')

        with app.test_client() as client:
            foo = client.get('/foo')

            # Python's dictionaries have random order (as of "new" Pythons,
            # anyway), so we can't verify the actual output here.  We just
            # assert that they're properly prettyprinted.
            lines = foo.data.splitlines()
            lines = [line.decode() for line in lines]
            self.assertEquals("{", lines[0])
            self.assertTrue(lines[1].startswith('    '))
            self.assertTrue(lines[2].startswith('    '))
            self.assertEquals("}", lines[3])

            # Assert our trailing newline.
            self.assertTrue(foo.data.endswith(b'\n'))

    def test_will_pass_options_to_json(self):

        app = Flask(__name__)
        api = flask_restful.Api(app)

        class Foo1(flask_restful.Resource):
            def get(self):
                return {'foo': 'bar'}

        api.add_resource(Foo1, '/foo', endpoint='bar')

        # We patch the representations module here, with two things:
        #   1. Set the settings dict() with some value
        #   2. Patch the json.dumps function in the module with a Mock object.

        from flask.ext.restful.representations import json as json_rep
        json_dumps_mock = Mock(return_value='bar')
        new_settings = {'indent': 123}

        with patch.multiple(json_rep, dumps=json_dumps_mock,
                            settings=new_settings):
            with app.test_client() as client:
                foo = client.get('/foo')

        # Assert that the function was called with the above settings.
        data, kwargs = json_dumps_mock.call_args
        self.assertTrue(json_dumps_mock.called)
        self.assertEqual(123, kwargs['indent'])


if __name__ == '__main__':
    unittest.main()
