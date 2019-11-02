import json
from json import dumps, loads, JSONEncoder
import unittest

import pytest

try:
    from mock import Mock
except:
    # python3
    from unittest.mock import Mock


import flask
from flask import Blueprint, redirect, views, abort as flask_abort
from flask.signals import got_request_exception, signals_available
import six
from werkzeug.exceptions import HTTPException, Unauthorized, BadRequest, _aborter
from werkzeug.http import quote_etag, unquote_etag

from flask_restful.utils import http_status_message, unpack
import flask_restful
import flask_restful.fields
from flask_restful import OrderedDict


def test_unpack():
    assert ("hey", 200, {}) == unpack("hey")
    assert (("hey",), 200, {}) == unpack(("hey",))
    assert ("hey", 201, {}) == unpack(("hey", 201))
    assert ("hey", 201, "foo") == unpack(("hey", 201, "foo"))
    assert (["hey", 201], 200, {}) == unpack(["hey", 201])


# Add a dummy Resource to verify that the app is properly set.
class HelloWorld(flask_restful.Resource):
    def get(self):
        return {}


class BadMojoError(HTTPException):
    pass


# Resource that always errors out
class HelloBomb(flask_restful.Resource):
    def get(self):
        raise BadMojoError("It burns..")


@pytest.fixture()
def api_401(app):
    return flask_restful.Api(app, serve_challenge_on_401=True)


@pytest.fixture()
def fields():
    return OrderedDict([('foo', flask_restful.fields.Raw)])


def test_http_code():
    assert http_status_message(200) == 'OK'
    assert http_status_message(404) == 'Not Found'


def test_unauthorized_no_challenge_by_default(api):
    response = Mock()
    response.headers = {}
    with api.app.test_request_context('/foo'):
        response = api.unauthorized(response)
    assert not 'WWW-Authenticate' in response.headers


def test_unauthorized(api_401):
    response = Mock()
    response.headers = {}
    with api_401.app.test_request_context('/foo'):
        response = api_401.unauthorized(response)
    assert response.headers['WWW-Authenticate'] == 'Basic realm="flask-restful"'


def test_unauthorized_custom_realm(api_401):
    api_401.app.config['HTTP_BASIC_AUTH_REALM'] = 'Foo'
    response = Mock()
    response.headers = {}
    with api_401.app.test_request_context('/foo'):
        response = api_401.unauthorized(response)
    assert response.headers['WWW-Authenticate'] == 'Basic realm="Foo"'


def test_handle_error_401_sends_challege_default_realm(api_401):
    exception = HTTPException()
    exception.code = 401
    exception.data = {'foo': 'bar'}

    with api_401.app.test_request_context('/foo'):
        resp = api_401.handle_error(exception)
        assert resp.status_code == 401
        assert resp.headers['WWW-Authenticate'] == 'Basic realm="flask-restful"'


def test_handle_error_401_sends_challege_configured_realm(api_401):
    api_401.app.config['HTTP_BASIC_AUTH_REALM'] = 'test-realm'

    with api_401.app.test_request_context('/foo'):
        resp = api_401.handle_error(Unauthorized())
        assert resp.status_code == 401
        assert resp.headers['WWW-Authenticate'] == 'Basic realm="test-realm"'


def test_handle_error_does_not_swallow_exceptions(api):
    exception = BadRequest('x')

    with api.app.test_request_context('/foo'):
        resp = api.handle_error(exception)
        assert resp.status_code == 400
        assert resp.get_data() == b'{"message": "x"}\n'

def test_handle_error_does_not_swallow_custom_exceptions(app):
    errors = {'BadMojoError': {'status': 409, 'message': 'go away'}}
    api = flask_restful.Api(app, errors=errors)
    api.add_resource(HelloBomb, '/bomb')

    app = app.test_client()
    resp = app.get('/bomb')
    assert resp.status_code == 409
    assert resp.content_type == api.default_mediatype
    resp_dict = json.loads(resp.data.decode())
    assert resp_dict.get('status') == 409
    assert resp_dict.get('message') == 'go away'


