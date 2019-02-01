.. _testing:

Running the Tests
=================

A ``Makefile`` is included to take care of setting up a virtualenv for running tests. All you need to do is run::

    $ make test

To change the Python version used to run the tests (default is Python 2.7), change the ``PYTHON_MAJOR`` and ``PYTHON_MINOR`` variables at the top of the ``Makefile``.

You can run on all supported versions with::

    $ make test-all

Individual tests can be run using a command with the format::

    nosetests <filename>:ClassName.func_name

Example::

    $ source env/bin/activate
    $ nosetests tests/test_reqparse.py:ReqParseTestCase.test_parse_choices_insensitive

Alternately, if you push changes to your fork on Github, Travis will run the tests
for your branch automatically.

A Tox config file is also provided so you can test against multiple python
versions locally (2.7, 3.4, 3.5, 3.6, 3.7) ::

    $ tox
