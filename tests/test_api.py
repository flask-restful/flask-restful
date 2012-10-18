import unittest
from flask import Flask, views
from mock import Mock
import flask
import werkzeug
from werkzeug.exceptions import HTTPException
from flask.ext.restful.utils import http_status_message, challenge, unauthorized, error_data, unpack
import flask_restful
import flask_restful.fields
from flask_restful import OrderedDict
from json import dumps
#noinspection PyUnresolvedReferences
from nose.tools import assert_equals # you need it for tests in form of continuations

def check_unpack(expected, value):
    assert_equals(expected, value)

def test_unpack():
    yield check_unpack, ("hey", 200, {}), unpack("hey")
    yield check_unpack, (("hey",), 200, {}), unpack(("hey",))
    yield check_unpack, ("hey", 201, {}), unpack(("hey", 201))
    yield check_unpack, ("hey", 201, "foo"), unpack(("hey", 201, "foo"))
    yield check_unpack, (["hey", 201], 200, {}), unpack(["hey", 201])

class APITestCase(unittest.TestCase):

    def test_http_code(self):
        self.assertEquals(http_status_message(200), 'OK')
        self.assertEquals(http_status_message(404), 'Not Found')


    def test_challenge(self):
        self.assertEquals(challenge('Basic', 'Foo'), 'Basic realm="Foo"')


    def test_unauthorized(self):
        response = Mock()
        response.headers = {}
        unauthorized(response, "flask-restful")
        self.assertEquals(response.headers['WWW-Authenticate'],
                      'Basic realm="flask-restful"')


    def test_unauthorized_custom_realm(self):
        response = Mock()
        response.headers = {}
        unauthorized(response, realm='Foo')
        self.assertEquals(response.headers['WWW-Authenticate'], 'Basic realm="Foo"')


    def test_handle_error_401_sends_challege_default_realm(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)
        exception = Mock()
        exception.code = 401
        exception.data = {'foo': 'bar'}

        with app.test_request_context('/foo'):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 401)
            self.assertEquals(resp.headers['WWW-Authenticate'],
                          'Basic realm="flask-restful"')


    def test_handle_error_401_sends_challege_configured_realm(self):
        app = Flask(__name__)
        app.config['HTTP_BASIC_AUTH_REALM'] = 'test-realm'
        api = flask_restful.Api(app)
        exception = Mock()
        exception.code = 401
        exception.data = {'foo': 'bar'}

        with app.test_request_context('/foo'):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 401)
            self.assertEquals(resp.headers['WWW-Authenticate'],
                          'Basic realm="test-realm"')


    def test_error_data(self):
        self.assertEquals(error_data(400), {
            'status': 400,
            'message': 'Bad Request',
            })


    def test_marshal(self):
        fields = {'foo': flask_restful.fields.Raw}
        output = flask_restful.marshal({'foo': 'bar', 'bat': 'baz'}, fields)
        self.assertEquals(output, {'foo': 'bar'})

    def test_marshal_decorator(self):
        fields = {'foo': flask_restful.fields.Raw}

        @flask_restful.marshal_with(fields)
        def try_me():
            return {'foo': 'bar', 'bat': 'baz'}
        self.assertEquals(try_me(), {'foo': 'bar'})

    def test_marshal_field(self):
        fields = {'foo': flask_restful.fields.Raw()}
        output = flask_restful.marshal({'foo': 'bar', 'bat': 'baz'}, fields)
        self.assertEquals(output, {'foo': 'bar'})



    def test_marshal_tuple(self):
        fields = {'foo': flask_restful.fields.Raw}
        output = flask_restful.marshal(({'foo': 'bar', 'bat': 'baz'},), fields)
        self.assertEquals(output, [{'foo': 'bar'}])


    def test_marshal_nested(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.Nested({
                'fye': flask_restful.fields.String
            })
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz', 'fee':
            {'fye': 'fum'}}], fields)
        self.assertEquals(output, [{'fee': OrderedDict({'fye': 'fum'}), 'foo': 'bar'}])


    def test_marshal_list(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.List(flask_restful.fields.String)
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz',
            'fee': ['fye', 'fum']}], fields)
        self.assertEquals(output, [OrderedDict({'fee': (['fye', 'fum']),
            'foo': 'bar'})])


    def test_marshal_list_of_nesteds(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.List(flask_restful.fields.Nested({
                'fye': flask_restful.fields.String
            }))
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz',
            'fee': {'fye': 'fum'}}], fields)
        self.assertEquals(output, [OrderedDict({'fee': [OrderedDict({'fye': 'fum'})],
            'foo': 'bar'})])


    def test_marshal_list_of_lists(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'fee': flask_restful.fields.List(flask_restful.fields.List(
                flask_restful.fields.String))
        }
        output = flask_restful.marshal([{'foo': 'bar', 'bat': 'baz',
            'fee': [['fye'], ['fum']]}], fields)
        self.assertEquals(output, [OrderedDict({'fee': [['fye'], ['fum']],
            'foo': 'bar'})])


    def test_marshal_nested_dict(self):
        fields = {
            'foo': flask_restful.fields.Raw,
            'bar': {
                'a': flask_restful.fields.Raw,
                'b': flask_restful.fields.Raw,
            },
        }
        output = flask_restful.marshal({'foo': 'foo-val', 'bar': 'bar-val', 'bat':
                                      'bat-val', 'a': 1, 'b': 2, 'c': 3}, fields)
        self.assertEquals(output, OrderedDict({'foo': 'foo-val',
            'bar': {'a': 1, 'b': 2}}))


    def test_api_representation(self):
        app = Mock()
        api = flask_restful.Api(app)

        @api.representation('foo')
        def foo():
            pass

        self.assertEquals(api.representations['foo'], foo)


    def test_api_base(self):
        app = Mock()
        api = flask_restful.Api(app)
        self.assertEquals(api.urls, {})
        self.assertEquals(api.prefix, '')
        self.assertEquals(api.default_mediatype, 'application/json')


    def test_api_prefix(self):
        app = Mock()
        api = flask_restful.Api(app, prefix='/foo')
        self.assertEquals(api.prefix, '/foo')


    def test_handle_server_error(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        exception = Mock()
        exception.code = 500
        exception.data = {'foo': 'bar'}

        with app.test_request_context("/foo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 500)
            self.assertEquals(resp.data, dumps({
                'foo': 'bar',
            }))


    def test_handle_auth(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        exception = Mock()
        exception.code = 401
        exception.data = {'foo': 'bar'}

        with app.test_request_context("/foo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 401)
            self.assertEquals(resp.data, dumps({
                'foo': 'bar',
            }))

            self.assertTrue('WWW-Authenticate' in resp.headers)


    def test_handle_real_error(self):
        app = Flask(__name__)
        flask_restful.Api(app)
        app = app.test_client()

        resp = app.get("/foo")
        self.assertEquals(resp.status_code, 404)
        self.assertEquals(resp.data, dumps(error_data(404)))


    def test_handle_error(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        exception = Mock()
        exception.code = 400
        exception.data = {'foo': 'bar'}

        with app.test_request_context("/foo"):
            resp = api.handle_error(exception)
            self.assertEquals(resp.status_code, 400)
            self.assertEquals(resp.data, dumps({
                'foo': 'bar',
            }))


    def test_media_types(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo",
            headers={'Accept': 'application/json'}):
            self.assertEquals(api.mediatypes(), ['application/json'])


    def test_media_types_method(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo",
            headers={'Accept': 'application/xml; q=.5'}):
            self.assertEquals(api.mediatypes_method()(Mock()),
                ['application/xml', 'application/json'])


    def test_media_types_q(self):
        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo",
            headers={'Accept': 'application/json; q=1; application/xml; q=.5'}):
            self.assertEquals(api.mediatypes(),
                          ['application/json', 'application/xml'])


    def test_decorator(self):
        def return_zero(func):
            return 0

        app = Mock()
        view = Mock()
        api = flask_restful.Api(app)
        api.decorators.append(return_zero)
        api.output = Mock()
        api.add_resource(view, '/foo', endpoint='bar')

        app.add_url_rule.assert_called_with('/foo', view_func=0)


    def test_add_resource_endpoint(self):
        app = Mock()
        view = Mock()

        api = flask_restful.Api(app)
        api.output = Mock()
        api.add_resource(view, '/foo', endpoint='bar')

        view.as_view.assert_called_with('bar')


    def test_add_resource(self):
        app = Mock()
        api = flask_restful.Api(app)
        api.output = Mock()
        api.add_resource(views.MethodView, '/foo')

        app.add_url_rule.assert_called_with('/foo',
            view_func=api.output())


    def test_output_unpack(self):

        def make_empty_resposne():
            return {'foo': 'bar'}

        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo"):
            wrapper = api.output(make_empty_resposne)
            resp = wrapper()
            self.assertEquals(resp.status_code, 200)
            self.assertEquals(resp.data, '{"foo": "bar"}')


    def test_output_func(self):

        def make_empty_resposne():
            return flask.make_response('')

        app = Flask(__name__)
        api = flask_restful.Api(app)

        with app.test_request_context("/foo"):
            wrapper = api.output(make_empty_resposne)
            resp = wrapper()
            self.assertEquals(resp.status_code, 200)
            self.assertEquals(resp.data, '')


    def test_resource(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        resource.get = Mock()
        with app.test_request_context("/foo"):
            resource.dispatch_request()


    def test_resource_resp(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        resource.get = Mock()
        with app.test_request_context("/foo"):
            resource.get.return_value = flask.make_response('')
            resource.dispatch_request()


    def test_resource_text_plain(self):
        app = Flask(__name__)

        def text(data, code, headers=None):
            return flask.make_response(unicode(data))

        class Foo(flask_restful.Resource):

            representations = {
                'text/plain': text,
                }

            def get(self):
                return 'hello'

        with app.test_request_context("/foo", headers={'Accept': 'text/plain'}):
            resource = Foo()
            resp = resource.dispatch_request()
            self.assertEquals(resp.data, 'hello')


    def test_resource_error(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        with app.test_request_context("/foo"):
            self.assertRaises(AssertionError, lambda: resource.dispatch_request())


    def test_resource_head(self):
        app = Flask(__name__)
        resource = flask_restful.Resource()
        with app.test_request_context("/foo", method="HEAD"):
            self.assertRaises(AssertionError, lambda: resource.dispatch_request())


    def test_abort_data(self):
        try:
            flask_restful.abort(404, foo='bar')
            assert False  # We should never get here
        except Exception as e:
            self.assertEquals(e.data, {'foo': 'bar'})


    def test_abort_type(self):
        self.assertRaises(werkzeug.exceptions.HTTPException, lambda: flask_restful.abort(404))

if __name__ == '__main__':
    unittest.main()