def test_handle_error_does_not_swallow_abort_response(api):
    class HelloBombAbort(flask_restful.Resource):
        def get(self):
            raise HTTPException(response=flask.make_response("{}", 403))
    api.add_resource(HelloBombAbort, '/bomb')

    app = api.app.test_client()
    resp = app.get('/bomb')

    resp_dict = json.loads(resp.data.decode())

    assert resp.status_code == 403
    assert resp_dict == {}


def test_marshal(fields):
    marshal_dict = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = flask_restful.marshal(marshal_dict, fields)
    assert output == {'foo': 'bar'}


def test_marshal_with_envelope(fields):
    marshal_dict = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = flask_restful.marshal(marshal_dict, fields, envelope='hey')
    assert output == {'hey': {'foo': 'bar'}}


def test_marshal_decorator(fields):
    @flask_restful.marshal_with(fields)
    def try_me():
        return OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    assert try_me() == {'foo': 'bar'}


def test_marshal_decorator_with_envelope(fields):
    @flask_restful.marshal_with(fields, envelope='hey')
    def try_me():
        return OrderedDict([('foo', 'bar'), ('bat', 'baz')])

    assert try_me() == {'hey': {'foo': 'bar'}}


def test_marshal_decorator_tuple(fields):
    @flask_restful.marshal_with(fields)
    def try_me():
        return OrderedDict([('foo', 'bar'), ('bat', 'baz')]), 200, {'X-test': 123}
    assert try_me(), ({'foo': 'bar'}, 200 == {'X-test': 123})


def test_marshal_decorator_tuple_with_envelope(fields):
    @flask_restful.marshal_with(fields, envelope='hey')
    def try_me():
        return OrderedDict([('foo', 'bar'), ('bat', 'baz')]), 200, {'X-test': 123}

    assert try_me(), ({'hey': {'foo': 'bar'}}, 200 == {'X-test': 123})


def test_marshal_field_decorator():
    field = flask_restful.fields.Raw

    @flask_restful.marshal_with_field(field)
    def try_me():
        return 'foo'
    assert try_me() == 'foo'


def test_marshal_field_decorator_tuple():
    field = flask_restful.fields.Raw

    @flask_restful.marshal_with_field(field)
    def try_me():
        return 'foo', 200, {'X-test': 123}
    assert ('foo', 200, {'X-test': 123}) == try_me()


def test_marshal_field(fields):
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = flask_restful.marshal(marshal_fields, fields)
    assert output == {'foo': 'bar'}


def test_marshal_tuple(fields):
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = flask_restful.marshal((marshal_fields,), fields)
    assert output == [{'foo': 'bar'}]


def test_marshal_tuple_with_envelope(fields):
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = flask_restful.marshal((marshal_fields,), fields, envelope='hey')
    assert output == {'hey': [{'foo': 'bar'}]}


def test_marshal_nested():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.Nested({
            'fye': flask_restful.fields.String,
        }))
    ])

    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'fye': 'fum'})])
    output = flask_restful.marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', 'fum')]))])
    assert output == expected


def test_marshal_nested_with_non_null():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.Nested(
            OrderedDict([
                ('fye', flask_restful.fields.String),
                ('blah', flask_restful.fields.String)
            ]), allow_null=False))
    ])
    marshal_fields = [OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', None)])]
    output = flask_restful.marshal(marshal_fields, fields)
    expected = [OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', None)]))])]
    assert output == expected


def test_marshal_nested_with_null():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.Nested(
            OrderedDict([
                ('fye', flask_restful.fields.String),
                ('blah', flask_restful.fields.String)
            ]), allow_null=True))
    ])
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', None)])
    output = flask_restful.marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'bar'), ('fee', None)])
    assert output == expected


def test_allow_null_presents_data():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.Nested(
            OrderedDict([
                ('fye', flask_restful.fields.String),
                ('blah', flask_restful.fields.String)
            ]), allow_null=True))
    ])
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'blah': 'cool'})])
    output = flask_restful.marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', 'cool')]))])
    assert output == expected


