.. _fields:

Output Fields
===============

.. currentmodule:: flask_restful


Flask-RESTful provides an easy way to control what data you actually render in
your response.  With the :mod:`fields` module, you can use whatever objects (ORM
models/custom classes/etc.) you want in your resource. :mod:`fields` also lets you
format and filter the response so you don't have to worry about exposing
internal data structures.

It's also very clear when looking at your code what data will be rendered and
how it will be formatted.


Basic Usage
-----------
You can define a dict or OrderedDict of fields whose keys are names of
attributes or keys on the object to render, and whose values are a class that
will format & return the value for that field.  This example has three fields:
two are :class:`~fields.String` and one is a :class:`~fields.DateTime`,
formatted as an RFC 822 date string (ISO 8601 is supported as well) ::

    from flask_restful import Resource, fields, marshal_with

    resource_fields = {
        'name': fields.String,
        'address': fields.String,
        'date_updated': fields.DateTime(dt_format='rfc822'),
    }

    class Todo(Resource):
        @marshal_with(resource_fields, envelope='resource')
        def get(self, **kwargs):
            return db_get_todo()  # Some function that queries the db


This example assumes that you have a custom database object (``todo``) that
has attributes ``name``, ``address``, and ``date_updated``.  Any additional
attributes on the object are considered private and won't be rendered in the
output. An optional ``envelope`` keyword argument is specified to wrap the
resulting output.

The decorator :class:`marshal_with` is what actually takes your data object and
applies the field filtering.  The marshalling can work on single objects,
dicts, or lists of objects.

.. note ::

    :class:`marshal_with` is a convenience decorator, that is functionally
    equivalent to ::

        class Todo(Resource):
            def get(self, **kwargs):
                return marshal(db_get_todo(), resource_fields), 200

This explicit expression can be used to return HTTP status codes other than 200
along with a successful response (see :func:`abort` for errors).


Renaming Attributes
-------------------

Often times your public facing field name is different from your internal field
name. To configure this mapping, use the ``attribute`` keyword argument. ::

    fields = {
        'name': fields.String(attribute='private_name'),
        'address': fields.String,
    }

A lambda (or any callable) can also be specified as the ``attribute`` ::

    fields = {
        'name': fields.String(attribute=lambda x: x._private_name),
        'address': fields.String,
    }

Nested properties can also be accessed with ``attribute`` ::

    fields = {
        'name': fields.String(attribute='people_list.0.person_dictionary.name'),
        'address': fields.String,
    }


Default Values
--------------

If for some reason your data object doesn't have an attribute in your fields
list, you can specify a default value to return instead of ``None``. ::

    fields = {
        'name': fields.String(default='Anonymous User'),
        'address': fields.String,
    }


Custom Fields & Multiple Values
-------------------------------

Sometimes you have your own custom formatting needs.  You can subclass the
:class:`fields.Raw` class and implement the ``format`` function.  This is especially
useful when an attribute stores multiple pieces of information. e.g. a
bit-field whose individual bits represent distinct values.  You can use fields
to multiplex a single attribute to multiple output values.


This example assumes that bit 1 in the ``flags`` attribute signifies a
"Normal" or "Urgent" item, and bit 2 signifies "Read" or "Unread".  These
items might be easy to store in a bitfield, but for a human readable output
it's nice to convert them to separate string fields. ::

    class UrgentItem(fields.Raw):
        def format(self, value):
            return "Urgent" if value & 0x01 else "Normal"

    class UnreadItem(fields.Raw):
        def format(self, value):
            return "Unread" if value & 0x02 else "Read"

    fields = {
        'name': fields.String,
        'priority': UrgentItem(attribute='flags'),
        'status': UnreadItem(attribute='flags'),
    }

Url & Other Concrete Fields
---------------------------

Flask-RESTful includes a special field, :class:`fields.Url`, that synthesizes a
uri for the resource that's being requested. This is also a good example of how
to add data to your response that's not actually present on your data object.::

    class RandomNumber(fields.Raw):
        def output(self, key, obj):
            return random.random()

    fields = {
        'name': fields.String,
        # todo_resource is the endpoint name when you called api.add_resource()
        'uri': fields.Url('todo_resource'),
        'random': RandomNumber,
    }


