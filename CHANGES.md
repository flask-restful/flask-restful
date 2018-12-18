Flask-RESTful Changelog
=======================

Here you can see the full list of changes between each Flask-RESTful release.

Version 0.3.7
-------------

Released December 18, 2018

- Fix error handling in python3 ([#696](https://github.com/flask-restful/flask-restful/pull/696))
- Fix arguments with type=list ([#705](https://github.com/flask-restful/flask-restful/pull/705))
- Return code for `parse_args()` is now configurable ([#722](https://github.com/flask-restful/flask-restful/pull/722))
- Removed `flask_restful.paging` module.
- Removed misleading `help_on_404` functionality ([#722](https://github.com/flask-restful/flask-restful/pull/722))
- JSON keys are no longer sorted by default in debug mode in python3 ([#680](https://github.com/flask-restful/flask-restful/pull/680))
- Various small fixes and updates to documentation

Version 0.3.6
-------------

Released May 31, 2017

- `Argument.help` now supports unicode strings ([#564](https://github.com/flask-restful/flask-restful/pull/564))
- Flags can now be passed to `inputs.regex` ([#621](https://github.com/flask-restful/flask-restful/pull/621))
- Fix behavior of `action='append'` in conjunction with `location='json'` ([#645](https://github.com/flask-restful/flask-restful/pull/645))
- `method_decorators` can be a `dict` to apply decorator behavior for only specific HTTP methods ([#532](https://github.com/flask-restful/flask-restful/pull/532))
- JSON keys are no longer sorted by default in debug mode in python3 ([#680](https://github.com/flask-restful/flask-restful/pull/680))
- Various small fixes and updates to documentation

Version 0.3.5
-------------

Released December 9, 2015

- Add `nullable` option to request parser to allow/disallow null values for arguments ([#538](https://github.com/flask-restful/flask-restful/pull/538))
- Use Flask's exception log method in `handle_error(e)` method instead of directly logging the exception notice. ([#496](https://github.com/flask-restful/flask-restful/pull/496))
- `Argument.help` now allows more flexible message formatting using the `{error_msg}` string interpolation token. ([#518](https://github.com/flask-restful/flask-restful/pull/518))
- Prevent representation from being chosen at random when `Accept: */*` ([#524](https://github.com/flask-restful/flask-restful/pull/524))
- Headers from `HTTPException`s are now returned in the response instead of being discarded ([#523](https://github.com/flask-restful/flask-restful/pull/523))
- Marshalling now checks for a `__marshallable__` method first before defaulting back to `__getitem__` ([](https://github.com/flask-restful/flask-restful/issues/324))
- Flask 1.0 compatability fixes ([#506](https://github.com/flask-restful/flask-restful/pull/506))

Version 0.3.4
-------------

Released July 20, 2015

- Fixed issue where `abort()` and `raise Exception` were not equivalent ([#205](https://github.com/flask-restful/flask-restful/issues/205))
- Fixed `RequestParser` settings not being copied properly ([#483](https://github.com/flask-restful/flask-restful/pull/483))
- Add ability to configure json serializer settings from application config ([#458](https://github.com/flask-restful/flask-restful/pull/458))
- Project metadata, tests, and examples are now included in source distributions ([#475](https://github.com/flask-restful/flask-restful/issues/475))
- Various documentation improvements

Version 0.3.3
-------------

Released May 22, 2015

- Disable [challenge on 401](https://github.com/flask-restful/flask-restful/commit/fe53f49bdc28dd83ee3acbeb0a313b411411e377)
  by default (**THIS IS A BREAKING CHANGE**, albeit a very small one with behavior that probably no one depended upon. You can easily change this back to the old way).
- Doc fixes ([#404](https://github.com/flask-restful/flask-restful/pull/404), [#406](https://github.com/flask-restful/flask-restful/pull/406), [#436](https://github.com/flask-restful/flask-restful/pull/436), misc. other commits)
- Fix truncation of microseconds in iso8601 datetime output ([#368](https://github.com/flask-restful/flask-restful/pull/405))
- `null` arguments from JSON no longer cast to string ([#390](https://github.com/flask-restful/flask-restful/pull/390))
- Made list fields work with classes ([#409](https://github.com/flask-restful/flask-restful/pull/409))
- Fix `url_for()` when used with Blueprints ([#410](https://github.com/flask-restful/flask-restful/pull/410))
- Add CORS "Access-Control-Expose-Headers" support ([#412](https://github.com/flask-restful/flask-restful/pull/412))
- Fix class references in RequestParser ([#414](https://github.com/flask-restful/flask-restful/pull/414))
- Allow any callables to be used as lazy attributes ([#417](https://github.com/flask-restful/flask-restful/pull/417))
- Fix references to `flask.ext.*` ([#420](https://github.com/flask-restful/flask-restful/issues/420))
- Trim support with fixes ([#428](https://github.com/flask-restful/flask-restful/pull/428))
- Added ability to pass-in parameters into Resource constructors ([#444](https://github.com/flask-restful/flask-restful/pull/444))
- Fix custom type docs on "Intermediate usage" and docstring ([#434](https://github.com/flask-restful/flask-restful/pull/434))
- Fixed problem with `RequestParser.copy` ([#435](https://github.com/flask-restful/flask-restful/pull/435))
- Feature/error bundling ([#431](https://github.com/flask-restful/flask-restful/pull/431))
- Explicitly check the class type for `propagate_exceptions` ([#445](https://github.com/flask-restful/flask-restful/pull/445))
- Remove min. year limit 1900 in `inputs.date` ([#446](https://github.com/flask-restful/flask-restful/pull/446))

Version 0.3.2
-------------

Released February 25, 2015

- Doc fixes ([#344](https://github.com/flask-restful/flask-restful/pull/344), [#378](https://github.com/flask-restful/flask-restful/issues/378), [#402](https://github.com/flask-restful/flask-restful/pull/402))
- Microseconds no longer truncated in ISO8601 format datetime inputs ([#381](https://github.com/flask-restful/flask-restful/pull/381))
- Datetime inputs now preserve timezone instead of forcing conversion to UTC ([#381](https://github.com/flask-restful/flask-restful/pull/381))
- Fixes content negotiation to respect q-values ([#245](https://github.com/flask-restful/flask-restful/pull/245))
- Fix `fields.URL` when used with Blueprints ([#379](https://github.com/flask-restful/flask-restful/pull/379))
- Fix `BadRequest` raised with empty body and `application/json` content type ([#366](https://github.com/flask-restful/flask-restful/pull/366))
- Improved argument validation error messages ([#386](https://github.com/flask-restful/flask-restful/pull/386))
- Allow custom validation for `FileStorage` type arguments ([#388](https://github.com/flask-restful/flask-restful/pull/388))
- Allow lambdas to be specified for field attributes ([#309](https://github.com/flask-restful/flask-restful/pull/309))
- Added regex input validator ([#374](https://github.com/flask-restful/flask-restful/pull/374))

Version 0.3.1
-------------

Released December 13, 2014

- Adds `strict` option to `parse_args()` ([#358](https://github.com/flask-restful/flask-restful/pull/358))
- Adds an option to envelop marshaled objects ([#349](https://github.com/flask-restful/flask-restful/pull/349))
- Fixes initialization of `Api.blueprint` attribute ([#263](https://github.com/flask-restful/flask-restful/pull/263))
- Makes `Api.error_router` fall back to Flask handlers ([#296](https://github.com/flask-restful/flask-restful/pull/296)/[#356](https://github.com/flask-restful/flask-restful/pull/356))
- Makes docs more viewable on mobile devices ([#347](https://github.com/flask-restful/flask-restful/issues/347))
- Wheel distribution is now universal ([#363](https://github.com/flask-restful/flask-restful/issues/363))

Version 0.3.0
--------------

Released November 22, 2014

- Adds `@api.resource` decorator ([#311](https://github.com/flask-restful/flask-restful/pull/311))
- Adds custom error handling ([#225](https://github.com/flask-restful/flask-restful/pull/225))
- Adds `RequestParser` inheritance ([#249](https://github.com/flask-restful/flask-restful/pull/249))
- Adds 1/0 as valid values for `inputs.boolean` ([#341](https://github.com/flask-restful/flask-restful/pull/341))
- Improved `datetime` serialization and deserialization ([#345](https://github.com/flask-restful/flask-restful/pull/345))
- `init_app` now follows Flask extension guidelines ([#130](https://github.com/flask-restful/flask-restful/pull/130))
- `types` module renamed to `inputs` ([#243](https://github.com/flask-restful/flask-restful/pull/243))
- Fixes `inputs.boolean` inability to parse values from JSON ([#314](https://github.com/flask-restful/flask-restful/pull/314))
- Fixes `RequestParser` inability to use arguments from multiple sources at once ([#261](https://github.com/flask-restful/flask-restful/pull/261))
- Fixes missing `Allow` header when HTTP 405 is returned ([#294](https://github.com/flask-restful/flask-restful/pull/294))
- Doc fixes and updates.


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
- Adds Boolean and Price types to fields.\_\_all\_\_ ([#180](https://github.com/twilio/flask-restful/issues/180))
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
