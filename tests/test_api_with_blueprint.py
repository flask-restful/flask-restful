from flask import Flask, Blueprint, request
try:
    from mock import Mock
except:
    # python3
    from unittest.mock import Mock
import flask
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


class TestAPIWithBlueprint(object):

    def test_api_base(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        assert api.urls == {}
        assert api.prefix == ''
        assert api.default_mediatype == 'application/json'

    def test_api_delayed_initialization(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api()
        api.init_app(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        api.add_resource(HelloWorld, '/', endpoint="hello")

    def test_add_resource_endpoint(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
        api.add_resource(view, '/foo', endpoint='bar')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        view.as_view.assert_called_with('bar')

    def test_add_resource_endpoint_after_registration(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        view = Mock(**{'as_view.return_value': Mock(__name__='test_view')})
        api.add_resource(view, '/foo', endpoint='bar')
        view.as_view.assert_called_with('bar')

    def test_url_with_api_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint, prefix='/api')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/api/hi'):
            assert request.endpoint == 'test.hello'

    def test_url_with_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/bp/hi'):
            assert request.endpoint == 'test.hello'

    def test_url_with_registration_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/reg')
        with app.test_request_context('/reg/hi'):
            assert request.endpoint == 'test.hello'

    def test_registration_prefix_overrides_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/reg')
        with app.test_request_context('/reg/hi'):
            assert request.endpoint == 'test.hello'

    def test_url_with_api_and_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint, prefix='/api')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/bp/api/hi'):
            assert request.endpoint == 'test.hello'

    def test_url_part_order_aeb(self):
        blueprint = Blueprint('test', __name__, url_prefix='/bp')
        api = flask_restful.Api(blueprint, prefix='/api', url_part_order='aeb')
        api.add_resource(HelloWorld, '/hi', endpoint='hello')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/api/hi/bp'):
            assert request.endpoint == 'test.hello'

    def test_error_routing(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        api.add_resource(HelloWorld(), '/hi', endpoint="hello")
        api.add_resource(GoodbyeWorld(404), '/bye', endpoint="bye")
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        with app.test_request_context('/hi', method='POST'):
            assert api._should_use_fr_error_handler() is True
            assert api._has_fr_route() is True
        with app.test_request_context('/bye'):
            api._should_use_fr_error_handler = Mock(return_value=False)
            assert api._has_fr_route() is True

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
            assert api._should_use_fr_error_handler() is False
            assert api2._should_use_fr_error_handler() is True
            assert api._has_fr_route() is False
            assert api2._has_fr_route() is True
        with app.test_request_context('/blueprint/hi', method='POST'):
            assert api._should_use_fr_error_handler() is True
            assert api2._should_use_fr_error_handler() is False
            assert api._has_fr_route() is True
            assert api2._has_fr_route() is False
        api._should_use_fr_error_handler = Mock(return_value=False)
        api2._should_use_fr_error_handler = Mock(return_value=False)
        with app.test_request_context('/bye'):
            assert api._has_fr_route() is False
            assert api2._has_fr_route() is True
        with app.test_request_context('/blueprint/bye'):
            assert api._has_fr_route() is True
            assert api2._has_fr_route() is False

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
            assert api._should_use_fr_error_handler() is False
            assert api._has_fr_route() is False
        with app.test_request_context('/blueprint/hi', method='POST'):
            assert api._should_use_fr_error_handler() is True
            assert api._has_fr_route() is True
        api._should_use_fr_error_handler = Mock(return_value=False)
        with app.test_request_context('/bye'):
            assert api._has_fr_route() is False
        with app.test_request_context('/blueprint/bye'):
            assert api._has_fr_route() is True
