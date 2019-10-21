from datetime import datetime
import re
import unittest

# noinspection PyUnresolvedReferences
import pytest
from nose.tools import assert_equal, assert_raises  # you need it for tests in form of continuations
import pytz
import six

from flask_restful import inputs


@pytest.mark.parametrize('date,expected', [
    ("Sat, 01 Jan 2011 00:00:00 -0000", datetime(2011, 1, 1, tzinfo=pytz.utc)),
    ("Sat, 01 Jan 2011 23:59:59 -0000", datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc)),
    ("Sat, 01 Jan 2011 21:59:59 -0200", datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc)),
])
def test_reverse_rfc822_datetime(date, expected):
    assert inputs.datetime_from_rfc822(date) == expected


@pytest.mark.parametrize('date,expected', [
    ("2011-01-01T00:00:00+00:00", datetime(2011, 1, 1, tzinfo=pytz.utc)),
    ("2011-01-01T23:59:59+00:00", datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc)),
    ("2011-01-01T23:59:59.001000+00:00", datetime(2011, 1, 1, 23, 59, 59, 1000, tzinfo=pytz.utc)),
    ("2011-01-01T23:59:59+02:00", datetime(2011, 1, 1, 21, 59, 59, tzinfo=pytz.utc))
])
def test_reverse_iso8601_datetime(date, expected):
    assert inputs.datetime_from_iso8601(date) == expected


@pytest.mark.parametrize('url', [
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
])
def test_urls(url):
    assert inputs.url(url) == url


@pytest.mark.parametrize('url', [
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
])
def test_bad_urls(url):
    with pytest.raises(ValueError) as error:
        inputs.url(url)
    assert six.text_type(error.value) == u"{0} is not a valid URL".format(url)


@pytest.mark.parametrize('url', [
    'google.com',
    'domain.google.com',
    'kevin:pass@google.com/path?query',
    u'google.com/path?\u2713',
])
def test_bad_url_error_message(url):
    check_url_error_message(url)


def check_url_error_message(value):
    with pytest.raises(ValueError) as error:
        inputs.url(value)

    assert six.text_type(error.value) == (
        u"{0} is not a valid URL. Did you mean: http://{0}".format(value))


@pytest.mark.parametrize('input', [
    'abc',
    '123abc',
    'abc123',
    '',
])
def test_regex_bad_input(input):
    num_only = inputs.regex(r'^[0-9]+$')

    with pytest.raises(ValueError):
        num_only(input)


@pytest.mark.parametrize('input', [
    '123',
    '1234567890',
    '00000',
])
def test_regex_good_input(input):
    num_only = inputs.regex(r'^[0-9]+$')
    assert num_only(input) == input


def test_regex_bad_pattern():
    """Regex error raised immediately when regex input parser is created."""
    with pytest.raises(re.error):
        inputs.regex('[')


@pytest.mark.parametrize('input', [
    'abcd',
    'ABCabc',
    'ABC',
])
def test_regex_flags_good_input(input):
    case_insensitive = inputs.regex(r'^[A-Z]+$', re.IGNORECASE)
    assert case_insensitive(input) == input


@pytest.mark.parametrize('case', [
    'abcd',
    'ABCabc',
])
def test_regex_flags_bad_input(case):
    case_sensitive = inputs.regex(r'^[A-Z]+$')
    with pytest.raises(ValueError):
        case_sensitive(case)


def test_boolean_false():
    assert not inputs.boolean("False")


def test_boolean_is_false_for_0():
    assert not inputs.boolean("0")


def test_boolean_true():
    assert inputs.boolean("true")


def test_boolean_is_true_for_1():
    assert inputs.boolean("1")


def test_boolean_upper_case():
    assert not inputs.boolean("FaLSE")


def test_boolean():
    assert not inputs.boolean("FaLSE")


def test_boolean_with_python_bool():
    """Input that is already a native python `bool` should be passed through
    without extra processing."""
    assert inputs.boolean(True)
    assert not inputs.boolean(False)


def test_bad_boolean():
    with pytest.raises(ValueError):
        inputs.boolean("blah")


def test_date_later_than_1900():
    assert inputs.date("1900-01-01") == datetime(1900, 1, 1)


def test_date_input_error():
    with pytest.raises(ValueError):
        inputs.date("2008-13-13")


def test_date_input():
    assert inputs.date("2008-08-01") == datetime(2008, 8, 1)


def test_natual_negative():
    with pytest.raises(ValueError):
        inputs.natural(-1)


def test_natural():
    assert 3 == inputs.natural(3)


def test_natual_string():
    with pytest.raises(ValueError):
        inputs.natural('foo')


def test_positive():
    assert 1 == inputs.positive(1)
    assert 10000 == inputs.positive(10000)


def test_positive_zero():
    with pytest.raises(ValueError):
        inputs.positive(0)


def test_positive_negative_input():
    with pytest.raises(ValueError):
        inputs.positive(-1)


def test_int_range_good():
    int_range = inputs.int_range(1, 5)
    assert 3 == int_range(3)


def test_int_range_inclusive():
    int_range = inputs.int_range(1, 5)
    assert 5 == int_range(5)


def test_int_range_low():
    int_range = inputs.int_range(0, 5)
    with pytest.raises(ValueError):
        int_range(-1)


def test_int_range_high():
    int_range = inputs.int_range(0, 5)
    with pytest.raises(ValueError):
        int_range(6)


