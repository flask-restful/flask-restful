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
