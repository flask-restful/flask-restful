.. _intermediate:

Intermediate Usage
==================

.. currentmodule:: flask.ext.restful

This page covers building a slightly more complex Flask-RESTful app
that will cover out some best practices when setting up a real-world
Flask-RESTful-based API. The :ref:`quickstart` section is great for
getting started with your first Flask-RESTful app, so if you're new
to Flask-RESTful you'd be better off checking that out first. 


Project Structure
-----------------

There are many different ways to organize your Flask-RESTful app, but here 
we'll describe one that scales pretty well with larger apps and maintains
a nice level organization.

The basic idea is to split your app into three main parts. The routes, the
resources, and any common infrastructure.

Here's an example directory structure: ::

    myapi/
        __init__.py
        app.py          # this file contains your app and routes
        resources/
            foo.py      # contains logic for /Foo
            bar.py      # contains logic for /Bar
        common/
            util.py     # just some common infrastructure

The common directory would probably just contain a set of helper functions
to fulfill common needs across your application. It could also contain, for
example, any custom input/output types your resources need to get the job done.

In the resource files, you just have your resource objects. So here's
what foo.py might look like: ::

    from flask.ext import restful

    class Foo(restful.Resource):
        def get(self):
            pass
        def post(self):
            pass

The key to this setup lies in app.py: ::

    from flask import Flask
    from flask.ext import restful
    from myapi.resources.foo import Foo
    from myapi.resources.bar import Bar
    from myapi.resources.baz import Baz

    app = Flask(__name__)
    api = restful.Api(app)
    
    api.add_resource(Foo, '/Foo', '/Foo/<str:id>')
    api.add_resource(Bar, '/Bar', '/Bar/<str:id>')
    api.add_resource(Baz, '/Baz', '/Baz/<str:id>') 

As you can imagine with a particularly large or complex API, this file
ends up being very valuable as a comprehensive list of all the routes
and resources in your API. You would also use this file to set up any
config values (before_request, after_request). Basically, this file
configures your entire API.

The things in the common directory are just things you'd want to support
your resource modules.

Full Parameter Parsing Example
------------------------------

Elsewhere in the documentation, we've described how to use the reqparse example
in detail. Here we'll set up a resource with multiple input parameters that
exercise a larger amount of options. We'll define a resource named "User". ::

    from flask.ext import restful
    from flask.ext.restful import fields, marshal_with, reqparse

    def email(email_str):
        """ return True if email_str is a valid email """
        if valid_email(email):
            return True
        else:
            raise ValidationError("{} is not a valid email")

    post_parser = reqparse.ArgumentParser()
    post_parser.add_argument(
        'username', dest='username',
        type=str, location='form',
        required=True, help='The user\'s username',
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
            'friends': fields.Url('/Users/{id}/Friends'),
            'posts': fields.Url('Users/{id}/Posts'),
        }),
    }

    class User(restful.Resource):

        @marshal_with(user_fields)
        def post(self):
            args = post_parser.parse_args()
            user = create_user(args.username, args.email, args.user_priority)
            return user

        @marshal_with(user_fields)
        def get(self, id):
            args = get_parser.parse_args()
            user = fetch_user(id)
            return user

As you can see, we create a `post_parser` specifically to handle parsing
the arguments provided on POST. Let's step through the definition of each
argument. ::

    post_parser.add_argument(
        'username', dest='username',
        type=str, location='form',
        required=True, help='The user\'s username',
    )

The `username` field is the most normal out of all of them. It takes
a string from the POST body and converts it to a string type. This argument
is required (`required=True`), which means that if it isn't provided,
Flask-RESTful will automatically return a 400 with a message along the lines
of 'the username field is required'. ::

    post_parser.add_argument(
        'email', dest='email',
        type=email, location='form',
        required=True, help='The user\'s email',
    )

The `email` field has a custom type of `email`. A few lines earlier we
defined an `email` function that takes a string and returns True if the
type is valid, else it raises a `ValidationError` exclaiming that the
email type was invalid. ::

    post_parser.add_argument(
        'user_priority', dest='user_priority',
        type=int, location='form',
        default=1, choices=range(5), help='The user\'s priority',
    )

The `user_priority` type takes advantage of the `choices` argument. This
means that if the provided `user_priority` value doesn't fall in the range
specified by the `choices` argument (in this case [1, 2, 3, 4]) Flask-RESTful
will automatically respond with a 400 and a descriptive error message.

That covers the inputs. We also defined some interesting field types in the
`user_fields` dictionary to show showcase a couple of the more exotic types.  ::

    user_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'email': fields.String,
        'user_priority': fields.Integer,
        'custom_greeting': fields.FormattedString('Hey there {username}!'),
        'date_created': fields.DateTime,
        'date_updated': fields.DateTime,
        'links': fields.Nested({
            'friends': fields.Url('/Users/{id}/Friends', absolute=True),
            'posts': fields.Url('Users/{id}/Posts', absolute=True),
        }),
    }

First up, there's `fields.FormattedString`. ::

    'custom_greeting': fields.FormattedString('Hey there {username}!'),

This field is primarily used to interpolate values from the response into
other values. In this instance, `custom_greeting` will always contain the
value returned from the `username` field.

Next up, check out `fields.Nested`. ::

    'links': fields.Nested({
        'friends': fields.Url('/Users/{id}/Friends', absolute=True),
        'posts': fields.Url('Users/{id}/Posts', absolute=True),
    }),

This field is used to create a sub-object in the response. In this case,
we want to create a `links` sub-object to contain urls of related objects.
Note that we passed `fields.Nested` another dict which is built in such a
way that it would be an acceptable argument to `marshal` by itself.

Finally, we used the `fields.Url` field type. ::

        'friends': fields.Url('/Users/{id}/Friends', absolute=True),
        'posts': fields.Url('Users/{id}/Posts', absolute=True),

It takes a string that can be formatted in the same manner as `fields.FormattedString`
which we covered above.  Passing `absolute=True` ensures that the generated Urls
will have the hostname included.
