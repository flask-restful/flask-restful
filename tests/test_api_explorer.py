
import unittest
from flask import Flask
from flask.ext.restful import LinkedResource, Api, Embed, Link

#noinspection PyUnresolvedReferences
from nose.tools import assert_equals # you need it for tests in form of continuations
from flask.ext.restful.declarative import Verb, parameters, output, link
from flask.ext.restful.fields import Integer, String
from flask.ext.restful.reqparse import Argument

class APIExplorerTestCase(unittest.TestCase):

    def test_explorer_basic(self):
        class Foo(LinkedResource):
            """
            comment1
            """
            _self = '/foo'

            @Verb(parameters(),
                  output())
            def get(self):
                """
                comment2
                """
                return output()

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Foo)

        app = app.test_client()
        resp = app.get("/foo", headers={'Accept': 'text/html'})
        self.assertEquals(resp.status_code, 200)
        self.assertGreater(resp.data.find('foo'),0)
        self.assertGreater(resp.data.find('Foo'),0)
        self.assertGreater(resp.data.find('comment1'),0)
        self.assertGreater(resp.data.find('comment2'),0)



    def test_explorer_linked_resource_with_params(self):
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
        resp = app.post("/foo", data=dict(my_int=42), headers={'Accept': 'text/html'})
        self.assertEquals(resp.status_code, 200)
        self.assertGreater(resp.data.find('my_int'),0)
        self.assertGreater(resp.data.find('test_out'),0)

    def test_explorer_linked_resource_with_argument_params(self):
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
        resp = app.get("/foo", headers={'Accept': 'text/html'})
        self.assertEquals(resp.status_code, 200)
        self.assertGreater(resp.data.find('This is the description of the parameter'),0)


    def test_explorer_linked_resource(self):
        class Foo(LinkedResource):
            _self = '/foo/{FOO_ID}'

            @Verb(parameters(),
                  output(Some_output=String),
                  link())
            def get(self, FOO_ID=None):
                return output(Some_output="This is my ID : [%s]" % FOO_ID)

        app = Flask(__name__)
        api = Api(app)
        api.add_root(Foo)

        app = app.test_client()
        resp = app.get("/foo/314", headers={'Accept': 'text/html'})
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data.find('FOO_ID'),-1) # it should not appear as it is parameterized

    def test_explorer_linked_resource(self):
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
        resp = app.get("/bar", headers={'Accept': 'text/html'})
        self.assertEquals(resp.status_code, 200)
        self.assertGreater(resp.data.find('My_dear_foo'),0)


    def test_explorer_embedded_linked_resource(self):
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
        resp = app.get("/bar", headers={'Accept': 'text/html'})
        self.assertEquals(resp.status_code, 200)
        self.assertGreater(resp.data.find('embedded'),0)
        self.assertGreater(resp.data.find('Foo'),0)

if __name__ == '__main__':
    unittest.main()
