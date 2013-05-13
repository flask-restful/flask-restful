.. _quickstart:

Quickstart
==========

.. currentmodule:: flask.ext.restful

It’s time to write your first REST API. This guide assumes you have `Flask
<http://flask.pocoo.org>`_ and Flask-RESTful installed and a working
understanding of Flask. If not, follow the steps in the Installation section,
or read through the Flask Quickstart.



A Minimal API
-------------

A minimal Flask-RESTful API looks like this: ::

    from flask.ext import restful

    class HelloWorld(restful.LinkedResource):
        _self = '/'

        @Verb(output_fields=output(Some_output=String)) # outputs a string
        def get(self):
            return output(Some_output="Hello User")

    api.add_root(HelloWorld)

    if __name__ == '__main__':
        app.run(debug=True)


Save this as api.py and run it using your Python interpreter. Note that we’ve enabled `Flask debugging <http://flask.pocoo.org/docs/quickstart/#debug-mode>`_ mode to provide code reloading and better error messages. Debug mode should never be used in a production environment. ::

    $ python api.py
     * Running on http://127.0.0.1:5000/


Now open up a new prompt to test out your API using curl ::

    $ curl http://127.0.0.1:5000/
    {"Hello User"}

Or you can use the embedded API explorer ::

Simply point your browser to http://127.0.0.1:5000/


Routing and Argument Parsing
----------------------------

Setting up the url pattern on which your resouce will be listen on is set by the _self class attribute. You need to use a flask standard pattern.
The parameters will be passed to the kwargs of your verb.

    from flask import Flask, request
    from flask.ext.restful import LinkedResource, Api

    app = Flask(__name__)
    api = Api(app)

    todos = {}

    class TodoSimple(LinkedResource):
        _self = '/<string:todo_id>'

        @Verb(output_fields=output(todo_id=String))
        def get(self, todo_id):
            return {todo_id: todos[todo_id]}

        @Verb(output_fields=output(todo_id=String))
        def put(self, todo_id):
            todos[todo_id] = request.form['data']
            return {todo_id: todos[todo_id]}

    api.add_root(TodoSimple)

    if __name__ == '__main__':
        app.run(debug=True)

You can try it like this: ::

    You can try this example as follow:
        $ curl http://localhost:5000/todo1 -d "data=Remember the milk" -X PUT
        {"todo1": "Remember the milk"}
        $ curl http://localhost:5000/todo1
        {"todo1": "Remember the milk"}
        $ curl http://localhost:5000/todo2 -d "data=Change my breakpads" -X PUT
        {"todo2": "Change my breakpads"}
        $ curl http://localhost:5000/todo2
        {"todo2": "Change my breakpads"}

    Or from python if you have the requests library installed:
     >>> from requests import put, get
     >>> put('http://localhost:5000/todo1', data={'data': 'Remember the milk'}).json
     {u'todo1': u'Remember the milk'}
     >>> get('http://localhost:5000/todo1').json
     {u'todo1': u'Remember the milk'}
     >>> put('http://localhost:5000/todo2', data={'data': 'Change my breakpads'}).json
     {u'todo2': u'Change my breakpads'}
     >>> get('http://localhost:5000/todo2').json
     {u'todo2': u'Change my breakpads'}

Flask-RESTful understands multiple kinds of return values from view methods.
Similar to Flask, you can return any iterable and it will be converted into a
response, including raw Flask response objects. Flask-RESTful also support
setting the response code and response headers using multiple return values,
as shown below: ::

    class Todo1(LinkedResource):
        [...]
        def get(self):
            # Default to 200 OK
            return {'task': 'Hello world'}
    
    class Todo2(LinkedResource):
        [...]
        def get(self):
            # Set the response code to 201
            return {'task': 'Hello world'}, 201
    
    class Todo3(LinkedResource):
        [...]
        def get(self):
            # Set the response code to 201 and return custom headers
            return {'task': 'Hello world'}, 201, {'Etag': 'some-opaque-string'}


Linking and embedding Resources
-------------------------------

Flask Restful supports HAL representation, you can learn more about it here : http://stateless.co/hal_specification.html

This is a sample showing how to generate links or embed resources within resources.

    class Office(LinkedResource):
        _self = '/town/office/<OFFICE_ID>'

        @Verb(output_fields=output(message=String))
        def get(self, OFFICE_ID=None):
            return output(message="This is the office called [%s]" % OFFICE_ID)


    class House(LinkedResource):
        _self = '/town/house/<HOUSE_ID>'

        @Verb(output_fields=output(message=String))
        def get(self, HOUSE_ID=None):
            return output(message="This is the house called : [%s]" % HOUSE_ID)


    class Town(LinkedResource):
        _self = '/town'

        @Verb(output_fields=output(Houses=House),
              output_links=link(Offices=Office))
        def get(self):
            return output(Houses=Embed(House, {"HOUSE_ID": "Simpsons"}), Offices=ResourceLink(Office, params={'OFFICE_ID': 'Twilio HQ'}))

This will generate a Town resource with a link to a single office and embed an House in the response.

Argument Parsing
----------------

While Flask provides easy access to request data (i.e. querysting or POST form
encoded data), it’s still a pain to validate form data. Flask-RESTful has
built-in support for request data validation using a library similar to
`argparse <http://docs.python.org/dev/library/argparse.html>`_. ::

Here is an example of how do declare arguments for

    class Call(LinkedResource):
        @Verb(parameters(To=Argument(location='args', type=str),
                     From=Argument(location='args', type=str),
                     Status=Argument(location='args', choices=('', 'queued', 'ringing', 'in-progress', 'completed', 'failed', 'busy', 'no-answer'),
                                     help='queued, ringing, in-progress, completed, failed, busy, or no-answer'),
                     StartTime=Argument(location='args', type=Date, help='An ISO 8601 date/time/duration')),


Using the reqparse module also gives you sane error messages for free. If an
argument fails to pass validation, Flask-RESTful will respond with a 400 Bad
Request and a response highlighting the error. ::

    $ curl -d 'rate=foo' http://127.0.0.1:5000/
    {'status': 400, 'message': 'foo cannot be converted to int'}


The ``types`` module provides a number of included common conversion functions
such as ``date`` and ``url``.

