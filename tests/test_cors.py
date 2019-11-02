import flask_restful
from flask_restful.utils import cors


def test_crossdomain(api):
    class Foo(flask_restful.Resource):
        @cors.crossdomain(origin='*')
        def get(self):
            return "data"
    api.add_resource(Foo, '/')

    with api.app.test_client() as client:
        res = client.get('/')
        assert res.status_code == 200
        assert res.headers['Access-Control-Allow-Origin'] == '*'
        assert res.headers['Access-Control-Max-Age'] == '21600'
        assert 'HEAD' in res.headers['Access-Control-Allow-Methods']
        assert 'OPTIONS' in res.headers['Access-Control-Allow-Methods']
        assert 'GET' in res.headers['Access-Control-Allow-Methods']


def test_access_control_expose_headers(api):
    class Foo(flask_restful.Resource):
        @cors.crossdomain(origin='*',
                          expose_headers=['X-My-Header', 'X-Another-Header'])
        def get(self):
            return "data"
    api.add_resource(Foo, '/')

    with api.app.test_client() as client:
        res = client.get('/')
        assert res.status_code == 200
        assert 'X-MY-HEADER' in res.headers['Access-Control-Expose-Headers']
        assert 'X-ANOTHER-HEADER' in res.headers['Access-Control-Expose-Headers']


def test_access_control_allow_methods(api):

    class Foo(flask_restful.Resource):
        @cors.crossdomain(origin='*',
                          methods={"HEAD","OPTIONS","GET"})
        def get(self):
            return "data"

        def post(self):
            return "data"
    api.add_resource(Foo, '/')

    with api.app.test_client() as client:
        res = client.get('/')
        assert res.status_code == 200
        assert 'HEAD' in res.headers['Access-Control-Allow-Methods']
        assert 'OPTIONS' in res.headers['Access-Control-Allow-Methods']
        assert 'GET' in res.headers['Access-Control-Allow-Methods']
        assert 'POST' not in res.headers['Access-Control-Allow-Methods']


def test_no_crossdomain(api):
    class Foo(flask_restful.Resource):
        def get(self):
            return "data"
    api.add_resource(Foo, '/')

    with api.app.test_client() as client:
        res = client.get('/')
        assert res.status_code == 200
        assert 'Access-Control-Allow-Origin' not in res.headers
        assert 'Access-Control-Allow-Methods' not in res.headers
        assert 'Access-Control-Max-Age' not in res.headers
