import unittest
from flask import Flask
from flask.ext.restful import LinkedResource, Api, Embed, Link

#noinspection PyUnresolvedReferences
from nose.tools import assert_equals # you need it for tests in form of continuations
from flask.ext.restful.declarative import Verb, parameters, output, link
from flask.ext.restful.fields import Integer, String
from flask.ext.restful.reqparse import Argument


class A(LinkedResource):
    _self = '/a'

    @Verb(parameters(),
          output(),
          link(b = "test_hal.B"))
    def get(self):
        return output()

class B(LinkedResource):
    _self = '/b'

    @Verb(parameters(),
          output(),
          link(a = A))
    def get(self):
        return output()


class HALTestCase(unittest.TestCase):
    def test_lowlevel_link(self):
        class Foo(LinkedResource):
            _self = '/foo/{p}'

        link = Link(Foo, 'my title', {'p': 'foo_p'})
        self.assertFalse(link.templated)
        self.assertEquals(link.title, 'my title')

    def test_standalone_linked_resource(self):
        class Foo(LinkedResource):
            _self = '/foo'

            @Verb(parameters(),
                  output(test_out=Integer))
            def get(self):
                return output(test_out=42)

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Foo)

        app = app.test_client()
        resp = app.get("/foo")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"test_out": 42}')

    def test_standalone_linked_resource_with_params(self):
        class Foo(LinkedResource):
            _self = '/foo'

            @Verb(parameters(my_int=int),
                  output(test_out=Integer))
            def post(self, my_int=None):
                return output(test_out=my_int)

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Foo)

        app = app.test_client()
        resp = app.post("/foo", data=dict(my_int=42))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"test_out": 42}')

    def test_standalone_linked_resource_with_argument_params(self):
        class Foo(LinkedResource):
            _self = '/foo'

            @Verb(parameters(my_int=Argument(type=int, default=2, help='This is the description of the parameter')),
                  output(test_out=Integer))
            def post(self, my_int=None):
                return output(test_out=my_int)

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Foo)

        app = app.test_client()
        resp = app.post("/foo", data=dict(my_int=42))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"test_out": 42}')

        resp = app.post("/foo") # no data it should return the default
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"test_out": 2}')


    def test_smart_error_for_arguments(self):
        class Foo(LinkedResource):
            _self = '/foo'

            @Verb(parameters(my_int=Argument(type=int, default=2, help='This is the description of the parameter')),
                  output(test_out=Integer))
            def post(self, my_int=None):
                return output(test_out=my_int)

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Foo)

        app = app.test_client()
        resp = app.post("/foo", data=dict(my_flint=42))
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(resp.data, '{"message": "Unknown parameter(s) [my_flint]. Did you mean my_int ?"}')


    def test_parameterized_linked_resource(self):
        class Foo(LinkedResource):
            _self = '/foo/<FOO_ID>'

            @Verb(parameters(),
                  output(Some_output=String),
                  link())
            def get(self, FOO_ID=None):
                return output(Some_output="This is my ID : [%s]" % FOO_ID)

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Foo)

        app = app.test_client()
        resp = app.get("/foo/314")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"_links": {"self": {"href": "/foo/314"}}, "Some_output": "This is my ID : [314]"}')

    def test_simple_linked_resource(self):
        class Foo(LinkedResource):
            _self = '/bar/foo'

            @Verb(parameters(),
                  output())
            def get(self):
                return output()

        class Bar(LinkedResource):
            _self = '/bar'

            @Verb(parameters(),
                  output(),
                  link(My_dear_foo=Foo))
            def get(self):
                return output(test_out=42)

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Bar)

        app = app.test_client()
        resp = app.get("/bar")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"_links": {"self": {"href": "/bar"}, "My_dear_foo": {"href": "/bar/foo"}}}')

    def test_circulardep_linked_resource(self):

        app = Flask(__name__)
        api = Api(app)
        api.add_root(A)
        app = app.test_client()
        resp = app.get("/a")
        self.assertEquals(resp.status_code, 200)

        resp = app.get("/b")
        self.assertEquals(resp.status_code, 200)


    def test_simple_embedded_linked_resource(self):
        class Foo(LinkedResource):
            _self = '/bar/foo'

            @Verb(parameters(),
                  output(Some_output=String))
            def get(self):
                return output(Some_output="Should be in the response directly")

        class Bar(LinkedResource):
            _self = '/bar'

            @Verb(parameters(),
                  output(My_dear_foo=Foo),
                  link())
            def get(self):
                return output(My_dear_foo=Embed(Foo))


        app = Flask(__name__)
        api = Api(app)
        api.add_root(Bar)

        app = app.test_client()
        resp = app.get("/bar")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"_links": {"self": {"href": "/bar"}}, "_embedded": {"My_dear_foo": {"Some_output": "Should be in the response directly"}}}')

    def test_parameterized_embedded_linked_resource(self):
        class Foo(LinkedResource):
            _self = '/bar/<FOO_ID>'

            @Verb(parameters(),
                  output(Some_output=String),
                  link())
            def get(self, FOO_ID=None):
                return output(Some_output="This is my ID : [%s]" % FOO_ID)

        class Bar(LinkedResource):
            _self = '/bar'

            @Verb(parameters(),
                  output(My_dear_foo=Foo),
                  link())
            def get(self):
                return output(My_dear_foo=Embed(Foo, {"FOO_ID": 42}))


        app = Flask(__name__)
        api = Api(app)
        api.add_root(Bar)

        app = app.test_client()
        resp = app.get("/bar")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"_links": {"self": {"href": "/bar"}}, "_embedded": {"My_dear_foo": {"_links": {"self": {"href": "/bar/42"}}, "Some_output": "This is my ID : [42]"}}}')

    def test_parameterized_links_output(self):
        class Foo(LinkedResource):
            _self = '/bar/<FOO_ID>'

            def get(self):
                pass

        class Bar(LinkedResource):
            _self = '/bar'

            @Verb(parameters(),
                  output(),
                  link(My_dear_foo=Foo))
            def get(self):
                return output(My_dear_foo=Link(Foo, title = 'my title', params={"FOO_ID": 42}))


        app = Flask(__name__)
        api = Api(app)
        api.add_root(Bar)

        app = app.test_client()
        resp = app.get("/bar")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"_links": {"self": {"href": "/bar"}, "My_dear_foo": {"href": "/bar/42", "title": "my title"}}}')

    def test_parameterized_links_array_output(self):
        class Foo(LinkedResource):
            _self = '/bar/<FOO_ID>'

            def get(self):
                pass

        class Bar(LinkedResource):
            _self = '/bar'

            @Verb(parameters(),
                  output(),
                  link(My_dear_foos=[Foo]))
            def get(self):
                return output(My_dear_foos=[Link(Foo, params={"FOO_ID": 42}), Link(Foo, params={"FOO_ID": 43})])


        app = Flask(__name__)
        api = Api(app)
        api.add_root(Bar)

        app = app.test_client()
        resp = app.get("/bar")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data, '{"_links": {"self": {"href": "/bar"}, "My_dear_foos": [{"href": "/bar/42"}, {"href": "/bar/43"}]}}')


if __name__ == '__main__':
    unittest.main()
