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
    
    
    def test_blueprint_registration_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/foo')
        self.assertEquals(api.prefix, '/foo')
    
    
    def test_blueprint_prefix_matches_api_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/foo')
        api = flask_restful.Api(blueprint, prefix='/foo')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        self.assertEquals(api.prefix, '/foo')
    
    def test_registration_prefix_overrides_blueprint_prefix(self):
        blueprint = Blueprint('test', __name__, url_prefix='/foo')
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/bar')
        self.assertEquals(api.prefix, '/bar')
    
    
    def test_registration_prefix_overrides_api_prefix(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint, prefix='/foo')
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/bar')
        self.assertEquals(api.prefix, '/bar')
    
    
    def test_blueprint_prefix_does_not_match_api_prefx(self):
        blueprint = Blueprint('test', __name__, url_prefix='/foo')
        self.assertRaises(ValueError, flask_restful.Api, blueprint, prefix='/bar')
    
    
    def test_add_resource_endpoint(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        view = Mock(**{'as_view.return_value' : Mock(__name__='test_view')})
        api.add_resource(view, '/foo', endpoint='bar')
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        view.as_view.assert_called_with('bar')


    def test_add_resource_endpoint_after_registration(self):
        blueprint = Blueprint('test', __name__)
        api = flask_restful.Api(blueprint)
        app = Flask(__name__)
        app.register_blueprint(blueprint)
        view = Mock(**{'as_view.return_value' : Mock(__name__='test_view')})
        api.add_resource(view, '/foo', endpoint='bar')
        view.as_view.assert_called_with('bar')


if __name__ == '__main__':
    unittest.main()
