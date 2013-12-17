from datetime import datetime
from email.utils import formatdate
import re

# https://code.djangoproject.com/browser/django/trunk/django/core/validators.py
# basic auth added by frank
from calendar import timegm

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:[^:@]+?:[^:@]*?@|)'  # basic auth
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def url(value):
    """Validate a URL.

    :param string value: The URL to validate
    :returns: The URL if valid.
    :raises: ValueError
    """
    if not regex.search(value):
        message = u"{0} is not a valid URL".format(value)
        if regex.search('http://' + value):
            message += u". Did you mean: http://{0}".format(value)
        raise ValueError(message)
    return value


def date(value):
    """Parse a valid looking date in the format YYYY-mm-dd"""
    date = datetime.strptime(value, "%Y-%m-%d")
    if date.year < 1900:
        raise ValueError(u"Year must be >= 1900")
    return date


def _get_integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError('{} is not a valid integer'.format(value))


def natural(value, argument='argument'):
    """ Restrict input type to the natural numbers (0, 1, 2, 3...) """
    value = _get_integer(value)
    if value < 0:
        error = ('Invalid {arg}: {value}. {arg} must be a non-negative '
                 'integer'.format(arg=argument, value=value))
        raise ValueError(error)
    return value


def positive(value, argument='argument'):
    """ Restrict input type to the positive integers (1, 2, 3...) """
    value = _get_integer(value)
    if value < 1:
        error = ('Invalid {arg}: {value}. {arg} must be a positive '
                 'integer'.format(arg=argument, value=value))
        raise ValueError(error)
    return value


def boolean(value):
    """Parse the string "true" or "false" as a boolean (case insensitive)"""
    value = value.lower()
    if value == 'true':
        return True
    if value == 'false':
        return False
    raise ValueError("Invalid literal for boolean(): {}".format(value))


def rfc822(dt):
    return formatdate(timegm(dt.utctimetuple()))
