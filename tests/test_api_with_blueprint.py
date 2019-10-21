import pytest

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


@pytest.fixture()
def blueprint():
    blueprint = Blueprint('test', __name__)
    return blueprint


# Add a dummy Resource to verify that the app is properly set.
class HelloWorld(flask_restful.Resource):
    def get(self):
        return {}


class GoodbyeWorld(flask_restful.Resource):
    def __init__(self, err):
        self.err = err

    def get(self):
        flask.abort(self.err)


def test_api_base(api):
    assert api.urls == {}
    assert api.prefix == ''
    assert api.default_mediatype == 'application/json'


def test_api_delayed_initialization(blueprint):
    api = flask_restful.Api()
    api.init_app(blueprint)
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    api.add_resource(HelloWorld, '/', endpoint="hello")


def test_add_resource_endpoint(api):
    view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
    api.add_resource(view, '/foo', endpoint='bar')
    view.as_view.assert_called_with('bar')


def test_add_resource_endpoint_after_registration(api):
    view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
    api.add_resource(view, '/foo', endpoint='bar')
    view.as_view.assert_called_with('bar')


def test_url_with_api_prefix(app, blueprint):
    api = flask_restful.Api(blueprint, prefix='/api')
    api.add_resource(HelloWorld, '/hi', endpoint='hello')
    app.register_blueprint(blueprint)
    with app.test_request_context('/api/hi'):
        assert request.endpoint == 'test.hello'


def test_url_with_blueprint_prefix(app):
    blueprint = Blueprint('test', __name__, url_prefix='/bp')
    api = flask_restful.Api(blueprint)
    api.add_resource(HelloWorld, '/hi', endpoint='hello')
    app.register_blueprint(blueprint)
    with app.test_request_context('/bp/hi'):
        assert request.endpoint == 'test.hello'


def test_url_with_registration_prefix(app, blueprint):
    api = flask_restful.Api(blueprint)
    api.add_resource(HelloWorld, '/hi', endpoint='hello')
    app.register_blueprint(blueprint, url_prefix='/reg')
    with app.test_request_context('/reg/hi'):
        assert request.endpoint == 'test.hello'


def test_registration_prefix_overrides_blueprint_prefix(app):
    blueprint = Blueprint('test', __name__, url_prefix='/bp')
    api = flask_restful.Api(blueprint)
    api.add_resource(HelloWorld, '/hi', endpoint='hello')
    app.register_blueprint(blueprint, url_prefix='/reg')
    with app.test_request_context('/reg/hi'):
        assert request.endpoint == 'test.hello'


def test_url_with_api_and_blueprint_prefix(app):
    blueprint = Blueprint('test', __name__, url_prefix='/bp')
    api = flask_restful.Api(blueprint, prefix='/api')
    api.add_resource(HelloWorld, '/hi', endpoint='hello')
    app.register_blueprint(blueprint)
    with app.test_request_context('/bp/api/hi'):
        assert request.endpoint == 'test.hello'


def test_url_part_order_aeb(app):
    blueprint = Blueprint('test', __name__, url_prefix='/bp')
    api = flask_restful.Api(blueprint, prefix='/api', url_part_order='aeb')
    api.add_resource(HelloWorld, '/hi', endpoint='hello')
    app.register_blueprint(blueprint)
    with app.test_request_context('/api/hi/bp'):
        assert request.endpoint == 'test.hello'


def test_error_routing(api):
    api.add_resource(HelloWorld(), '/hi', endpoint="hello")
    api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
    with api.app.test_request_context('/hi', method='POST'):
        assert api._should_use_fr_error_handler()
        assert api._has_fr_route()
    with api.app.test_request_context('/bye'):
        api._should_use_fr_error_handler = Mock(return_value=False)
        assert api._has_fr_route()


def test_non_blueprint_rest_error_routing(app, blueprint):
    api = flask_restful.Api(blueprint)
    api.add_resource(HelloWorld(), '/hi', endpoint="hello")
    api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
    app.register_blueprint(blueprint, url_prefix='/blueprint')
    api2 = flask_restful.Api(app)
    api2.add_resource(HelloWorld(), '/hi', endpoint="hello")
    api2.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
    with app.test_request_context('/hi', method='POST'):
        assert not api._should_use_fr_error_handler()
        assert api2._should_use_fr_error_handler()
        assert not api._has_fr_route()
        assert api2._has_fr_route()
    with app.test_request_context('/blueprint/hi', method='POST'):
        assert api._should_use_fr_error_handler()
        assert not api2._should_use_fr_error_handler()
        assert api._has_fr_route()
        assert not api2._has_fr_route()
    api._should_use_fr_error_handler = Mock(return_value=False)
    api2._should_use_fr_error_handler = Mock(return_value=False)
    with app.test_request_context('/bye'):
        assert not api._has_fr_route()
        assert api2._has_fr_route()
    with app.test_request_context('/blueprint/bye'):
        assert api._has_fr_route()
        assert not api2._has_fr_route()


def test_non_blueprint_non_rest_error_routing(app, blueprint):
    api = flask_restful.Api(blueprint)
    api.add_resource(HelloWorld(), '/hi', endpoint="hello")
    api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
    app.register_blueprint(blueprint, url_prefix='/blueprint')

    @app.route('/hi')
    def hi():
        return 'hi'

    @app.route('/bye')
    def bye():
        flask.abort(404)
    with app.test_request_context('/hi', method='POST'):
        assert not api._should_use_fr_error_handler()
        assert not api._has_fr_route()
    with app.test_request_context('/blueprint/hi', method='POST'):
        assert api._should_use_fr_error_handler()
        assert api._has_fr_route()
    api._should_use_fr_error_handler = Mock(return_value=False)
    with app.test_request_context('/bye'):
        assert not api._has_fr_route()
    with app.test_request_context('/blueprint/bye'):
        assert api._has_fr_route()


if __name__ == '__main__':
    unittest.main()