def test_marshal_nested_property():
    class TestObject(object):
        @property
        def fee(self):
            return {'blah': 'cool'}
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.Nested(
            OrderedDict([
                ('fye', flask_restful.fields.String),
                ('blah', flask_restful.fields.String)
            ]), allow_null=True))
    ])
    obj = TestObject()
    obj.foo = 'bar'
    obj.bat = 'baz'
    output = flask_restful.marshal([obj], fields)
    expected = [OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', 'cool')]))])]
    assert output == expected


def test_marshal_list():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.List(flask_restful.fields.String))
    ])
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', ['fye', 'fum'])])
    output = flask_restful.marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'bar'), ('fee', (['fye', 'fum']))])
    assert output == expected


def test_marshal_list_of_nesteds():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.List(flask_restful.fields.Nested({
            'fye': flask_restful.fields.String
        })))
    ])
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'fye': 'fum'})])
    output = flask_restful.marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'bar'), ('fee', [OrderedDict([('fye', 'fum')])])])
    assert output == expected


def test_marshal_list_of_lists():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('fee', flask_restful.fields.List(flask_restful.fields.List(
            flask_restful.fields.String)))
    ])
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', [['fye'], ['fum']])])
    output = flask_restful.marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'bar'), ('fee', [['fye'], ['fum']])])
    assert output == expected


def test_marshal_nested_dict():
    fields = OrderedDict([
        ('foo', flask_restful.fields.Raw),
        ('bar', OrderedDict([
            ('a', flask_restful.fields.Raw),
            ('b', flask_restful.fields.Raw),
        ])),
    ])
    marshal_fields = OrderedDict([('foo', 'foo-val'), ('bar', 'bar-val'), ('bat', 'bat-val'),
                                  ('a', 1), ('b', 2), ('c', 3)])
    output = flask_restful.marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'foo-val'), ('bar', OrderedDict([('a', 1), ('b', 2)]))])
    assert output == expected


def test_api_representation():
    app = Mock()
    api = flask_restful.Api(app)

    @api.representation('foo')
    def foo():
        pass

    assert api.representations['foo'] == foo


def test_api_base():
    app = Mock()
    app.configure_mock(**{'record.side_effect': AttributeError})
    api = flask_restful.Api(app)
    assert api.urls == {}
    assert api.prefix == ''
    assert api.default_mediatype == 'application/json'


def test_api_delayed_initialization(app):
    api = flask_restful.Api()
    api.add_resource(HelloWorld, '/', endpoint="hello")
    api.init_app(app)
    with app.test_client() as client:
        assert client.get('/').status_code == 200


def test_api_prefix():
    app = Mock()
    app.configure_mock(**{'record.side_effect': AttributeError})
    api = flask_restful.Api(app, prefix='/foo')
    assert api.prefix == '/foo'


def test_handle_server_error(app):
    api = flask_restful.Api(app)

    with app.test_request_context("/foo"):
        resp = api.handle_error(Exception())
        assert resp.status_code == 500
        assert resp.data.decode() == dumps({
            "message": "Internal Server Error"
        }) + "\n"


def test_handle_error_with_code(api_401):
    exception = Exception()
    exception.code = "Not an integer"
    exception.data = {'foo': 'bar'}

    with api_401.app.test_request_context("/foo"):
        resp = api_401.handle_error(exception)
        assert resp.status_code == 500
        assert resp.data.decode() == dumps({"foo": "bar"}) + "\n"


def test_handle_auth(api_401):
    with api_401.app.test_request_context("/foo"):
        resp = api_401.handle_error(Unauthorized())
        assert resp.status_code == 401
        expected_data = dumps({'message': Unauthorized.description}) + "\n"
        assert resp.data.decode() == expected_data
        assert 'WWW-Authenticate' in resp.headers


