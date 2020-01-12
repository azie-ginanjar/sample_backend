import os

"""Default configuration

Use env var to override
"""
DEBUG = False
SECRET_KEY = "3796a924-4508-4abe-9ae2-925252f4cf3d"

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SENTRY_DSN = os.environ['SENTRY_DSN']