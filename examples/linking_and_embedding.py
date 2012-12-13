from flask import Flask
from flask.ext.restful import Api, LinkedResource, Embed, Link, ResourceLink
from flask.ext.restful.declarative import parameters, output, Verb, link
from flask.ext.restful.fields import String

app = Flask(__name__)
api = Api(app)

class Foo(LinkedResource):
    _self = '/bar/foo/<FOO_ID>'

    @Verb(parameters(),
          output(Some_output=String),
          link())
    def get(self, FOO_ID=None):
        return output(Some_output="This is my ID : [%s]" % FOO_ID)

class Baz(LinkedResource):
    _self = '/bar/baz/<BAZ_ID>'

    @Verb(parameters(),
          output(Some_output=String),
          link())
    def get(self, BAZ_ID=None):
        return output(Some_output="This is my ID : [%s]" % BAZ_ID)



class Bar(LinkedResource):
    _self = '/bar'

    @Verb(parameters(),
          output(My_dear_embedded_foo=Foo),
          link(My_dear_linked_baz=Baz))
    def get(self):
        return output(My_dear_embedded_foo=Embed(Foo, {"FOO_ID": 42}), My_dear_linked_baz = ResourceLink(Baz, params={'BAZ_ID': '43'}))


api.add_root(Bar)

if __name__ == '__main__':
    app.run(debug=True)


