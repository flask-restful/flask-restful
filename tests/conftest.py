import pytest
from flask import Flask

import flask_restful


@pytest.fixture()
def app():
    return Flask(__name__)


@pytest.fixture()
def api(app):
    return flask_restful.Api(app)
