import unittest

import pytest
from flask import Flask
from nose.tools import assert_equals

import flask_restful


class Foo(flask_restful.Resource):
    def get(self):
        return "data"


@pytest.fixture()
def api_with_mediatype(api):
    api.add_resource(Foo, '/')

    return api


@pytest.fixture()
def api_no_mediatype(app):
    api = flask_restful.Api(app, default_mediatype=None)
    api.add_resource(Foo, '/')

    return api


@pytest.mark.parametrize('headers', [
    [('Accept', 'application/json')],
    [('Accept', 'text/plain')],
])
def test_accept_default_headers_to_json(api_with_mediatype, headers):
    with api_with_mediatype.app.test_client() as client:
        res = client.get('/', headers=headers)
        assert res.status_code == 200
        assert res.content_type == 'application/json'


def test_accept_default_any_pick_first(api_with_mediatype):
    @api_with_mediatype.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = api_with_mediatype.app.make_response((str(data), status_code, headers))
        return resp

    with api_with_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', '*/*')])
        assert res.status_code == 200
        assert res.content_type == 'application/json'


def test_accept_no_default_no_match_not_acceptable(api_no_mediatype):
    with api_no_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'text/plain')])
        assert res.status_code == 406
        assert res.content_type == 'application/json'


def test_accept_no_default_custom_repr_match(api_no_mediatype):
    api_no_mediatype.representations = {}

    @api_no_mediatype.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = api_no_mediatype.app.make_response((str(data), status_code, headers))
        return resp

    with api_no_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'text/plain')])
        assert res.status_code == 200
        assert res.content_type == 'text/plain'


def test_accept_no_default_custom_repr_not_acceptable(api_no_mediatype):
    api_no_mediatype.representations = {}

    @api_no_mediatype.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = api_no_mediatype.app.make_response((str(data), status_code, headers))
        return resp

    with api_no_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'application/json')])
        assert res.status_code == 406
        assert res.content_type == 'text/plain'


def test_accept_no_default_match_q0_not_acceptable(api_no_mediatype):
    """
    q=0 should be considered NotAcceptable,
    but this depends on werkzeug >= 1.0 which is not yet released
    so this test is expected to fail until we depend on werkzeug >= 1.0
    """
    with api_no_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'application/json; q=0')])
        assert res.status_code == 406
        assert res.content_type == 'application/json'


def test_accept_no_default_accept_highest_quality_of_two(api_no_mediatype):
    @api_no_mediatype.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = api_no_mediatype.app.make_response((str(data), status_code, headers))
        return resp

    with api_no_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=1.0')])
        assert res.status_code == 200
        assert res.content_type == 'text/plain'


def test_accept_no_default_accept_highest_quality_of_three(api_no_mediatype):
    @api_no_mediatype.representation('text/html')
    @api_no_mediatype.representation('text/plain')
    def text_rep(data, status_code, headers=None):
        resp = api_no_mediatype.app.make_response((str(data), status_code, headers))
        return resp

    with api_no_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'application/json; q=0.1, text/plain; q=0.3, text/html; q=0.2')])
        assert res.status_code == 200
        assert res.content_type == 'text/plain'


def test_accept_no_default_no_representations(api_no_mediatype):
    api_no_mediatype.representations = {}

    with api_no_mediatype.app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'text/plain')])
        assert res.status_code == 406
        assert res.content_type == 'text/plain'


def test_accept_invalid_default_no_representations(app):
    api = flask_restful.Api(app, default_mediatype='nonexistant/mediatype')
    api.representations = {}

    api.add_resource(Foo, '/')

    with app.test_client() as client:
        res = client.get('/', headers=[('Accept', 'text/plain')])
        assert res.status_code == 500
