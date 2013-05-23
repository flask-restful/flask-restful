import unittest
from flask_restful.paging import retrieve_next_page


class PagingTestCase(unittest.TestCase):
    def test_bookmark_paging(self):
        key = '0123456789abcdef0123456789abcdef'
        seed = 'deadbeefcafebabe'

        def fetch_data(filters, bookmark, page_size):
            self.assertEquals(filters['my_filter'], 'yes')
            self.assertEquals(len(filters), 1)  # we don't want extraneous paging metadata in there
            if bookmark is None:
                bookmark = 0
            return [i for i in range(bookmark, bookmark + page_size)], bookmark + page_size, 100000

        filter = {'my_filter': 'yes', 'page_size': 3}

        result, filter, approx_result_size = retrieve_next_page(key, seed, filter, fetch_data)

        self.assertEquals(result, [0, 1, 2])
        self.assertEquals(approx_result_size, 100000)

        result, filter, approx_result_size = retrieve_next_page(key, seed, filter, fetch_data)

        self.assertEquals(approx_result_size, 100000)
        self.assertEquals(result, [3, 4, 5])
