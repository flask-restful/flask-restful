from flask import Flask, request, render_template
from flask.ext.restful import Resource, Api
from flask.ext.restful.declarative import parameters, output, Verb
from flask.ext.restful.fields import Integer, String
from flask.ext.restful.reqparse import RequestParser

app = Flask(__name__)
api = Api(app, output_errors=False)

todos = {}

class Declarative(Resource):
    @Verb(parameters(one = int, two = str),
          output(a = Integer, b = String))
    def get(self, one = None, two = None):
        """
        Documentation of the get verb, it takes one and two and returns the same thing as a and b.
        Enjoy reading the rest.
        """
        return {'a': one, 'b' : two}


    # backward verbose compatible representation
    parser = RequestParser()
    parser.add_argument('param1', int, help = 'This is the explanation of the param 1')
    parser.add_argument('param2', int, help = 'This is the explanation of the param 2')
    post_out_params = output(result = Integer)

    @Verb(parser, post_out_params)
    def post(self, param1, param2):
        """
        This makes the addition of param1 and param2
        """
        return {'result': param1 + param2}


api.add_resource(Declarative, '/')

if __name__ == '__main__':
    app.run(debug=True)


