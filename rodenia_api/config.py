"""Default configuration

Use env var to override
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
SECRET_KEY = "changeme"

SQLALCHEMY_DATABASE_URI = "postgresql:///rodenia_api"
SQLALCHEMY_TRACK_MODIFICATIONS = False

PROPAGATE_EXCEPTIONS = True
SIGHTENGINE_API_USER = os.environ.get('SIGHTENGINE_API_USER')
SIGHTENGINE_API_KEY = os.environ.get('SIGHTENGINE_API_KEY')
