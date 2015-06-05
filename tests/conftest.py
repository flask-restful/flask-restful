#!/usr/bin/env python

import pytest

from flask import Flask
from flask_restful import Api


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def api(app):
    return Api(app)
