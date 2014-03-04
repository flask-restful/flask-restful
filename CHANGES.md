Flask-RESTful Changelog
=======================

Here you can see the full list of changes between each Flask-RESTful release.

Version 0.2.12
--------------

Released March 4, 2014

- Fixed a bug in error handling code.
- Don't install tests by default.
- Doc fixes and updates.

Version 0.2.11
--------------

Released January 17, 2014

- Fixes the List field when marshalling a list of dictionaries. ([#165](https://github.com/twilio/flask-restful/issues/165))
- Adds Boolean and Price types to fields.__all__ ([#180](https://github.com/twilio/flask-restful/issues/180))
- Adds support for serializing a set object with a List field. ([#175](https://github.com/twilio/flask-restful/pull/175))
- Fixes support for using callables as reqparser type arguments ([#167](https://github.com/twilio/flask-restful/pull/167))
- Add configuration variable to control smart-errors behavior on 404 responses. ([#181](https://github.com/twilio/flask-restful/issues/181))
- Fixes bug preventing use of Flask redirects. ([#162](https://github.com/twilio/flask-restful/pull/162))
- Documentation fixes ([#173](https://github.com/twilio/flask-restful/pull/173))
- Fixes bug swallowing tracebacks in handle_error. ([#166](https://github.com/twilio/flask-restful/pull/166))

Version 0.2.10
--------------

Released December 17, 2013

- Removes twilio-specific type checks present in version 0.2.9.
- Correctly bump version number in setup.py.

Version 0.2.9
-------------

Released December 17, 2013.

- Adds new `positive` and `iso8601interval` types.
- Typo fix.
- Updating the test infrastructure to use common Twilio conventions and testing
  styles.

Version 0.2.8
-------------

Released November 22, 2013

- Add 'absolute' and 'scheme' to fields.Url

Version 0.2.6
-------------

Released November 18, 2013

- blueprint support
- CORS support
- allow custom unauthorized response
- when failing to marshal custom indexable objects, its attributes are checked
- better error messages

Version 0.2.5
-------------

Released Aug 6, 2013

- add callable location
- allow field type Fixed to take an attribute argument
- added url_for() wrapper as Api.url_for(resource)

Version 0.2.4
-------------

Released Aug 5, 2013

- Python 3.3 support.
- You can now marshal nested fields.
- Small fixes in docs.

Version 0.2.2
-------------

Released on May 5, 2013

- JSON will be pretty-printed if you're running your app in debug mode.
- pycrypto is now an optional dependency.

Version 0.2.1
-------------

Released on April 9, 2013

- Use the default Flask-RESTful error handler, instead of the default Flask
  error handler, to handle 405 Not Allowed errors on requests to Api endpoints.

Version 0.2.0
-------------

Released on April 9, 2013

- Flask-RESTful will no longer clobber your app's error handler; it will only
handle errors that occur while handling Flask-RESTful routes. The breaking
change is that 404 errors will default to using the Flask text/html error
handler. Override this behavior by passing `catch_all_404s=True` to the `Api`
constructor. (via [@yaniv-aknin]( /yaniv-aknin ))
- Arguments can now take `location` as a tuple, in case you want to
specify that an argument could be passed in multiple places. (via
[@mindflayer](/mindflayer))
- Fixes a problem where passing an empty post body to a resource that expected
  a json argument would throw a 500.
- Creation of the `Api` and initialization of the Flask `app` are no longer
  bundled together. (via [@andrew-d](/andrew-d))
- `marshal_with` now works with responses that are tuples. (via
[@noise](/noise))
- `types.url` will no longer throw a ascii decoding ValueError if you pass it
Unicode characters

Version 0.1.7
-------------

Released on March 24, 2013

The first released version of 0.1.6 contained a problem with the tar.gz
uploaded to PyPI. 0.1.7 contains the same changes as 0.1.6 but ensures the
version you download from PyPI does not contain problems (if for example, you
cached the old, broken version of 0.1.6).

Version 0.1.6
-------------

Released on February 27th, 2013

- Update the documentation with a fuller example (https://github.com/twilio/flask-restful/pull/37)
- Update the test runner to use setuptools (https://github.com/twilio/flask-restful/pull/46)
- Don't set exception data if we have no data to set (https://github.com/twilio/flask-restful/pull/49)
- action='append' in the RequestParser always returns a list. (https://github.com/twilio/flask-restful/pull/41)

Version 0.1.5
-------------

Released on Jan 9th, 2013

- Fix error handler for exceptions that do not have a message


Version 0.1.4
-------------

Released on Jan 8th, 2013

- Crypto support for paging
- Added paging helper for resources
- Stricter arg parse
- Flask view arguments are no longer implicitly parsed by RequestParser
- Fixed incorrectly formatted err message


Version 0.1.3
-------------

Released on Jan 8th, 2013

- Smart 404 error in case of slight mistakes in the URL
- Scheme error message
- Attribute/key accessible namespace for reqparse
- Add Namespace with dual attribute/item access
- Added the original requested URI in the error
- Better message if user passes URL w/ no scheme
- Allow chaining of add_argument calls
- Fixed bug 21 : Endpoint name clash on different views
- Fixed string formatting for python 2.6
- Fixed dictionary comprehensions for python 2.6
- Fixed r'' for python 2.6


Version 0.1.2
-------------

Released on Nov 19th, 2012

- Fixed a bug in fields.Fixed when formatting a value of 0


Version 0.1.1
-------------

Released on Nov 19th, 2012

- Added the Fixed field


Version 0.1
-------------

First public release
