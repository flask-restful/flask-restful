#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Flask-RESTful',
    version='0.1',
    url='https://www.github.com/twilio/flask-restful/',
    author='Kyle Conroy',
    author_email='kyle@twilio.com',
    description='Simple framework for creating REST APIs',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
    ],
)
