#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

PY26 = sys.version_info[:2] == (2, 6,)

requirements = [
    'aniso8601>=0.82',
    'Flask>=0.8',
    'six>=1.3.0',
    'pytz',
]
if PY26:
    requirements.append('ordereddict')

setup(
    name='Flask-RESTful',
    version='0.3.1',
    url='https://www.github.com/flask-restful/flask-restful/',
    author='Twilio API Team',
    author_email='help@twilio.com',
    description='Simple framework for creating REST APIs',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    install_requires=requirements,
    tests_require=['Flask-RESTful[paging]', 'mock>=0.8', 'blinker'],
    # Install these with "pip install -e '.[paging]'" or '.[docs]'
    extras_require={
        'paging': 'pycrypto>=2.6',
        'docs': 'sphinx',
    }
)
