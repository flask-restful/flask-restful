import unittest
from flask import Flask
from flask.ext.restful.paging import retreive_next_page
from flask.ext.restful import LinkedResource, ResourceLink, Api
from flask.ext.restful.declarative import Verb, parameters, output, link

key = '0123456789abcdef0123456789abcdef'
seed = 'deadbeefcafebabe'


def fetch_data(filters, bookmark, page_size):
    if bookmark is None:
        bookmark = 0
    return [i for i in range(bookmark, bookmark + page_size)], bookmark + page_size, 100000


class Foo(LinkedResource):
    _self = '/bar/<FOO_ID>'

    def get(self):
        pass


class Bar(LinkedResource):
    _self = '/bar'

    @Verb(parameters(),
          output(),
          link(My_dear_foos=[Foo]), output_paging=True)
    def get(self, **kwargs):  # To=None, From=None, Status=None, StartTime=None
        result, f, approx_result_size = retreive_next_page(key, seed, kwargs, fetch_data)
        return output(My_dear_foos=[ResourceLink(Foo, params={"FOO_ID": i}) for i in result]), f, approx_result_size


class PagingTestCase(unittest.TestCase):
    def test_bookmark_paging(self):
        f = {'my_filter': 'yes', 'page_size': 3}

        result, f, approx_result_size = retreive_next_page(key, seed, f, fetch_data)

        self.assertEquals(result, [0, 1, 2])
        self.assertEquals(approx_result_size, 100000)

        result, f, approx_result_size = retreive_next_page(key, seed, f, fetch_data)

        self.assertEquals(approx_result_size, 100000)
        self.assertEquals(result, [3, 4, 5])


    def test_linkedresource_paging(self):
        app = Flask(__name__)
        api = Api(app)
        api.add_root(Bar)

        app = app.test_client()
        resp = app.get("/bar")
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.data,
                          '{"_links": {"self": {"href": "/bar"}, "My_dear_foos": [{"href": "/bar/0"}, {"href": "/bar/1"}, {"href": "/bar/2"}, {"href": "/bar/3"}, '
                          '{"href": "/bar/4"}, {"href": "/bar/5"}, {"href": "/bar/6"}, {"href": "/bar/7"}, {"href": "/bar/8"}, {"href": "/bar/9"}, {"href": "/bar/10"}, '
                          '{"href": "/bar/11"}, {"href": "/bar/12"}, {"href": "/bar/13"}, {"href": "/bar/14"}, {"href": "/bar/15"}, {"href": "/bar/16"}, {"href": "/bar/17"}, '
                          '{"href": "/bar/18"}, {"href": "/bar/19"}, {"href": "/bar/20"}, {"href": "/bar/21"}, {"href": "/bar/22"}, {"href": "/bar/23"}, {"href": "/bar/24"}, '
                          '{"href": "/bar/25"}, {"href": "/bar/26"}, {"href": "/bar/27"}, {"href": "/bar/28"}, {"href": "/bar/29"}, {"href": "/bar/30"}, {"href": "/bar/31"}, '
                          '{"href": "/bar/32"}, {"href": "/bar/33"}, {"href": "/bar/34"}, {"href": "/bar/35"}, {"href": "/bar/36"}, {"href": "/bar/37"}, {"href": "/bar/38"}, '
                          '{"href": "/bar/39"}, {"href": "/bar/40"}, {"href": "/bar/41"}, {"href": "/bar/42"}, {"href": "/bar/43"}, {"href": "/bar/44"}, {"href": "/bar/45"}, '
                          '{"href": "/bar/46"}, {"href": "/bar/47"}, {"href": "/bar/48"}, {"href": "/bar/49"}], '
                          '"next": {"href": "/bar?pager_info=B2QAhkXMxhkjWpJyiy1djg%3D%3D&page_size=50", "title": "Next results"}}}')
