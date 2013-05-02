.. _declarative:

Using the integrated paging feature.
====================================

.. currentmodule:: flask.ext.restful

The paging mechanism in flask-restful is now standardized and use a encrypted bookmark to track the current page of your list resources.


Callback to implement
---------------------

The paging mechanism is based on callback, you need to give one with the following signature: ::


    def fetch_houses(filters, bookmark, page_size):

Where:
  filters will be a dictionary of the current url parameters your user used on the list resource.
  bookmark the plain text bookmark position he wants to retreive
  page_size the number of elements requested


You need to return from this callback a tuple : ::


    return (objects, next_bookmark, approx_set_size)

Where:
  objects is the list of links or embedded resources you want to return.
  next_bookmark is the bookmark in clear text for the next position
  approx_set_size is a hint for the user of the total size of the set (or total number of pages), on most systems it will be too expensive to count exactly.


