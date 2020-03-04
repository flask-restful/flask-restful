.. _intermediate:

Intermediate Usage
==================

.. currentmodule:: flask_restful

This page covers building a slightly more complex Flask-RESTful app that will
cover out some best practices when setting up a real-world Flask-RESTful-based
API. The :ref:`quickstart` section is great for getting started with your first
Flask-RESTful app, so if you're new to Flask-RESTful you'd be better off
checking that out first.


Project Structure
-----------------

There are many different ways to organize your Flask-RESTful app, but here
we'll describe one that scales pretty well with larger apps and maintains
a nice level organization.

The basic idea is to split your app into three main parts: the routes, the
resources, and any common infrastructure.

Here's an example directory structure: ::

    myapi/
        __init__.py
        app.py          # this file contains your app and routes
        resources/
            __init__.py
            foo.py      # contains logic for /Foo
            bar.py      # contains logic for /Bar
        common/
            __init__.py
            util.py     # just some common infrastructure

The common directory would probably just contain a set of helper functions
to fulfill common needs across your application. It could also contain, for
example, any custom input/output types your resources need to get the job done.

In the resource files, you just have your resource objects. So here's what
``foo.py`` might look like: ::

    from flask_restful import Resource

    class Foo(Resource):
        def get(self):
            pass
        def post(self):
            pass

The key to this setup lies in ``app.py``: ::

    from flask import Flask
    from flask_restful import Api
    from myapi.resources.foo import Foo
    from myapi.resources.bar import Bar
    from myapi.resources.baz import Baz

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Foo, '/Foo', '/Foo/<string:id>')
    api.add_resource(Bar, '/Bar', '/Bar/<string:id>')
    api.add_resource(Baz, '/Baz', '/Baz/<string:id>')

As you can imagine with a particularly large or complex API, this file ends up
being very valuable as a comprehensive list of all the routes and resources in
your API. You would also use this file to set up any config values
(:meth:`~flask.Flask.before_request`, :meth:`~flask.Flask.after_request`).
Basically, this file configures your entire API.

The things in the common directory are just things you'd want to support your
resource modules.

Use With Blueprints
-------------------

See :ref:`blueprints` in the Flask documentation for what blueprints are and
why you should use them. Here's an example of how to link an :class:`Api`
up to a :class:`~flask.Blueprint`. ::

    from flask import Flask, Blueprint
    from flask_restful import Api, Resource, url_for

    app = Flask(__name__)
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)

    class TodoItem(Resource):
        def get(self, id):
            return {'task': 'Say "Hello, World!"'}

    api.add_resource(TodoItem, '/todos/<int:id>')
    app.register_blueprint(api_bp)

.. note ::

    Calling :meth:`Api.init_app` is not required here because registering the
    blueprint with the app takes care of setting up the routing for the
    application.

Full Parameter Parsing Example
------------------------------

Elsewhere in the documentation, we've described how to use the reqparse example
in detail. Here we'll set up a resource with multiple input parameters that
exercise a larger amount of options. We'll define a resource named "User". ::

    from flask_restful import fields, marshal_with, reqparse, Resource

    def email(email_str):
        """Return email_str if valid, raise an exception in other case."""
        if valid_email(email_str):
            return email_str
        else:
            raise ValueError('{} is not a valid email'.format(email_str))

    post_parser = reqparse.RequestParser()
    post_parser.add_argument(
        'username', dest='username',
        location='form', required=True,
        help='The user\'s username',
    )
    post_parser.add_argument(
        'email', dest='email',
        type=email, location='form',
        required=True, help='The user\'s email',
    )
    post_parser.add_argument(
        'user_priority', dest='user_priority',
        type=int, location='form',
        default=1, choices=range(5), help='The user\'s priority',
    )

    user_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'email': fields.String,
        'user_priority': fields.Integer,
        'custom_greeting': fields.FormattedString('Hey there {username}!'),
        'date_created': fields.DateTime,
        'date_updated': fields.DateTime,
        'links': fields.Nested({
            'friends': fields.Url('user_friends'),
            'posts': fields.Url('user_posts'),
        }),
    }

    class User(Resource):

        @marshal_with(user_fields)
        def post(self):
            args = post_parser.parse_args()
            user = create_user(args.username, args.email, args.user_priority)
            return user

        @marshal_with(user_fields)
        def get(self, id):
            args = post_parser.parse_args()
            user = fetch_user(id)
            return user