def test_handle_api_error(api):
    class Test(flask_restful.Resource):
        def get(self):
            flask.abort(404)

    api.add_resource(Test(), '/api', endpoint='api')
    app = api.app.test_client()

    resp = app.get("/api")
    assert resp.status_code == 404
    assert 'application/json' == resp.headers['Content-Type']
    data = loads(resp.data.decode())
    assert 'message' in data


def test_handle_non_api_error(api):
    app = api.app.test_client()

    resp = app.get("/foo")
    assert resp.status_code == 404
    assert 'text/html' == resp.headers['Content-Type']


def test_non_api_error_404_catchall(app):
    api = flask_restful.Api(app, catch_all_404s=True)
    app = app.test_client()

    resp = app.get("/foo")
    assert api.default_mediatype == resp.headers['Content-Type']


def test_handle_error_signal(api):
    if not signals_available:
        # This test requires the blinker lib to run.
        print("Can't test signals without signal support")
        return

    exception = BadRequest()

    recorded = []

    def record(sender, exception):
        recorded.append(exception)

    got_request_exception.connect(record, api.app)
    try:
        with api.app.test_request_context("/foo"):
            api.handle_error(exception)
            assert len(recorded) == 1
            assert exception is recorded[0]
    finally:
        got_request_exception.disconnect(record, api.app)


def test_handle_error(api):
    with api.app.test_request_context("/foo"):
        resp = api.handle_error(BadRequest())
        assert resp.status_code == 400
        assert resp.data.decode() == dumps({
            'message': BadRequest.description,
        }) + "\n"


def test_error_router_falls_back_to_original(api):
    """Verify that if an exception occurs in the Flask-RESTful error handler,
    the error_router will call the original flask error handler instead.
    """
    api.app.handle_exception = Mock()
    api.handle_error = Mock(side_effect=Exception())
    api._has_fr_route = Mock(return_value=True)
    exception = Mock(spec=HTTPException)

    with api.app.test_request_context('/foo'):
        api.error_router(exception, api.app.handle_exception)

    assert api.app.handle_exception.called_with(exception)


def test_media_types(api):
    with api.app.test_request_context("/foo", headers={
        'Accept': 'application/json'
    }):
        assert api.mediatypes() == ['application/json']


def test_media_types_method(api):
    with api.app.test_request_context("/foo", headers={
        'Accept': 'application/xml; q=.5'
    }):
        assert api.mediatypes_method()(Mock()) == ['application/xml', 'application/json']

def test_media_types_q(api):
    with api.app.test_request_context("/foo", headers={
        'Accept': 'application/json; q=1, application/xml; q=.5'
    }):
        assert api.mediatypes() == ['application/json', 'application/xml']


def test_decorator():
    def return_zero(func):
        return 0

    app = Mock(flask.Flask)
    app.view_functions = {}
    view = Mock()
    api = flask_restful.Api(app)
    api.decorators.append(return_zero)
    api.output = Mock()
    api.add_resource(view, '/foo', endpoint='bar')

    app.add_url_rule.assert_called_with('/foo', view_func=0)


def test_add_resource_endpoint():
    app = Mock()
    app.view_functions = {}
    view = Mock()

    api = flask_restful.Api(app)
    api.output = Mock()
    api.add_resource(view, '/foo', endpoint='bar')

    view.as_view.assert_called_with('bar')


def test_add_two_conflicting_resources_on_same_endpoint(api):
    class Foo1(flask_restful.Resource):
        def get(self):
            return 'foo1'

    class Foo2(flask_restful.Resource):
        def get(self):
            return 'foo2'

    api.add_resource(Foo1, '/foo', endpoint='bar')
    with pytest.raises(ValueError):
        api.add_resource(Foo2, '/foo/toto', endpoint='bar')


