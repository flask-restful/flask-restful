.. _api:

API Docs
========

.. module:: flask.ext.restful


.. autofunction:: marshal
.. autofunction:: marshal_with
.. autofunction:: marshal_with_field
.. autofunction:: abort


Api
---
.. autoclass:: Api
   :members:

    .. automethod:: unauthorized

.. autoclass:: Resource
   :members:

ReqParse
--------
.. module:: reqparse

.. autoclass:: RequestParser
   :members:

.. autoclass:: Argument
   :members:

   .. automethod:: __init__

Fields
------
.. automodule:: fields
   :members:

Inputs
-----

.. module:: flask.ext.restful.inputs 
.. autofunction:: url
.. autofunction:: date
.. autofunction:: iso8601interval
.. autofunction:: natural 
.. autofunction:: boolean
.. autofunction:: rfc822
