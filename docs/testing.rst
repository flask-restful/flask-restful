.. _testing:

Running the Tests
=================

To run the Flask-RESTful test suite, you need to do two things.

1. Install the extra required dependency ::

       pip install -e '.[paging]' --use-mirrors

2. Run the tests ::

       python setup.py nosetests

Alternately, push changes to your fork on Github, and Travis will run the tests
for your branch automatically.

A Tox config file is also provided so you can test against multiple python
versions locally (2.6, 2.7, 3.3, and 3.4) ::

       $ tox