def test_add_the_same_resource_on_same_endpoint(api):
    class Foo1(flask_restful.Resource):
        def get(self):
            return 'foo1'

    api.add_resource(Foo1, '/foo', endpoint='bar')
    api.add_resource(Foo1, '/foo/toto', endpoint='blah')

    with api.app.test_client() as client:
        foo1 = client.get('/foo')
        assert foo1.data == b'"foo1"\n'
        foo2 = client.get('/foo/toto')
        assert foo2.data == b'"foo1"\n'


def test_add_resource():
    app = Mock(flask.Flask)
    app.view_functions = {}
    api = flask_restful.Api(app)
    api.output = Mock()
    api.add_resource(views.MethodView, '/foo')

    app.add_url_rule.assert_called_with('/foo',
                                        view_func=api.output())


def test_resource_decorator():
    app = Mock(flask.Flask)
    app.view_functions = {}
    api = flask_restful.Api(app)
    api.output = Mock()

    @api.resource('/foo', endpoint='bar')
    class Foo(flask_restful.Resource):
        pass

    app.add_url_rule.assert_called_with('/foo',
                                        view_func=api.output())


def test_add_resource_kwargs():
    app = Mock(flask.Flask)
    app.view_functions = {}
    api = flask_restful.Api(app)
    api.output = Mock()
    api.add_resource(views.MethodView, '/foo', defaults={"bar": "baz"})

    app.add_url_rule.assert_called_with('/foo',
                                        view_func=api.output(),
                                        defaults={"bar": "baz"})


def test_add_resource_forward_resource_class_parameters(api):
    class Foo(flask_restful.Resource):
        def __init__(self, *args, **kwargs):
            self.one = args[0]
            self.two = kwargs['secret_state']

        def get(self):
            return "{0} {1}".format(self.one, self.two)

    api.add_resource(Foo, '/foo',
            resource_class_args=('wonderful',),
            resource_class_kwargs={'secret_state': 'slurm'})

    with api.app.test_client() as client:
        foo = client.get('/foo')
        assert foo.data == b'"wonderful slurm"\n'


def test_output_unpack(api):
    def make_empty_response():
        return {'foo': 'bar'}
    with api.app.test_request_context("/foo"):
        wrapper = api.output(make_empty_response)
        resp = wrapper()
        assert resp.status_code == 200
        assert resp.data.decode() == '{"foo": "bar"}\n'


def test_output_func(api):
    def make_empty_response():
        return flask.make_response('')

    with api.app.test_request_context("/foo"):
        wrapper = api.output(make_empty_response)
        resp = wrapper()
        assert resp.status_code == 200
        assert resp.data.decode() == ''


def test_resource(app):
    resource = flask_restful.Resource()
    resource.get = Mock()
    with app.test_request_context("/foo"):
        resource.dispatch_request()


def test_resource_resp(app):
    resource = flask_restful.Resource()
    resource.get = Mock()
    with app.test_request_context("/foo"):
        resource.get.return_value = flask.make_response('')
        resource.dispatch_request()


def test_resource_text_plain(app):
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
        assert resp.data.decode() == 'hello'


def test_resource_error(app):
    resource = flask_restful.Resource()
    with app.test_request_context("/foo"):
        with pytest.raises(AssertionError):
            resource.dispatch_request()


def test_resource_head(app):
    resource = flask_restful.Resource()
    with app.test_request_context("/foo", method="HEAD"):
        with pytest.raises(AssertionError):
            resource.dispatch_request()


def test_abort_data():
    with pytest.raises(Exception) as error:
        flask_restful.abort(404, foo='bar')
    assert error.value.data == {'foo': 'bar'}


def test_abort_no_data():
    with pytest.raises(Exception) as error:
        flask_restful.abort(404)
    assert hasattr(error.value, "data") == False


def test_abort_custom_message():
    with pytest.raises(Exception) as error:
        flask_restful.abort(404, message="no user")
    assert error.value.data['message'] == "no user"


def test_abort_type():
    with pytest.raises(HTTPException):
        flask_restful.abort(404)


def test_endpoints(api):
    api.add_resource(HelloWorld, '/ids/<int:id>', endpoint="hello")
    with api.app.test_request_context('/foo'):
        assert api._has_fr_route() == False

    with api.app.test_request_context('/ids/3'):
        assert api._has_fr_route()