As you can see, we create a ``post_parser`` specifically to handle the parsing
of arguments provided on POST. Let's step through the definition of each
argument. ::

    post_parser.add_argument(
        'username', dest='username',
        location='form', required=True,
        help='The user\'s username',
    )

The ``username`` field is the most normal out of all of them. It takes
a string from the POST body and converts it to a string type. This argument
is required (``required=True``), which means that if it isn't provided,
Flask-RESTful will automatically return a 400 with a message along the lines
of 'the username field is required'. ::

    post_parser.add_argument(
        'email', dest='email',
        type=email, location='form',
        required=True, help='The user\'s email',
    )

The ``email`` field has a custom type of ``email``. A few lines earlier we
defined an ``email`` function that takes a string and returns it if the type is
valid, else it raises an exception, exclaiming that the email type was
invalid. ::

    post_parser.add_argument(
        'user_priority', dest='user_priority',
        type=int, location='form',
        default=1, choices=range(5), help='The user\'s priority',
    )

The ``user_priority`` type takes advantage of the ``choices`` argument. This
means that if the provided `user_priority` value doesn't fall in the range
specified by the ``choices`` argument (in this case ``[0, 1, 2, 3, 4]``),
Flask-RESTful will automatically respond with a 400 and a descriptive error
message.

That covers the inputs. We also defined some interesting field types in the
``user_fields`` dictionary to showcase a couple of the more exotic types.  ::

    user_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'email': fields.String,
        'user_priority': fields.Integer,
        'custom_greeting': fields.FormattedString('Hey there {username}!'),
        'date_created': fields.DateTime,
        'date_updated': fields.DateTime,
        'links': fields.Nested({
            'friends': fields.Url('user_friends', absolute=True),
            'posts': fields.Url('user_posts', absolute=True),
        }),
    }

First up, there's :class:`fields.FormattedString`. ::

    'custom_greeting': fields.FormattedString('Hey there {username}!'),

This field is primarily used to interpolate values from the response into
other values. In this instance, ``custom_greeting`` will always contain the
value returned from the ``username`` field.

Next up, check out :class:`fields.Nested`. ::

    'links': fields.Nested({
        'friends': fields.Url('user_friends', absolute=True),
        'posts': fields.Url('user_posts', absolute=True),
    }),

This field is used to create a sub-object in the response. In this case,
we want to create a ``links`` sub-object to contain urls of related objects.
Note that we passed `fields.Nested` another dict which is built in such a
way that it would be an acceptable argument to :func:`marshal` by itself.

Finally, we used the :class:`fields.Url` field type. ::

        'friends': fields.Url('user_friends', absolute=True),
        'posts': fields.Url('user_posts', absolute=True),

It takes as its first parameter the name of the endpoint associated with the
urls of the objects in the ``links`` sub-object.  Passing ``absolute=True``
ensures that the generated urls will have the hostname included.


Passing Constructor Parameters Into Resources
---------------------------------------------
Your :class:`Resource` implementation may require outside dependencies. Those
dependencies are best passed-in through the constructor to loosely couple each
other. The :meth:`Api.add_resource` method has two keyword arguments:
``resource_class_args`` and ``resource_class_kwargs``. Their values will be forwarded
and passed into your Resource implementation's constructor.

So you could have a :class:`Resource`: ::

    from flask_restful import Resource

    class TodoNext(Resource):
        def __init__(self, **kwargs):
            # smart_engine is a black box dependency
            self.smart_engine = kwargs['smart_engine']

        def get(self):
            return self.smart_engine.next_todo()

You can inject the required dependency into TodoNext like so: ::

    smart_engine = SmartEngine()

    api.add_resource(TodoNext, '/next',
        resource_class_kwargs={ 'smart_engine': smart_engine })

Same idea applies for forwarding `args`.
