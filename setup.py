#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Flask-RESTful',
    version='0.2.6',
    url='https://www.github.com/twilio/flask-restful/',
    author='Kyle Conroy',
    author_email='help@twilio.com',
    description='Simple framework for creating REST APIs',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    setup_requires=[
        'nose>=1.1.2',
        'mock>=0.8',
        'blinker>=1.2',
    ],
    install_requires=[
        'Flask>=0.8',
        'six>=1.3.0',
    ],
    # Install these with "pip install -e '.[paging]'" or '.[docs]'
    extras_require={
        'paging': 'pycrypto>=2.6',
        'docs': 'sphinx',
    }
)
