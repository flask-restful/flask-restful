from flask import Flask
import flask_restful
from flask_restful.utils import cors


class TestCORS(object):

    def test_crossdomain(self):

        class Foo(flask_restful.Resource):
            @cors.crossdomain(origin='*')
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            assert res.status_code == 200
            assert res.headers['Access-Control-Allow-Origin'] == '*'
            assert res.headers['Access-Control-Max-Age'] == '21600'
            assert 'HEAD' in res.headers['Access-Control-Allow-Methods']
            assert 'OPTIONS' in res.headers['Access-Control-Allow-Methods']
            assert 'GET' in res.headers['Access-Control-Allow-Methods']

    def test_no_crossdomain(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            assert res.status_code == 200
            assert 'Access-Control-Allow-Origin' not in res.headers
            assert 'Access-Control-Allow-Methods' not in res.headers
            assert 'Access-Control-Max-Age' not in res.headers
