.. _quickstart:

Quickstart
==========

.. currentmodule:: flask_restful

It's time to write your first REST API. This guide assumes you have a working
understanding of `Flask <http://flask.pocoo.org>`_, and that you have already
installed both Flask and Flask-RESTful.  If not, then follow the steps in the
:ref:`installation` section.

A Minimal API
-------------

A minimal Flask-RESTful API looks like this: ::

    from flask import Flask
    from flask_restful import Resource, Api

    app = Flask(__name__)
    api = Api(app)

    class HelloWorld(Resource):
        def get(self):
            return {'hello': 'world'}

    api.add_resource(HelloWorld, '/')

    if __name__ == '__main__':
        app.run(debug=True)

Save this as api.py and run it using your Python interpreter. Note that we've
enabled `Flask debugging <http://flask.pocoo.org/docs/quickstart/#debug-mode>`_
mode to provide code reloading and better error messages. ::

    $ python api.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

.. warning::

    Debug mode should never be used in a production environment!

Now open up a new prompt to test out your API using curl ::

    $ curl http://127.0.0.1:5000/
    {"hello": "world"}

Resourceful Routing
-------------------
The main building block provided by Flask-RESTful are resources. Resources are
built on top of `Flask pluggable views <http://flask.pocoo.org/docs/views/>`_,
giving you easy access to multiple HTTP methods just by defining methods on
your resource. A basic CRUD resource for a todo application (of course) looks
like this: ::

    from flask import Flask, request
    from flask_restful import Resource, Api

    app = Flask(__name__)
    api = Api(app)

    todos = {}

    class TodoSimple(Resource):
        def get(self, todo_id):
            return {todo_id: todos[todo_id]}

        def put(self, todo_id):
            todos[todo_id] = request.form['data']
            return {todo_id: todos[todo_id]}

    api.add_resource(TodoSimple, '/<string:todo_id>')

    if __name__ == '__main__':
        app.run(debug=True)

You can try it like this: ::

    $ curl http://localhost:5000/todo1 -d "data=Remember the milk" -X PUT
    {"todo1": "Remember the milk"}
    $ curl http://localhost:5000/todo1
    {"todo1": "Remember the milk"}
    $ curl http://localhost:5000/todo2 -d "data=Change my brakepads" -X PUT
    {"todo2": "Change my brakepads"}
    $ curl http://localhost:5000/todo2
    {"todo2": "Change my brakepads"}


Or from python if you have the ``requests`` library installed::

     >>> from requests import put, get
     >>> put('http://localhost:5000/todo1', data={'data': 'Remember the milk'}).json()
     {u'todo1': u'Remember the milk'}
     >>> get('http://localhost:5000/todo1').json()
     {u'todo1': u'Remember the milk'}
     >>> put('http://localhost:5000/todo2', data={'data': 'Change my brakepads'}).json()
     {u'todo2': u'Change my brakepads'}
     >>> get('http://localhost:5000/todo2').json()
     {u'todo2': u'Change my brakepads'}

Flask-RESTful understands multiple kinds of return values from view methods.
Similar to Flask, you can return any iterable and it will be converted into a
response, including raw Flask response objects. Flask-RESTful also support
setting the response code and response headers using multiple return values,
as shown below: ::

    class Todo1(Resource):
        def get(self):
            # Default to 200 OK
            return {'task': 'Hello world'}

    class Todo2(Resource):
        def get(self):
            # Set the response code to 201
            return {'task': 'Hello world'}, 201

    class Todo3(Resource):
        def get(self):
            # Set the response code to 201 and return custom headers
            return {'task': 'Hello world'}, 201, {'Etag': 'some-opaque-string'}


Endpoints
---------

Many times in an API, your resource will have multiple URLs. You can pass
multiple URLs to the :meth:`~Api.add_resource` method on the `Api` object.
Each one will be routed to your :class:`Resource` ::

    api.add_resource(HelloWorld,
        '/',
        '/hello')

You can also match parts of the path as variables to your resource methods. ::

    api.add_resource(Todo,
        '/todo/<int:todo_id>', endpoint='todo_ep')


Argument Parsing
----------------

While Flask provides easy access to request data (i.e. querystring or POST
form encoded data), it's still a pain to validate form data. Flask-RESTful
has built-in support for request data validation using a library similar to
`argparse <http://docs.python.org/dev/library/argparse.html>`_. ::

    from flask_restful import reqparse

    parser = reqparse.RequestParser()
    parser.add_argument('rate', type=int, help='Rate to charge for this resource')
    args = parser.parse_args()

.. note ::

    Unlike the argparse module, :meth:`reqparse.RequestParser.parse_args`
    returns a Python dictionary instead of a custom data structure.

Using the :class:`reqparse` module also gives you sane error messages for
free. If an argument fails to pass validation, Flask-RESTful will respond with
a 400 Bad Request and a response highlighting the error. ::

    $ curl -d 'rate=foo' http://127.0.0.1:5000/todos
    {'status': 400, 'message': 'foo cannot be converted to int'}


The :class:`inputs` module provides a number of included common conversion
functions such as :meth:`inputs.date` and :meth:`inputs.url`.

Calling ``parse_args`` with ``strict=True`` ensures that an error is thrown if
the request includes arguments your parser does not define. ::

    args = parser.parse_args(strict=True)

