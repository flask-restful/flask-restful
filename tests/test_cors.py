import unittest
from flask import Flask
import flask_restful
from flask_restful.utils import cors


class CORSTestCase(unittest.TestCase):

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
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers['Access-Control-Allow-Origin'], '*')
            self.assertEqual(res.headers['Access-Control-Max-Age'], '21600')
            self.assertTrue('HEAD' in res.headers['Access-Control-Allow-Methods'])
            self.assertTrue('OPTIONS' in res.headers['Access-Control-Allow-Methods'])
            self.assertTrue('GET' in res.headers['Access-Control-Allow-Methods'])

    def test_access_control_expose_headers(self):

        class Foo(flask_restful.Resource):
            @cors.crossdomain(origin='*',
                              expose_headers=['X-My-Header', 'X-Another-Header'])
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertTrue('X-MY-HEADER' in res.headers['Access-Control-Expose-Headers'])
            self.assertTrue('X-ANOTHER-HEADER' in res.headers['Access-Control-Expose-Headers'])

    def test_access_control_allow_methods(self):

        class Foo(flask_restful.Resource):
            @cors.crossdomain(origin='*',
                              methods={"HEAD","OPTIONS","GET"})
            def get(self):
                return "data"

            def post(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertTrue('HEAD' in res.headers['Access-Control-Allow-Methods'])
            self.assertTrue('OPTIONS' in res.headers['Access-Control-Allow-Methods'])
            self.assertTrue('GET' in res.headers['Access-Control-Allow-Methods'])
            self.assertTrue('POST' not in res.headers['Access-Control-Allow-Methods'])

    def test_no_crossdomain(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)
        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertTrue('Access-Control-Allow-Origin' not in res.headers)
            self.assertTrue('Access-Control-Allow-Methods' not in res.headers)
            self.assertTrue('Access-Control-Max-Age' not in res.headers)
