.. _declarative:

The modern way of declarating resources.
========================================

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


    class Calls(LinkedResource):
        _self = '/v3/accounts/<Account_SID>/Calls'



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
