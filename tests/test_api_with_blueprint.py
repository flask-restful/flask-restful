try:
    from mock import Mock
except ImportError:
    # python3
    from unittest.mock import Mock
import unittest

import flask
from flask import Flask, Blueprint, request
#noinspection PyUnresolvedReferences
from nose.tools import assert_true, assert_false  # you need it for tests in form of continuations

import flask_restful
import flask_restful.fields


# Add a dummy Resource to verify that the app is properly set.
class HelloWorld(flask_restful.Resource):
    def get(self):
        return {}


class GoodbyeWorld(flask_restful.Resource):
    def __init__(self, err):
        self.err = err

    def get(self):
        flask.abort(self.err)


class APIWithBlueprintTestCase(unittest.TestCase):

    def setUp(self):
        self.blueprint = Blueprint('test', __name__)
        self.api = flask_restful.Api(self.blueprint)
        self.app = Flask(__name__)
        self.app.register_blueprint(self.blueprint)


    def test_api_base(self):
        self.assertEquals(self.api.urls, {})
        self.assertEquals(self.api.prefix, '')
        self.assertEquals(self.api.default_mediatype, 'application/json')

    def test_api_delayed_initialization(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api()
        api.init_app(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        api.add_resource(HelloWorld, '/', endpoint="hello")

    def test_add_resource_endpoint(self):
        view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
        self.api.add_resource(view, '/foo', endpoint='bar')
        view.as_view.assert_called_with('bar')

    def test_add_resource_endpoint_after_registration(self):
        view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
        self.api.add_resource(view, '/foo', endpoint='bar')
        view.as_view.assert_called_with('bar')

    def test_url_with_api_prefix(self):
        api = flask_restful.Api(self.blueprint, prefix='/api')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(self.blueprint)
        with app.test_request_context('/api/hi'):
            self.assertEquals(request.endpoint, 'test.hello')

    def test_url_with_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/bp/hi'):
            self.assertEquals(request.endpoint, 'test.hello')

    def test_url_with_registration_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/reg')
        with app.test_request_context('/reg/hi'):
            self.assertEquals(request.endpoint, 'test.hello')

    def test_registration_prefix_overrides_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/reg')
        with app.test_request_context('/reg/hi'):
            self.assertEquals(request.endpoint, 'test.hello')

    def test_url_with_api_and_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint, prefix='/api')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/bp/api/hi'):
            self.assertEquals(request.endpoint, 'test.hello')

    def test_url_part_order_aeb(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint, prefix='/api', url_part_order='aeb')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/api/hi/bp'):
            self.assertEquals(request.endpoint, 'test.hello')

    def test_error_routing(self):
        self.api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        self.api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        with self.app.test_request_context('/hi', method='POST'):
            assert_true(self.api._should_use_fr_error_handler())
            assert_true(self.api._has_fr_route())
        with self.app.test_request_context('/bye'):
            self.api._should_use_fr_error_handler = Mock(return_value=False)
            assert_true(self.api._has_fr_route())

    def test_non_blueprint_rest_error_routing(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/blueprint')
        api2 = flask_restful.Api(app)
        api2.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api2.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        with app.test_request_context('/hi', method='POST'):
            assert_false(api._should_use_fr_error_handler())
            assert_true(api2._should_use_fr_error_handler())
            assert_false(api._has_fr_route())
            assert_true(api2._has_fr_route())
        with app.test_request_context('/blueprint/hi', method='POST'):
            assert_true(api._should_use_fr_error_handler())
            assert_false(api2._should_use_fr_error_handler())
            assert_true(api._has_fr_route())
            assert_false(api2._has_fr_route())
        api._should_use_fr_error_handler = Mock(return_value=False)
        api2._should_use_fr_error_handler = Mock(return_value=False)
        with app.test_request_context('/bye'):
            assert_false(api._has_fr_route())
            assert_true(api2._has_fr_route())
        with app.test_request_context('/blueprint/bye'):
            assert_true(api._has_fr_route())
            assert_false(api2._has_fr_route())

    def test_non_blueprint_non_rest_error_routing(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/blueprint')

        @app.route('/hi')
        def hi():
            return 'hi'

        @app.route('/bye')
        def bye():
            flask.abort(404)
        with app.test_request_context('/hi', method='POST'):
            assert_false(api._should_use_fr_error_handler())
            assert_false(api._has_fr_route())
        with app.test_request_context('/blueprint/hi', method='POST'):
            assert_true(api._should_use_fr_error_handler())
            assert_true(api._has_fr_route())
        api._should_use_fr_error_handler = Mock(return_value=False)
        with app.test_request_context('/bye'):
            assert_false(api._has_fr_route())
        with app.test_request_context('/blueprint/bye'):
            assert_true(api._has_fr_route())


if __name__ == '__main__':
    unittest.main()