def test_isointerval():
    intervals = [
        (
            # Full precision with explicit UTC.
            "2013-01-01T12:30:00Z/P1Y2M3DT4H5M6S",
            (
                datetime(2013, 1, 1, 12, 30, 0, tzinfo=pytz.utc),
                datetime(2014, 3, 5, 16, 35, 6, tzinfo=pytz.utc),
            ),
        ),
        (
            # Full precision with alternate UTC indication
            "2013-01-01T12:30+00:00/P2D",
            (
                datetime(2013, 1, 1, 12, 30, 0, tzinfo=pytz.utc),
                datetime(2013, 1, 3, 12, 30, 0, tzinfo=pytz.utc),
            ),
        ),
        (
            # Implicit UTC with time
            "2013-01-01T15:00/P1M",
            (
                datetime(2013, 1, 1, 15, 0, 0, tzinfo=pytz.utc),
                datetime(2013, 1, 31, 15, 0, 0, tzinfo=pytz.utc),
            ),
        ),
        (
            # TZ conversion
            "2013-01-01T17:00-05:00/P2W",
            (
                datetime(2013, 1, 1, 22, 0, 0, tzinfo=pytz.utc),
                datetime(2013, 1, 15, 22, 0, 0, tzinfo=pytz.utc),
            ),
        ),
        (
            # Date upgrade to midnight-midnight period
            "2013-01-01/P3D",
            (
                datetime(2013, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
                datetime(2013, 1, 4, 0, 0, 0, 0, tzinfo=pytz.utc),
            ),
        ),
        (
            # Start/end with UTC
            "2013-01-01T12:00:00Z/2013-02-01T12:00:00Z",
            (
                datetime(2013, 1, 1, 12, 0, 0, tzinfo=pytz.utc),
                datetime(2013, 2, 1, 12, 0, 0, tzinfo=pytz.utc),
            ),
        ),
        (
            # Start/end with time upgrade
            "2013-01-01/2013-06-30",
            (
                datetime(2013, 1, 1, tzinfo=pytz.utc),
                datetime(2013, 6, 30, tzinfo=pytz.utc),
            ),
        ),
        (
            # Start/end with TZ conversion
            "2013-02-17T12:00:00-07:00/2013-02-28T15:00:00-07:00",
            (
                datetime(2013, 2, 17, 19, 0, 0, tzinfo=pytz.utc),
                datetime(2013, 2, 28, 22, 0, 0, tzinfo=pytz.utc),
            ),
        ),
        # Resolution expansion for single date(time)
        (
            # Second with UTC
            "2013-01-01T12:30:45Z",
            (
                datetime(2013, 1, 1, 12, 30, 45, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 12, 30, 46, tzinfo=pytz.utc),
            ),
        ),
        (
            # Second with tz conversion
            "2013-01-01T12:30:45+02:00",
            (
                datetime(2013, 1, 1, 10, 30, 45, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 10, 30, 46, tzinfo=pytz.utc),
            ),
        ),
        (
            # Second with implicit UTC
            "2013-01-01T12:30:45",
            (
                datetime(2013, 1, 1, 12, 30, 45, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 12, 30, 46, tzinfo=pytz.utc),
            ),
        ),
        (
            # Minute with UTC
            "2013-01-01T12:30+00:00",
            (
                datetime(2013, 1, 1, 12, 30, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 12, 31, tzinfo=pytz.utc),
            ),
        ),
        (
            # Minute with conversion
            "2013-01-01T12:30+04:00",
            (
                datetime(2013, 1, 1, 8, 30, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 8, 31, tzinfo=pytz.utc),
            ),
        ),
        (
            # Minute with implicit UTC
            "2013-01-01T12:30",
            (
                datetime(2013, 1, 1, 12, 30, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 12, 31, tzinfo=pytz.utc),
            ),
        ),
        (
            # Hour, explicit UTC
            "2013-01-01T12Z",
            (
                datetime(2013, 1, 1, 12, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 13, tzinfo=pytz.utc),
            ),
        ),
        (
            # Hour with offset
            "2013-01-01T12-07:00",
            (
                datetime(2013, 1, 1, 19, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 20, tzinfo=pytz.utc),
            ),
        ),
        (
            # Hour with implicit UTC
            "2013-01-01T12",
            (
                datetime(2013, 1, 1, 12, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 13, tzinfo=pytz.utc),
            ),
        ),
        (
            # Interval with trailing zero fractional seconds should
            # be accepted.
            "2013-01-01T12:00:00.0/2013-01-01T12:30:00.000000",
            (
                datetime(2013, 1, 1, 12, tzinfo=pytz.utc),
                datetime(2013, 1, 1, 12, 30, tzinfo=pytz.utc),
            ),
        ),
    ]

    for value, expected in intervals:
        assert inputs.iso8601interval(value) == expected


def test_invalid_isointerval_error():
    with pytest.raises(ValueError) as error:
        inputs.iso8601interval('2013-01-01/blah')
    assert str(error.value) == "Invalid argument: 2013-01-01/blah. " \
                               "argument must be a valid ISO8601 date/time interval."


@pytest.mark.parametrize('interval', [
    '2013-01T14:',
    '',
    'asdf',
    '01/01/2013',
])
def test_bad_isointervals(interval):
    with pytest.raises(Exception):
        inputs.iso8601interval(interval)


if __name__ == '__main__':
    unittest.main()
