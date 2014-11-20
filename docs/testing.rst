.. _testing:

Running the Tests
=================

Test setup (see the Makefile if you want to do this manually): ::

       make test-install

Run test suite: ::

       make test

To run an individual test, you need to be inside the venv that ``make test-install`` created.
Use the nosetests convention of ``nosetests <filename>:ClassName.func_name`` to run one test. ::

       source ./venv/bin/activate
       nosetests tests/test_reqparse.py:ReqParseTestCase.test_parse_choices_insensitive

Alternately, push changes to your fork on Github, and Travis will run the tests
for your branch automatically.