def test_url_for(api):
    api.add_resource(HelloWorld, '/ids/<int:id>')
    with api.app.test_request_context('/foo'):
        assert api.url_for(HelloWorld, id=123) == '/ids/123'


def test_url_for_with_blueprint(app):
    """Verify that url_for works when an Api object is mounted on a
    Blueprint.
    """
    api_bp = Blueprint('api', __name__)
    api = flask_restful.Api(api_bp)
    api.add_resource(HelloWorld, '/foo/<string:bar>')
    app.register_blueprint(api_bp)
    with app.test_request_context('/foo'):
        assert api.url_for(HelloWorld, bar='baz') == '/foo/baz'


def test_fr_405(api):
    api.add_resource(HelloWorld, '/ids/<int:id>', endpoint="hello")
    app = api.app.test_client()
    resp = app.post('/ids/3')
    assert resp.status_code == 405
    assert resp.content_type == api.default_mediatype
    # Allow can be of the form 'GET, PUT, POST'
    allow = ', '.join(set(resp.headers.get_all('Allow')))
    allow = set(method.strip() for method in allow.split(','))
    assert allow == {'HEAD', 'OPTIONS'}.union(HelloWorld.methods)


def test_exception_header_forwarded(api):
    """Test that HTTPException's headers are extended properly"""
    api.app.config['DEBUG'] = True

    class NotModified(HTTPException):
        code = 304

        def __init__(self, etag, *args, **kwargs):
            super(NotModified, self).__init__(*args, **kwargs)
            self.etag = quote_etag(etag)

        def get_headers(self, *args, **kwargs):
            """Get a list of headers."""
            return [('ETag', self.etag)]

    class Foo1(flask_restful.Resource):
        def get(self):
            flask_abort(304, etag='myETag')

    api.add_resource(Foo1, '/foo')
    _aborter.mapping.update({304: NotModified})

    with api.app.test_client() as client:
        foo = client.get('/foo')
        assert foo.get_etag() == unquote_etag(quote_etag('myETag'))


def test_exception_header_forwarding_doesnt_duplicate_headers(api):
    """Test that HTTPException's headers do not add a duplicate
    Content-Length header

    https://github.com/flask-restful/flask-restful/issues/534
    """
    with api.app.test_request_context('/'):
        r = api.handle_error(BadRequest())

    assert len(r.headers.getlist('Content-Length')) == 1


def test_will_prettyprint_json_in_debug_mode(api):
    api.app.config['DEBUG'] = True

    class Foo1(flask_restful.Resource):
        def get(self):
            return {'foo': 'bar', 'baz': 'asdf'}

    api.add_resource(Foo1, '/foo', endpoint='bar')

    with api.app.test_client() as client:
        foo = client.get('/foo')

        # Python's dictionaries have random order (as of "new" Pythons,
        # anyway), so we can't verify the actual output here.  We just
        # assert that they're properly prettyprinted.
        lines = foo.data.splitlines()
        lines = [line.decode() for line in lines]
        assert "{" == lines[0]
        assert lines[1].startswith('    ')
        assert lines[2].startswith('    ')
        assert "}" == lines[3]

        # Assert our trailing newline.
        assert foo.data.endswith(b'\n')


def test_read_json_settings_from_config(api):
    class TestConfig(object):
        RESTFUL_JSON = {'indent': 2,
                        'sort_keys': True,
                        'separators': (', ', ': ')}

    api.app.config.from_object(TestConfig)

    class Foo(flask_restful.Resource):
        def get(self):
            return {'foo': 'bar', 'baz': 'qux'}

    api.add_resource(Foo, '/foo')

    with api.app.test_client() as client:
        data = client.get('/foo').data

    expected = b'{\n  "baz": "qux", \n  "foo": "bar"\n}\n'

    assert data == expected