Data Formatting
---------------

By default, all fields in your return iterable will be rendered as-is. While
this works great when you're just dealing with Python data structures,
it can become very frustrating when working with objects. To solve this
problem, Flask-RESTful provides the :class:`fields` module and the
:meth:`marshal_with` decorator. Similar to the Django ORM and WTForm, you
use the ``fields`` module to describe the structure of your response. ::

    from flask_restful import fields, marshal_with

    resource_fields = {
        'task':   fields.String,
        'uri':    fields.Url('todo_ep')
    }

    class TodoDao(object):
        def __init__(self, todo_id, task):
            self.todo_id = todo_id
            self.task = task

            # This field will not be sent in the response
            self.status = 'active'

    class Todo(Resource):
        @marshal_with(resource_fields)
        def get(self, **kwargs):
            return TodoDao(todo_id='my_todo', task='Remember the milk')

The above example takes a python object and prepares it to be serialized. The
:meth:`marshal_with` decorator will apply the transformation described by
``resource_fields``. The only field extracted from the object is ``task``. The
:class:`fields.Url` field is a special field that takes an endpoint name
and generates a URL for that endpoint in the response. Many of the field types
you need are already included. See the :class:`fields` guide for a complete
list.

Full Example
------------

Save this example in api.py ::

    from flask import Flask
    from flask_restful import reqparse, abort, Api, Resource

    app = Flask(__name__)
    api = Api(app)

    TODOS = {
        'todo1': {'task': 'build an API'},
        'todo2': {'task': '?????'},
        'todo3': {'task': 'profit!'},
    }


    def abort_if_todo_doesnt_exist(todo_id):
        if todo_id not in TODOS:
            abort(404, message="Todo {} doesn't exist".format(todo_id))

    parser = reqparse.RequestParser()
    parser.add_argument('task')


    # Todo
    # shows a single todo item and lets you delete a todo item
    class Todo(Resource):
        def get(self, todo_id):
            abort_if_todo_doesnt_exist(todo_id)
            return TODOS[todo_id]

        def delete(self, todo_id):
            abort_if_todo_doesnt_exist(todo_id)
            del TODOS[todo_id]
            return '', 204

        def put(self, todo_id):
            args = parser.parse_args()
            task = {'task': args['task']}
            TODOS[todo_id] = task
            return task, 201


    # TodoList
    # shows a list of all todos, and lets you POST to add new tasks
    class TodoList(Resource):
        def get(self):
            return TODOS

        def post(self):
            args = parser.parse_args()
            todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
            todo_id = 'todo%i' % todo_id
            TODOS[todo_id] = {'task': args['task']}
            return TODOS[todo_id], 201

    ##
    ## Actually setup the Api resource routing here
    ##
    api.add_resource(TodoList, '/todos')
    api.add_resource(Todo, '/todos/<todo_id>')


    if __name__ == '__main__':
        app.run(debug=True)


Example usage ::

    $ python api.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

GET the list ::

    $ curl http://localhost:5000/todos
    {"todo1": {"task": "build an API"}, "todo3": {"task": "profit!"}, "todo2": {"task": "?????"}}

GET a single task ::

    $ curl http://localhost:5000/todos/todo3
    {"task": "profit!"}

DELETE a task ::

    $ curl http://localhost:5000/todos/todo2 -X DELETE -v

    > DELETE /todos/todo2 HTTP/1.1
    > User-Agent: curl/7.19.7 (universal-apple-darwin10.0) libcurl/7.19.7 OpenSSL/0.9.8l zlib/1.2.3
    > Host: localhost:5000
    > Accept: */*
    >
    * HTTP 1.0, assume close after body
    < HTTP/1.0 204 NO CONTENT
    < Content-Type: application/json
    < Content-Length: 0
    < Server: Werkzeug/0.8.3 Python/2.7.2
    < Date: Mon, 01 Oct 2012 22:10:32 GMT

Add a new task ::

    $ curl http://localhost:5000/todos -d "task=something new" -X POST -v

    > POST /todos HTTP/1.1
    > User-Agent: curl/7.19.7 (universal-apple-darwin10.0) libcurl/7.19.7 OpenSSL/0.9.8l zlib/1.2.3
    > Host: localhost:5000
    > Accept: */*
    > Content-Length: 18
    > Content-Type: application/x-www-form-urlencoded
    >
    * HTTP 1.0, assume close after body
    < HTTP/1.0 201 CREATED
    < Content-Type: application/json
    < Content-Length: 25
    < Server: Werkzeug/0.8.3 Python/2.7.2
    < Date: Mon, 01 Oct 2012 22:12:58 GMT
    <
    * Closing connection #0
    {"task": "something new"}

Update a task ::

    $ curl http://localhost:5000/todos/todo3 -d "task=something different" -X PUT -v

    > PUT /todos/todo3 HTTP/1.1
    > Host: localhost:5000
    > Accept: */*
    > Content-Length: 20
    > Content-Type: application/x-www-form-urlencoded
    >
    * HTTP 1.0, assume close after body
    < HTTP/1.0 201 CREATED
    < Content-Type: application/json
    < Content-Length: 27
    < Server: Werkzeug/0.8.3 Python/2.7.3
    < Date: Mon, 01 Oct 2012 22:13:00 GMT
    <
    * Closing connection #0
    {"task": "something different"}

