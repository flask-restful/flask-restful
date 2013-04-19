.. _reqparse:

Request Parsing
===============

.. currentmodule:: flask.ext.restful

Flask-RESTful's request parsing interface is modeled after the ``argparse``
interface.  It's designed to provide simple and uniform access to any
variable on the :py:class:`flask.request` object in Flask.


Basic Arguments
---------------

Here's a simple example of the request parser. It looks for two arguments in
the :py:attr:`flask.Request.values` dict. One of type ``int``, and the other of
type ``str`` ::

    from flask.ext.restful import reqparse
    
    parser = reqparse.RequestParser()
    parser.add_argument('rate', type=int, help='Rate cannot be converted')
    parser.add_argument('name', type=str)
    args = parser.parse_args()

If you specify the help value, it will be rendered as the error message
when a type error is raised while parsing it.  If you do not
specify a help message, the default behavior is to return the message from the
type error itself.

By default, arguments are **not** required.  Also, arguments supplied in the
request that are not part of the RequestParser will be ignored.

Also note: Arguments declared in your request parser but not set in
the request itself will default to ``None``.


Required Arguments
------------------

To require a value be passed for an argument, just add ``required=True`` to
the call to :py:meth:`~reqparse.RequestParser.add_argument`. ::

    parser.add_argument('name', type=str, required=True, 
    help="Name cannot be blank!")

Multiple Values & Lists
-----------------------

If you want to accept multiple values for a key as a list, you can pass
``action='append'`` ::

    parser.add_argument('name', type=str, action='append')

This will let you make queries like ::

    curl http://api.example.com -d "Name=bob" -d "Name=sue" -d "Name=joe"

And your args will look like this ::

    args = parser.parse_args()
    args['name']    # ['bob', 'sue', 'joe']

Other Destinations
------------------

If for some reason you'd like your argument stored under a different name once
it's parsed, you can use the ``dest`` kwarg. ::

    parser.add_argument('name', type=str, dest='public_name')

    args = parser.parse_args()
    args['public_name']   


Other Locations
---------------

By default, the :py:class:`~reqparse.RequestParser` tries to parse values
from :py:attr:`flask.Request.values`. This dict will contain both querystring
arguments and POST/PUT body arguments.

:py:meth:`~reqparse.RequestParser.add_argument` lets you specify
alternate locations to pull the values from. Any variable on the
:py:class:`flask.Request` can be used. For example: ::

    # Look only in the POST body
    parser.add_argument('name', type=int, location='form')

    # Look only in the querystring
    parser.add_argument('PageSize', type=int, location='args')

    # From the request headers
    parser.add_argument('User-Agent', type=str, location='headers')

    # From http cookies
    parser.add_argument('session_id', type=str, location='cookies')

    # From file uploads
    parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')

