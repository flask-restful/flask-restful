from flask import Flask
from flask_restful import Api

from flask.ext.restful import LinkedResource
from flask.ext.restful.declarative import parameters, output, Verb, link

class A(LinkedResource):
    _self = '/a'

    @Verb(parameters(),
          output(),
          link(b = "circulardep.B"))
    def get(self):
        return output()

class B(LinkedResource):
    _self = '/b'

    @Verb(parameters(),
          output(),
          link(a = A))
    def get(self):
        return output()


app = Flask(__name__)
api = Api(app)
api.add_root(A)

if __name__ == '__main__':

    app.run(debug=True)

