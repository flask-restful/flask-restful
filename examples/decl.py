from flask import Flask, request, render_template
from flask.ext.restful import Resource, Api
from flask.ext.restful.declarative import parameters, output, Verb
from flask.ext.restful.fields import Integer, String, Float
from flask.ext.restful.reqparse import RequestParser, Argument

app = Flask(__name__)
api = Api(app, output_errors=False)

class Arithmetic(Resource):
    """
    This provides basic arithmetics.
    This is a long documentation coming straight from the source code.
    It should appear correctly.
    """

    @Verb(parameters(numerator = float, denominator = float),
          output(result = Float))
    def get(self, numerator, denominator):
        """
        This makes the division of numerator and denominator.
        It only supports floats.
        The result will be put in "result"
        """
        return {'result': numerator/denominator}


    # backward verbose compatible representation
    parser = RequestParser()
    parser.add_argument('left', 'this is a default from the code', type = int, help = 'This is the left member of the addition')
    parser.add_argument('right',  'this is another default from the code', type = int, help = 'This is the right member of the addition')
    post_out_params = output(result = Integer)

    @Verb(parser, post_out_params)
    def post(self, left, right):
        """
        This makes the addition of left and right.
        It only supports integer.
        The result will be put in "result"
        """
        return {'result': left + right}

class Words(Resource):
    """
    This provides words services !
    """

    @Verb(parameters(subject = Argument(type = str, default='from the code too !', help='inline help'), verb = str),
          output(result = String))
    def put(self, subject, verb):
        """
        This concatenates the 2 words given.
        It only supports strings
        The result will be put in "result"
        """
        return {'result': subject + ' ' + verb}


api.add_resource(Words, '/words')
api.add_resource(Arithmetic, '/arithmetics')

if __name__ == '__main__':
    app.run(debug=True)