By default :class:`fields.Url` returns a relative uri. To generate an absolute uri
that includes the scheme, hostname and port, pass the keyword argument
``absolute=True`` in the field declaration. To override the default scheme,
pass the ``scheme`` keyword argument::

    fields = {
        'uri': fields.Url('todo_resource', absolute=True),
        'https_uri': fields.Url('todo_resource', absolute=True, scheme='https')
    }

Complex Structures
------------------

You can have a flat structure that :meth:`marshal` will
transform to a nested structure ::

    >>> from flask_restful import fields, marshal
    >>> import json
    >>>
    >>> resource_fields = {'name': fields.String}
    >>> resource_fields['address'] = {}
    >>> resource_fields['address']['line 1'] = fields.String(attribute='addr1')
    >>> resource_fields['address']['line 2'] = fields.String(attribute='addr2')
    >>> resource_fields['address']['city'] = fields.String
    >>> resource_fields['address']['state'] = fields.String
    >>> resource_fields['address']['zip'] = fields.String
    >>> data = {'name': 'bob', 'addr1': '123 fake street', 'addr2': '', 'city': 'New York', 'state': 'NY', 'zip': '10468'}
    >>> json.dumps(marshal(data, resource_fields))
    '{"name": "bob", "address": {"line 1": "123 fake street", "line 2": "", "state": "NY", "zip": "10468", "city": "New York"}}'

.. note ::
    The address field doesn't actually exist on the data object, but any of
    the sub-fields can access attributes directly from the object as if they
    were not nested.

.. _list-field:

List Field
----------

You can also unmarshal fields as lists ::

    >>> from flask_restful import fields, marshal
    >>> import json
    >>>
    >>> resource_fields = {'name': fields.String, 'first_names': fields.List(fields.String)}
    >>> data = {'name': 'Bougnazal', 'first_names' : ['Emile', 'Raoul']}
    >>> json.dumps(marshal(data, resource_fields))
    >>> '{"first_names": ["Emile", "Raoul"], "name": "Bougnazal"}'

.. _nested-field:

Advanced : Nested Field
-----------------------

While nesting fields using dicts can turn a flat data object into a nested
response, you can use :class:`~fields.Nested` to unmarshal nested data
structures and render them appropriately. ::

    >>> from flask_restful import fields, marshal
    >>> import json
    >>>
    >>> address_fields = {}
    >>> address_fields['line 1'] = fields.String(attribute='addr1')
    >>> address_fields['line 2'] = fields.String(attribute='addr2')
    >>> address_fields['city'] = fields.String(attribute='city')
    >>> address_fields['state'] = fields.String(attribute='state')
    >>> address_fields['zip'] = fields.String(attribute='zip')
    >>>
    >>> resource_fields = {}
    >>> resource_fields['name'] = fields.String
    >>> resource_fields['billing_address'] = fields.Nested(address_fields)
    >>> resource_fields['shipping_address'] = fields.Nested(address_fields)
    >>> address1 = {'addr1': '123 fake street', 'city': 'New York', 'state': 'NY', 'zip': '10468'}
    >>> address2 = {'addr1': '555 nowhere', 'city': 'New York', 'state': 'NY', 'zip': '10468'}
    >>> data = { 'name': 'bob', 'billing_address': address1, 'shipping_address': address2}
    >>>
    >>> json.dumps(marshal_with(data, resource_fields))
    '{"billing_address": {"line 1": "123 fake street", "line 2": null, "state": "NY", "zip": "10468", "city": "New York"}, "name": "bob", "shipping_address": {"line 1": "555 nowhere", "line 2": null, "state": "NY", "zip": "10468", "city": "New York"}}'

This example uses two ``Nested`` fields. The ``Nested`` constructor takes a
dict of fields to render as sub-fields. The important difference between
the ``Nested`` constructor and nested dicts (previous example), is the context
for attributes. In this example, ``billing_address`` is a complex object that
has its own fields and the context passed to the nested field is the sub-object
instead of the original ``data`` object. In other words:
``data.billing_address.addr1`` is in scope here, whereas in the previous
example ``data.addr1`` was the location attribute. Remember: ``Nested`` and
``List`` objects create a new scope for attributes.

Use :class:`~fields.Nested` with :class:`~fields.List` to marshal lists of more
complex objects: ::

    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
    }

    user_list_fields = {
        fields.List(fields.Nested(user_fields)),
    }
