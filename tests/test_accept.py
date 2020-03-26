import unittest
from flask import Flask
import flask_restful
from werkzeug import exceptions



class AcceptTestCase(unittest.TestCase):

    def test_accept_default_application_json(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_no_default_match_acceptable(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_default_override_accept(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_default_any_pick_first(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app)

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', '*/*')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_no_default_no_match_not_acceptable(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'application/json')


    def test_accept_no_default_custom_repr_match(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.representations = {}

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_custom_repr_not_acceptable(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.representations = {}

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_match_q0_not_acceptable(self):
        """
        q=0 should be considered NotAcceptable,
        but this depends on werkzeug >= 1.0 which is not yet released
        so this test is expected to fail until we depend on werkzeug >= 1.0
        """
        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'application/json')

    def test_accept_no_default_accept_highest_quality_of_two(self):
        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=1.0')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_accept_highest_quality_of_three(self):
        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)

        @api.representation('text/html')
        @api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = app.make_response((str(data), status_code, headers))
            return resp

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=0.3, text/html; q=0.2')])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/plain')


    def test_accept_no_default_no_representations(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype=None)
        api.representations = {}

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 406)
            self.assertEqual(res.content_type, 'text/plain')

    def test_accept_invalid_default_no_representations(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        app = Flask(__name__)
        api = flask_restful.Api(app, default_mediatype='nonexistant/mediatype')
        api.representations = {}

        api.add_resource(Foo, '/')

        with app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            self.assertEqual(res.status_code, 500)
