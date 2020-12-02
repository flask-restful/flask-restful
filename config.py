import os
basedir = os.path.abspath(os.path.dirname(__file__))
# mysql://username:password@server/db

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vCQXcMwOYBOgktYzm5ls9SzcxS3kqlHpN9ZWaosaqeDO5vgxiqL9'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://fr:fr@localhost/fr'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

