from csv import writer
from StringIO import StringIO

from flask import Flask, make_response, request
from flask.ext.restful import Api, Resource, reqparse

CSV_TYPE = 'text/csv'
app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('format', type=str, help='Specify CSV format')


class Hello(Resource):
    """
        # you need requests
        >>> from requests import get
        >>> get('http://localhost:5000/hello/bob').content # default_mediatype (json)
        '{"hello": "bob"}'
        >>> get('http://localhost:5000/hello/bob?format=csv'}).content
        'greeting,name\r\nhello,bob\r\n'
    """
    def get(self, greeting, name):
        args = parser.parse_args()
        format = args['format']
        data = {greeting: name}
        if format == 'csv':
            fh = StringIO()
            w = writer(fh)
            w.writerow(["greeting", "name"])
            w.writerows(data.items())
            return make_response(fh.getvalue(), 200)
        return data

api.add_resource(Hello, '/<string:greeting>/<string:name>')

if __name__ == '__main__':
    app.run(debug=True)
