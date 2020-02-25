import unittest

from flask import Flask
from nose.tools import assert_equals

import flask_restful


class AcceptTestCase(unittest.TestCase):

    def setUp(self):

        class Foo(flask_restful.Resource):
            def get(self):
                return "data"

        self.app = Flask(__name__)
        self.api = flask_restful.Api(self.app)
        self.api.add_resource(Foo, '/')

        self.app_no_mediatype = Flask(__name__)
        self.api_no_mediatype = flask_restful.Api(self.app_no_mediatype, default_mediatype=None)
        self.api_no_mediatype.add_resource(Foo, '/')

    def test_accept_default_application_json(self):
        with self.app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            assert_equals(res.status_code, 200)
            assert_equals(res.content_type, 'application/json')

    def test_accept_no_default_match_acceptable(self):
        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            assert_equals(res.status_code, 200)
            assert_equals(res.content_type, 'application/json')

    def test_accept_default_override_accept(self):
        with self.app.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            assert_equals(res.status_code, 200)
            assert_equals(res.content_type, 'application/json')

    def test_accept_default_any_pick_first(self):
        @self.api.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = self.app.make_response((str(data), status_code, headers))
            return resp

        with self.app.test_client() as client:
            res = client.get('/', headers=[('Accept', '*/*')])
            assert_equals(res.status_code, 200)
            assert_equals(res.content_type, 'application/json')

    def test_accept_no_default_no_match_not_acceptable(self):
        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            assert_equals(res.status_code, 406)
            assert_equals(res.content_type, 'application/json')

    def test_accept_no_default_custom_repr_match(self):
        self.api_no_mediatype.representations = {}

        @self.api_no_mediatype.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = self.app_no_mediatype.make_response((str(data), status_code, headers))
            return resp

        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            assert_equals(res.status_code, 200)
            assert_equals(res.content_type, 'text/plain')

    def test_accept_no_default_custom_repr_not_acceptable(self):
        self.api_no_mediatype.representations = {}

        @self.api_no_mediatype.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = self.app_no_mediatype.make_response((str(data), status_code, headers))
            return resp

        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json')])
            assert_equals(res.status_code, 406)
            assert_equals(res.content_type, 'text/plain')

    def test_accept_no_default_match_q0_not_acceptable(self):
        """
        q=0 should be considered NotAcceptable,
        but this depends on werkzeug >= 1.0 which is not yet released
        so this test is expected to fail until we depend on werkzeug >= 1.0
        """
        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0')])
            assert_equals(res.status_code, 406)
            assert_equals(res.content_type, 'application/json')

    def test_accept_no_default_accept_highest_quality_of_two(self):
        @self.api_no_mediatype.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = self.app_no_mediatype.make_response((str(data), status_code, headers))
            return resp

        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=1.0')])
            assert_equals(res.status_code, 200)
            assert_equals(res.content_type, 'text/plain')

    def test_accept_no_default_accept_highest_quality_of_three(self):
        @self.api_no_mediatype.representation('text/html')
        @self.api_no_mediatype.representation('text/plain')
        def text_rep(data, status_code, headers=None):
            resp = self.app_no_mediatype.make_response((str(data), status_code, headers))
            return resp

        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=0.3, text/html; q=0.2')])
            assert_equals(res.status_code, 200)
            assert_equals(res.content_type, 'text/plain')

    def test_accept_no_default_no_representations(self):
        self.api_no_mediatype.representations = {}

        with self.app_no_mediatype.test_client() as client:
            res = client.get('/', headers=[('Accept', 'text/plain')])
            assert_equals(res.status_code, 406)
            assert_equals(res.content_type, 'text/plain')

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
            assert_equals(res.status_code, 500)
