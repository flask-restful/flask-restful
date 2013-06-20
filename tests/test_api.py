import unittest
from flask import Flask, views
from flask.signals import got_request_exception, signals_available
from mock import Mock, patch
import flask
import werkzeug
from flask.ext.restful.utils import http_status_message, challenge, unauthorized, error_data, unpack
import flask_restful
import flask_restful.fields
from flask_restful import OrderedDict
from json import dumps, loads
#noinspection PyUnresolvedReferences
from nose.tools import assert_equals, assert_true # you need it for tests in form of continuations

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
        fields = {'foo': flask_restful.fields.Raw}
        output = flask_restful.marshal({'foo': 'bar', 'bat': 'baz'}, fields)
        self.assertEquals(output, {'foo': 'bar'})

    def test_marshal_decorator(self):
        fields = {'foo': flask_restful.fields.Raw}

        @flask_restful.marshal_with(fields)
        def try_me():
            return {'foo': 'bar', 'bat': 'baz'}
        self.assertEquals(try_me(), {'foo': 'bar'})

    def test_marshal_decorator_tuple(self):
        fields = {'foo': flask_restful.fields.Raw}

        @flask_restful.marshal_with(fields)
        def try_me():
            return {'foo': 'bar', 'bat': 'baz'}, 200, {'X-test': 123}
        self.assertEquals(try_me(), ({'foo': 'bar'}, 200, {'X-test': 123}))

    def test_marshal_field(self):
        fields = {'foo': flask_restful.fields.Raw()}
        output = flask_restful.marshal({'foo': 'bar', 'bat': 'baz'}, fields)
        self.assertEquals(output, {'foo': 'bar'})



    def test_marshal_tuple(self):
        fields = {'foo': flask_restful.fields.Raw}
        output = flask_restful.marshal(({'foo': 'bar', 'bat': 'baz'},), fields)
        self.assertEquals(output, [{'foo': 'bar'}])


    def test_marshal_nested(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.Nested({
                'fye': flask_restful.fields.String,
            })
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz', 'fee':
            {'fye': 'fum'}}], fields)
        self.assertEquals(output, [{'fee': OrderedDict({'fye': 'fum'}), 'foo': 'bar'}])

    def test_marshal_nested_with_non_null(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.Nested({
                'fye': flask_restful.fields.String,
                'blah': flask_restful.fields.String,
            }, allow_null=False)
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz', 'fee':
            None}], fields)
        self.assertEquals(output, [{'fee': { 'fye': None, 'blah': None}, 'foo': 'bar'}])

    def test_marshal_nested_with_null(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.Nested({
                'fye': flask_restful.fields.String,
                'blah': flask_restful.fields.String,
            }, allow_null=True)
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz', 'fee':
            None}], fields)
        self.assertEquals(output, [{'fee': None, 'foo': 'bar'}])


    def test_allow_null_presents_data(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.Nested({
                'fye': flask_restful.fields.String,
                'blah': flask_restful.fields.String,
            }, allow_null=True)
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz', 'fee':
                                         {'blah': 'cool'}}], fields)
        self.assertEquals(output, [{'fee': {'blah': 'cool', 'fye': None}, 'foo': 'bar'}])


    def test_marshal_list(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.List(flask_restful.fields.String)
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz',
            'fee': ['fye', 'fum']}], fields)
        self.assertEquals(output, [OrderedDict({'fee': (['fye', 'fum']),
            'foo': 'bar'})])


    def test_marshal_list_of_nesteds(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.List(flask_restful.fields.Nested({
                'fye': flask_restful.fields.String
            }))
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz',
            'fee': {'fye': 'fum'}}], fields)
        self.assertEquals(output, [OrderedDict({'fee': [OrderedDict({'fye': 'fum'})],
            'foo': 'bar'})])


    def test_marshal_list_of_lists(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.List(flask_restful.fields.List(
                flask_restful.fields.String))
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz',
            'fee': [['fye'], ['fum']]}], fields)
        self.assertEquals(output, [OrderedDict({'fee': [['fye'], ['fum']],
            'foo': 'bar'})])


    def test_marshal_nested_dict(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'bar': {
                'a': flask_restful.fields.Raw,
                'b': flask_restful.fields.Raw,
            },
        }
        output = flask_restful.marshal({'foo': 'foo-val', 'bar': 'bar-val', 'bat':
                                      'bat-val', 'a': 1, 'b': 2, 'c': 3}, fields)
        self.assertEquals(output, OrderedDict({'foo': 'foo-val',
            'bar': {'a': 1, 'b': 2}}))


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
            self.assertEquals(resp.data, dumps({
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
            self.assertEquals(resp.data, dumps({
                'foo': 'bar',
            }))

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
        data = loads(resp.data)
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
            self.assertEquals(resp.data, dumps({
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
            self.assertEquals(resp.data, dumps({
                "status": 404, "message": "Not Found",
            }))

        with app.test_request_context("/fOo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 404)
            self.assertEquals(resp.data, dumps({
                "status": 404, "message": "Not Found. You have requested this URI [/fOo] but did you mean /foo ?",
            }))

        with app.test_request_context("/fOo"):
            del exception.data["message"]
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 404)
            self.assertEquals(resp.data, dumps({
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
            self.assertEquals(foo1.data, '"foo1"')
            foo2 = client.get('/foo/toto')
            self.assertEquals(foo2.data, '"foo1"')


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
            self.assertEquals(resp.data, '{"foo": "bar"}')


    def test_output_func(self):

        def make_empty_resposne():
            return flask.make_response('')

        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo"):
            wrapper = api.output(make_empty_resposne)
            resp = wrapper()
            self.assertEquals(resp.status_code, 200)
            self.assertEquals(resp.data, '')


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
            return flask.make_response(unicode(data))

        class Foo(flask_restful.Resource):

            representations = {
                'text/plain': text,
                }

            def get(self):
                return 'hello'

        with app.test_request_context("/foo", headers={'Accept': 'text/plain'}):
            resource = Foo()
            resp = resource.dispatch_request()
            self.assertEquals(resp.data, 'hello')


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
            self.assertEquals("{", lines[0])
            self.assertTrue(lines[1].startswith('    '))
            self.assertTrue(lines[2].startswith('    '))
            self.assertEquals("}", lines[3])

            # Assert our trailing newline.
            self.assertTrue(foo.data.endswith('\n'))

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
        from flask_restful.representations import json as json_rep
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
