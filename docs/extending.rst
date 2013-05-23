.. _extending:

Extending Flask-RESTful
=======================

.. currentmodule:: flask.ext.restful


We realize that everyone has different needs in a REST framework.
Flask-RESTful tries to be as flexible as possible, but sometimes you might
find that the builtin functionality is not enough to meet your needs.
Flask-RESTful has a few different extension points that can help in that case.

Content Negotiation
-------------------

Out of the box, Flask-RESTful is only configured to support JSON. We made this
decision to give API maintainers full control of over API format support, so a
year down the road you don’t have to support people using the CSV
representation of your API you didn’t even know existed. To add additional
mediatypes to your api, you’ll need to declare your supported representations
on the :class:`~Api` object. ::

    app = Flask(__name__)
    api = restful.Api(app)

    @api.representation('application/json')
    def json(data, code, headers):
        resp = make_response(json.dumps(data), code)
        resp.headers.extend(headers)
        return resp

These representation functions must return a Flask :class:`~flask.Response`
object.


Custom Fields & Inputs
----------------------

One of the most common additions to Flask-RESTful is to define custom types or
fields based on the data your own data types.  

Fields
~~~~~~

Custom output fields let you perform your own output formatting without having
to modify your internal objects directly. All you have to do is subclass
:class:`~fields.Raw` and implement the :meth:`~fields.Raw.format` method::

    class AllCapsString(fields.Raw):
        def format(self, value):
            return value.upper()
    

    # example usage
    fields = {
        'name': fields.String,
        'all_caps_name': AllCapsString(attribute=name),
    }

Inputs
~~~~~~

For parsing arguments, you might want to perform custom validation.  Creating
your own input type lets you extend request parsing with ease.  ::

    def odd_number(value):
        if value % 2 == 0:
            raise ValueError("Value is not odd")

        return value

The request parser will also give you access to the name of the argument for cases where you want to reference the name in the error message ::

    def odd_number(value, name):
        if value % 2 == 0:
            raise ValueError("The parameter '{}' is not odd. You gave us the value: {}".format(name, value))

        return value

You can also convert public parameter values to internal representations ::

    # maps the strings to their internal integer representation
    # 'init' => 0
    # 'in-progress' => 1
    # 'completed' => 2

    def task_status(value):
        statuses = [u"init", u"in-progress", u"completed"]
        return statuses.index(value)


Then you can use these custom types in your RequestParser ::

    parser = reqparse.RequestParser()
    parser.add_argument('OddNumber', type=odd_number)
    parser.add_argument('Status', type=task_status)
    args = parser.parse_args()


Response Formats
----------------

To support other representations (like xml, csv, html) you can use the
:meth:`~Api.representation` decorator.  You need to have a reference to your api ::

    api = restful.Api(app)

    @api.representation('text/csv')
    def output_csv(data, code, headers=None):
        pass
        # implement csv output!

These output functions take three parameters, ``data``, ``code``, and
``headers``

``data`` is the object you return from your resource method, code is the HTTP
status code that it expects, and headers are any HTTP headers to set in the
response.  Your output function should return a Flask response object. ::

    def output_json(data, code, headers=None):
        """Makes a Flask response with a JSON encoded body"""
        resp = make_response(json.dumps(data), code)
        resp.headers.extend(headers or {})

        return resp

Another way to accomplish this is to subclass the :class:`~Api` class and
provide your own output functions. ::

    class Api(restful.Api):
        representations = {
            'application/xml': output_xml,
            'text/html': output_html,
            'text/csv': output_csv,
            'application/json': output_json,
        }

Resource Method Decorators
--------------------------

There is a property on the :meth:`~flask.ext.restful.Resource` called
method_decorators.  You can subclass the Resource and add your own decorators
that will be added to all ``method`` functions in resource.  For instance, if
you want to build custom authentication into every request ::

    def authenticate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not getattr(func, 'authenticated', True):
                return func(*args, **kwargs)
            
            acct = basic_authentication()  # custom account lookup function

            if acct:
                return func(*args, **kwargs)

            restful.abort(401)
        return wrapper


    class Resource(restful.Resource):
        method_decorators = [authenticate]   # applies to all inherited resources 

Since Flask-RESTful Resources are actually Flask view objects, you can also
use standard `flask view decorators <http://flask.pocoo.org/docs/views/#decorating-views>`_.

Custom Error Handlers
---------------------

Error handling is a tricky problem. Your Flask application may be wearing
multiple hats, yet you want to handle all Flask-RESTful errors with the correct
content type and error syntax as your 200-level requests.

Flask-RESTful will call the :meth:`~flask.ext.restful.Api.handle_error`
function on any 400 or 500 error that happens on a Flask-RESTful route, and
leave other routes alone. You may want your app to return an error message with
the correct media type on 404 Not Found errors; in which case, use the
`catch_all_404s` parameter of the :class:`~flask.ext.restful.Api` constructor ::

    app = Flask(__name__)
    api = flask_restful.Api(app, catch_all_404s=True)

Then Flask-RESTful will handle 404s in addition to errors on its own routes.

Sometimes you want to do something special when an error occurs - log to a
file, send an email, etc. Use the :meth:`~flask.got_request_exception` method
to attach custom error handlers to an exception. ::

    def log_exception(sender, exception, **extra):
        """ Log an exception to our logging framework """
        sender.logger.debug('Got exception during processing: %s', exception)

    from flask import got_request_exception
    got_request_exception.connect(log_exception, app)

