import unittest
from flask_restful import types
import datetime
#noinspection PyUnresolvedReferences
from nose.tools import assert_equals # you need it for tests in form of continuations
import six

# http://docs.python.org/library/datetime.html?highlight=datetime#datetime.tzinfo.fromutc
ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)


class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

def test_datetime_formatters():
    dates = [
        (datetime.datetime(2011, 1, 1), "Sat, 01 Jan 2011 00:00:00 -0000"),
        (datetime.datetime(2011, 1, 1, 23, 59, 59),
         "Sat, 01 Jan 2011 23:59:59 -0000"),
        (datetime.datetime(2011, 1, 1, 23, 59, 59, tzinfo=UTC()),
                  "Sat, 01 Jan 2011 23:59:59 -0000"),
        ]
    for date_obj, expected in dates:
        yield assert_equals, types.rfc822(date_obj), expected

def test_urls():
    urls = [
        'http://www.djangoproject.com/',
        'http://localhost/',
        'http://example.com/',
        'http://www.example.com/',
        'http://www.example.com:8000/test',
        'http://valid-with-hyphens.com/',
        'http://subdomain.example.com/',
        'http://200.8.9.10/',
        'http://200.8.9.10:8000/test',
        'http://valid-----hyphens.com/',
        'http://example.com?something=value',
        'http://example.com/index.php?something=value&another=value2',
        'http://foo:bar@example.com',
        'http://foo:@example.com',
        'http://foo:@2001:db8:85a3::8a2e:370:7334',
        'http://foo2:qd1%r@example.com',
        ]

    for value in urls:
        yield assert_equals, types.url(value), value

def check_bad_url_raises(value):
    try:
        types.url(value)
        assert False, "shouldn't get here"
    except ValueError as e:
        assert_equals(six.text_type(e), u"{0} is not a valid URL".format(value))

def test_bad_urls():
    values = [
        'foo',
        'http://',
        'http://example',
        'http://example.',
        'http://.com',
        'http://invalid-.com',
        'http://-invalid.com',
        'http://inv-.alid-.com',
        'http://inv-.-alid.com',
        'foo bar baz',
        u'foo \u2713',
        'http://@foo:bar@example.com',
        'http://:bar@example.com',
        'http://bar:bar:bar@example.com',
    ]

    for value in values:
        yield check_bad_url_raises, value

def test_bad_url_error_message():
    values = [
        'google.com',
        'domain.google.com',
        'kevin:pass@google.com/path?query',
        u'google.com/path?\u2713',
    ]

    for value in values:
        yield check_url_error_message, value

def check_url_error_message(value):
    try:
        types.url(value)
        assert False, u"types.url({0}) should raise an exception".format(value)
    except ValueError as e:
        assert_equals(six.text_type(e), 
                      (u"{0} is not a valid URL. Did you mean: http://{0}".format(value)))


class TypesTestCase(unittest.TestCase):

    def test_boolean_false(self):
        self.assertEquals(types.boolean("False"), False)


    def test_boolean_true(self):
        self.assertEquals(types.boolean("true"), True)


    def test_boolean_upper_case(self):
        self.assertEquals(types.boolean("FaLSE"), False)


    def test_boolean(self):
        self.assertEquals(types.boolean("FaLSE"), False)


    def test_date_later_than_1900(self):
        self.assertEquals(types.date("1900-01-01"), datetime.datetime(1900, 1, 1))


    def test_date_too_early(self):
        self.assertRaises(ValueError, lambda: types.date("0001-01-01"))


    def test_date_input_error(self):
        self.assertRaises(ValueError, lambda: types.date("2008-13-13"))

    def test_date_input(self):
        self.assertEquals(types.date("2008-08-01"), datetime.datetime(2008, 8, 1))

    def test_natual_negative(self):
        self.assertRaises(ValueError, lambda: types.natural(-1))

    def test_natual(self):
        self.assertEquals(3, types.natural(3))


    def test_natual_string(self):
        self.assertRaises(ValueError, lambda: types.natural('foo'))


if __name__ == '__main__':
    unittest.main()