def test_use_custom_jsonencoder(api):
    class CabageEncoder(JSONEncoder):
        def default(self, obj):
            return 'cabbage'

    class TestConfig(object):
        RESTFUL_JSON = {'cls': CabageEncoder}

    api.app.config.from_object(TestConfig)

    class Cabbage(flask_restful.Resource):
        def get(self):
            return {'frob': object()}

    api.add_resource(Cabbage, '/cabbage')

    with api.app.test_client() as client:
        data = client.get('/cabbage').data

    expected = b'{"frob": "cabbage"}\n'
    assert data == expected


def test_json_with_no_settings(api):

    class Foo(flask_restful.Resource):
        def get(self):
            return {'foo': 'bar'}

    api.add_resource(Foo, '/foo')

    with api.app.test_client() as client:
        data = client.get('/foo').data

    expected = b'{"foo": "bar"}\n'
    assert data == expected


def test_redirect(api):
    class FooResource(flask_restful.Resource):
        def get(self):
            return redirect('/')

    api.add_resource(FooResource, '/api')

    app = api.app.test_client()
    resp = app.get('/api')
    assert resp.status_code == 302
    assert resp.headers['Location'] == 'http://localhost/'


def test_json_float_marshalled(api):
    class FooResource(flask_restful.Resource):
        fields = {'foo': flask_restful.fields.Float}
        def get(self):
            return flask_restful.marshal({"foo": 3.0}, self.fields)

    api.add_resource(FooResource, '/api')

    app = api.app.test_client()
    resp = app.get('/api')
    assert resp.status_code == 200
    assert resp.data.decode('utf-8') == '{"foo": 3.0}\n'


def test_custom_error_message(app):
    errors = {
        'FooError': {
            'message': "api is foobar",
            'status': 418,
        }
    }

    class FooError(ValueError):
        pass

    api = flask_restful.Api(app, errors=errors)

    exception = FooError()
    exception.code = 400
    exception.data = {'message': 'FooError'}

    with app.test_request_context("/foo"):
        resp = api.handle_error(exception)
        assert resp.status_code == 418
        assert loads(resp.data.decode('utf8')) == {"message": "api is foobar", "status": 418}


def test_calling_owns_endpoint_before_api_init():
    api = flask_restful.Api()

    try:
        api.owns_endpoint('endpoint')
    except AttributeError as ae:
        pytest.fail(ae.message)


def test_selectively_apply_method_decorators(api):
    def upper_deco(f):
        def upper(*args, **kwargs):
            return f(*args, **kwargs).upper()
        return upper

    class TestResource(flask_restful.Resource):
        method_decorators = {'get': [upper_deco]}

        def get(self):
            return 'get test'

        def post(self):
            return 'post test'

    with api.app.test_request_context('/', method='POST'):
        r = TestResource().dispatch_request()
        assert r == 'post test'

    with api.app.test_request_context('/', method='GET'):
        r = TestResource().dispatch_request()
        assert r == 'GET TEST'


def test_apply_all_method_decorators_if_not_mapping(api):
    def upper_deco(f):
        def upper(*args, **kwargs):
            return f(*args, **kwargs).upper()
        return upper

    class TestResource(flask_restful.Resource):
        method_decorators = [upper_deco]

        def get(self):
            return 'get test'

        def post(self):
            return 'post test'

    with api.app.test_request_context('/', method='POST'):
        r = TestResource().dispatch_request()
        assert r == 'POST TEST'

    with api.app.test_request_context('/', method='GET'):
        r = TestResource().dispatch_request()
        assert r == 'GET TEST'


def test_decorators_only_applied_at_dispatch():
    def upper_deco(f):
        def upper(*args, **kwargs):
            return f(*args, **kwargs).upper()
        return upper

    class TestResource(flask_restful.Resource):
        method_decorators = [upper_deco]

        def get(self):
            return 'get test'

        def post(self):
            return 'post test'

    r = TestResource()

    assert r.get() == 'get test'
    assert r.post() == 'post test'


if __name__ == '__main__':
    unittest.main()
