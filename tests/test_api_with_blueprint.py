import unittest
from flask import Flask, views, Blueprint
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


# Add a dummy Resource to verify that the app is properly set.
class HelloWorld(flask_restful.Resource):
    def get(self):
        return {}


class APIWithBlueprintTestCase(unittest.TestCase):


    def test_api_base(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        self.assertEquals(api.urls, {})
        self.assertEquals(api.prefix, '')
        self.assertEquals(api.default_mediatype, 'application/json')


    def test_api_delayed_initialization(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api()
        api.init_app(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)

        api.add_resource(HelloWorld, '/', endpoint="hello")


    def test_api_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint, prefix='/foo')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        self.assertEquals(api.prefix, '/foo')


    def test_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/foo')
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        self.assertEquals(api.prefix, '/foo')


    def test_blueprint_register_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/foo')
        self.assertEquals(api.prefix, '/foo')
    
    
    def test_add_resource_endpoint(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        view = Mock()
        view.__name__ = 'foobar_view'
        api.add_resource(view, '/foo', endpoint='bar')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        api.output = Mock()
        api.output.__name__ = 'output'
        view.as_view.assert_called_with('bar')


    def test_add_resource_endpoint_after_registration(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        view = Mock()
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
